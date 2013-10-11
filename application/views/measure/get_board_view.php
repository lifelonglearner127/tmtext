<?php if(count($board_list) > 0) { ?>

	<?php 
		$item_per_row = 4;
		$render_rows = ceil(count($board_list)/$item_per_row);
	?>

	<?php for($i = 1; $i <= $render_rows; $i++) { ?>
		<?php $position = $item_per_row*($i-1); ?>
		<?php $board_row = array_slice($board_list, $position, $item_per_row); ?>
		<div class='board_item_row'>
			<?php foreach($board_row as $k => $v) { ?>
			  <?php 
			  	$red_border_cl = "";
			  	$item_lm = "";
			  	if($v['description_words'] == 0) {
			  		$red_border_cl = " red_border_cl";
			  	}
			  	if($k != 0) $item_lm = " board_item_ml";
			  ?>
				<div class="board_item<?php echo $red_border_cl.$item_lm; ?>">
					<input type='hidden' name='dm_id' value="<?php echo $v['id'] ?>">
					<p><?php echo $v['text']; ?></p>
					<img src="<?php echo $v['snap'] ?>">
					<div class='prod_description_new'>
						<p style='font-size: 11px; margin-top: 15px; margin-bottom: 0px; color: #949494'>Description: <?php echo $v['description_words'] ?> words</p>
					</div>
				</div>
			<?php } ?>
		</div>
	<?php } ?>

<?php } ?>