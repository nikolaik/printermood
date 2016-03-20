from __future__ import print_function
import argparse
import dlib
import sys
import logging
import time

import requests

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


class ImageLocation(object):
    def __init__(self, frame, location):
        self.frame = frame
        self.location = location
        self._face = None
        self._sharpness = None

    @property
    def face(self):
        if self._face is None:
            x, y, w, h = self.location
            self._face = self.frame[y:y+h, x:x+w]
        return self._face

    @property
    def sharpness(self):
        if self._sharpness is None:
            gy, gx = numpy.gradient(self.face)
            norm = gx**2 + gy**2
            self._sharpness = numpy.average(norm)
        return self._sharpness


class FaceCamera(object):
    def __init__(self, cascade_path, fps=25, show_preview=False):
        self.fps = fps
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.object_tracker = None
        self.show_preview = show_preview
        self.video_capture = None

    def capture_frame(self):
        ret, frame = self.video_capture.read()
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def get_faces(self, frame):
        if CV2_VERSION < (3, 0, 0):
            flags = cv2.cv.CV_HAAR_SCALE_IMAGE
        else:
            flags = cv2.CASCADE_SCALE_IMAGE

        rectangles = self.face_cascade.detectMultiScale(
            frame,
            scaleFactor=1.1,
            minNeighbors=7,
            minSize=(60, 90),
            flags=flags,
        )
        return [ImageLocation(frame, rectangle) for rectangle in rectangles]

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
            faces = self.get_faces(frame)
            end_time = time.time()
            duration_s = end_time - start_time

            if len(faces) > 0:
                return faces

            sleep_str = ''
            if duration_s < seconds_per_frame:
                sleep_for = seconds_per_frame - duration_s
                time.sleep(sleep_for)
                sleep_str = ' (slept for %0.2fms)' % (sleep_for * 1000,)

            logger.debug("Time per frame: %0.2fms%s",
                         duration_s * 1000,
                         sleep_str)

    def detect(self):
        faces = self._wait_for_faces()
        logger.debug('Found %d faces at locations %s.',
                     len(faces),
                     ', '.join(map(lambda x: str(x.location), faces)))

        if len(faces) == 0:
            return []

        # We care only about the first person in the picture for now
        face = faces[0]
        x, y, w, h = map(int, face.location)
        face_rectangle = dlib.rectangle(x, y, x+w, y+h)

        # This will eventually be returned from this function. List of all
        # faces for this person:
        face_series = [face]

        # Initialize the object tracker:
        self.object_tracker = dlib.correlation_tracker()
        self.object_tracker.start_track(face.frame, face_rectangle)

        logger.info("Starting tracking using dlib.correlation_tracker.")
        while True:
            frame = self.capture_frame()
            psr = self.object_tracker.update(frame)
            if psr < 8.0:
                return face_series

            position = self.object_tracker.get_position()
            rectangle = (int(position.left()),
                         int(position.top()),
                         int(position.width()),
                         int(position.height()))

            face_series.append(ImageLocation(frame, rectangle))
            self.draw_rect(frame, rectangle)
            if self.show_preview:
                cv2.imshow('Preview', frame)
                if cv2.waitKey(1) & 0xFF in map(ord, list('cq')):
                    return face_series

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
    argument_parser.add_argument(
        '-f',
        '--forward-url',
        action='store',
        default=None
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
            for image in face_series:
                face = image.face
                cv2.putText(face,
                            "Sharpness: %d" % image.sharpness, (50, 24),
                            cv2.FONT_HERSHEY_PLAIN,
                            1.0,
                            (180, 180, 180))
                cv2.imshow('Video', face)
                if cv2.waitKey(100) & 0xFF in map(ord, list('cq')):
                    sys.exit(0)
        else:
            msg = 'Preview disabled. Camera returned {0} images of faces'
            print(msg.format(len(face_series)))

        if args.forward_url is not None:
            for image in face_series:
                retval, jpeg_data = cv2.imencode('.jpg', image.face)
                jpeg_data = jpeg_data.tostring()
                res = requests.put(args.forward_url, files={'image': ('whatever.jpg', jpeg_data)})

                if res.status_code != 200:
                    logger.warning('Endpoint at {} returned HTTP {}'.format(args.forward_url, res.status_code))

    except KeyboardInterrupt:
        pass
    finally:
        print("Closing...", end='')
        cam.stop()
        print('done!')
