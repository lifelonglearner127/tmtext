<div class="<?php echo $wrapper_class . ( $is_extended_partial ? ' selectable_summary_info' : '') ?>" >
	<div class="batch1_filter_item summary_filter_batch_name <?php echo $batch_set ?>batch1_name"></div>
	<div class="batch2_filter_item summary_filter_batch_name <?php echo $batch_set ?>batch2_name"></div>
	<div class="summary_sortable_wrapper">
		<?php if ($is_extended_partial): ?>			
			<div class="total_items_selected_by_filter_wrapper non-selectable mt_10 ml_15" data-filterid="<?php echo $batch_set ?>total_items_selected_by_filter" style="display: none">
				<div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_number.png">Total items selected: <span class="<?php echo $batch_set ?>total_items_selected_by_filter mr_10" ></span></div>
			</div>
		<?php endif ?>
					
		<?php 
			if ($is_extended_partial)														
				$this->load->view('assess/_summary_compare', array(
					'batch_set' => $batch_set,
					'user_filters' => $user_filters,
					'user_filters_order' => $user_filters_order,
				));					
			else																		
				$this->load->view('assess/_summary_summary', array(
					'batch_set' => $batch_set
				));										
		?>
	</div>
</div>
