<script>
	$("#user_customerss").chosen();
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
		<div class="row-fluid">
			<div class="span9 admin_system_content">
				<p>Name :</p>
				<input type="text" id="user_name" placeholder="Name">
				<div class="clear-fix"></div>
			</div>
			<div class="span9 admin_system_content">
				<p>Email :</p>
				<input type="text" id="user_mail" placeholder="Email">
				<div class="clear-fix"></div>
			</div>
			<div class="span9 admin_system_content">
				<p>Password :</p>
				<input type="text" id="user_password" placeholder="Password">
				<div class="clear-fix"></div>
			</div>
			<div class="span9 admin_system_content aclist">
				<p>Customers :</p>
		        <select id="user_customerss" data-placeholder="Click to select customers" multiple class="chzn-select" tabindex="8">
					<option>Walmart</option>
					<option>Sears</option>
					<option>Staples</option>
		        </select>
				<div class="clear-fix"></div>
			</div>
			<div class="span9 admin_system_content aclist">
				<p>Role :</p>
				<select id="user_role" data-placeholder="Select user role" class="chzn-select" tabindex="8">
					<?php 
					foreach ($user_groups as $user_group) {
						print '<option value="'.$user_group->name.'">'.$user_group->name.'</option>';
					}
					 ?>
				</select>
				<div class="clear-fix"></div>
			</div>
			<div class="span9 admin_system_content">
				<p>Active :</p>
				<input type="checkbox" id="user_active">
				<div class="clear-fix"></div>
			</div>
		</div>
		<div class="row-fluid">
		    <div class="control-group">
			    <div class="controls align_center">
					<button class="btn new_btn btn-primary"><i class="icon-white icon-file"></i>&nbsp;New</button>
				    <button class="btn btn-success" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Update</button>
			    </div>
		    </div>
		</div>
    </div>
  </div>
</div>
