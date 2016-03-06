from __future__ import print_function
import argparse
import sys
import dlib
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
    def __init__(self, cascade_path, fps=25, delay=0.5, show_preview=False):
        self.fps = fps
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.face_extraction_delay = delay
        self.show_preview = show_preview
        self.video_capture = None
        self._face_store = []

    def _faces_overlapping(self, face1, face2):
        f1_x1, f1_x2 = face1[0], face1[0] + face1[2]
        f1_y1, f1_y2 = face1[1], face1[1] + face1[3]

        f2_x1, f2_x2 = face2[0], face2[0] + face2[2]
        f2_y1, f2_y2 = face2[1], face2[1] + face2[3]

        op_x1 = f1_x1 <= f2_x1 <= f1_x2
        op_x2 = f2_x1 <= f1_x1 <= f2_x2
        op_x =  op_x1 or op_x2

        op_y1 = f2_y1 <= f1_y1 <= f2_y2
        op_y2 = f1_y1 <= f2_y1 <= f1_y2
        op_y = op_y1 or op_y2

        return op_x and op_y

    def _so_sharpness(self, face):
        gy, gx = numpy.gradient(face)
        norm = gx**2 + gy**2
        return numpy.average(norm)

    def _better_face(self, face1, face2):
        f = self._so_sharpness
        sharpness1 = f(face1)
        sharpness2 = f(face2)
        return sharpness1 > sharpness2

    def _update_face_store(self, face_coords, face_img):
        face_index = -1
        for index, stored_face_tuple in enumerate(self._face_store):
            if self._faces_overlapping(stored_face_tuple[1], face_coords):
                face_index = index
                break
        
        face_stored = cv2.resize(face_img, (120, int(120 * (float(face_coords[3]) / face_coords[2]))))

        if face_index >= 0:
            t, old_coords, img, face = self._face_store[face_index]
            if self._better_face(face_img, img):
                img = face_img

            if time.time() - t > self.face_extraction_delay:
                del self._face_store[face_index]
                return img
            self._face_store[face_index] = ((t, face_coords, img, face_stored))
        else:
            self._face_store.append((time.time(), face_coords, face_img, face_stored))
            
    def capture_frame(self):
        ret, frame = self.video_capture.read()

        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


    def get_face_locations(self, frame):
        return self.face_cascade.detectMultiScale(
            frame,
            scaleFactor=1.1,
            minNeighbors=7,
            minSize=(60, 90),
            flags=cv2.cv.CV_HAAR_SCALE_IMAGE if CV2_VERSION < (3, 0, 0) else cv2.CASCADE_SCALE_IMAGE
        )

    def extract_face(self, frame, face=None, rect=None):
        assert face or rect
        if rect:
            x, y, w, h = rect
        else:
            x, y, w, h = self.get_rect(face)
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

    def loop(self):
        seconds_per_frame = 1.0 / self.fps
        while True:
            start_time = time.time()
            frame = self.capture_frame()
            faces = self.get_face_locations(frame)
            logger.debug('Found %d faces at locations %s.', len(faces), ', '.join(map(str, faces)))

            if self.show_preview:
                cv2.imshow('Preview', frame)

            ready_faces = []
            for face in faces:
                rect = self.get_rect(face)
                if self.show_preview:
                    self.draw_rect(frame, rect)

                face_img = self.extract_face(frame, rect=rect)
                ready_face = self._update_face_store(rect, face_img)
                if ready_face is not None:
                    ready_faces.append(ready_face)
    

            for ready_face in ready_faces:
                yield ready_face

            if cv2.waitKey(1) & 0xFF in map(ord, list('cq')):
                break

            end_time = time.time()
            duration_s = end_time - start_time

            sleep_str = ''
            if duration_s < seconds_per_frame:
                sleep_for = seconds_per_frame - duration_s
                time.sleep(sleep_for)
                sleep_str = ' (slept for %0.2fms)' % (sleep_for * 1000,)

            logger.debug("Time per frame: %0.2fms%s" % (duration_s * 1000, sleep_str))

    def stop(self):
        self.video_capture.release()
        cv2.destroyAllWindows()

    def __iter__(self):
        self.start()
        try:
            for face in self.loop():
                yield face
        finally:
            self.stop()


def get_arguments():
    argument_parser = argparse.ArgumentParser(description="Face detection script.")
    argument_parser.add_argument(
        '-c', 
        '--cascade', 
        action='store',
        default='printermood/haarcascade_frontalface_default.xml',
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

    cam = FaceCamera(haar, show_preview=True)

    try:
        for frame in cam:
            cv2.imshow('Video', frame)
    except KeyboardInterrupt:
        pass
    finally:
        print("Closing...", end='')
        cam.stop()
        print('done!')
   
