<div>
	<div id="content">
<?php echo $search_results; ?>
	</div>

<?php echo $file_id; ?>
	<div id="products">
<?php echo ul($product_descriptions,
			array('id' => 'product_descriptions')
		); ?>
	</div>

	<p id="product_title"><?php echo $product_title; ?></p>
</div>