<div>
<input type='hidden' name='measure_res_status' id='measure_res_status' value="<?php echo $search_flag; ?>" >
<?php if(isset($search_flag) && $search_flag === 'db' ) { ?>

	<?php 
		$pr_title = "";
		$pr_url = "";
		if(isset($search_results['product_name']) && $search_results['product_name'] !== "") {
			$pr_title = $search_results['product_name'];
		}
		if(isset($search_results['url']) && $search_results['url'] !== "") {
			$pr_url = $search_results['url'];
		}
	?>
	<div style="float: left; margin-top: 0px; width: 530px;" id='measure_product_ind_wrap'>
		<div class="item_title" style="float: left; width: 520px; margin-bottom: 15px;"><b class='btag_elipsis an_search'><a href="<?php echo $pr_url; ?>"><?php echo $pr_title; ?></a></b></div>
		
		<?php if($search_results['description'] !== null && $search_results['description'] !== "") { ?>
		<span class='analysis_content_head'>Short Description:</span>
		<p id="details-short-desc"><?php echo preg_replace('/[^A-Za-z0-9\. -!]/', ' ', $search_results['description']); ?></p>
		<?php } else { ?>
		<span class='analysis_content_head'>&nbsp;</span>
		<p id="details-short-desc">&nbsp;</p>
		<?php } ?>

		<?php if($search_results['long_description'] !== null && $search_results['long_description'] !== "") { ?>
		<span class='analysis_content_head'>Long Description:</span>
		<p id="details-long-desc"><?php echo preg_replace('/[^A-Za-z0-9\. -!]/', '', $search_results['long_description']); ?></p>
		<?php } else { ?>
		<span class='analysis_content_head'>&nbsp;</span>
		<p id="details-long-desc">&nbsp;</p>
		<?php } ?>
	</div>
<?php } else {  ?>
	
	<div class='item_body'>
	    <div>
	        <span id="details-short-desc" class="ql-details-short-desc">Short description not finded</span>
	    </div>
	</div>
	<div class="item_body">
		<br>
	    <div id="details-long-desc">Long description not finded</div>
	</div>

<?php } ?>

</div>
