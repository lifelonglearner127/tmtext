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

	<div class='item_body'>
		<input type="hidden" id="link_m_title" value='<?php echo $pr_title; ?>'>
		<input type="hidden" id="link_m_url" value='<?php echo $pr_url; ?>'>
		<span class='analysis_content_head'>Short Description:</span>
	    <div>
	        <span id="details-short-desc" class="ql-details-short-desc">
	        	<?php if(isset($search_results['short_desc']) && $search_results['short_desc'] !== "") { ?> 
	        		<?php echo preg_replace('/[^A-Za-z0-9\. -!]/', '', $search_results['short_desc']); ?> 
        		<?php } else { ?> 
        			No short description 
    			<?php } ?>
    		</span>
	    </div>
	</div>
	<br>
	<div class="item_body">
		<span class='analysis_content_head'>Long Description:</span>
	    <div id="details-long-desc">
	    	<?php if(isset($search_results['long_desc']) && $search_results['long_desc'] !== "") { ?> 
	    		<?php echo preg_replace('/[^A-Za-z0-9\. -!]/', '', $search_results['long_desc']); ?>
    		<?php } else { ?> 
    			No long description 
			<?php } ?>
	    </div>
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
