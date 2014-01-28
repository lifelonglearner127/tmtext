<?php
	$this->load->helper('html');
	$this->load->helper('summary');	
	$is_extended_partial = $wrapper_class == 'assess_report_compare';		
?>
<div class="<?php echo $wrapper_class ?>" style="display: <?php echo $display ?>">
	<ul class="ui-sortable">
		<li class="boxes">
			<h3>
				<span>
					Summary
					<!--<span id="summary_message"></span>-->
				</span>
				<input class="summary_search_field" />
				<a href="#" class="clean_summary_search_field" >
					<i class="icon-large icon-remove"></i>
				</a>
				
				<select class="pre_stored_filters_combos" style="position: relative; top: 3px">
					<option value="0">Select Filter</option>
					<?php foreach ($filters_combos as $filters_combo): ?>
						<option data-comboid="<?php echo $filters_combo->id ?>" value='<?php echo $filters_combo->filters_ids ?>'><?php echo $filters_combo->title ?></option>
					<?php endforeach ?>
				</select>
				<button id="new_filters_combination" class="btn btn-success" style="position: relative; bottom: 2px">New...</button>
				
				<a class="ml_10 research_arrow hideShow" onclick="return false;" href="#">
					<img src="<?php echo base_url();?>img/arrownew.png">
				</a>
				<a href="#" class="show_filters_configuration_popup">
					<!-- <img style="width:32px; heihgt: 32px;" src="<?php echo base_url();?>img/settings@2x.png"> -->
					<img style="width:32px; heihgt: 32px;" src="<?php echo base_url();?>img/gear_32_32.png">
				</a>
                                <div id="div_export" style="float:right;margin: 4px;"></div>
                                <span class="assess_report_download_panel" style="float: right;width: 65px;">

					<div style="display: none">
						<span>Download</span>
						<a class="assess_report_download_pdf" target="_blank" data-type="pdf">PDF</a> |
						<a class="assess_report_download_doc" target="_blank" data-type="doc">DOC</a>
					</div>
					<?php if (isset($direct_access) && $direct_access): ?>
						<button class="update_filter_btn btn-success btn" style="float: right;margin-top: 4px;" title="Filter" >Update</button>
                                	<?php else: ?>
						<!--<button class="assess_report_options_dialog_button btn" style="float: right;margin-top: 7px;" title="Report Options"><img class="other-icon" src="<?php echo base_url();?>img/ico-gear.png" /></button>-->
					<?php endif ?>
				</span>
				<button type="button" class="btn btn-primary summary_edit_btn" id="edit_summary" data-toggle="button">Edit</button>
				<button id="research_assess_update2" class="btn btn-success">Update</button>
			</h3>
			<div style="clear: both;"></div>												
			<div class="boxes_content resizable" style="padding:0px; height: 200px; overflow-y: scroll">	
					
				<?php
					$this->load->view('assess/_summary_data', array(
						'is_extended_partial' => $is_extended_partial,
						'batch_set' => 'batch_me_',
						'user_filters' => $user_filters,
						'user_filters_order' => $user_filters_order,
						'wrapper_class' => 'common_batch1_filter_items',						
					));
					
					$this->load->view('assess/_summary_data', array(
						'is_extended_partial' => $is_extended_partial,
						'batch_set' => 'batch_competitor_',
						'user_filters' => $user_filters,
						'user_filters_order' => $user_filters_order,
						'wrapper_class' => 'hidden_batch2_filter_items',						
					));
				?>				
			</div>
			<div class="filter_expand_btn_wrapper" >	
				<a href="#" class="filter_expand_btn">
					<?php echo img('img/filter_expand_btn.jpg') ?>
				</a>
			</div>
		</li>
		<!--li class="boxes ui-resizable">
			<h3>
				<span>
					<a class="hideShow" onclick="return false;" href="#">
						<img src="<?php echo base_url();?>img/arrow-down.png" style="width:12px;margin-right: 10px">
					</a>
					Product Comparisons
				</span>
			</h3>
			<div style="clear: both;"></div>
			<div class="boxes_content" style="padding:0px;">
				<div id="comparison_detail"></div>
				<div id="comparison_pagination"></div>
			</div>
		</li-->
	</ul>
</div>
<?php 
	if ($is_extended_partial)
		$this->load->view('assess/_summary_filter_config');
?>