<div class="row-fluid">
	<div class="span6 offset3">
        <div class="solution-login"></div>
		<div class="login_container">
			<div class="login_header">
				<h3 class="text-center">New Client Registration</h3>
			</div>
			<div class="login_content">
				<?php echo form_open("auth/clientreg", array("class"=>"form-horizontal", "id"=>"clientreg_form", "name"=>"clientreg_form"));?>
					<div class="control-group">
						<label for='fname' class='control-label'>Name:</label>
						<div class="controls">
							<?php echo form_input($fname, null, 'placeholder="Name" required');?>
							<p class='help-block form_hb_error' id='fname_error'>&nbsp;</p>
						</div>
					</div>
					<div class="control-group">
						<label for='email' class='control-label'>Email Address:</label>
						<div class="controls">
							<?php echo form_input($email, null, 'placeholder="Email" required');?>
							<p class='help-block form_hb_error' id='email_error'>&nbsp;</p>
						</div>
					</div>
					<div class="control-group">
						<label for='password' class='control-label'>Create Password:</label>
						<div class="controls">
							<?php echo form_input($password, null, 'placeholder="Password" required');?>
							<p class='help-block form_hb_error' id='password_error'>&nbsp;</p>
						</div>
					</div>
					<div class="control-group">
						<label class='control-label'>&nbsp;</label>
						<div class="controls">
							By clicking below you agree to the<br/><a href='javascript:void(0)'>Terms of Service</a>
						</div>
					</div>
					<div class="control-group">
						<div class="controls">
							<button id='reg_form_sbm_btn' type='submit' class='btn login_btn' onclick="return submitRegForm();">Create Account</button>
						</div>
					</div>
				<?php echo form_close();?>
			</div>
		</div>
	</div>
</div>

<script type='text/javascript'>

	$(document).ready(function() {

		$("#clientreg_form input[type=text], #clientreg_form input[type=password]").keypress(function() {
			if(empty_check_validation()) {
				$("#reg_form_sbm_btn").removeClass('disabled');
				$("#reg_form_sbm_btn").removeAttr('disabled');
				if(!$("#reg_form_sbm_btn").hasClass('btn-success')) {
					$("#reg_form_sbm_btn").addClass('btn-success');
				}
			}
		});

		$("#clientreg_form input[type=text], #clientreg_form input[type=password]").blur(function() {
			if(empty_check_validation()) {
				$("#reg_form_sbm_btn").removeClass('disabled');
				$("#reg_form_sbm_btn").removeAttr('disabled');
				if(!$("#reg_form_sbm_btn").hasClass('btn-success')) {
					$("#reg_form_sbm_btn").addClass('btn-success');
				}
			}
		});

		function empty_check_validation() {
			var res = false;
			var fname = $.trim($("#fname").val());
			var email = $.trim($("#email").val());
			var psw = $.trim($("#password").val());
			if(fname !== '' && email !== "" && psw !== '') {
				res = true;
			}
			return res;
		}

	});

	function fullFormReset() {
		$(".form_hb_error").hide();
		$(".form_hb_error").text('');
		$("#fname, #email, #password").val('');
		$("#fname, #email, #password").blur('');
		$("#reg_form_sbm_btn").removeClass('btn-success');
		$("#reg_form_sbm_btn").addClass('disabled');
		$("#reg_form_sbm_btn").attr('disabled', true);
	}

	function submitRegForm() {
		$(".form_hb_error").hide();
		$(".form_hb_error").text('');
		var fname = $.trim($("#fname").val());
		var email = $.trim($("#email").val());
		var psw = $.trim($("#password").val());
		// var email_pattern = /^([a-z0-9_\-]+\.)*[a-z0-9_\-]+@([a-z0-9][a-z0-9\-]*[a-z0-9]\.)+[a-z]{2,4}$/i;
		var email_pattern = /^([a-z0-9_\-]+\.\+)*[a-z0-9_\-\+]+@([a-z0-9][a-z0-9\-]*[a-z0-9]\.)+[a-z]{2,4}$/i;
		if(fname === '' || !email_pattern.test(email) || (psw.length < 8 || psw.length > 20)) {
			if(fname === '') {
				$('#fname_error').text('field can not be empty');
			    $('#fname_error').fadeOut();
			    $('#fname_error').fadeIn();
			}
			if(!email_pattern.test(email)) {
				$('#email_error').text('invalid email format');
			    $('#email_error').fadeOut();
			    $('#email_error').fadeIn();
			}
			if(psw.length < 8 || psw.length > 20) {
				$('#password_error').text('should be min 8 and max 20 chars');
			    $('#password_error').fadeOut();
			    $('#password_error').fadeIn();
			}
		} else {
			var checkregEmailBaseUrl = base_url + 'index.php/auth/ajaxcheckregemail';
			$.post(checkregEmailBaseUrl, {email: email}, 'json').done(function(data_c) {
				if(data_c) {
					var clRegBaseUrl = base_url + 'index.php/auth/ajaxregclient';
					var obj = {
						fname: fname,
						email: email,
						psw: psw
					};
					$.post(clRegBaseUrl, obj, 'json').done(function(data) {
						fullFormReset();
						if(data) location.href = base_url + 'index.php/measure/index';
				    });
				} else {
					$('#email_error').text('that email already exists');
				    $('#email_error').fadeOut();
				    $('#email_error').fadeIn();
				}
			});
		}
		return false;
	}
</script>