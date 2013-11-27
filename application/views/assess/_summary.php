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
					<span>Download</span>
					<a class="assess_report_download_pdf" target="_blank" data-type="pdf">PDF |</a> 
					<a class="assess_report_download_doc" target="_blank" data-type="doc">DOC</a>
					<button class="assess_report_options_dialog_button btn" style="float: right;margin-top: 7px;" title="Report Options"><img class="other-icon" src="<?php echo base_url();?>img/ico-gear.png" /></button>
				</span>
			</h3>
			<div style="clear: both;"></div>												
			<div class="boxes_content" style="padding:0px; height: 200px; overflow-y: scroll">
				<div class="mt_10 ml_15">
					<div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_number.png">Total SKUs analyzed: <span class="assess_report_total_items mr_10" ></span></div>
				</div>
				
				<?php if ($is_extended_partial): ?>				
					<div class="mt_10 ml_15">
						<div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_number.png">Total number of competitor matches: <span class="assess_report_competitor_matches_number mr_10" ></span></div>
					</div>				
				<?php endif ?>
				
				
				<div class="mt_10 ml_15">
					<div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_dollar.png">SKUs priced higher than competitors: <span class="assess_report_items_priced_higher_than_competitors mr_10" ></span></div>
				</div>
				
				<?php 
					if ($is_extended_partial)														
						$this->load->view('assess/_summary_compare');					
					else																		
						$this->load->view('assess/_summary_summary');										
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