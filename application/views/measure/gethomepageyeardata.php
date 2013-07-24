<div class='span12 head_section'>
	<p class='head_line1'>Home page reports are generated weekly. <a onclick="configureEmailReportsModal()" href="javascript:void(0)">Configure email reports.</a></p>
	<div class='head_line_2'>
		<div class="span2">View Reports for:</div>
		<div class="span2 w_100 ml_disable">
			<select id='year_s' class='year_s' onchange="changeHomePageYersHandler()">
				<?php for($i = 1980; $i <= 2013; $i++) { ?>
				<?php $selected = ""; if($i == $year) $selected = 'selected'; ?>
				<option <?php echo $selected; ?> value="<?php echo $i; ?>"><?php echo $i; ?></option>
				<?php } ?>
			</select>
		</div>
		<div class="span1 ml_disable">week:</div>
		<div class='span6 ml_disable'>
			<div class="pagination">
				<ul id='timeline_ctr'>
					<?php if($status == 'selected') { ?>
						<li class='page_prev'><a id="slide_prev_timeline" class='tl_full_left disabled' onclick="return false;" href="javascript:void(0)"><i class='icon-chevron-left icon-white'></i></a></li>
						<li id='page_prev' class="page_prev disabled"><a onclick="prevLocaHomePageWeekData()" href="javascript:void(0)">&laquo;</a></li>
						<?php for($i = 1; $i <= 7; $i++) { ?>
							<?php if($i == 1) { $active = 'active'; } else { $active = ''; } ?>
							<li data-week="<?php echo $i; ?>" class="page <?php echo $active; ?>"><a href="javascript:void(0)" onclick="locaHomePageWeekData('<?php echo $i; ?>')"><?php echo $i; ?></a></li>
						<?php } ?>
						<li id='page_next' class='page_next'><a onclick="nextLocaHomePageWeekData()" href="javascript:void(0)">&raquo;</a></li>
						<li class='page_next'><a id="slide_next_timeline" class='tl_full_left' onclick="slideTimeline('next')" href="javascript:void(0)"><i class='icon-chevron-right icon-white'></i></a></li>
					<?php } else { ?>
						<?php 
							$intervals_count = ceil(52/7);
							$intervals = array(
								array(1, 2, 3, 4, 5, 6, 7),
								array(8, 9, 10, 11, 12, 13, 14),
								array(15, 16, 17, 18, 19, 20, 21),
								array(22, 23, 24, 25, 26, 27, 28),
								array(29, 30, 32, 32, 33, 34, 35),
								array(36, 37, 38, 39, 40, 41, 42),
								array(43, 44, 45, 46, 47, 48, 49),
								array(50, 51, 52)
							);
							$key_int = 0;
							foreach ($intervals as $key => $value) {
								if(in_array($week, $value)) {
									$key_int = $key;
								}
							}
							$int_cell = $intervals[$key_int];
							$int_cell_start = $int_cell[0];
							$int_cell_end = $int_cell[count($int_cell) - 1];
						?>
						<?php if($key_int == 0) { ?>
						<li class='page_prev'><a id="slide_prev_timeline" class='tl_full_left disabled' onclick="return false;" href="javascript:void(0)"><i class='icon-chevron-left icon-white'></i></a></li>
						<?php } else { ?>
						<li class='page_prev'><a id="slide_prev_timeline" class='tl_full_left' onclick="slideTimeline('prev')" href="javascript:void(0)"><i class='icon-chevron-left icon-white'></i></a></li>
						<?php } ?>
						<?php if($int_cell_start == $week) { ?>
						<li id='page_prev' class="page_prev disabled"><a onclick="return false;" href="javascript:void(0)">&laquo;</a></li>
						<?php } else { ?>
						<li id='page_prev' class="page_prev"><a onclick="prevLocaHomePageWeekData()" href="javascript:void(0)">&laquo;</a></li>
						<?php } ?>
						<?php for($i = $int_cell_start; $i <= $int_cell_end; $i++) { ?>
							<?php if($i == $week) { $active = 'active'; } else { $active = ''; } ?>
							<li data-week="<?php echo $i; ?>" class="page <?php echo $active; ?>"><a href="javascript:void(0)" onclick="locaHomePageWeekData('<?php echo $i; ?>')"><?php echo $i; ?></a></li>
						<?php } ?>
						<?php if($int_cell_end == $week) { ?>
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
	</div>
</div>

<div id='hp_ajax_content' class='span12 body_section ml_disable mt_30'>
	<div style='margin-bottom: 10px;'>
		<?php if($img_av !== false) { ?>
			<button class='btn btn-primary'><i class='icon-eye-open icon-white'></i>&nbsp;View All Week Images</i></button>
			<span class='label label-success'>images view available for this week</span>
		<?php } else { ?>
			<button class='btn btn-primary disabled'><i class='icon-eye-open icon-white'></i>&nbsp;View All Week Images</i></button>
			<span class='label label-important'>no available images for this week</span>
		<?php } ?>
	</div>
	<div style='margin-bottom: 15px;'>
		<span class='label label-success'><?php if($status == 'selected') { ?>Selected date:<?php } else { ?>Current date:<?php } ?> <b id='current_date'><?php echo $ct_final; ?></b></span>
		<span class='label label-success'><?php if($status == 'selected') { ?>Selected week:<?php } else { ?>Current week:<?php } ?> <b id='current_week'><?php echo $week; ?></b></label>
	</div>
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
					?>
					<?php if(count($customers_list) > 0) { ?>
					    <div data-pos="<?php echo $pos; ?>" data-itemid="<?php echo $v; ?>" id="hp_boot_drop_<?php echo $v; ?>" class="btn-group hp_boot_drop">
						    <button class="btn btn-danger btn_caret_sign">[ Choose site ]</button>
						    <button class="btn btn-danger dropdown-toggle" data-toggle="dropdown">
						    	<span class="caret"></span>
						    </button>
						    <ul class="dropdown-menu">
						    	<?php foreach($customers_list as $val) { ?>
						    		<?php $val_name = $val['name_val']; ?>
						    		<li><a onclick="clickScreenDrop('<?php echo $val_name; ?>', '<?php echo $v; ?>', '<?php echo $pos; ?>')" data-pos="<?php echo $pos; ?>" data-item="<?php echo $v; ?>" data-value="<?php echo $val['name_val']; ?>" href="javascript:void(0)"><?php echo $val['name']; ?></a></li>
						    	<?php } ?>
						    </ul>
					    </div>
					    <span id="crawl_date_<?php echo $v; ?>" class="label label-info">date</span>
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

<a id='customers_screens_crawl' onclick="openCrawlLaunchPanelModal()" class='btn btn-warning'><i class='icon-file'></i>&nbsp;Crawl sites screenshots interface</a>
<!-- <a id='overview_screens_crawl' onclick="openOverviewScreensCrawlModal()" class='btn btn-success'><i class='icon-print'></i>&nbsp;Overview crawl results</a> -->

<script type="text/javascript">
	function clickScreenDrop(new_caret, item_id, pos) {
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
			var send_data = {
				url: new_caret,
				year: $("#year_s > option:selected").val(),
				week: $(".pagination ul li.page.active").data('week'),
				pos: pos
			}
			var getwebshootbyurl = $.post(base_url + 'index.php/measure/getwebshootbyurl', send_data, function(data) {
				$("#screen_lightbox_img_" + item_id).attr('src', data['img']);
				$("#loader_over_" + item_id).remove();
				// $("#art_img_" + item_id).html("<a href='#screen_lightbox_" + item_id  + "' data-toggle='lightbox'><img style='cursor: pointer;' src='" + data['thumb'] + "'></a>");
				// $("#art_img_" + item_id).html("<a href='#screen_lightbox_" + item_id  + "' data-toggle='lightbox' style='background-image: url(" + data['img'] + ")'></a>");
				$("#art_img_" + item_id).html("<a href='#screen_lightbox_" + item_id  + "' data-toggle='lightbox' style='background-image: url(" + data['thumb'] + "); background-position: top center; background-repeat: no-repeat;'></a>");
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
					// $("#art_img_" + item_id).html("<a href='#screen_lightbox_" + item_id  + "' data-toggle='lightbox'><img style='cursor: pointer;' src='" + data[i]['cell']['thumb'] + "'></a>");
					// $("#art_img_" + item_id).html("<a href='#screen_lightbox_" + item_id  + "' data-toggle='lightbox' style='background-image: url(" + data[i]['cell']['img'] + ")'></a>");
					$("#art_img_" + item_id).html("<a href='#screen_lightbox_" + item_id  + "' data-toggle='lightbox' style='background-image: url(" + data[i]['cell']['thumb'] + "); background-position: top center; background-repeat: no-repeat;'></a>");
					var t = moment(data[i]['cell']['screen_stamp']).format('MMMM Do, YYYY');
					$("#crawl_date_" + item_id).text(t);
					$("#hp_boot_drop_" + item_id + " .btn_caret_sign").text(data[i]['cell']['site']);
	    		}
	    	}
	    });
	    // --- screens dropdowns selections scanner (end)

	});
</script>
