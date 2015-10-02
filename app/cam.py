import cv2
import sys


class FaceCamera(object):
    def __init__(self, cascade_path):
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def capture_frame(self, video_capture):
        ret, frame = video_capture.read()
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

    def extract_face(self, frame, face):
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
        video_capture = cv2.VideoCapture(0)

        try:
            while True:
                frame = self.capture_frame(video_capture)
                faces = self.get_face_locations(frame)

                for face in faces:
                    rect = self.get_rect(face)
                    self.draw_rect(frame, rect)
                    
                # Be nice, quit if asked
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                # Display the resulting frame
                cv2.imshow('Video', frame)
        finally:
            print "Closing...",
            video_capture.release()
            cv2.destroyAllWindows()
            print 'done!'


if __name__ == "__main__":
    cam = FaceCamera(sys.argv[1])
    try:
        cam.start()
    except KeyboardInterrupt:
        pass
   
