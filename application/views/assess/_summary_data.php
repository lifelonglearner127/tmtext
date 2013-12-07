<div class="<?php echo $wrapper_class . ( $is_extended_partial ? ' selectable_summary_info' : '') ?>" >
	<?php if ($is_extended_partial): ?>	
		<div class="total_items_selected_by_filter_wrapper non-selectable mt_10 ml_15" data-filterid="<?php echo $batch_set ?>total_items_selected_by_filter" style="display: none">
			<div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_number.png">Total items selected: <span class="<?php echo $batch_set ?>total_items_selected_by_filter mr_10" ></span></div>
		</div>
	<?php endif ?>
	
	<div class="mt_10 ml_15 non-selectable" data-filterid="<?php echo $batch_set ?>assess_report_total_items">
		<div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_number.png">Total SKUs analyzed: <span class="<?php echo $batch_set ?>assess_report_total_items mr_10" ></span></div>
	</div>
	
	<?php if ($is_extended_partial): ?>				
		<div class="mt_10 ml_15 non-selectable" data-filterid="<?php echo $batch_set ?>assess_report_competitor_matches_number">
			<div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_number.png">Total number of corresponding SKUs found on competitor site: <span class="<?php echo $batch_set ?>assess_report_competitor_matches_number mr_10" ></span></div>
		</div>				
	<?php endif ?>
	
	
	<div class="mt_10 ml_15 <?php echo $is_extended_partial ? 'ui-widget-content' : '' ?>" data-filterid="<?php echo $batch_set ?>assess_report_items_priced_higher_than_competitors">
		<div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_dollar.png">SKUs priced higher than competitors: <span class="<?php echo $batch_set ?>assess_report_items_priced_higher_than_competitors mr_10" ></span></div>
	</div>
	
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
