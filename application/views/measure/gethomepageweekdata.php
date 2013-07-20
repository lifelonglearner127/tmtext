<div style='margin-bottom: 15px;'><span class='label label-success'><?php echo $ct_final; ?></span></div>
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
</script>