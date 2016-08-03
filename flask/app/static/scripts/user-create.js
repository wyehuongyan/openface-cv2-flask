$(document).ready(function(){
	var usernameValid = false;

	function checkUsernameAvailable() {
		console.log('Check availability button clicked.');

		if($('#inputUsername').val().length > 0) {
			let data = {
				username: $('#inputUsername').val()
			};

			$.ajax("/user", {
				method: 'POST',
				contentType: 'application/json;charset=UTF-8',
				data: JSON.stringify(data),
				success: function(response) {
					users = response.payload;

					if(users) {
						if(users.length) {
							console.log("Username already taken!");
							$('.username-form-group').addClass('has-error');
							$('#usernameHelpBlock').text('Oops, this username is already taken!');

							usernameValid = false;
							validateForm()
							
							return usernameValid;
						} else {
							console.log("Username is available!");	
							$('.username-form-group').removeClass('has-error').addClass('has-success');
							$('#usernameHelpBlock').text('Awesome, this username is available!');

							usernameValid = true;
							validateForm()

							return usernameValid;
						}
					}
				},
				error: function(err) {
					console.log(err);
				}
			})
		} else {
			console.log("Username is required");	
			$('.username-form-group').removeClass('has-error has-success').addClass('has-error');
			$('#usernameHelpBlock').text('Please enter a username.');

			usernameValid = false;
			validateForm()

			return usernameValid;
		}
	}

	$('#btnAvailability').click(function() {
		checkUsernameAvailable();
	});
	
	$('#inputUsername').bind('keyup', function() {
		checkUsernameAvailable();
	});

	$('#inputUsername, #inputFirstName, #inputLastName').bind('keyup', function() {
		validateForm();
	});

	function validateForm() {
		if(allFilled() && usernameValid) {
			$('#submitBtn').removeAttr('disabled')
		} else {
			$('#submitBtn').attr('disabled', 'disabled');
		};
	}

	function allFilled() {
		var filled = true;
		$('body input').each(function() {
			if($(this).val() == '') filled = false;
		});
		return filled;
	}
});