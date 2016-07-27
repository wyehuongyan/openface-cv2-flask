import cv2
from app import app

class VideoCamera(object):
	def __init__(self):
		# Using OpenCV to capture from device 0. If you have trouble capturing
		# from a webcam, comment the line below out and use a video file
		# instead.
		app.logger.info("OpenCV version :  {0}".format(cv2.__version__))
		self.video = cv2.VideoCapture(0)

		# If you decide to use video.mp4, you must have this file in the folder
		# as the main.py.
		# self.video = cv2.VideoCapture('Beach-Mode.mp4')
    
	def __del__(self):
		self.video.release()
    
	def get_frame(self):
		app.logger.info("get frame")

		success, image = self.video.read()

		# We are using Motion JPEG, but OpenCV defaults to capture raw images,
		# so we must encode it into JPEG in order to correctly display the
		# video stream.

		ret, jpeg = cv2.imencode('.jpg', image)
		return jpeg.tobytes()