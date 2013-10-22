<?php if(count($board_list) > 0) { ?>
	<div style='width: 100%; margin-top: 15px;'><a target="_blank" href="<?php echo base_url() ?>index.php/measure/get_board_view_pdf?site_id=<?php echo $site_id; ?>" class='btn btn-primary'>PDF Export</a></div>
	<?php 
		// === re-order stack of items (start)
		$board_list_empty = array();
		$board_list_full = array();
		foreach ($board_list as $key => $value) {
			if($value['description_words'] == 0) {
				$board_list_empty[] = $value;
			} else {
				$board_list_full[] = $value;
			}
		}
		$sort_e = array();
    foreach ($board_list_empty as $k => $v) {
        $sort_e['text'][$k] = $v['text'];
    }
    array_multisort($sort_e['text'], SORT_ASC, $board_list_empty);
    $sort_f = array();
    foreach ($board_list_full as $k => $v) {
        $sort_e['text'][$k] = $v['text'];
    }
    array_multisort($sort_f['text'], SORT_ASC, $board_list_full);
		$board_list = array_merge($board_list_empty, $board_list_full);
		// === re-order stack of items (end)
	?>

	<?php $item_per_row = 4; ?>

	<!-- Render red boxea (start) -->
	<?php if(count($board_list_empty) > 0) { ?>
		<?php 
			$render_red_rows = ceil(count($board_list_empty)/$item_per_row);
		?>
		<?php for($i = 1; $i <= $render_red_rows; $i++) { ?>
			<?php $position = $item_per_row*($i-1); ?>
			<?php $board_row = array_slice($board_list_empty, $position, $item_per_row); ?>
			<div class='board_item_row'>
				<?php foreach($board_row as $k => $v) { ?>
					<?php 
						// $handle = @fopen($v['snap'],'r');
						$handle = false;
						$ch = curl_init($v['snap']);
		        curl_setopt($ch, CURLOPT_TIMEOUT, 5);
		        curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
		        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
		        $data = curl_exec($ch);
		        $httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
		        curl_close($ch);
		        if ($httpcode >= 200 && $httpcode <= 302) {
		        	$handle = true;
		        } 
					?>
					<?php if($handle !== false) { ?>
					  <?php 
					  	$item_lm = "";
					  	if($k != 0) $item_lm = " board_item_ml";
					  ?>
						<div class="board_item red_border_cl<?php echo $item_lm; ?>">
							<div class='board_item_dicon'><img src="<?php echo base_url() ?>/img/diagramm_high.png"></div>
							<input type='hidden' name='dm_id' value="<?php echo $v['id'] ?>">
							<p class='board_item_title st'><?php echo $v['text']; ?></p>
	            <img src="<?php echo $v['snap']; ?>">
							<div class='prod_description_new'>
								<p style='font-size: 11px; margin-top: 15px; margin-bottom: 0px; color: #949494'>Description: <?php echo $v['description_words'] ?> words</p>
							</div>
						</div>
					<?php } ?>
				<?php } ?>
			</div>
		<?php } ?>
	<?php } ?>
	<!-- Render red boxea (end) -->

	<!-- Render gray boxea (start) -->
	<?php if(count($board_list_full) > 0) { ?>
		<?php 
			$render_gray_rows = ceil(count($board_list_full)/$item_per_row);
		?>
		<?php for($i = 1; $i <= $render_gray_rows; $i++) { ?>
			<?php $position = $item_per_row*($i-1); ?>
			<?php $board_row = array_slice($board_list_full, $position, $item_per_row); ?>
			<div class='board_item_row'>
				<?php foreach($board_row as $k => $v) { ?>
					<?php 
						// $handle = @fopen($v['snap'],'r');
						$handle = false;
						$ch = curl_init($v['snap']);
		        curl_setopt($ch, CURLOPT_TIMEOUT, 5);
		        curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
		        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
		        $data = curl_exec($ch);
		        $httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
		        curl_close($ch);
		        if ($httpcode >= 200 && $httpcode <= 302) {
		        	$handle = true;
		        } 
					?>
					<?php if($handle !== false) { ?>
					  <?php 
					  	$item_lm = "";
					  	if($k != 0) $item_lm = " board_item_ml";
					  ?>
						<div class="board_item <?php echo $item_lm; ?>">
							<div class='board_item_dicon'><img src="<?php echo base_url() ?>/img/diagramm_low.png"></div>
							<input type='hidden' name='dm_id' value="<?php echo $v['id'] ?>">
							<p class='board_item_title st'><?php echo $v['text']; ?></p>
	            <img src="<?php echo $v['snap']; ?>">
							<div class='prod_description_new'>
								<p style='font-size: 11px; margin-top: 15px; margin-bottom: 0px; color: #949494'>Description: <?php echo $v['description_words'] ?> words</p>
							</div>
						</div>
					<?php } ?>
				<?php } ?>
			</div>
		<?php } ?>
	<?php } ?>
	<!-- Render gray boxea (end) -->

<?php } ?>

<script type='text/javascript'>
	$(document).ready(function() {
		$(".board_item .board_item_title").bind('mouseover', function(e) {
			$(e.target).addClass('full');
		});

		$(".board_item .board_item_title").bind('mouseleave', function(e) {
			$(e.target).removeClass('full');
		});
	});
</script>