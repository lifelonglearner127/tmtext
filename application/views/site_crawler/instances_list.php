<div class="tabbable">
    <ul class="nav nav-tabs jq-system-tabs">
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system');?>">General</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/sites_view');?>">Sites</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('site_crawler');?>">Site Crawler</a></li>
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('site_crawler/instances_list');?>">Crawler Instances <?php $this->load->helper("crawler_instances_helper"); echo crawler_instances_number();?></a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_uploadmatchurls');?>">Upload Match URLs</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_dostatsmonitor');?>">Do_stats Monitor</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('brand/import');?>">Brands</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/batch_review');?>">Batch Review</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_compare');?>">Product Compare</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_productsmatch');?>">Product Match</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_reports');?>">Reports</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_logins');?>">Logins</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/keywords');?>">Keywords</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_rankings');?>">Rankings</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_pricing');?>">Pricing </a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/product_models');?>">Product models </a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/snapshot_queue');?>">Snapshot Queue</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/sync_keyword_status');?>">Sync Keyword Status</a></li>
    </ul>
	  <div class="tab-content">

		<div class="info-message"></div>
		<div class="site_crawler_content">
			<h3 class="span3 current_list_title">Instances: <br/></h3>

			<div id="crawl_div" style="margin-top:15px;">
                <input type="text" class="span1 ml_10" name="instances" >
                <button id="run_instances" class="btn new_btn btn-success ml_10"><i class="icon-white icon-ok"></i>&nbsp;Run</button>
                <button id="run_spot_instances" class="btn new_btn btn-success  ml_10" disabled><i class="icon-white icon-ok"></i>&nbsp;Spot Run</button>
            </div>
			<div class="row-fluid mt_5">
				<div class="search_area uneditable-input span10" style="cursor: text; width: 765px; height: 320px; overflow : auto;" id="Current_List">
				<ul>
					<lh><span><input type="checkbox" style='margin-top: -6px;' value="" id="checkAll"/></span>
						<span style='width: 80px;'>Instance Id</span>
						<span>Type</span>
						<span>State</span>
						<span>Public DNS Name</span>
					</lh>
				</ul>
				</div>
				<button id="terminate_instances" class="btn new_btn btn-danger mt_10 ml_15"><i class="icon-white icon-ok"></i>&nbsp;Terminate</button>
			</div>
		</div>
	  </div>
</div>

<script>

function loadCurrentList(wait, ids) {
	$("#checkAll").removeAttr('checked');
	url = '<?php echo site_url('site_crawler/get_instances');?>';

	$.get(url, function(data) {
		$('#Current_List ul li').remove();
//                console.log(data.instances.length);
		$.each(data.instances, function (index, node) {
			$('#Current_List ul').append("<li id=\"id_"+node.id+"\"><span><input data-instance_id=\""+node.instance_id+"\" data-id=\""+node.id+"\" type=\"checkbox\" name=\"ids[]\" value=\""+node.id+"\"/></span><span style='width: 80px;'>"+node.instance_id+"</span><span>"+node.instance_type+"</span><span>"+node.state_name+"</span><span class=\"url ellipsis\">"+node.public_dns_name+"</span></li>");
		});

		if (wait !== 'undefined' && wait) {
			$.post('<?php echo site_url('site_crawler/wait_start_instances');?>', { ids: ids }, function(data) {
				loadCurrentList();
			});
		}
    });
}

function loadCurrentListStop(wait, ids) {
	$("#checkAll").removeAttr('checked');
	url = '<?php echo site_url('site_crawler/get_instances');?>';

	$.get(url, function(data) {
		$('#Current_List ul li').remove();
//                console.log(data);
		$.each(data.instances, function (index, node) {
			$('#Current_List ul').append("<li id=\"id_"+node.id+"\"><span><input data-instance_id=\""+node.instance_id+"\" data-id=\""+node.id+"\" type=\"checkbox\" name=\"ids[]\" value=\""+node.id+"\"/></span><span style='width: 80px;'>"+node.instance_id+"</span><span>"+node.instance_type+"</span><span>"+node.state_name+"</span><span class=\"url ellipsis\">"+node.public_dns_name+"</span></li>");
		});

		if (wait !== 'undefined' && wait) {
			$.post('<?php echo site_url('site_crawler/wait_terminate_instances');?>', { ids: ids }, function(data) {
				loadCurrentList();
			});
		}
    });
}

$(function () {
	jQuery(document).ready(function($) {
		loadCurrentList();
	});

	$(document).on('click', 'input#checkAll', function(){
		$("#Current_List > ul > li input[type='checkbox']").each(function(index, value) {
			$(this).attr('checked', $('input#checkAll').is(':checked'));
    	});
	});
});
</script>
