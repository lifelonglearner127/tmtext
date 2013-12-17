<?php $filter_items = get_filters() ?>
<?php foreach ($filter_items as $filter_item): ?>
	
	<?php		
		if (!$user_filters)
			$is_displayed = isset($filter_item['is_default']) && $filter_item['is_default'] ? 'block' : 'none';
		else
			$is_displayed = in_array($filter_item['data_filter_id'], $user_filters) ? 'block' : 'none';		
	?>
	
	<?php if (isset($filter_item['has_competitor']) && $filter_item['has_competitor']): ?>
			
		<?php echo render_filter_item($batch_set . $filter_item['data_filter_id'], $filter_item['icon'], $filter_item['label'], 'batch1_filter_item', true, $filter_item['question']['batch1'], $is_displayed) ?>				
		<?php echo render_filter_item($batch_set . $filter_item['data_filter_id'] . '_competitor', $filter_item['icon'], 'Competitor ' . $filter_item['label'], 'batch2_filter_item', true, $filter_item['question']['batch2'], $is_displayed) ?>										
	<?php else: ?>		
		<?php echo render_filter_item($batch_set . $filter_item['data_filter_id'], $filter_item['icon'], $filter_item['label'], '', true, $filter_item['question'], $is_displayed) ?>				
	<?php endif ?>	
	
	<div style="clear: both" class="item_line_clear"></div>
	
	
<?php endforeach ?>