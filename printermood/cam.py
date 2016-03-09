from __future__ import print_function
import argparse
import dlib
import sys
import logging
import time

try:
    import cv2
    import numpy
except ImportError:
    # Hack in site path for opencv and numpy
    sys.path.append('/usr/lib/python3/dist-packages/')
    import cv2
    import numpy


CV2_VERSION = tuple(map(lambda x: int(x), cv2.__version__.split('.')))
logger = logging.getLogger(__name__)


class FaceCamera(object):
    def __init__(self, cascade_path, fps=25, show_preview=False):
        self.fps = fps
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.object_tracker = None
        self.show_preview = show_preview
        self.video_capture = None

    def _sharpness(self, face):
        gy, gx = numpy.gradient(face)
        norm = gx**2 + gy**2
        return numpy.average(norm)

    def _better_face(self, face1, face2):
        sharpness1 = self._sharpness(face1)
        sharpness2 = self._sharpness(face2)
        return sharpness1 > sharpness2

    def capture_frame(self):
        ret, frame = self.video_capture.read()
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def get_face_locations(self, frame):
        if CV2_VERSION < (3, 0, 0):
            flags = cv2.cv.CV_HAAR_SCALE_IMAGE
        else:
            flags = cv2.CASCADE_SCALE_IMAGE

        return self.face_cascade.detectMultiScale(
            frame,
            scaleFactor=1.1,
            minNeighbors=7,
            minSize=(60, 90),
            flags=flags,
        )

    def extract_face(self, frame, rect):
        x, y, w, h = rect
        return frame[y:y+h, x:x+w]

    def get_rect(self, face, margins_x=30, margins_y=80):
        x, y, w, h = face

        return (
            max(0, x - margins_x),
            max(0, y - margins_y),
            w + 2 * margins_x,
            h + 2 * margins_y,
        )

    def draw_rect(self, frame, rect):
        x, y, w, h = rect
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    def start(self):
        self.video_capture = cv2.VideoCapture(0)

    def _wait_for_faces(self):
        seconds_per_frame = 1.0 / self.fps
        while True:
            start_time = time.time()
            frame = self.capture_frame()
            faces = self.get_face_locations(frame)
            end_time = time.time()
            duration_s = end_time - start_time

            if len(faces) > 0:
                return frame, faces

            sleep_str = ''
            if duration_s < seconds_per_frame:
                sleep_for = seconds_per_frame - duration_s
                time.sleep(sleep_for)
                sleep_str = ' (slept for %0.2fms)' % (sleep_for * 1000,)

            logger.debug("Time per frame: %0.2fms%s",
                         duration_s * 1000,
                         sleep_str)

    def detect(self):
        frame, faces = self._wait_for_faces()
        logger.debug('Found %d faces at locations %s.',
                     len(faces),
                     ', '.join(map(str, faces)))

        if len(faces) == 0:
            return []

        # We care only about the first person in the picture for now
        face = faces[0]
        x, y, w, h = map(int, face)
        face_rectangle = dlib.rectangle(x, y, x+w, y+h)

        # This will eventually be returned from this function. List of all
        # faces for this person:
        face_series = [self.extract_face(frame, rect=face)]

        # Initialize the object tracker:
        self.object_tracker = dlib.correlation_tracker()
        self.object_tracker.start_track(frame, face_rectangle)

        logger.info("Starting tracking using dlib.correlation_tracker.")
        while True:
            frame = self.capture_frame()
            psr = self.object_tracker.update(frame)
            if psr < 10:
                return face_series

            position = self.object_tracker.get_position()
            rectangle = (int(position.left()),
                         int(position.top()),
                         int(position.width()),
                         int(position.height()))

            face_series.append(self.extract_face(frame, rect=rectangle))
            self.draw_rect(frame, rectangle)
            if self.show_preview:
                cv2.imshow('Preview', frame)
                if cv2.waitKey(1) & 0xFF in map(ord, list('cq')):
                    return None

    def stop(self):
        if self.video_capture:
            self.video_capture.release()
        cv2.destroyAllWindows()


def get_arguments():
    argument_parser = argparse.ArgumentParser(
        description="Face detection script."
    )
    argument_parser.add_argument(
        '-c',
        '--cascade',
        action='store',
        default='printermood/haarcascade_frontalface_default.xml',
    )
    argument_parser.add_argument(
        '-p',
        '--preview',
        action='store_true',
    )
    return argument_parser.parse_args()


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

    args = get_arguments()
    haar = args.cascade

    try:
        open(haar, 'r').close()
    except IOError:
        logger.error('Given cascade "%s" does not exist!', haar)
        sys.exit(1)

    cam = FaceCamera(haar, show_preview=args.preview)
    cam.start()

    try:
        face_series = cam.detect()
        logger.debug('A series of %d images was returned.', len(face_series))
        cv2.destroyAllWindows()
        if args.preview:
            for frame in face_series:
                cv2.imshow('Video', frame)
                if cv2.waitKey(100) & 0xFF in map(ord, list('cq')):
                    sys.exit(0)
        else:
            print('Preview disabled. Camera returned {0} images of faces'.format(len(face_series)))
    except KeyboardInterrupt:
        pass
    finally:
        print("Closing...", end='')
        cam.stop()
        print('done!')
