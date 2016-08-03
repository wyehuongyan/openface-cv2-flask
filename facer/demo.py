# import the necessary packages
from __future__ import print_function
from imutils.video import WebcamVideoStream
from imutils.video import FPS
import argparse
import imutils
import os
import cv2
import openface
 
# directories
fileDir = os.path.dirname(os.path.realpath(__file__))
modelDir = os.path.join(fileDir, '..', 'models')
dlibModelDir = os.path.join(modelDir, 'dlib')
openfaceModelDir = os.path.join(modelDir, 'openface')

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-n", "--num-frames", type=int, default=100,
	help="# of frames to loop over for FPS test")
ap.add_argument("-d", "--display", type=int, default=-1,
	help="Whether or not frames should be displayed")
ap.add_argument("-c", "--cascade_classifier", type=str,
	help="The cascade classifier")
ap.add_argument('--dlibFacePredictor', type=str,
                        help="Path to dlib's face predictor.",
                        default=os.path.join(dlibModelDir,
                                             "shape_predictor_68_face_landmarks.dat"))
ap.add_argument('--imgDim', type=int,
                    help="Default image dimension.", default=96)

args = vars(ap.parse_args())

faceCascade = cv2.CascadeClassifier(args["cascade_classifier"])
align = openface.AlignDlib(args["dlibFacePredictor"])

# created a *threaded* video stream, allow the camera sensor to warmup,
# and start the FPS counter
print("[INFO] sampling THREADED frames from webcam...")
vs = WebcamVideoStream(src=0).start() # 0 = lifecam, 1 = iSight
fps = FPS().start()
 
# loop over some frames...this time using the threaded stream
#while fps._numFrames < args["num_frames"]:
while True:
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels
	frame = vs.read()
	frame = imutils.resize(frame, width=640)
 
 	# openface face detection
	rgbImg = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	bbs = align.getAllFaceBoundingBoxes(rgbImg)
	if bbs is None:
		raise Exception("Unable to find a face: {}".format(rgbImg))

	for bb in bbs:
		bl = (bb.left(), bb.bottom())
		tr = (bb.right(), bb.top())
		cv2.rectangle(frame, bl, tr, (0, 255, 0), 2)	
		landmarks = align.findLandmarks(rgbImg, bb)
		alignedFace = align.align(args["imgDim"], rgbImg, bb,
									landmarks=landmarks,
									landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE) 	
	# end of openface face detection

	# start of opencv face detection
	# gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	# faces = faceCascade.detectMultiScale(
	# 	gray,
	# 	scaleFactor=1.1,
	# 	minNeighbors=5,
	# 	minSize=(30, 30),
	# 	flags=cv2.cv.CV_HAAR_SCALE_IMAGE
	# )

	# # Draw a rectangle around the faces
	# for (x, y, w, h) in faces:
	# 	cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
	# end of opencv face detection

	# check to see if the frame should be displayed to our screen
	if args["display"] > 0:
		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF
 
	# update the FPS counter
	fps.update()
 
# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
 
# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()