<div class="<?php echo $wrapper_class . ( $is_extended_partial ? ' selectable_summary_info' : '') ?>" >
	<?php if ($is_extended_partial): ?>			
		<div class="total_items_selected_by_filter_wrapper non-selectable mt_10 ml_15" data-filterid="<?php echo $batch_set ?>total_items_selected_by_filter" style="display: none">
			<div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_number.png">Total items selected: <span class="<?php echo $batch_set ?>total_items_selected_by_filter mr_10" ></span></div>
		</div>
	<?php endif ?>
	
	<?php echo render_filter_item($batch_set . 'assess_report_total_items', 'assess_report_number.png', 'Total SKUs Analyzed:', 'batch1_filter_item', $is_extended_partial, array('explanation' => 'The total number of SKUs in the batch that were analyzed.')) ?>	
	
	<?php if ($is_extended_partial): ?>				
		<?php echo render_filter_item($batch_set . 'assess_report_competitor_matches_number', 'assess_report_number.png', 'Total number of corresponding SKUs on competitor site:', 'batch2_filter_item', $is_extended_partial, array('explanation' => 'The total number of SKUs from the batch for which we found corresponding products on the competitor’s site.')) ?>			
	<?php endif ?>
	
	<?php echo render_filter_item($batch_set . 'assess_report_items_priced_higher_than_competitors', 'assess_report_dollar.png', 'SKUs priced higher than competitor:', '', $is_extended_partial, array('explanation' => 'The number of your SKUs with matching competitor SKUs that are priced higher than your competitor.')) ?>				
	
	<?php 
		if ($is_extended_partial)														
			$this->load->view('assess/_summary_compare', array(
				'batch_set' => $batch_set
			));					
		else																		
			$this->load->view('assess/_summary_summary', array(
				'batch_set' => $batch_set
			));										
	?>
</div>
