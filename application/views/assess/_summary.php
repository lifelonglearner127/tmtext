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
					Download
					<a class="assess_report_download_pdf" target="_blank" data-type="pdf">PDF</a> |
					<a class="assess_report_download_doc" target="_blank" data-type="doc">DOC</a>
					<button class="assess_report_options_dialog_button btn" style="float: right;margin-top: 7px;" title="Report Options"><img class="other-icon" src="<?php echo base_url();?>img/ico-gear.png" /></button>
				</span>
			</h3>
			<div style="clear: both;"></div>
			<div class="boxes_content" style="padding:0px;">
				<div class="mt_10 ml_15">
					<div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_number.png">Total SKUs analyzed: <span class="assess_report_total_items mr_10" ></span></div>
				</div>
				<div class="mt_10 ml_15">
					<div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_dollar.png">SKUs priced higher than competitors: <span class="assess_report_items_priced_higher_than_competitors mr_10" ></span></div>
				</div>
				<div class="mt_10 ml_15 items_have_more_than_20_percent_duplicate_content">
					<div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_D.png"><span class="assess_report_items_have_more_than_20_percent_duplicate_content mr_10" ></span>items have more than 20% duplicate content</div>
				</div>
				<div class="mt_10 ml_15">
					<div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_seo.png">SKUs that have non-keyword optimized product content: <span class="assess_report_items_unoptimized_product_content mr_10" ></span></div>
				</div>
				<div class="assess_report_items_1_descriptions_pnl">
					<div class="mt_10 mb_10 ml_15"> 
						<div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_arrow_down.png">SKUs that have descriptions that are shorter than <span class="assess_report_items_have_product_descriptions_that_are_less_than_value"></span> words: <span class="assess_report_items_have_product_descriptions_that_are_too_short mr_10" ></span></div>
					</div>
				</div>
				<div class="assess_report_items_2_descriptions_pnl" style="display: none;">
					<div class="assess_report_items_2_descriptions_pnl_s mt_10 mb_10 ml_15" >
						<div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_arrow_down.png"><span class="assess_report_items_have_product_short_descriptions_that_are_too_short mr_10" ></span>items have short descriptions that are less than <span class="assess_report_items_have_product_short_descriptions_that_are_less_than_value"></span> words</div>
					</div>
					<div class="assess_report_items_2_descriptions_pnl_l mt_10 mb_10 ml_15" >
						<div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_arrow_down.png"><span class="assess_report_items_have_product_long_descriptions_that_are_too_short mr_10" ></span>items have long descriptions that are less than <span class="assess_report_items_have_product_long_descriptions_that_are_less_than_value"></span> words</div>
					</div>
				</div>
				<div class="assess_report_compare_panel mt_10 mb_10 ml_15" >
					<div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_comparison.png">
						<span class="assess_report_absent_items_count mr_10" ></span>
						items in
						<span class="assess_report_compare_customer_name"></span>
						-
						<span class="assess_report_compare_batch_name"></span>
						are absent from
						<span class="assess_report_own_batch_name"></span>
					</div>
				</div>
				<div class="assess_report_numeric_difference mt_10 mb_10 ml_15" >
					<div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_cart.png"><span class="assess_report_numeric_difference_caption mr_10" ></span></div>
				</div>
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