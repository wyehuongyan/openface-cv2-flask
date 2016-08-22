from app import app

# start process
if __name__ == '__main__': # code is being loaded directly
	app.debug = False
	app.threaded = True
	app.run(host='0.0.0.0')

# $ gunicorn --chdir ./flask run:app --timeout 31104000 -k gevent -w 3 -b 0.0.0.0:5000   