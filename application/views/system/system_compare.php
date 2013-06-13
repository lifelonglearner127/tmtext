<script type='text/javascript'>
	// ----- COMPARE INTERFACE UI (START)

	// ----- COMPARE INTERFACE UI (END)
</script>

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
			</div>
		</div>
		<!-- INTERACTIONS CONTROL BOX -->
		<div class='span2'>
    		<div class='well'>
    			<p class='centered'><span class="label label-info">CONTROLS</span></p>
			</div>
		</div>
		<!-- SELECTED FOR COMPARE BOX -->
		<div class='span5'>
    		<div class='well'>
    			<p class='centered'><span class="label label-success">PRODUCTS FOR COMPARE</span></p>
			</div>
		</div>

    </div>
  </div>
</div>
