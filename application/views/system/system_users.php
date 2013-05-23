<script>
	$("#user_customers").chosen();
	$("#user_role").chosen();
</script>
<style>
	
	.chzn-container-multi .chzn-choices{
		min-height: 28px;
		border: 1px solid #CCCCCC;
		border-radius: 4px;
	}

	.chzn-container-multi  .chzn-choices .search-field input{
		min-height: 28px;
		font-size: 14px !important;
	}

	.chzn-container-single .chzn-single{
		font-size: 14px;
		background: none;
		min-height: 28px;
		border: 1px solid #CCCCCC;
		border-radius: 4px;
		line-height: 28px;
		color: #555555;
	}

	.chzn-container-multi .chzn-choices .search-choice{
		background: none repeat scroll 0 0 #FBFBFB;
	    border: 1px solid #CCCCCC;
	    border-radius: 4px 4px 4px 4px;
	    cursor: pointer;
	    height: 18px;
		line-height: 18px;
	}
	
	.chzn-container-multi .chzn-choices .search-choice a{
		margin-top: 2px;
	}
	#system_save_new_user .admin_system_content{
		margin-left: 2.12766%;
	}
</style>
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
				<p>Name :</p>
				<input type="text" id="user_name" name="user_name" placeholder="Name" value="">
				<div class="clear-fix"></div>
			</div>
			<div class="span9 admin_system_content">
				<p>Email :</p>
				<input type="text" id="user_mail" name="user_mail" placeholder="Email">
				<div class="clear-fix"></div>
			</div>
			<div class="span9 admin_system_content">
				<p>Password :</p>
				<input type="text" id="user_password" name="user_password" placeholder="Password">
				<div class="clear-fix"></div>
			</div>
			<div class="span9 admin_system_content aclist">
				<p>Customers :</p>
		        <select id="user_customers" data-placeholder="Click to select customers" multiple class="chzn-select" tabindex="8" name="user_customers[]">
					<?php 
					foreach ($customers as $customer) {
						print '<option value="'.$customer->id.'">'.$customer->name.'</option>';
					}
					 ?>
		        </select>
				<div class="clear-fix"></div>
			</div>
			<div class="span9 admin_system_content aclist">
				<p>Role :</p>
				<select id="user_role" data-placeholder="Select user role" class="chzn-select" tabindex="8" name="user_role">
					<?php 
					foreach ($user_groups as $user_group) {
						print '<option value="'.$user_group->id.'">'.$user_group->name.'</option>';
					}
					 ?>
				</select>
				<div class="clear-fix"></div>
			</div>
			<div class="span9 admin_system_content">
				<p>Active :</p>
				<input type="checkbox" id="user_active" name="user_active">
				<div class="clear-fix"></div>
			</div>
		</div>
		<div class="row-fluid">
		    <div class="control-group">
			    <div class="controls align_center">
					<button class="btn new_btn btn-primary" type="submit"><i class="icon-white icon-file"></i>&nbsp;New</button>
				    <button class="btn btn-success" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Update</button>
			    </div>
		    </div>
		</div>
		<?php echo form_close();?>
    </div>
  </div>
</div>
