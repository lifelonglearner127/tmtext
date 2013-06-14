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
    		<div class='well limited_list'>
    			<p class='centered'><span class="label">SELECT PRODUCTS BOX</span></p>
    			<ul id='select_pr_boxer' class='nav nav-pills nav-stacked'>
    				<?php if(count($all_products) > 0) { ?>
    					<?php foreach($all_products as $k=>$v) { ?>
    					<li><a data-id="<?php echo $k; ?>" href='javascript:void(0)'><?php echo $v['product_name']; ?></a></li>
    					<?php } ?>
    				<?php } ?>
				</ul>
			</div>
		</div>
		<!-- INTERACTIONS CONTROL BOX -->
		<div class='span2'>
    		<div class='well'>
    			<p class='centered'><span class="label label-info">CONTROLS</span></p>
    			<button id='ibc_move_btn' onclick="moveProductsToCompare()" type='button' disabled='true' class='btn btn-primary icb_systme_compare_btn margin_bottom disabled'><i class="icon-chevron-right icon-white"></i>&nbsp;Move</button>
    			<button id='ibc_clean_btn' onclick="cleanAndRestore()" type='button' disabled='true' class='btn btn-danger icb_systme_compare_btn margin_bottom disabled'><i class="icon-off icon-white"></i>&nbsp;Clean</button>
				<button id='ibc_start_btn' type='button' disabled='true' class='btn btn-success icb_systme_compare_btn disabled'><i class="icon-ok icon-white"></i>&nbsp;Start</button>
			</div>
		</div>
		<!-- SELECTED FOR COMPARE BOX -->
		<div class='span5'>
    		<div class='well'>
    			<p class='centered'><span class="label label-success">PRODUCTS FOR COMPARE</span></p>
    			<ul id='compare_pr_boxer' class='nav nav-pills nav-stacked'>&nbsp;</ul>
			</div>
		</div>

    </div>
  </div>
</div>

<script type='text/javascript'>
	// ----- TOOLTIPS INTERFACE UI (START)
	// function destroySelectProductTooltips() {
	// 	$("#select_pr_boxer li:not('.active')").tooltip('destroy');
	// }
	// function initSelectProductTooltips() {
	// 	$("#select_pr_boxer li:not('.active')").tooltip({
	// 		placement: 'left',
	// 		title: 'click to select'
	// 	});
	// };
	// initSelectProductTooltips();

	// $("#ibc_move_btn").tooltip({
	// 	placement: 'right',
	// 	title: "move to compare list"
	// });
	// $("#ibc_clean_btn").tooltip({
	// 	placement: 'right',
	// 	title: "clean compare list"
	// });
	// $("#ibc_start_btn").tooltip({
	// 	placement: 'right',
	// 	title: "start comparing process"
	// });
	// ----- TOOLTIPS INTERFACE UI (END)

	// $("#select_pr_boxer li:not('.active')").click(function(e) {
	// 	var act_count = $("#select_pr_boxer li.active").length;
	// 	if(act_count < 2) {
	// 		$(this).addClass('active');	
	// 	}
	// });
	// $("#select_pr_boxer li.active").click(function(e) {
	// 	console.log("AAAA");
	// 	$(this).removeClass('active');
	// });

	function cleanAndRestore() {
		$('#ibc_clean_btn').addClass('disabled');
		$('#ibc_clean_btn').attr('disabled', true);
		$('#ibc_start_btn').addClass('disabled');
		$('#ibc_start_btn').attr('disabled', true);
		$("#compare_pr_boxer").empty();
		$("#select_pr_boxer > li > a").bind('click', selectPrBoxerClickHandler);
	}

	function moveProductsToCompare() {
		var cli = $("#select_pr_boxer li.active").clone();
		$("#compare_pr_boxer").append(cli);
		$('#ibc_move_btn').addClass('disabled');
		$('#ibc_move_btn').attr('disabled', true);
		$('#ibc_clean_btn').removeClass('disabled');
		$('#ibc_clean_btn').removeAttr('disabled');
		$('#ibc_start_btn').removeClass('disabled');
		$('#ibc_start_btn').removeAttr('disabled');
		$("#select_pr_boxer > li").each(function(index, value) {
			$(value).removeClass('active');
		});
		$("#select_pr_boxer > li > a").unbind('click');
	}
	
	function checkMoveButtonStatus() {
		var act_count = $("#select_pr_boxer li.active").length;
		if(act_count === 2) {
			$('#ibc_move_btn').removeClass('disabled');
			$('#ibc_move_btn').removeAttr('disabled');
		} else {
			$('#ibc_move_btn').addClass('disabled');
			$('#ibc_move_btn').attr('disabled', true);
		}
	}

	$("#select_pr_boxer > li > a").bind('click', selectPrBoxerClickHandler);

	function selectPrBoxerClickHandler(e) {
		var act_count = $("#select_pr_boxer li.active").length;
		var act = $(this).parent('li').hasClass('active');
		if(act === false) { // select product attempt
			if(act_count < 2) {
				$(this).parent('li').addClass('active');
			}
		} else { // cancel selection
			$(this).parent('li').removeClass('active');
		}
		checkMoveButtonStatus();
	}

</script>
