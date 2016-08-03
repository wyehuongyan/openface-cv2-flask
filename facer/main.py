from imutils.video import FPS
import sys
import os
import cv2
import openface

fileDir = os.path.dirname(os.path.realpath(__file__))
modelDir = os.path.join(fileDir, '..', 'models')
dlibModelDir = os.path.join(modelDir, 'dlib')
openfaceModelDir = os.path.join(modelDir, 'openface')

cascPath = sys.argv[1]
faceCascade = cv2.CascadeClassifier(cascPath)
align = openface.AlignDlib(os.path.join(dlibModelDir,
                                             "shape_predictor_68_face_landmarks.dat"))

# -1 = lifecam, 0 = iSight
video_capture = cv2.VideoCapture(-1)
video_capture.set(3,600)
video_capture.set(4,480)
fps = FPS().start()

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # faces = faceCascade.detectMultiScale(
    #     gray,
    #     scaleFactor=1.1,
    #     minNeighbors=5,
    #     minSize=(30, 30),
    #     flags=cv2.cv.CV_HAAR_SCALE_IMAGE
    # )

    # # Draw a rectangle around the faces
    # for (x, y, w, h) in faces:
    #     cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # openface face detection
    rgbImg = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    bbs = align.getAllFaceBoundingBoxes(rgbImg)
    if bbs is None:
        raise Exception("Unable to find a face: {}".format(rgbImg))

    for bb in bbs:
        bl = (bb.left(), bb.bottom())
        tr = (bb.right(), bb.top())
        cv2.rectangle(frame, bl, tr, (0, 255, 0), 2)	

    # Display the resulting frame
    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # update the FPS counter
	fps.update()

# When everything is done,
# stop the timer and display FPS information
# and release the capture
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
video_capture.release()
cv2.destroyAllWindows()