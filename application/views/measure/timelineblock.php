<ul id='timeline_ctr'>
	<?php $block_next_sl = false; ?>
	<?php if($state == 'prev' && ($first_cwp - 7) == 1) { ?>
	<li class='page_prev'><a class='tl_full_left disabled' onclick="return false;" href="javascript:void(0)"><i class='icon-chevron-left icon-white'></i></a></li>
	<?php } else { ?>
	<li class='page_prev'><a class='tl_full_left' onclick="slideTimeline('prev')" href="javascript:void(0)"><i class='icon-chevron-left icon-white'></i></a></li>
	<?php } ?>

	
	<li id='page_prev' class="page_prev disabled"><a onclick="return false;" href="javascript:void(0)">&laquo;</a></li>
	
	<?php if($state == 'next') { ?>

		<?php
			$start_it = $last_cwp + 1; 
			if($last_cwp ==  49) {
				$limit_it = 52; 
			} else {
				$limit_it = $last_cwp + 7; 
			}
		?>
		<?php for($i = $start_it; $i <= $limit_it; $i++) { ?>
			<?php if($i == $week) { $active = 'active'; } else { $active = ''; } ?>
			<?php if($i <= $week) { ?>
				<li data-week="<?php echo $i; ?>" class="page <?php echo $active; ?>"><a href="javascript:void(0)" onclick="locaHomePageWeekData('<?php echo $i; ?>')"><?php echo $i; ?></a></li>
			<?php } else { ?>
				<?php $block_next_sl = true; ?>
				<li data-week="<?php echo $i; ?>" class="page disabled blocked"><a href="javascript:void(0)"><?php echo $i; ?></a></li>
			<?php } ?>
		<?php } ?>

	<?php } else if($state == 'prev') { ?>

		<?php
			$start_it = $first_cwp - 7; 
			$limit_it = $start_it + 7; 
		?>
		<?php for($i = $start_it; $i < $limit_it; $i++) { ?>
			<?php if($i == $start_it) { $active = 'active'; } else { $active = ''; } ?>
			<?php if($i <= $week) { ?>
				<li data-week="<?php echo $i; ?>" class="page <?php echo $active; ?>"><a href="javascript:void(0)" onclick="locaHomePageWeekData('<?php echo $i; ?>')"><?php echo $i; ?></a></li>
			<?php } else { ?>
				<li data-week="<?php echo $i; ?>" class="page disabled blocked"><a href="javascript:void(0)"><?php echo $i; ?></a></li>
			<?php } ?>
		<?php } ?>

	<?php } ?>
	<?php if($block_next_sl) { ?>
		<li id='page_next' class='page_next disabled'><a onclick="return false;" href="javascript:void(0)">&raquo;</a></li>
		<li class='page_next'><a class='tl_full_left disabled' onclick="return false;" href="javascript:void(0)"><i class='icon-chevron-right icon-white'></i></a></li>
	<?php } else { ?>
		<li id='page_next' class='page_next'><a onclick="nextLocaHomePageWeekData()" href="javascript:void(0)">&raquo;</a></li>
		<?php if($state == 'next' && $limit_it == 52) { ?>
		<li class='page_next'><a class='tl_full_left disabled' onclick="return false;" href="javascript:void(0)"><i class='icon-chevron-right icon-white'></i></a></li>
		<?php } else { ?>
		<li class='page_next'><a class='tl_full_left' onclick="slideTimeline('next')" href="javascript:void(0)"><i class='icon-chevron-right icon-white'></i></a></li>
		<?php } ?>
	<?php } ?>
</ul>

