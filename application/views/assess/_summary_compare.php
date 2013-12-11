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
			'has_competitor' => true
		),		
		array(
			'data_filter_id' => 'skus_fewer_100_product_content',
			'icon' => 'assess_report_seo_red.png',
			'label' => 'SKUs with product content < 100 words:',
			'has_competitor' => true
		),		
		array(
			'data_filter_id' => 'skus_fewer_150_product_content',
			'icon' => 'assess_report_seo_red.png',
			'label' => 'SKUs with product content < 150 words:',
			'has_competitor' => true
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
			'data_filter_id' => 'skus_zero_reviews',
			'icon' => 'assess_report_seo_red.png',
			'label' => 'SKUs that have 0 reviews:',	
			'has_competitor' => true			
		),
		array(
			'data_filter_id' => 'skus_one_four_reviews',
			'icon' => 'assess_report_seo_red.png',
			'label' => 'SKUs that have 1 - 4 reviews:',	
			'has_competitor' => true			
		),
		array(
			'data_filter_id' => 'skus_more_than_five_reviews',
			'icon' => 'assess_report_seo_red.png',
			'label' => 'SKUs that have 5 or more reviews:',	
			'has_competitor' => true			
		),
		array(
			'data_filter_id' => 'skus_more_than_hundred_reviews',
			'icon' => 'assess_report_seo_red.png',
			'label' => 'SKUs that have 100 or more reviews:',	
			'has_competitor' => true			
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
			'has_competitor' => true				
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
			'has_competitor' => true	
		),		
		array(
			'data_filter_id' => 'skus_pdfs',
			'icon' => 'assess_report_seo.png',
			'label' => 'SKUs that have PDFs:',
			'has_competitor' => true	
		)		
	);
?>
<?php foreach ($filter_items as $filter_item): ?>
	
	<?php if (isset($filter_item['has_competitor']) && $filter_item['has_competitor']): ?>
	
		<div class="mt_10 ml_15 ui-widget-content batch1_filter_item" data-filterid="<?php echo $batch_set . $filter_item['data_filter_id'] ?>">
			<div class="mr_10">
				<img src="<?php echo base_url(); ?>img/<?php echo $filter_item['icon'] ?>" />
				<?php echo $filter_item['label'] ?> 
				<span class="<?php echo $batch_set . $filter_item['data_filter_id'] ?> mr_10" ></span>
			</div>
		</div>
		
		<div class="mt_10 ml_15 ui-widget-content batch2_filter_item" data-filterid="<?php echo $batch_set . $filter_item['data_filter_id'] ?>_competitor">
			<div class="mr_10">
				<img src="<?php echo base_url(); ?>img/<?php echo $filter_item['icon'] ?>" />
				Competitor <?php echo $filter_item['label'] ?> 
				<span class="<?php echo $batch_set . $filter_item['data_filter_id'] ?>_competitor mr_10" ></span>
			</div>
		</div>
		
		<div style="clear: both"></div>
		
	<?php else: ?>
	
		<div class="mt_10 ml_15 ui-widget-content" data-filterid="<?php echo $batch_set . $filter_item['data_filter_id'] ?>">
			<div class="mr_10">
				<img src="<?php echo base_url(); ?>img/<?php echo $filter_item['icon'] ?>" />
				<?php echo $filter_item['label'] ?> 
				<span class="<?php echo $batch_set . $filter_item['data_filter_id'] ?> mr_10" ></span>
			</div>
		</div>
	
	<?php endif ?>	
	
<?php endforeach ?>