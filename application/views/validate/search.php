<div>
	<div id="content">
	<?php
	echo ul($search_results,
			array('id' => 'items_list')
		);
	?>
	</div>
	<div id="pagination">
	<?php echo $pagination; ?>
	</div>
</div>