<div class="main_content_other"></div>
<div class="tabbable">
    <ul class="nav nav-tabs jq-measure-tabs">
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('measure');?>">Home Pages</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_departments');?>">Categories</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_products');?>">Products</a></li>
        <!--<li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_social'); ?>">Social</a></li>-->
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_pricing');?>">Pricing</a></li>
    </ul>
    <div class="tab-content">
    	<div class="row-fluid home_pages">

    		<div class='span12 head_section'>
	    		<p class='head_line1'>Home page reports are generated weekly. <a onclick="viewRecipientsList()" href='javascript:void(0)'>Configure Recipients</a></p>
				<div class='head_line_2'>
					<div class="span2 span_lh_30">View Reports for:</div>
					<div class="span2 w_100 ml_disable">
						<select id='year_s' class='year_s' onchange="changeHomePageYersHandler()">
							<?php for($i = 1980; $i <= $c_year; $i++) { ?>
							<?php $selected = ""; if($i == $c_year) $selected = 'selected'; ?>
							<option <?php echo $selected; ?> value="<?php echo $i; ?>"><?php echo $i; ?></option>
							<?php } ?>
						</select>
					</div>
					<div class="span1 ml_disable span_lh_30">week:</div>
					<div class='span6 ml_disable'>
						<div class="pagination">
							<ul id='timeline_ctr'>
								<?php 
									$intervals_count = ceil(52/7);
									$intervals = array(
										array(1, 2, 3, 4, 5, 6, 7),
										array(8, 9, 10, 11, 12, 13, 14),
										array(15, 16, 17, 18, 19, 20, 21),
										array(22, 23, 24, 25, 26, 27, 28),
										array(29, 30, 31, 32, 33, 34, 35),
										array(36, 37, 38, 39, 40, 41, 42),
										array(43, 44, 45, 46, 47, 48, 49),
										array(50, 51, 52)
									);
									$key_int = 0;
									foreach ($intervals as $key => $value) {
										if(in_array($c_week, $value)) {
											$key_int = $key;
										}
									}
									$int_cell = $intervals[$key_int];
									$int_cell_start = $int_cell[0];
									$int_cell_end = $int_cell[count($int_cell) - 1];
									$block_next_sl = false;
								?>
								<?php if($key_int == 0) { ?>
								<li class='page_prev'><a id="slide_prev_timeline" class='tl_full_left disabled' onclick="return false;" href="javascript:void(0)"><i class='icon-chevron-left icon-white'></i></a></li>
								<?php } else { ?>
								<li class='page_prev'><a id="slide_prev_timeline" class='tl_full_left' onclick="slideTimeline('prev')" href="javascript:void(0)"><i class='icon-chevron-left icon-white'></i></a></li>
								<?php } ?>
								<?php if($int_cell_start == $c_week) { ?>
								<li id='page_prev' class="page_prev disabled"><a onclick="return false;" href="javascript:void(0)">&laquo;</a></li>
								<?php } else { ?>
								<li id='page_prev' class="page_prev"><a onclick="prevLocaHomePageWeekData()" href="javascript:void(0)">&laquo;</a></li>
								<?php } ?>
								<?php for($i = $int_cell_start; $i <= $int_cell_end; $i++) { ?>
									<?php 
										$week_screens_count = count($webshoots_model->getWeekAvailableScreens($i, $c_year));
										if($week_screens_count > 0 && $i == $c_week) {
											$mixed_screen = ' mixed_screen';
										} else {
											$mixed_screen = '';
										}
									?>
									<?php if($week_screens_count > 0) { $have_screen = 'have_screen'; } else { $have_screen = ''; } ?>
									<?php if($i == $c_week) { $active = 'active'; $link_active = ' current_week'; } else { $active = ''; $link_active = ''; } ?>
									<?php if($i <= $c_week) { ?>
										<li data-week="<?php echo $i; ?>" class="page <?php echo $active; ?>"><a class="<?php echo $have_screen.$link_active.$mixed_screen; ?>" href="javascript:void(0)" onclick="locaHomePageWeekData('<?php echo $i; ?>')"><?php echo $i; ?></a></li>
									<?php } else { ?>
										<?php $block_next_sl = true; ?>
										<li data-week="<?php echo $i; ?>" class="page disabled blocked"><a class="<?php echo $have_screen.$link_active.$mixed_screen; ?>" href="javascript:void(0)"><?php echo $i; ?></a></li>
									<?php } ?>
								<?php } ?>
								<?php if($block_next_sl) { ?>
									<li id='page_next' class='page_next disabled'><a onclick="return false;" href="javascript:void(0)">&raquo;</a></li>
									<li class='page_next'><a id="slide_next_timeline" class='tl_full_left disabled' onclick="return false;" href="javascript:void(0)"><i class='icon-chevron-right icon-white'></i></a></li>
								<?php } else { ?>
									<?php if($int_cell_end == $c_week) { ?>
									<li id='page_next' class='page_next disabled'><a onclick="return false;" href="javascript:void(0)">&raquo;</a></li>
									<?php } else { ?>
									<li id='page_next' class='page_next'><a onclick="nextLocaHomePageWeekData()" href="javascript:void(0)">&raquo;</a></li>
									<?php } ?>
									<?php if($key_int == 7) { ?>
									<li class='page_next'><a id="slide_next_timeline" class='tl_full_left disabled' onclick="return false;" href="javascript:void(0)"><i class='icon-chevron-right icon-white'></i></a></li>
									<?php } else { ?>
									<li class='page_next'><a id="slide_next_timeline" class='tl_full_left' onclick="slideTimeline('next')" href="javascript:void(0)"><i class='icon-chevron-right icon-white'></i></a></li>
									<?php } ?>
								<?php } ?>
							</ul>
						</div>
					</div>
					<div id="screens_images_slider_wrap" class='span2'>
					<?php if(count($img_av) !== 0) { ?>
						<button onclick='openScreensModalSlider()' class='btn btn-primary enabled-view-all'><i class='icon-eye-open icon-white'></i>&nbsp;View All</button>
						<div class="modal hide fade screens_modal_slider" id='screens_modal_slider'>
							<div class="modal-body">
								<ul id='screens_slider'>
									<?php foreach($img_av as $ka => $va) { ?>
										<li><div class='ss_slider_item_wrapper'><img src="<?php echo $va->img; ?>"></div></li>
									<?php } ?>
								</ul>
							</div>
						</div>
					<?php } else { ?>
						<button class='btn btn-primary disabled-view-all disabled'><i class='icon-eye-open icon-white'></i>&nbsp;View All</button>
					<?php } ?>
					</div>
				</div>
			</div>
			
			<div id='hp_ajax_content' class='span12 body_section ml_disable mt_30'>
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
							$row_items = array(rand(), rand());
						?>
						<?php $dropup = ''; ?>
						<?php foreach($row_items as $k=>$v) { ?>
							<div class='span6 item'>
								<?php 
									$pos = 0;
									if($i == 1 && $k == 0) {
										$pos = 1;
									}
									if($i == 1 && $k == 1) {
										$pos = 2;
									}
									if($i == 2 && $k == 0) {
										$pos = 3;
									}
									if($i == 2 && $k == 1) {
										$pos = 4;
									}
									if($i == 3 && $k == 0) {
										$pos = 5;
									}
									if($i == 3 && $k == 1) {
										$pos = 6;
									}
									// ---- make auto-selection (if it is empty) (start)
									$webshoots_model->screenAutoSelection($c_year, $c_week, $pos, $user_id);
									// ---- make auto-selection (if it is empty) (end)
								?>
								<?php if(count($customers_list) > 0) { ?>
								    <div data-pos="<?php echo $pos; ?>" data-itemid="<?php echo $v; ?>" id="hp_boot_drop_<?php echo $v; ?>" class="btn-group hp_boot_drop">
									    <button class="btn btn-danger btn_caret_sign">[ Choose site ]</button>
									    <button class="btn btn-danger dropdown-toggle" data-toggle="dropdown">
									    	<span class="caret"></span>
									    </button>
									    <ul class="dropdown-menu">
									    	<li><a onclick="resetScreenDrop('<?php echo $user_id; ?>', '<?php echo $pos; ?>', '<?php echo $c_year; ?>', '<?php echo $c_week; ?>')" href="javascript:void(0)">Choose Site</a></li>
									    	<?php foreach($customers_list as $val) { ?>
									    		<?php $val_name = $val['name_val']; $c_url = $val['c_url'];  ?>
									    		<li><a onclick="clickScreenDrop('<?php echo $c_url; ?>', '<?php echo $v; ?>', '<?php echo $pos; ?>', '<?php echo $val_name; ?>')" data-pos="<?php echo $pos; ?>" data-item="<?php echo $v; ?>" data-value="<?php echo $val['name_val']; ?>" href="javascript:void(0)"><?php echo $val['name']; ?></a></li>
									    	<?php } ?>
									    </ul>
								    </div>
								    <span id="crawl_date_<?php echo $v; ?>" class="label label-info label_custom_regular">&nbsp;</span>
							    <?php } ?>
								<div class='art_hp_item'>
									<div id="art_img_<?php echo $v; ?>" class='art_img'>&nbsp;</div>
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
			<a id='customers_screens_crawl' onclick="openCrawlLaunchPanelModal()" class='btn btn-warning'><i class='icon-screenshot'></i>&nbsp;Update screenshots</a>
		</div>
    </div>
</div>

<!-- MODALS (START) -->
<div class="modal hide fade ci_hp_modals" id='shrinktheweb_crawl_modal'>
	<div class="modal-body">&nbsp;</div>
</div>

<div class="modal hide fade ci_hp_modals" id='loading_crawl_modal'>
	<div class="modal-body">
		<p><img src="<?php echo base_url();?>img/loader_scr.gif">&nbsp;&nbsp;&nbsp;Generating screenshot. Please wait...</p>
	</div>
</div>

<div class="modal hide fade ci_hp_modals" id='loader_emailsend_modal'>
	<div class="modal-body">
		<p><img src="<?php echo base_url();?>img/loader_scr.gif">&nbsp;&nbsp;&nbsp;Sending report. Please wait...</p>
	</div>
</div>

<div class="modal hide fade ci_hp_modals" id='success_emailsend_modal'>
	<div class="modal-body">
		<p>Report sent.</p>
	</div>
</div>

<div class="modal hide fade ci_hp_modals" id='configure_email_reports_success'>
	<div class="modal-header">
		<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
		<h3>Reports Configuration Saved</h3>
	</div>
	<div class="modal-body">
		<p><span>Email configuration successfully saved!</span> <span>Use</span> <a href='javascript:void(0)' onclick='redirectToRecipientsListAfterAdd()' >'Recipients List'</a> <span>button to view results.</span></p>
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
				<label class="control-label" for="email_rec">Email recipient(s):</label>
				<div class="controls">
					<input type="text" style="width: 220px;" id="email_rec" name="email_rec" placeholder="recipients..">
					<p class='help-block custom_help_block'>* separate emails by commas</p>
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

<div class="modal hide fade ci_hp_modals crawl_launch_panel" id='recipients_control_panel_modal'></div>

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
		<a href="javascript:void(0)" id="crawl_modal_sbm_btn" class="btn btn-success" onclick="startAllCrawl()">Crawl (refresh) all sites</a>
		<a href="javascript:void(0)" class="btn" data-dismiss="modal">Close</a>
	</div>
</div>

<!-- bootstrap lightbox holder (start) -->
<div id="preview_screenshot_modal" class='lightbox hide fade' tabindex="-1" role="dialog" aria-hidden="true">
	<div class='lightbox-content'>
		<img id="sc_preview" src="">
	</div>
</div>
<!-- bootstrap lightbox holder (end) -->

<!-- MODALS (END) -->

<script type="text/javascript">
	function clickScreenDrop(new_caret, item_id, pos, new_label) {
		$("#hp_boot_drop_" + item_id + " .btn_caret_sign").text(new_label);
		// ---- ATTEMPT TO GET SCREENSHOT (START)
		$("#art_img_" + item_id).append("<div id='loader_over_" + item_id + "' class='loader_over'><img src='" + base_url + "img/loader_scr.gif'></div>");
		var send_data = {
			url: new_caret,
			label: new_label,
			year: $("#year_s > option:selected").val(),
			week: $(".pagination ul li.page.active").data('week'),
			pos: pos
		}
		var getwebshootbyurl = $.post(base_url + 'index.php/measure/getwebshootbyurl', send_data, function(data) {
			$("#loader_over_" + item_id).remove();
			// if(new_caret === 'bloomingdales.com') {
			// 	$("#screen_lightbox_img_" + item_id).attr('src', base_url + "img/bloomingdales_com_wide_half.png");
			// 	var tmp_thumb = base_url + "img/bloomingdales_com_wide_half.png";
			// 	$("#art_img_" + item_id).html("<a href='#screen_lightbox_" + item_id  + "' data-toggle='lightbox'><img style='cursor: pointer; height: 100%' src='" + tmp_thumb + "'></a>");
			// } else {
			// 	$("#screen_lightbox_img_" + item_id).attr('src', data['img']);
			// 	$("#art_img_" + item_id).html("<a href='#screen_lightbox_" + item_id  + "' data-toggle='lightbox' style='background-image: url(" + data['thumb'] + "); background-position: top left; background-repeat: no-repeat;'></a>");
			// }
			$("#screen_lightbox_img_" + item_id).attr('src', data['img']);
			$("#art_img_" + item_id).html("<a href='#screen_lightbox_" + item_id  + "' data-toggle='lightbox' style='background-image: url(" + data['img'] + "); background-position: top left; background-repeat: no-repeat;'></a>");
			
			var t = moment(data['stamp']).format('MMMM Do, YYYY');
			$("#crawl_date_" + item_id).text(t);
		});
		// ---- ATTEMPT TO GET SCREENSHOT (END)
	}
	$(document).ready(function() {
		
		// ---- timeline tooltips (start)
		$("#timeline_ctr .page:not(.disabled, .active) a:not(.have_screen, .current_week, .mixed_screen)").tooltip({
			placement: 'bottom',
			title: 'regular week / no screenshots'
		});
		$("#timeline_ctr .page:not(.disabled) a.current_week:not(.have_screen, .mixed_screen)").tooltip({
			placement: 'bottom',
			title: 'current week / no screenshots'
		});
		$("#timeline_ctr .page:not(.disabled) a.have_screen:not(.current_week, .mixed_screen)").tooltip({
			placement: 'bottom',
			title: 'regular week / available screenshots'
		});
		$("#timeline_ctr .page:not(.disabled) a.mixed_screen").tooltip({
			placement: 'bottom',
			title: 'current week / available screenshots'
		});
		$("#timeline_ctr .page.active:not(.disabled) a:not(.have_screen, .current_week, .mixed_screen)").tooltip({
			placement: 'bottom',
			title: 'selected week / no screenshots'
		});
		// ---- timeline tooltips (end)

		// ---- UI tooltips (start)
		$(".disabled-view-all").tooltip({
			placement: 'bottom',
			title: 'No images on current/selected week'
		});
		$(".btn-rec-ind-send").tooltip({
			placement: 'bottom',
			title: 'Send Report'
		});
		$(".btn-rec-remove").tooltip({
			placement: 'right',
			title: 'Remove'
		});
		// ---- UI tooltips (end)

		$("#customers_screens_crawl").tooltip({
			placement: 'bottom',
			title: 'Open Crawl Launch Control Panel'
		});
        $('title').text("Competitive Intelligence");

        // --- screens dropdowns selections scanner (start)
        var send_data = {
			year: $("#year_s > option:selected").val(),
			week: $(".pagination ul li.page.active").data('week')
		}
        var drop_selection_scan = $.post(base_url + 'index.php/measure/dropselectionscan', send_data, function(data) {
        	for(var i=0; i < data.length; i++) {
        		if(data[i]['cell'] !== false) {
        			var item_id = $(".hp_boot_drop[data-pos='" + data[i]['pos'] + "']").data('itemid'); 
        			$("#screen_lightbox_img_" + item_id).attr('src', data[i]['cell']['img']);
					$("#art_img_" + item_id).html("<a href='#screen_lightbox_" + item_id  + "' data-toggle='lightbox' style='background-image: url(" + data[i]['cell']['img'] + "); background-position: top left; background-repeat: no-repeat;'></a>");
					var t = moment(data[i]['cell']['screen_stamp']).format('MMMM Do, YYYY');
					$("#crawl_date_" + item_id).text(t);
					$("#hp_boot_drop_" + item_id + " .btn_caret_sign").text(data[i]['cell']['label']);
        		}
        	}
        });
        // --- screens dropdowns selections scanner (end)

	});
</script>

<script src="<?php echo base_url();?>js/ci_home_pages.js"></script>

