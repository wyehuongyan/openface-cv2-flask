from flask import render_template, Response
from app import app

# device camera
from camera import VideoCamera

@app.route('/')
def main():

	#app.logger.warning('A warning occurred (%d apples)', 42)
	#app.logger.error('An error occurred')

	return render_template('index.html')

def gen(camera):
	# Video streaming generator function.
	while True:
		frame = camera.get_frame()

		print frame

		yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
	# Video streaming route. Put this in the src attribute of an img tag
	return Response(
		gen(VideoCamera()),
		mimetype='multipart/x-mixed-replace; boundary=frame'
	)

