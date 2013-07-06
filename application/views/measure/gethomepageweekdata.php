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
			$row_items = array('1', '2', '3'); // tmp for mockup
		?>
		<?php foreach($row_items as $k=>$v) { ?>
			<div class='span4 item'>
				<div class='art_hp_select_item'>&nbsp;</div>
				<div class='art_hp_item'>
					<div class='art_img'>&nbsp;</div>
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