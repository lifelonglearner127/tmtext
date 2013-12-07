<?php 
	$filter_items = array(
		array(
			'data_filter_id' => 'skus_shorter_than_competitor_product_content',
			'icon' => 'assess_report_seo_red.png',
			'label' => 'SKUs that have shorter product content than competitor:'
		),
		array(
			'data_filter_id' => 'skus_longer_than_competitor_product_content',
			'icon' => 'assess_report_seo.png',
			'label' => 'SKUs that have longer product content than competitor:'
		),
		array(
			'data_filter_id' => 'skus_same_competitor_product_content',
			'icon' => 'assess_report_seo.png',
			'label' => 'SKUs that have same length product content as competitor:'
		),
		array(
			'data_filter_id' => 'skus_fewer_50_product_content',
			'icon' => 'assess_report_seo_red.png',
			'label' => 'SKUs with product content < 50 words:',
			'class' => 'batch1_filter_item'
		),
		array(
			'data_filter_id' => 'skus_fewer_50_product_content_competitor',
			'icon' => 'assess_report_seo_red.png',
			'label' => 'Competitor SKUs with product content < 50 words:',
			'class' => 'batch2_filter_item'
		),
		array(
			'data_filter_id' => 'skus_fewer_100_product_content',
			'icon' => 'assess_report_seo_red.png',
			'label' => 'SKUs with product content < 100 words:',
			'class' => 'batch1_filter_item'
		),
		array(
			'data_filter_id' => 'skus_fewer_100_product_content_competitor',
			'icon' => 'assess_report_seo_red.png',
			'label' => 'Competitor SKUs with product content < 100 words:',
			'class' => 'batch2_filter_item'
		),
		array(
			'data_filter_id' => 'skus_fewer_150_product_content',
			'icon' => 'assess_report_seo_red.png',
			'label' => 'SKUs with product content < 150 words:',
			'class' => 'batch1_filter_item'
		),
		array(
			'data_filter_id' => 'skus_fewer_150_product_content_competitor',
			'icon' => 'assess_report_seo_red.png',
			'label' => 'Competitor SKUs with product content < 150 words:',
			'class' => 'batch2_filter_item'
		),
		array(
			'data_filter_id' => 'skus_fewer_competitor_optimized_keywords',
			'icon' => 'assess_report_seo_red.png',
			'label' => 'SKUs that have product content with fewer keywords optimized than competitor:',			
		),
		array(
			'data_filter_id' => 'skus_zero_optimized_keywords',
			'icon' => 'assess_report_seo_red.png',
			'label' => 'SKUs that have product content with zero optimized title keywords:',			
		),
		array(
			'data_filter_id' => 'skus_one_optimized_keywords',
			'icon' => 'assess_report_seo_red.png',
			'label' => 'SKUs that have product content with one optimized title keyword:',			
		),
		array(
			'data_filter_id' => 'skus_two_optimized_keywords',
			'icon' => 'assess_report_seo_yellow.png',
			'label' => 'SKUs that have product content with two optimized title keywords:',			
		),
		array(
			'data_filter_id' => 'skus_three_optimized_keywords',
			'icon' => 'assess_report_seo.png',
			'label' => 'SKUs that have product content with three optimized title keywords:',			
		),
		array(
			'data_filter_id' => 'skus_fewer_reviews_than_competitor',
			'icon' => 'assess_report_seo_red.png',
			'label' => 'SKUs that have fewer reviews than competitor:',			
		),
		array(
			'data_filter_id' => 'skus_reviews',
			'icon' => 'assess_report_seo_red.png',
			'label' => 'SKUs that have reviews:',	
			'class' => 'batch1_filter_item'			
		),
		array(
			'data_filter_id' => 'skus_reviews_competitor',
			'icon' => 'assess_report_seo_red.png',
			'label' => 'Competitor SKUs that have reviews:',	
			'class' => 'batch2_filter_item'			
		),
		array(
			'data_filter_id' => 'skus_fewer_features_than_competitor',
			'icon' => 'assess_report_seo.png',
			'label' => 'SKUs that have fewer features than competitor:',				
		),
		array(
			'data_filter_id' => 'skus_features',
			'icon' => 'assess_report_seo.png',
			'label' => 'SKUs that have features:',
			'class' => 'batch1_filter_item'				
		),
		array(
			'data_filter_id' => 'skus_features_competitor',
			'icon' => 'assess_report_seo.png',
			'label' => 'Competitor SKUs that have features:',
			'class' => 'batch2_filter_item'				
		),
		array(
			'data_filter_id' => 'skus_75_duplicate_content',
			'icon' => 'assess_report_seo_red.png',
			'label' => 'SKUs that have 75% or more duplicate content:',						
		),
		array(
			'data_filter_id' => 'skus_50_duplicate_content',
			'icon' => 'assess_report_seo_red.png',
			'label' => 'SKUs that have 50% or more duplicate content:',						
		),
		array(
			'data_filter_id' => 'skus_25_duplicate_content',
			'icon' => 'assess_report_seo_yellow.png',
			'label' => 'SKUs that have 25% or more duplicate content:',						
		),
		array(
			'data_filter_id' => 'skus_third_party_content',
			'icon' => 'assess_report_seo.png',
			'label' => 'SKUs that have third party content:',
			'class' => 'batch1_filter_item'	
		),
		array(
			'data_filter_id' => 'skus_third_party_content_competitor',
			'icon' => 'assess_report_seo.png',
			'label' => 'Competitor SKUs that have third party content:',
			'class' => 'batch2_filter_item'	
		),
		array(
			'data_filter_id' => 'skus_pdfs',
			'icon' => 'assess_report_seo.png',
			'label' => 'SKUs that have PDFs:',
			'class' => 'batch1_filter_item'	
		),
		array(
			'data_filter_id' => 'skus_pdfs_competitor',
			'icon' => 'assess_report_seo.png',
			'label' => 'Competitor SKUs that have PDFs:',
			'class' => 'batch2_filter_item'	
		),
	);
?>
<?php foreach ($filter_items as $filter_item): ?>
	<div class="mt_10 ml_15 ui-widget-content <?php echo isset($filter_item['class']) ? $filter_item['class'] : '' ?>" data-filterid="<?php echo $batch_set . $filter_item['data_filter_id'] ?>">
		<div class="mr_10">
			<img src="<?php echo base_url(); ?>img/<?php echo $filter_item['icon'] ?>" />
			<?php echo $filter_item['label'] ?> 
			<span class="<?php echo $batch_set . $filter_item['data_filter_id'] ?> mr_10" ></span>
		</div>
	</div>
<?php endforeach ?>