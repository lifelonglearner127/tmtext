<div class="tabbable">
  <ul class="nav nav-tabs jq-system-tabs">
	<li class=""><a data-toggle="tab" href="<?php echo site_url('system');?>">General</a></li>
	<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_accounts');?>">New Accounts</a></li>
	<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_roles');?>">Roles</a></li>
	<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_users');?>">Users</a></li>
	<li class="active"><a data-toggle="tab" href="<?php echo site_url('system/system_compare');?>">Product Compare Interface</a></li>
	<li class=""><a data-toggle="tab" href="<?php echo site_url('site_crawler');?>">Site Crawler</a></li>
    <li class=""><a data-toggle="tab" href="<?php echo site_url('system/batch_review');?>">Batch Review</a></li>
    <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_productsmatch');?>">Product Match</a></li>
  </ul>
  <div class="tab-content">
    <div id="tab5" class="tab-pane active">

    	<!-- NEW SUB TABS INTERFACE (START) -->
    	<div class='tabbable'>
    		<ul id='sub_pci_tabset' class="nav nav-tabs jq-system-tabs">
    			<li class="active"><a data-content="tab1_pci_tabset" href="javascript:void(0)">Match Now</a></li>
    			<li><a data-content="tab2_pci_tabset" href="javascript:void(0)">Matched</a></li>
			</ul>
			<div class='tab-content' style='border-bottom: none;'>
				<div id="tab1_pci_tabset" class="tab-pane active">&nbsp;</div>
				<div id="tab2_pci_tabset" class='tab-pane'>&nbsp;</div>
			</div>
		</div>
    	<!-- NEW SUB TABS INTERFACE (END) -->

    </div>
  </div>
</div>

<script type='text/javascript'>

	var systemCompareGetProductsVotedBaseUrl = base_url + 'index.php/system/getproductscomparevoted';
	var systemRenderMatchNowInterface = base_url + 'index.php/system/getmatchnowinterface';

	function renderComparedProductsData(page, container) {
		var get_products_voted = $.post(systemCompareGetProductsVotedBaseUrl, {page: page}, 'html').done(function(data) {
			$(container).html(data);
        });
	}

	function renderMatchNowInterface(container) {
		var get_matchnow_int = $.post(systemRenderMatchNowInterface, {}, 'html').done(function(data) {
			$(container).html(data);
        });
	}

	$(document).ready(function() {

		$("#sub_pci_tabset > li:eq(0)").on('click', function(e) { // 'Match Now' tab
			$("#sub_pci_tabset > li").removeClass('active');
			$("#sub_pci_tabset").siblings().find('.tab-pane').removeClass('active');
			$(this).addClass('active');
			$("#sub_pci_tabset").siblings().find('.tab-pane:eq(0)').empty();
			$("#sub_pci_tabset").siblings().find('.tab-pane:eq(0)').addClass('active');
			var data_container = "#" + $(this).find('a').attr('data-content');
			renderMatchNowInterface(data_container);
		});

		$("#sub_pci_tabset > li:eq(1)").on('click', function(e) { // 'Matched' tab
			$("#sub_pci_tabset > li").removeClass('active');
			$("#sub_pci_tabset").siblings().find('.tab-pane').removeClass('active');
			$(this).addClass('active');
			$("#sub_pci_tabset").siblings().find('.tab-pane:eq(1)').empty();
			$("#sub_pci_tabset").siblings().find('.tab-pane:eq(1)').addClass('active');
			var data_container = "#" + $(this).find('a').attr('data-content');
			renderComparedProductsData(1, data_container);
		});

		$("#sub_pci_tabset > li:eq(0)").trigger('click');

	});

</script>
