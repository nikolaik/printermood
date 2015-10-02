import cv2
import sys
import time


class FaceCamera(object):
    def __init__(self, cascade_path):
        self.video_capture = None
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self._face_extraction_delay = 2
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

    def _update_face_store(self, face_coords, face_img):
        face_index = -1
        for index, stored_face_tuple in enumerate(self._face_store):
            if self._faces_overlapping(stored_face_tuple[1], face_coords):
                face_index = index
                break
        
        if face_index >= 0:
            t, old_coords, img = self._face_store[face_index]
            if face_coords[2] > old_coords[2]:
                # bigger == better?
                img = face_img

            if time.time() - t > self._face_extraction_delay:
                del self._face_store[face_index]
                return img
            self._face_store[face_index] = ((t, face_coords, img))
        else:
            self._face_store.append((time.time(), face_coords, face_img))
            
    def capture_frame(self):
        ret, frame = self.video_capture.read()
        return frame


    def get_face_locations(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=7,
            minSize=(60, 90),
            flags=cv2.cv.CV_HAAR_SCALE_IMAGE
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
        while True:
            frame = self.capture_frame()
            faces = self.get_face_locations(frame)

            for face in faces:
                rect = self.get_rect(face)
                self.draw_rect(frame, rect)
                
            # Be nice, quit if asked
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # Display the resulting frame
            cv2.imshow('Video', frame)

    def stop(self):
        self.video_capture.release()
        cv2.destroyAllWindows()

    def __iter__(self):
        self.start()

        while True:
            frame = self.capture_frame()
            faces = self.get_face_locations(frame)

            ready_faces = []
            for face in faces:
                rect = self.get_rect(face)
                face_img = self.extract_face(frame, rect=rect)
                ready_face = self._update_face_store(rect, face_img)
                if ready_face is not None:
                    ready_faces.append(ready_face)
        
            for ready_face in ready_faces:
                yield ready_face

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.stop()

if __name__ == "__main__":
    cam = FaceCamera(sys.argv[1])
    try:
        for frame in cam:
            cv2.imshow('Video', frame)

        #cam.start()
        #cam.loop()
    except KeyboardInterrupt:
        pass
    finally:
        print "Closing...",
        cam.stop()
        print 'done!'
   
