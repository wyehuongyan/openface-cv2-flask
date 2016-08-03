(function(exports) {
	const namespace = '/live'; 
	const ORIGINAL_DOC_TITLE = document.title;
	let setInt = null;
	let startTime = null;
	let endTime = null;

	// the socket.io documentation recommends sending an explicit package upon connection
	// this is specially important when using the global namespace
	console.log('http://' + document.domain + ':' + location.port + namespace);
	var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);

	socket.on('connect', function () {
		console.log('connection event');
		socket.emit('event', { data: 'Client, Here' });
	});

	socket.on('response', function (data) {
		//console.log(data);

		switch(data.type) {
			case "LIVE_IMAGE": 
				$('#myImage').setAttribute('src', data.data);
				break;
			default:
				break;
		}
	});

	function $(selector) {
		return document.querySelector(selector) || null;
	}

	// Expose $ function to the global object
	exports.$ = $;

	// Webcam start, stop and snapshot
	//--------------------
	// GET USER MEDIA CODE
	//--------------------
	navigator.getUserMedia = ( navigator.getUserMedia ||
						navigator.webkitGetUserMedia ||
						navigator.mozGetUserMedia ||
						navigator.msGetUserMedia);

	let video;
	let webcamStream;

	function startWebcam() {
		if (navigator.getUserMedia) {
			navigator.getUserMedia (

				// constraints
				{
					video: true,
					audio: false
				},

				// successCallback
				function(localMediaStream) {
					video = document.querySelector('video');
					video.src = window.URL.createObjectURL(localMediaStream);
					webcamStream = localMediaStream;

					// start sending frames to the server
					startTime = Date.now();
  					socket.emit('event', { data: 'RECORDING!' });
					console.log("RECORDING!");

					setInt = setInterval(function() {
						sendVideoFrame()
					}, 1000 / 20) // call this function every 50ms
				},

				// errorCallback
				function(err) {
					console.log("The following error occured: " + err);
				}
			);
		} else {
			console.log("getUserMedia not supported");
		}  
	}

	function stopWebcam() {
		let track = webcamStream.getTracks()[0];  // if only one media track
		track.stop();
		clearInterval(setInt);
		document.title = ORIGINAL_DOC_TITLE;
		endTime = Date.now();
	}
	//---------------------
	// TAKE A SNAPSHOT CODE
	//---------------------
	let canvas, ctx;

	function init() {
		// Get the canvas and obtain a context for
		// drawing in it
		$('#start-btn').addEventListener('click', startWebcam);
		$('#stop-btn').addEventListener('click', stopWebcam);
		$('#snapshot-btn').addEventListener('click', snapshot);

		canvas = $("#myCanvas");
		ctx = canvas.getContext('2d');
	}

	function snapshot() {
		// Draws current image from the video element into the canvas
		ctx.drawImage(video, 0,0, canvas.width, canvas.height);
	}

	function sendVideoFrame() {
		// draw the video contents into the canvas x, y, width, height
		ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
		// get the image data from the canvas object
		// and send them through websockets
		socket.emit('livevideo', { data: canvas.toDataURL('image/jpeg', 0.7) });  // Send video frame to server
		//console.log(canvas.toDataURL());
		document.title = 'Live streaming...' + Math.round((Date.now() - startTime) / 1000) + 's';
	};

	init();

})(window);