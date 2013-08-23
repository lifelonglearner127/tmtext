<div class='ph_placeholder' data-week="<?php echo $week; ?>">
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
					$webshoots_model->screenAutoSelection($year, $week, $pos, $user_id);
					// ---- make auto-selection (if it is empty) (end)
				?>
				<?php if(count($customers_list) > 0) { ?>
				    <div data-pos="<?php echo $pos; ?>" data-itemid="<?php echo $v; ?>" id="hp_boot_drop_<?php echo $v; ?>" class="btn-group hp_boot_drop">
					    <button class="btn btn-danger btn_caret_sign">[ Choose site ]</button>
					    <button class="btn btn-danger dropdown-toggle" data-toggle="dropdown">
					    	<span class="caret"></span>
					    </button>
					    <ul class="dropdown-menu">
					    	<?php foreach($customers_list as $val) { ?>
					    		<?php $val_name = $val['name_val']; $c_url = $val['c_url']; ?>
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
			$("#art_img_" + item_id).html("<a href='#screen_lightbox_" + item_id  + "' data-toggle='lightbox' style='background-image: url(" + data['thumb'] + "); background-position: top left; background-repeat: no-repeat;'></a>");

			var t = moment(data['stamp']).format('MMMM Do, YYYY');
			$("#crawl_date_" + item_id).text(t);
		});
		// ---- ATTEMPT TO GET SCREENSHOT (END)
	}

	// --- screens dropdowns selections scanner (start)
    var send_data = {
		year: $("#year_s > option:selected").val(),
		week: $(".pagination ul li.page.active").data('week')
	}
    var drop_selection_scan = $.post(base_url + 'index.php/measure/dropselectionscan', send_data, function(data) {
    	for(var i=0; i < data.length; i++) {
    		if(data[i]['cell'] !== false) {
    			var item_id = $(".hp_boot_drop[data-pos='" + data[i]['pos'] + "']").data('itemid'); 
    			
    	// 		if(data[i]['cell']['site'] === 'bloomingdales.com') {
    	// 			$("#screen_lightbox_img_" + item_id).attr('src', base_url + "img/bloomingdales_com_wide_half.png");
					// var tmp_thumb = base_url + "img/bloomingdales_com_wide_half.png";
					// $("#art_img_" + item_id).html("<a href='#screen_lightbox_" + item_id  + "' data-toggle='lightbox'><img style='cursor: pointer; height: 100%' src='" + tmp_thumb + "'></a>");
    	// 		} else {
    	// 			$("#screen_lightbox_img_" + item_id).attr('src', data[i]['cell']['img']);
					// $("#art_img_" + item_id).html("<a href='#screen_lightbox_" + item_id  + "' data-toggle='lightbox' style='background-image: url(" + data[i]['cell']['thumb'] + "); background-position: top left; background-repeat: no-repeat;'></a>");
    	// 		}

    			$("#screen_lightbox_img_" + item_id).attr('src', data[i]['cell']['img']);
				$("#art_img_" + item_id).html("<a href='#screen_lightbox_" + item_id  + "' data-toggle='lightbox' style='background-image: url(" + data[i]['cell']['thumb'] + "); background-position: top left; background-repeat: no-repeat;'></a>");
    			
				var t = moment(data[i]['cell']['screen_stamp']).format('MMMM Do, YYYY');
				$("#crawl_date_" + item_id).text(t);
				$("#hp_boot_drop_" + item_id + " .btn_caret_sign").text(data[i]['cell']['label']);
    		}
    	}
    });
    // --- screens dropdowns selections scanner (end)

</script>