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

    	<div id='sc_compare_voted_list'>&nbsp;</div>

    	<div class='sc_compare_selection_block' id='sc_compare_selection_block'>
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
	    		<div class='well h_400'>
	    			<p class='centered'><span class="label label-info">CONTROLS</span></p>
	    			<button id='ibc_move_btn' onclick="moveProductsToCompare()" type='button' disabled='true' class='btn btn-primary icb_systme_compare_btn margin_bottom disabled'><i class="icon-chevron-right icon-white"></i>&nbsp;Move</button>
	    			<button id='ibc_clean_btn' onclick="cleanAndRestore()" type='button' disabled='true' class='btn btn-danger icb_systme_compare_btn margin_bottom disabled'><i class="icon-off icon-white"></i>&nbsp;Clean</button>
					<button id='ibc_start_btn' onclick="renderCompareSection()" type='button' disabled='true' class='btn btn-success icb_systme_compare_btn disabled'><i class="icon-ok icon-white"></i>&nbsp;Start</button>
				</div>
			</div>
			<!-- SELECTED FOR COMPARE BOX -->
			<div class='span5'>
	    		<div class='well h_400'>
	    			<p class='centered'><span class="label label-success">PRODUCTS FOR COMPARE</span></p>
	    			<ul id='compare_pr_boxer' class='nav nav-pills nav-stacked'>&nbsp;</ul>
				</div>
			</div>
		</div>

		<div class='sc_compare_block' id='sc_compare_block'>&nbsp;</div>

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

	var systemCompareProductsBaseUrl = base_url + 'index.php/system/getcompareproducts';
	var systemCompareProductsVoteBaseUrl = base_url + 'index.php/system/votecompareproducts';
	var systemCompareGetProductsVotedBaseUrl = base_url + 'index.php/system/getproductscomparevoted';
	var systemCompareDeleteProductsVotedPairBaseUrl = base_url + 'index.php/system/deleteproductsvotedpair';

	function reComparePair(im_pr_f, im_pr_s) {
		cleanAndRestore();
		var ids = [im_pr_f, im_pr_s];
		var render_compare_section = $.post(systemCompareProductsBaseUrl, { ids: ids }, 'html').done(function(data) {
			$("#sc_compare_block").html(data);
			$("#sccb_yes_btn, #sccb_not_btn, #sccb_notsure_btn").removeClass('disabled');
			$("#sccb_yes_btn, #sccb_not_btn, #sccb_notsure_btn").removeAttr('disabled');
			$.scrollTo("#sc_compare_block", 400);
        });
	}

	function deleteComparePair(id) {
		if(confirm('Are you sure?')) {
			var delete_products_votedpair = $.post(systemCompareDeleteProductsVotedPairBaseUrl, { id: id }, 'json').done(function(data) {
				if(data) {
					renderComparedProductsData();
				}
			});
		}
	}

	function productCompareDecision(dec) {
		var ids = [];
		$("input[type='hidden'][name='get_pc']").each(function(index, value) {
			ids.push($(value).val());
		});		
		// $("#compare_pr_boxer > li > a").each(function(index, value) {
		// 	ids.push($(value).data('id'));
		// });
		if(ids.length === 2) {
			var product_compare_decision = $.post(systemCompareProductsVoteBaseUrl, { ids: ids, dec: dec }, 'json').done(function(data) {
				if(data) {
					cleanAndRestore();
					$.scrollTo("#sc_compare_selection_block", 400);
					$("#sc_compare_selection_block .limited_list").scrollTop(0);
					renderComparedProductsData();
				}
	        });
		}
	}

	function renderComparedProductsData() {
		var get_products_voted = $.post(systemCompareGetProductsVotedBaseUrl, {}, 'html').done(function(data) {
			$("#sc_compare_voted_list").html(data);
        });
	}

	renderComparedProductsData();
	
	function renderCompareSection() {
		var ids = [];
		$("#compare_pr_boxer > li > a").each(function(index, value) {
			ids.push($(value).data('id'));
		});
		var render_compare_section = $.post(systemCompareProductsBaseUrl, { ids: ids }, 'html').done(function(data) {
			$("#sc_compare_block").html(data);
			$("#sccb_yes_btn, #sccb_not_btn, #sccb_notsure_btn").removeClass('disabled');
			$("#sccb_yes_btn, #sccb_not_btn, #sccb_notsure_btn").removeAttr('disabled');
			$.scrollTo("#sc_compare_block", 400);
        });
	}

	function cleanAndRestore() {
		$('#ibc_clean_btn').addClass('disabled');
		$('#ibc_clean_btn').attr('disabled', true);
		$('#ibc_start_btn').addClass('disabled');
		$('#ibc_start_btn').attr('disabled', true);
		$("#compare_pr_boxer").empty();
		$("#select_pr_boxer > li > a").bind('click', selectPrBoxerClickHandler);
		$("#sc_compare_block").empty();
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
