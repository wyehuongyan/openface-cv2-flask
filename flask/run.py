from app import app

# start process
if __name__ == '__main__': # code is being loaded directly
	app.debug = False
	app.threaded = True
	app.run(host='0.0.0.0')