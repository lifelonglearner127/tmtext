<div class='ph_placeholder' data-week="<?php echo $week; ?>">
	<?php 
		$items_count = 6;
		$item_per_row = 3;
		$items_rows = ceil($items_count/$item_per_row);
	?>

	<?php for($i = 1; $i <= $items_rows; $i++) { ?>
		<div class='span12 items_row ml_disable'>
		<?php 
			$position = $item_per_row*($i-1); 
			// $row_items = getRowItemsRowFromBackend($item_per_row, $position); // -- method template to get items from backend // designed in such way that row will not have more than 3 items  
			$row_items = array(rand(), rand(), rand()); // tmp for mockup
		?>
		<?php if($i == $items_rows) $dropup = 'dropup'; else $dropup = ''; ?>
		<?php foreach($row_items as $k=>$v) { ?>
			<div class='span4 item'>
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
					<div class='art_img'><img src="http://images.shrinktheweb.com/xino.php?stwembed=1&stwaccesskeyid=28c77fca6deb748&stwsize=sm&stwurl=http://www.google.com" /></div>
					<div class='art_oview'>
						<p class='h'>Overview</p>
						<p class='t'>text sample</p>
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
		});
	});
</script>