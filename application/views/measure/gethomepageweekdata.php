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
					    		<li><a data-item="<?php echo $v; ?>" data-value="<?php echo $val['name_val']; ?>" href="javascript:void(0)"><?php echo $val['name']; ?></a></li>
					    	<?php } ?>
					    </ul>
				    </div>
			    <?php } ?>
				<div class='art_hp_item'>
					<div id="art_img_<?php echo $v; ?>" class='art_img'>&nbsp;</div>
					<div class='art_oview'>
						<p class='h'>&nbsp;</p>
						<p class='t'>&nbsp;</p>
					</div>
				</div>
			</div>	
		<?php } ?>
		</div>
	<?php } ?>
</div>

<script type="text/javascript">
	$(document).ready(function() {
		$(".hp_boot_drop .dropdown-menu > li > a").bind('click', function(e) {
			var new_caret = $.trim($(this).text());
			var item_id = $(this).data('item');
			$("#hp_boot_drop_" + item_id + " .btn_caret_sign").text(new_caret);
			// ---- ATTEMPT TO GET SCREENSHOT (START)
			var getwebshootbyurl = $.post(base_url + 'index.php/measure/getwebshootbyurl', { url: new_caret }, function(data) {
				$("#art_img_" + item_id).html("<img src='" + data['img'] + "'>");
			});
			// ---- ATTEMPT TO GET SCREENSHOT (END)
		});
	});
</script>