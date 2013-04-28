			<div class="row-fluid">
				<div class="span6 offset3">
					<div class="login_container">
						<div class="login_header">
							<h3 class="text-center"><?php echo lang('login_heading');?></h3>
						</div>
						<div class="login_content">
							<?php echo form_open("auth/login", array("class"=>"form-horizontal", "id"=>"login_form", "name"=>"login_form"));?>
								<div class="control-group">
									<?php echo lang('login_identity_label', 'indentity', ' class="control-label"');?>
									<div class="controls">
										<?php echo form_input($identity, null, 'placeholder="Email" required');?>
									</div>
								</div>
								<div class="control-group">
									<?php echo lang('login_password_label', 'password', ' class="control-label"');?>
									<div class="controls">
										<?php echo form_input($password, null, ' placeholder="Password" required');?>
									</div>
								</div>
								<div class="control-group">
									<?php echo lang('login_remember_label', 'remember', ' class="control-label"');?>
									<div class="controls">
										<?php echo form_checkbox('remember', '1', FALSE, 'id="remember"');?>
									</div>
								</div>
								<div class="control-group">
									<a href="forgot_password" class="control-label"><?php echo lang('login_forgot_password');?></a>
									<div class="controls">
										<?php echo form_submit('submit', lang('login_submit_btn'), ' class="btn login_btn"');?>
									</div>
								</div>
							<?php echo form_close();?>
						</div>
					</div>
				</div>
			</div>
