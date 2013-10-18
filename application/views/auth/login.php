<div class="row-fluid">
    <div class="pull-left">

    </div>
</div>
<div class="row-fluid">
	<div class="span6 offset3">
        <div class="solution-login"></div>
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
						<div class="controls remember_me">
                            <?php echo form_checkbox('remember', '1', FALSE, 'id="remember"');?>
						</div>
                        <?php echo lang('login_remember_label', 'remember', ' class="control-label label_remember"');?>
					</div>
					<div class="control-group">
						<div class="controls">
							<?php echo form_submit('submit', lang('login_submit_btn'), ' class="btn login_btn"');?>
						</div>
					</div>
                    <div class="control-group">
                        <div class="controls">
                            <a href="forgot_password" class="forgot_pass"><?php echo lang('login_forgot_password');?></a>
                        </div>
                    </div>
				<?php echo form_close();?>
			</div>
		</div>
		<div class='add_login_lnk'>
			<div class='add_login_lnk_left ml_10    '><a href="<?php echo base_url(); ?>index.php/auth/clientreg">New Client</a></div>
		</div>
	</div>
</div>
