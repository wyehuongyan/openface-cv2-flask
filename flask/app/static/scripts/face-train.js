$(document).ready(function() {
	let users = [];
	let activeUser = {};
	let isTraining = false;

	// autocomplete
	$('#inputAutocomplete').typeahead({
		source: function(query, process) {

			let data = {
				username: query
			};

			$.ajax("/users", {
				method: 'POST',
				contentType: 'application/json;charset=UTF-8',
				data: JSON.stringify(data),
				success: function(response) {
					users = response.payload;

					let usernames = users.map(function (user) {
						return user.username;
					})

					return process(usernames);
				},
				error: function(err) {
					console.log(err);
				}
			});
		},
		items: 5,
		fitToElement: true,
		afterSelect: function(selectedUsername) {

			let result = users.filter(function (user) {
				return user.username === selectedUsername;
			});

			activeUser = result[0];

			console.log(activeUser);
		}
	});

	$('#btnTraining').click(function() {
		if($('#inputAutocomplete').val().length > 0 && !jQuery.isEmptyObject(activeUser)) {
			toggleTraining();
		} else {
			console.log("Please select a user first.");
		}
	})

	function toggleTraining() {
		isTraining = !isTraining;

		if(isTraining) {
			// set dynamic variable 
			src = "/video/feed/train?id=" + activeUser.id;
			$('.live-image-feed').attr("src", src);
			$('#btnTraining').removeClass('btn-primary').addClass('btn-default');
			$('#inputAutocomplete').prop('disabled', true);
			$('#btnTraining').html('Loading...');

			setTimeout(function() {
				$('.jumbotron').slideDown(400);
				$('#btnTraining').removeClass('btn-default').addClass('btn-danger');
				$('#btnTraining').text('Stop Recording');
			}, 2000);
		} else {
			$('#inputAutocomplete').prop('disabled', false);
			$('#inputAutocomplete').val('');
			activeUser = {};
			$('#btnTraining').removeClass('btn-danger').addClass('btn-primary');
			$('#btnTraining').text('Start Training');

			$('.jumbotron').slideUp(400, function() {
				$('.live-image-feed').removeAttr("src");
			});
		}
	}
});