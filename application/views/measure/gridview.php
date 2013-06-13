<?php 
	$s_product_description = $s_product['description'];
	$s_product_long_description = $s_product['long_description'];
?>

<div id='grid_se_section_1' class='grid_se_section'>
    <div class='h'>
        <div id='an_grd_view_drop_gr1' class='an_grd_view_drop'></div>
    </div>
    <div class='c'>
        <img class='preloader_grids_box' src="<?php echo base_url() ?>/img/grids_boxes_preloader.gif">
        <div class='c_content'>
            <span class='analysis_content_head'>Short Description (<span class='short_desc_wc'><?php echo $s_product_short_desc_count ?> words</span>):</span>
            <p class='short_desc_con'><?php echo $s_product_description; ?></p>
            <span class='analysis_content_head'>Long Description (<span class='long_desc_wc'><?php echo $s_product_long_desc_count; ?> words</span>):</span>
            <p class='long_desc_con'><?php echo $s_product_long_description; ?></p>
        </div>
    </div>
    <div class='grid_seo'>
        <ul>
            <li><a href='javascript:void()'>SEO Phrases:</a></li>
        </ul>
        <ul class='gr_seo_short_ph' style='margin-top: 5px;'>
            <li class='bold'>Short Description:</li>
            <?php if(count($seo['short']) > 0) { ?>
            	<?php foreach ($seo['short'] as $key => $value) { ?>
            	<?php $v_ph = $value['ph']; ?>
            	<li style='margin-top: 5px;'>
            		<span data-status='seo_link' onclick="wordGridModeHighLighter('section_1', '<?php echo $v_ph; ?>', 'short')" class='word_wrap_li_pr hover_en'>
            			<?php echo $value['ph']; ?>
            		</span>
            		<span class='word_wrap_li_sec'><?php echo $value['count']; ?></span>
            	</li>
            	<?php } ?>
            <?php } else { ?>
            <li style='margin-top: 5px;'>none</li>
            <?php } ?>
        </ul>
        <ul class='gr_seo_long_ph' style='margin-top: 5px;'>
            <li class='bold'>Long Description:</li>
            <?php if(count($seo['long']) > 0) { ?>
            	<?php foreach ($seo['long'] as $key => $value) { ?>
            	<?php $v_ph = $value['ph']; ?>
            	<li style='margin-top: 5px;'>
            		<span data-status='seo_link' onclick="wordGridModeHighLighter('section_1', '<?php echo $v_ph; ?>', 'long')" class='word_wrap_li_pr hover_en'>
            			<?php echo $value['ph']; ?>
            		</span>
            		<span class='word_wrap_li_sec'><?php echo $value['count']; ?></span>
            	</li>
            	<?php } ?>
            <?php } else { ?>
            <li style='margin-top: 5px;'>none</li>
            <?php } ?>
        </ul>
        <ul>
            <li><a href='javascript:void()'>Attributes used (<span class='gr_attr_count'>0</span>):</a></li>
            <li class='gr_attr_con'>no attributes</li>
        </ul>
    </div>
</div>

<div id='grid_se_section_2' class='grid_se_section left'>
    <div class='h'>
        <div id='an_grd_view_drop_gr2' class='an_grd_view_drop'></div>
    </div>
    <div class='c'>
        <img class='preloader_grids_box' src="<?php echo base_url() ?>/img/grids_boxes_preloader.gif">
        <div class='c_content'>
            <span class='analysis_content_head'>Short Description (<span class='short_desc_wc'><?php echo $s_product_short_desc_count ?> words</span>):</span>
            <p class='short_desc_con'><?php echo $s_product['description']; ?></p>
            <span class='analysis_content_head'>Long Description (<span class='long_desc_wc'><?php echo $s_product_long_desc_count; ?> words</span>):</span>
            <p class='long_desc_con'><?php echo $s_product['long_description']; ?></p>
        </div>
    </div>
    <div class='grid_seo'>
        <ul>
            <li><a href='javascript:void()'>SEO Phrases:</a></li>
        </ul>
        <ul class='gr_seo_short_ph' style='margin-top: 5px;'>
            <li class='bold'>Short Description:</li>
            <?php if(count($seo['short']) > 0) { ?>
            	<?php foreach ($seo['short'] as $key => $value) { ?>
            	<?php $v_ph = $value['ph']; ?>
            	<li style='margin-top: 5px;'>
            		<span data-status='seo_link' onclick="wordGridModeHighLighter('section_2', '<?php echo $v_ph; ?>', 'short')" class='word_wrap_li_pr hover_en'>
            			<?php echo $value['ph']; ?>
            		</span>
            		<span class='word_wrap_li_sec'><?php echo $value['count']; ?></span>
            	</li>
            	<?php } ?>
            <?php } else { ?>
            <li style='margin-top: 5px;'>none</li>
            <?php } ?>
        </ul>
        <ul class='gr_seo_long_ph' style='margin-top: 5px;'>
            <li class='bold'>Long Description:</li>
            <?php if(count($seo['long']) > 0) { ?>
            	<?php foreach ($seo['long'] as $key => $value) { ?>
            	<?php $v_ph = $value['ph']; ?>
            	<li style='margin-top: 5px;'>
            		<span data-status='seo_link' onclick="wordGridModeHighLighter('section_2', '<?php echo $v_ph; ?>', 'long')" class='word_wrap_li_pr hover_en'>
            			<?php echo $value['ph']; ?>
            		</span>
            		<span class='word_wrap_li_sec'><?php echo $value['count']; ?></span>
            	</li>
            	<?php } ?>
            <?php } else { ?>
            <li style='margin-top: 5px;'>none</li>
            <?php } ?>
        </ul>
        <ul>
            <li><a href='javascript:void()'>Attributes used (<span class='gr_attr_count'>0</span>):</a></li>
            <li class='gr_attr_con'>no attributes</li>
        </ul>
    </div>
</div>

<div id='grid_se_section_3' class='grid_se_section left'>
    <div class='h'>
        <div id='an_grd_view_drop_gr3' class='an_grd_view_drop'></div>
    </div>
    <div class='c'>
        <img class='preloader_grids_box' src="<?php echo base_url() ?>/img/grids_boxes_preloader.gif">
        <div class='c_content'>
            <span class='analysis_content_head'>Short Description (<span class='short_desc_wc'><?php echo $s_product_short_desc_count ?> words</span>):</span>
            <p class='short_desc_con'><?php echo $s_product['description']; ?></p>
            <span class='analysis_content_head'>Long Description (<span class='long_desc_wc'><?php echo $s_product_long_desc_count; ?> words</span>):</span>
            <p class='long_desc_con'><?php echo $s_product['long_description']; ?></p>
        </div>
    </div>
    <div class='grid_seo'>
        <ul>
            <li><a href='javascript:void()'>SEO Phrases:</a></li>
        </ul>
        <ul class='gr_seo_short_ph' style='margin-top: 5px;'>
            <li class='bold'>Short Description:</li>
            <?php if(count($seo['short']) > 0) { ?>
            	<?php foreach ($seo['short'] as $key => $value) { ?>
            	<?php $v_ph = $value['ph']; ?>
            	<li style='margin-top: 5px;'>
            		<span data-status='seo_link' onclick="wordGridModeHighLighter('section_3', '<?php echo $v_ph; ?>', 'short')" class='word_wrap_li_pr hover_en'>
            			<?php echo $value['ph']; ?>
            		</span>
            		<span class='word_wrap_li_sec'><?php echo $value['count']; ?></span>
            	</li>
            	<?php } ?>
            <?php } else { ?>
            <li style='margin-top: 5px;'>none</li>
            <?php } ?>
        </ul>
        <ul class='gr_seo_long_ph' style='margin-top: 5px;'>
            <li class='bold'>Long Description:</li>
            <?php if(count($seo['long']) > 0) { ?>
            	<?php foreach ($seo['long'] as $key => $value) { ?>
            	<?php $v_ph = $value['ph']; ?>
            	<li style='margin-top: 5px;'>
            		<span data-status='seo_link' onclick="wordGridModeHighLighter('section_3', '<?php echo $v_ph; ?>', 'long')" class='word_wrap_li_pr hover_en'>
            			<?php echo $value['ph']; ?>
            		</span>
            		<span class='word_wrap_li_sec'><?php echo $value['count']; ?></span>
            	</li>
            	<?php } ?>
            <?php } else { ?>
            <li style='margin-top: 5px;'>none</li>
            <?php } ?>
        </ul>
        <ul>
            <li><a href='javascript:void()'>Attributes used (<span class='gr_attr_count'>0</span>):</a></li>
            <li class='gr_attr_con'>no attributes</li>
        </ul>
    </div>
</div>