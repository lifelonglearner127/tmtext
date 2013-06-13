<div class="tabbable">
  <ul class="nav nav-tabs jq-system-tabs">
	<li class=""><a data-toggle="tab" href="<?php echo site_url('system');?>">General</a></li>
	<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_accounts');?>">New Accounts</a></li>
	<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_roles');?>">Roles</a></li>
	<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_users');?>">Users</a></li>
	<li class="active"><a data-toggle="tab" href="<?php echo site_url('system/system_compare');?>">Product Compare Interface</a></li>
  </ul>
  <div class="tab-content">
    <div id="tab5" class="tab-pane active">

    	<!-- PRODUCTS SELECTION BOX -->
    	<div class='span5'>
    		<div class='well'>
    			<p class='centered'><span class="label">SELECT PRODUCTS BOX</span></p>
    			<ul class='nav nav-pills nav-stacked'>
    				<li class='active'><a href='javascript:void(0)'>Test 1</a></li>
    				<li><a href='javascript:void(0)'>Test 2</a></li>
    				<li><a href='javascript:void(0)'>Test 3</a></li>
    				<li><a href='javascript:void(0)'>Test 4</a></li>
				</ul>
			</div>
		</div>
		<!-- INTERACTIONS CONTROL BOX -->
		<div class='span2'>
    		<div class='well'>
    			<p class='centered'><span class="label label-info">CONTROLS</span></p>
    			<button id='ibc_move_btn' type='button' class='btn btn-primary icb_systme_compare_btn margin_bottom'><i class="icon-chevron-right icon-white"></i>&nbsp;Move</button>
    			<button id='ibc_clean_btn' type='button' class='btn btn-danger icb_systme_compare_btn'><i class="icon-off icon-white"></i>&nbsp;Clean</button>
			</div>
		</div>
		<!-- SELECTED FOR COMPARE BOX -->
		<div class='span5'>
    		<div class='well'>
    			<p class='centered'><span class="label label-success">PRODUCTS FOR COMPARE</span></p>
    			<ul class='nav nav-pills nav-stacked'>
    				<li><a href='javascript:void(0)'>Test 1</a></li>
    				<li><a href='javascript:void(0)'>Test 2</a></li>
    				<li><a href='javascript:void(0)'>Test 3</a></li>
    				<li><a href='javascript:void(0)'>Test 4</a></li>
				</ul>
			</div>
		</div>

    </div>
  </div>
</div>

<script type='text/javascript'>
	// ----- COMPARE INTERFACE UI (START)
	$("#ibc_move_btn").tooltip({
		placement: 'right',
		title: "move to compare list"
	});
	$("#ibc_clean_btn").tooltip({
		placement: 'right',
		title: "clean compare list"
	});
	// ----- COMPARE INTERFACE UI (END)
</script>
