<div>
<input type='hidden' name='measure_res_status' id='measure_res_status' value="<?php echo $search_flag; ?>" >
<?php if(isset($search_flag) && $search_flag === 'db' && !empty($search_results) ) {//max ?>
   
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
                <span class='analysis_content_head' style="width: 100%;float: left;margin-bottom: 15px;">Price: <span style="font-weight: normal;"><?php if(!empty($search_results['price'])){echo '$'.sprintf("%01.2f", floatval($search_results['price'][0]->price));}?></span></span>
                    <?php // echo "<pre>";print_r($search_results); ?>
                
		<?php if($search_results['description'] !== null && $search_results['description'] !== "") { ?>
		<span class='analysis_content_head'>Short Description:</span>
		<p id="details-short-desc"><?php echo htmlspecialchars($search_results['description']); ?></p>
		<?php } else { ?>
		<span class='analysis_content_head'></span>
		<p id="details-short-desc"></p>
		<?php } ?>

		<?php if($search_results['long_description'] !== null && $search_results['long_description'] !== "") { ?>
		<span class='analysis_content_head'>Long Description:</span>
		<p id="details-long-desc"><?php echo htmlspecialchars($search_results['long_description']); ?></p>
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
