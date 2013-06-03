<script type="text/javascript">
var autocompleteURL = $('#system_autocomplete').attr('action');
$("#user_customers").chosen().change(function(e){
	var marcked = $(this).val();
	var check = $.inArray('all', marcked);
	if(check > -1){
		$("#user_customers option").prop("selected", "selected");
		$("#user_customers option.all").prop("selected", false);
		$("#user_customers option").trigger("liszt:updated");
	}
});
$("#user_role").chosen();
$("#user_name").autocomplete({
    source: autocompleteURL+'?column=username',
    minChars: 2,
    deferRequestBy: 300,
    select: function(event, ui){
        afterAutocomplete(ui);
    }
});
$("#user_mail").autocomplete({
    source: autocompleteURL+'?column=email',
    minChars: 2,
    deferRequestBy: 300,
    select: function(event, ui){
        afterAutocomplete(ui);
    }
});
</script>
<div class="tabbable">
  <ul class="nav nav-tabs jq-system-tabs">
	<li class=""><a data-toggle="tab" href="<?php echo site_url('system');?>">General</a></li>
	<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_accounts');?>">New Accounts</a></li>
	<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_roles');?>">Roles</a></li>
	<li class="active"><a data-toggle="tab" href="<?php echo site_url('system/system_users');?>">Users</a></li>
  </ul>
  <div class="tab-content">
    <div id="tab4" class="tab-pane active">
    	<div class="info-message"></div>
     	<?php echo form_open("system/save_new_user", array("class"=>"form-horizontal", "id"=>"system_save_new_user"));?>
		<div class="row-fluid">
			<div class="span9 admin_system_content">
				<p>Name:</p>
				<input type="text" id="user_name" name="user_name" placeholder="Name" value="">
				<div class="clear-fix"></div>
			</div>
			<div class="span9 admin_system_content">
				<p>Email:</p>
				<input type="text" id="user_mail" name="user_mail" placeholder="Email">
				<div class="clear-fix"></div>
			</div>
			<div class="span9 admin_system_content">
				<p>Password:</p>
				<input type="text" id="user_password" name="user_password" placeholder="Password">
				<div class="clear-fix"></div>
			</div>
			<div class="span9 admin_system_content aclist">
				<p>Customers:</p>
		        <select id="user_customers" data-placeholder="Click to select customers" multiple class="chzn-select" tabindex="8" name="user_customers[]">
					<?php 
					foreach ($customers as $key => $value) {
						print '<option class="'.$key.'" value="'.$key.'">'.$value.'</option>';
					}
					 ?>
		        </select>
				<div class="clear-fix"></div>
			</div>
			<div class="span9 admin_system_content aclist">
				<p>Role:</p>
				<select id="user_role" data-placeholder="Select user role" class="chzn-select" tabindex="8" name="user_role">
					<?php 
					foreach ($user_groups as $user_group) {
						print '<option value="'.$user_group->id.'">'.$user_group->description.'</option>';
					}
					 ?>
				</select>
				<div class="clear-fix"></div>
			</div>
			<div class="span9 admin_system_content">
				<p>Active:</p>
				<input type="checkbox" class="user_active" name="user_active" checked="checked">
				<div class="clear-fix"></div>
			</div>
			<div class="user_id"></div>
		</div>
		<div class="row-fluid">
		    <div class="control-group">
			    <div class="controls align_center">
					<button id="btn_system_new_user" class="btn new_btn btn-primary" type="submit"><i class="icon-white icon-file"></i>&nbsp;Create</button>
				    <button id="btn_system_update_user" class="btn btn-success" disabled type="submit"><i class="icon-white icon-ok"></i>&nbsp;Update</button>
			    </div>
		    </div>
		</div>
		<?php echo form_close();?>
		<?php echo form_open("system/jqueryAutocomplete", array("id"=>"system_autocomplete"));?><?php echo form_close();?>
		<?php echo form_open("auth/getUserById", array("id"=>"auth_getuser"));?><?php echo form_close();?>
    </div>
  </div>
</div>
