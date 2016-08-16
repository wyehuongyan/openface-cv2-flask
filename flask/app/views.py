from flask import render_template, request, flash, jsonify, Response
from app import app, socketio, db
from app.models import User
from camera import VideoCamera
from flask_socketio import emit
import urllib
import base64
import cv2
import os

#################
##### Video #####
#################
@app.route('/')
def main():
	#app.logger.warning('A warning occurred (%d apples)', 42)
	#app.logger.error('An error occurred')

	return render_template('index.html')

def gen_livestream(camera, hasMultiple=None, id=None):
	# Video streaming generator function.
	while True:
		frame = camera.get_frame(hasMultiple, id)
		
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

		yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video/feed/train')
def video_feed_train():
	# get arguments (id is a string, cast to int)
	id = int(request.args.get('id'))

	# Video streaming route. Put this in the src attribute of an img tag
	return Response(
		gen_livestream(VideoCamera(), None, id),
		mimetype='multipart/x-mixed-replace; boundary=frame'
	)

@app.route('/video/feed/infer')
def video_feed_infer():
	return Response(
		gen_livestream(VideoCamera(), True),
		mimetype='multipart/x-mixed-replace; boundary=frame'
	)

################
##### User #####
################
@app.route('/user/create', methods=['POST', 'GET'])
def user_create():
	if request.method == 'POST':
		#data = request.json
		user = User(request.form['username'], request.form['firstname'], request.form['lastname'])
		db.session.add(user)
		db.session.commit()
		print user.username

		# create folder in ./training/:username/
		directory = './app/training/' + user.username
		if not os.path.exists(directory):
			print 'directory does not exist, creating it now...'
			os.makedirs(directory)

		flash('Success! \'' + user.username + '\' has been added to the list of users.')
	
	return render_template('user/create.html')

@app.route('/users', methods=['POST', 'GET'])
def users():
	if request.method == 'POST':
		data = request.json

		results = db.session.query(User).filter(User.username.like("%" + data['username'] + "%")).all()

		return jsonify(payload=[i.serialize for i in results])

@app.route('/user', methods=['POST', 'GET'])
def user():
	if request.method == 'POST':
		data = request.json

		results = db.session.query(User).filter(User.username.like(data['username'])).all()

		return jsonify(payload=[i.serialize for i in results])

################
##### Face #####
################
@app.route('/face/train', methods=['POST'])
def face_train():
	if request.method == "POST":
		data = request.json
	
	return jsonify(msg="orh, lai liao lo")

@app.route('/face/infer', methods=['GET'])
def face_infer():
	return render_template('face/infer.html')

################
## WebSockets ##
################
@socketio.on('connect', namespace='/live')
def test_connect():
    """Connect event."""
    print('Client wants to connect.')
    emit('response', {'data': 'OK'})

@socketio.on('disconnect', namespace='/live')
def test_disconnect():
    """Disconnect event."""
    print('Client disconnected')

@socketio.on('event', namespace='/live')
def test_message(message):
	"""Simple websocket echo."""
	emit('response', {'data': message['data']})
	print(message['data'])

@socketio.on('livevideo', namespace='/live')
def test_live(message):
	"""Video stream reader."""
	#app.queue.put(message['data'])

	#print(app.queue.qsize())
	print("livevideo socket called")
	imgdata = videoCamera.get_frame(message['data'])

	content = 'data:image/jpeg;base64,' + \
                urllib.quote(base64.b64encode(imgdata))

	print("done with bb")

	emit('response', {
		'type': 'LIVE_IMAGE',
		'data': content
	})