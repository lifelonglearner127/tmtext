<?php $filter_items = get_filters() ?>
<?php foreach ($user_filters_order ? array_flip($user_filters_order): $filter_items as $key => $filter_item): ?>
	<?php $filter_item = $filter_items[$key] ?>
	<?php		
		if (!$user_filters)
			$is_displayed = isset($filter_item['is_default']) && $filter_item['is_default'] ? 'block' : 'none';
		else
			$is_displayed = in_array($filter_item['data_filter_id'], $user_filters) ? 'block' : 'none';		
	?>
	
	<?php if (isset($filter_item['has_competitor']) && $filter_item['has_competitor']): ?>
		<div class="batch_me_and_competitor" style="display: <?php echo $is_displayed ?>" data-filterid="<?php echo $batch_set . $filter_item['data_filter_id'] ?>">
			<?php echo render_filter_item($key, $batch_set . $filter_item['data_filter_id'], $filter_item['icon'], $filter_item['label'], 'batch1_filter_item', true, $filter_item['question']['batch1'], $is_displayed) ?>					
			<div class="selectable_summary_handle_with_competitor"><i class="icon-move"></i></div>
			
			<?php
				$batch2_id = isset($filter_item['competitor']) ? $filter_item['competitor']['data_filter_id'] : $filter_item['data_filter_id'] . '_competitor';
				$batch2_label = isset($filter_item['competitor']) ? $filter_item['competitor']['label'] : 'Competitor ' . $filter_item['label'];
			?>
			
			<?php echo render_filter_item($key, $batch_set . $batch2_id, $filter_item['icon'], $batch2_label, 'batch2_filter_item', true, $filter_item['question']['batch2'], $is_displayed) ?>										
			<div style="clear: both" class="item_line_clear"></div>
		</div>
	<?php else: ?>		
		<?php echo render_filter_item($key, $batch_set . $filter_item['data_filter_id'], $filter_item['icon'], $filter_item['label'], '', true, $filter_item['question'], $is_displayed) ?>						
	<?php endif ?>	
		
<?php endforeach ?>