<div class="main_content_other"></div>
<div class="tabbable">
    <ul class="nav nav-tabs jq-measure-tabs">
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('measure');?>">Home Pages</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_departments');?>">Departments & Categories</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_products');?>">Products</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_pricing');?>">Pricing</a></li>
    </ul>
    <div class="tab-content">
    	<div class="row-fluid home_pages">

    		<div class='span12 head_section'>
	    		<p class='head_line1'>Home page reports are generated weekly. <a onclick="configureEmailReportsModal()" href="javascript:void(0)">Configure email reports.</a></p>
				<div class='head_line_2'>
					<div class="span2">View Reports for:</div>
					<div class="span2 w_100 ml_disable">
						<select id='year_s' class='year_s' onchange="changeHomePageYersHandler()">
							<?php for($i = 1980; $i <= 2013; $i++) { ?>
							<?php $selected = ""; if($i == 2013) $selected = 'selected'; ?>
							<option <?php echo $selected; ?> value="<?php echo $i; ?>"><?php echo $i; ?></option>
							<?php } ?>
						</select>
					</div>
					<div class="span1 ml_disable">week:</div>
					<div class='span6 ml_disable'>
						<div class="pagination">
							<!-- <ul>
								<li class='page_prev disabled'><a href="javascript:void(0)">&lsaquo;</a></li>
								<li id='page_prev' class="page_prev disabled"><a onclick="prevLocaHomePageWeekData()" href="javascript:void(0)">&laquo;</a></li>
								<li data-week='1' class="page active"><a href="javascript:void(0)" onclick="locaHomePageWeekData('1')">1</a></li>
								<li data-week='2' class='page'><a href="javascript:void(0)" onclick="locaHomePageWeekData('2')">2</a></li>
								<li data-week='3' class='page'><a href="javascript:void(0)" onclick="locaHomePageWeekData('3')">3</a></li>
								<li data-week='4' class='page'><a href="javascript:void(0)" onclick="locaHomePageWeekData('4')">4</a></li>
								<li data-week='5' class='page'><a href="javascript:void(0)" onclick="locaHomePageWeekData('5')">5</a></li>
								<li data-week='6' class='page'><a href="javascript:void(0)" onclick="locaHomePageWeekData('6')">6</a></li>
								<li data-week='7' class='page'><a href="javascript:void(0)" onclick="locaHomePageWeekData('7')">7</a></li>
								<li id='page_next' class='page_next'><a onclick="nextLocaHomePageWeekData()" href="javascript:void(0)">&raquo;</a></li>
								<li class='page_next disabled'><a href="javascript:void(0)">&rsaquo;</a></li>
							</ul> -->
							<ul id='timeline_ctr'>
								<li class='page_prev'><a id="slide_prev_timeline" class='tl_full_left disabled' onclick="return false;" href="javascript:void(0)"><i class='icon-chevron-left icon-white'></i></a></li>
								<li id='page_prev' class="page_prev disabled"><a onclick="prevLocaHomePageWeekData()" href="javascript:void(0)">&laquo;</a></li>
								<?php for($i = 1; $i <= 7; $i++) { ?>
									<?php if($i == 1) { $active = 'active'; } else { $active = ''; } ?>
									<li data-week="<?php echo $i; ?>" class="page <?php echo $active; ?>"><a href="javascript:void(0)" onclick="locaHomePageWeekData('<?php echo $i; ?>')"><?php echo $i; ?></a></li>
								<?php } ?>
								<li id='page_next' class='page_next'><a onclick="nextLocaHomePageWeekData()" href="javascript:void(0)">&raquo;</a></li>
								<li class='page_next'><a id="slide_next_timeline" class='tl_full_left' onclick="slideTimeline('next')" href="javascript:void(0)"><i class='icon-chevron-right icon-white'></i></a></li>
							</ul>
						</div>
					</div>
				</div>
			</div>
			
			<div id='hp_ajax_content' class='span12 body_section ml_disable mt_30'>
				<div style='margin-bottom: 15px;'><span class='label label-success'><?php echo $ct_final; ?></span></div>
				<div class='ph_placeholder' data-week='1'>
					<?php
						$items_count = 6;
						$item_per_row = 2;
						$items_rows = ceil($items_count/$item_per_row);
					?>

					<?php for($i = 1; $i <= $items_rows; $i++) { ?>
						<div class='span12 items_row ml_disable'>
						<?php
							$position = $item_per_row*($i-1);
							// $row_items = getRowItemsRowFromBackend($item_per_row, $position); // -- method template to get items from backend // designed in such way that row will not have more than 3 items
							// $row_items = array(rand(), rand(), rand()); // tmp for mockup
							$row_items = array(rand(), rand()); // tmp for mockup
						?>
						<?php // if($i == $items_rows) $dropup = 'dropup'; else $dropup = ''; ?>
						<?php $dropup = ''; ?>
						<?php foreach($row_items as $k=>$v) { ?>
							<div class='span6 item'>
								<?php if(count($customers_list) > 0) { ?>
								    <div id="hp_boot_drop_<?php echo $v; ?>" class="btn-group <?php echo $dropup; ?> hp_boot_drop">
									    <button class="btn btn-danger btn_caret_sign">[ Choose site ]</button>
									    <button class="btn btn-danger dropdown-toggle" data-toggle="dropdown">
									    	<span class="caret"></span>
									    </button>
									    <ul class="dropdown-menu">
									    	<?php foreach($customers_list as $val) { ?>
									    		<?php $val_name = $val['name_val']; ?>
									    		<li><a onclick="clickScreenDrop('<?php echo $val_name; ?>', '<?php echo $v; ?>')" data-item="<?php echo $v; ?>" data-value="<?php echo $val['name_val']; ?>" href="javascript:void(0)"><?php echo $val['name']; ?></a></li>
									    	<?php } ?>
									    </ul>
								    </div>
								    <span id="crawl_date_<?php echo $v; ?>" class="label label-info">date</span>
							    <?php } ?>
								<div class='art_hp_item'>
									<div id="art_img_<?php echo $v; ?>" class='art_img'>&nbsp;</div>
									<!-- <div class='art_oview'>
										<p class='h'>&nbsp;</p>
										<p class='t'>&nbsp;</p>
									</div> -->
								</div>
							</div>
							<!-- lightbox holder (start) -->
							<div id="screen_lightbox_<?php echo $v; ?>" class='lightbox hide fade' tabindex="-1" role="dialog" aria-hidden="true">
								<div class='lightbox-content'>
									<img id="screen_lightbox_img_<?php echo $v; ?>" src="">
								</div>
							</div>
							<!-- lightbox holder (end) -->
						<?php } ?>
						</div>
					<?php } ?>
				</div>
			</div>
			<a id='customers_screens_crawl' onclick="openCrawlLaunchPanelModal()" class='btn btn-warning'><i class='icon-file'></i>&nbsp;Crawl sites screenshots interface</a>
			<!-- <a id='overview_screens_crawl' onclick="openOverviewScreensCrawlModal()" class='btn btn-success'><i class='icon-print'></i>&nbsp;Overview crawl results</a> -->
			<!-- <a href="javascript:void(0)" class="btn btn-primary" onclick="test_screenshot()">Test Screenshot</a> -->
		</div>
    </div>
</div>

<!-- MODALS (START) -->
<div class="modal hide fade ci_hp_modals" id='configure_email_reports_success'>
	<div class="modal-header">
		<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
		<h3>Reports Configuration Saved</h3>
	</div>
	<div class="modal-body">
		<p>Email configuration successfully saved!</p>
	</div>
	<div class="modal-footer">
		<a href="javascript:void(0)" class="btn" data-dismiss="modal">Close</a>
	</div>
</div>

<div class="modal hide fade ci_hp_modals" id='configure_email_reports'>
	<div class="modal-header">
		<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
		<h3>Email Reports Configuration</h3>
	</div>
	<div class="modal-body">
		<form action='' onsubmit="return false;" class="form-horizontal">
			<div class="control-group">
				<label class="control-label" for="email_rec">Email recipients:</label>
				<div class="controls">
					<input type="text" style="width: 220px;" id="email_rec" name="email_rec" placeholder="recipients..">
				</div>
			</div>
			<div class="control-group">
				<label class="control-label" style="width: 172px;" for="week_day_rep">Day of week to send report:</label>
				<div class="controls">
					<select id="week_day_rep" name="week_day_rep">
						<option value='monday' selected>Monday</option>
						<option value='tuesday'>Tuesday</option>
						<option value='wednesday'>Wednesday</option>
						<option value='thursday'>Thursday</option>
						<option value="friday">Friday</option>
						<option value='saturday'>Saturday</option>
						<option value='sunday'>Sunday</option>
					</select>
				</div>
			</div>
		</form>
	</div>
	<div class="modal-footer">
		<a href="javascript:void(0)" class="btn" data-dismiss="modal">Cancel</a>
		<a href="javascript:void(0)" class="btn btn-success" onclick="submitEmailReportsConfig()">Save</a>
	</div>
</div>

<div class="modal hide fade ci_hp_modals" id='overview_screens_crawl_modal'>
	<div class="modal-header">
		<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
		<h3>Overview Crawl Results</h3>
	</div>
	<div class="modal-body">

	</div>
	<div class="modal-footer">
		<a href="javascript:void(0)" class="btn" data-dismiss="modal">Close</a>
	</div>
</div>

<div class="modal hide fade ci_hp_modals crawl_launch_panel" id='customers_screens_crawl_modal'>
	<div class="modal-header">
		<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
		<h3>Crawl Launch Control Panel</h3>
	</div>
	<div class="modal-body">
		<div id="cl_cp_crawl_modal" class='cl_cp_crawl_modal'>

		</div>
	</div>
	<div class="modal-footer">
		<a href="javascript:void(0)" class="btn" data-dismiss="modal">Close</a>
		<!-- <a href="javascript:void(0)" id="crawl_modal_sbm_btn" class="btn btn-success" onclick="startCrawl()">Start all crawl</a> -->
	</div>
</div>

<div class="modal hide fade ci_hp_modals" id='preview_screenshot_modal'>
	<div class="modal-header">
		<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
		<h3>Screenshot Review</h3>
	</div>
	<div class="modal-body">
		<div id="sc_preview">&nbsp;</div>
	</div>
	<div class="modal-footer">
		<a href="javascript:void(0)" class="btn" data-dismiss="modal">Close</a>
		<a href="javascript:void(0)" onclick="openCrawlLaunchPanelModal(true)" class="btn btn-success">Back to list</a>
	</div>
</div>

<div class="modal hide fade" id='loading_crawl_modal'>
	<div class="modal-body">
		<p style='line-height: 24px;'><img src="<?php echo base_url() ?>/img/fancybox_loading.gif">&nbsp;&nbsp;Wait for it. Screenshot generating and saving ...</p>
	</div>
</div>

<!-- MODALS (END) -->

<script type="text/javascript">
	function clickScreenDrop(new_caret, item_id) {
		$("#hp_boot_drop_" + item_id + " .btn_caret_sign").text(new_caret);
		if(new_caret === 'bloomingdales.com') { // --- static tmp screens for bloomingdales.com
			$("#screen_lightbox_img_" + item_id).attr('src', base_url + "img/bloomingdales_com_wide_half.png");
			var tmp_thumb = base_url + "img/bloomingdales_com_wide_half.png";
			$("#art_img_" + item_id).html("<a href='#screen_lightbox_" + item_id  + "' data-toggle='lightbox'><img style='cursor: pointer; height: 100%' src='" + tmp_thumb + "'></a>");
			var t = moment().format('MMMM Do, YYYY');
			$("#crawl_date_" + item_id).text(t);
		} else {
			// ---- ATTEMPT TO GET SCREENSHOT (START)
			$("#art_img_" + item_id).append("<div id='loader_over_" + item_id + "' class='loader_over'><img src='" + base_url + "img/loader_scr.gif'></div>");
			var getwebshootbyurl = $.post(base_url + 'index.php/measure/getwebshootbyurl', { url: new_caret }, function(data) {
				$("#screen_lightbox_img_" + item_id).attr('src', data['img']);
				$("#loader_over_" + item_id).remove();
				$("#art_img_" + item_id).html("<a href='#screen_lightbox_" + item_id  + "' data-toggle='lightbox'><img style='cursor: pointer;' src='" + data['thumb'] + "'></a>");
				var t = moment(data['stamp']).format('MMMM Do, YYYY');
				$("#crawl_date_" + item_id).text(t);
			});
			// ---- ATTEMPT TO GET SCREENSHOT (END)
		}
	}
	$(document).ready(function() {
		$("#customers_screens_crawl").tooltip({
			placement: 'bottom',
			title: 'Open Crawl Launch Control Panel'
		});
        $('title').text("Competitive Intelligence");
	});
</script>

<script src="<?php echo base_url();?>js/ci_home_pages.js"></script>

