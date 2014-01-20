<div class="tabbable">
    <ul class="nav nav-tabs jq-system-tabs">
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system');?>">General</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/sites_view');?>">Sites</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('site_crawler');?>">Site Crawler</a></li>
        <li class="active"><a data-toggle="tab" id="ttl" href="<?php echo site_url('site_crawler/instances_list');?>">Crawler Instances <?php $this->load->helper("crawler_instances_helper"); echo crawler_instances_number();?></a></li>
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
                <input type="text" class="span1 ml_20" name="instances" placeholder="Quantity" style="width:10%" />
                <input type="text" class="span1 ml_10" name="instance_price" placeholder="Price" style="width:10%" />
                <button id="run_instances" class="btn new_btn btn-success ml_10"><i class="icon-white icon-ok"></i>&nbsp;Run</button>
                <button id="run_spot_instances" class="btn new_btn btn-success  ml_10"><i class="icon-white icon-ok"></i>&nbsp;Spot Run</button>
                <span class="ml_10" style="font-size: 11px;" >For spot instances enter quantity and price per hour for one instance</span>
            </div>
			<div class="row-fluid mt_5" style="width: 75%; float: right; padding-right: 60px;">
				<div class="search_area uneditable-input span10" style="cursor: text; width: 765px; height: 120px; overflow : auto;" id="Spot_List">
				<ul>
					<lh><span><input type="checkbox" style='margin-top: -6px;' value="" id="checkAllSpots"/></span>
						<span style='width: 80px;'>Request Id</span>
						<span>Price</span>
						<span>InstanceId</span>
						<span>State</span>
						<span>Status Code</span>
					</lh>
				</ul>
				</div>
				<button id="terminate_requests" class="btn new_btn btn-danger mt_10 ml_15"><i class="icon-white icon-ok"></i>&nbsp;Terminate Request</button>
			</div>
			<div class="row-fluid mt_5" style="width: 75%; float: right; padding-right: 60px;">
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

function loadSpotList(wait, ids) {
	$("#checkAllSpots").removeAttr('checked');
	url = '<?php echo site_url('site_crawler/get_spot_requests');?>';

	var from_data = false;
	if (wait == undefined) {
		if (ids == undefined) {
			from_data = true;
		}
	}

	$.get(url, function(data) {
		$('#Spot_List ul li').remove();
		if (data.requests.length && data.requests.length > 0) {
			$('#Spot_List').parent().show();

			if (from_data) {
				wait = true;
				var ids = [];
			}
		} else {
			$('#Spot_List').parent().hide();
		}

		$.each(data.requests, function (index, node) {
			$('#Spot_List ul').append("<li id=\"id_"+node.id+"\"><span><input data-request_id=\""+node.request_id+"\" data-id=\""+node.id+"\" type=\"checkbox\" name=\"ids[]\" value=\""+node.id+"\"/></span><span style='width: 80px;'>"+node.request_id+"</span><span>"+node.price+"</span><span>"+node.instanceid+"</span><span>"+node.state_name+"</span><span class=\"url ellipsis\">"+node.status_code+"</span></li>");
			if (from_data) {
				ids[ids.length] = node.request_id;
			}
		});

		if (wait !== undefined && wait) {
			$.post('<?php echo site_url('site_crawler/wait_spot_instances');?>', { ids: ids }, function(data) {
				if (data.refresh) {
					setTimeout(loadSpotList, 30000);
				} else if (!data.refresh && (ids.length == data.instances.length)) {
					$.post('<?php echo site_url('site_crawler/wait_start_instances/1');?>', { ids: data.instances }, function(data) {
						loadCurrentList();
						loadSpotList(false);
					});
				}
			});
		}
    });
}

function loadCurrentList(wait, ids) {
	$("#checkAll").removeAttr('checked');
	url = '<?php echo site_url('site_crawler/get_instances');?>';

	$.get(url, function(data) {
		$('#Current_List ul li').remove();
		$.each(data.instances, function (index, node) {
			$('#Current_List ul').append("<li id=\"id_"+node.id+"\"><span><input data-instance_id=\""+node.instance_id+"\" data-id=\""+node.id+"\" type=\"checkbox\" name=\"ids[]\" value=\""+node.id+"\"/></span><span style='width: 80px;'>"+node.instance_id+"</span><span>"+node.instance_type+"</span><span>"+node.state_name+"</span><span class=\"url ellipsis\">"+node.public_dns_name+"</span></li>");
		});
		$("#ttl").html("Crawler Instances " + (data.instances.length && data.instances.length > 0 ? "(" + data.instances.length + ")" : ""));

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
		loadSpotList();
		loadCurrentList();
	});

	$(document).on('click', 'input#checkAll', function(){
		$("#Current_List > ul > li input[type='checkbox']").each(function(index, value) {
			$(this).attr('checked', $('input#checkAll').is(':checked'));
    	});
	});

	$(document).on('click', 'input#checkAllSpots', function(){
		$("#Spot_List > ul > li input[type='checkbox']").each(function(index, value) {
			$(this).attr('checked', $('input#checkAllSpots').is(':checked'));
    	});
	});
});
</script>
