<?php $is_extended_partial = $wrapper_class == 'assess_report_compare' ?>
<div class="<?php echo $wrapper_class ?>" style="display: <?php echo $display ?>">
	<ul class="ui-sortable">
		<li class="boxes">
			<h3>
				<span>
					Summary
					<!--<span id="summary_message"></span>-->
				</span>
				<a class="ml_10 research_arrow hideShow" onclick="return false;" href="#">
					<img src="<?php echo base_url();?>img/arrow.png">
				</a>
				<span class="assess_report_download_panel" style="float: right;width: 500px;">

					<div style="display: none">
						<span>Download</span>
						<a class="assess_report_download_pdf" target="_blank" data-type="pdf">PDF</a> |
						<a class="assess_report_download_doc" target="_blank" data-type="doc">DOC</a>
					</div>
					<?php if (isset($direct_access) && $direct_access): ?>
						<button class="update_filter_btn btn" style="float: right;margin-top: 7px;" title="Filter" >Update</button>
					<?php else: ?>
						<!--<button class="assess_report_options_dialog_button btn" style="float: right;margin-top: 7px;" title="Report Options"><img class="other-icon" src="<?php echo base_url();?>img/ico-gear.png" /></button>-->
					<?php endif ?>
				</span>
			</h3>
			<div style="clear: both;"></div>												
			<div class="boxes_content resizable" style="padding:0px; height: 200px; overflow-y: scroll">	
					
				<?php
					$this->load->view('assess/_summary_data', array(
						'is_extended_partial' => $is_extended_partial,
						'batch_set' => 'batch_me_',
						'wrapper_class' => 'common_batch1_filter_items',						
					));
					
					$this->load->view('assess/_summary_data', array(
						'is_extended_partial' => $is_extended_partial,
						'batch_set' => 'batch_competitor_',
						'wrapper_class' => 'hidden_batch2_filter_items',						
					));
				?>
				
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