<?php
//if(count($same_pr) === 3) {
//$selectedUrl = $_POST['selectedUrl'];
//echo $selectedUrl;
?>
<?php $i = 1; ?>
<?php
//Max
$min_price = 1000000000;
$j = 0;
foreach ($same_pr as $ks => $vs) {

    foreach ($vs['three_last_prices'] as $key => $last_price) {

        $price = sprintf("%01.2f", floatval($last_price->price));
        if ($price < $min_price) {
            $min_price = $price;
        }


    }


}
?>
<?php

function fsort(&$ar, $field_name){
	$func_code = "
		if (\$a['$field_name'] == \$b['$field_name']) {
			return 0;
		}
		return (\$a['$field_name'] > \$b['$field_name']) ? -1 : 1;
	";
	$sort_func = create_function ('$a,$b' , $func_code );
	usort($ar, $sort_func);
	return $ar;
}
//echo "<pre>";
//print_r($same_pr);
$row=1;
foreach ($same_pr as $ks => $vs) {
    $row=ceil($i/3);
    foreach ($vs['three_last_prices'] as $key => $last_price) {
         if(count($vs['three_last_prices'])>1){
         foreach ($vs['three_last_prices'] as $key1 => $last_price1) {
             if(($key1!=$key) && (date("m/d/Y", strtotime($last_price->created))=== date("m/d/Y", strtotime($last_price1->created)))){

                 unset($vs['three_last_prices'][$key1]);

             }

         }
         }
    }

    $customer = $vs['customer'];
    $class_left = "";
    if ($i % 3 != 1)
        $class_left = 'left';
    // $s_product_description = $vs['description'];
    //           $s_product_long_description = $vs['long_description'];
    //            $s_product_short_desc_count = count(explode(" ", $s_product_description));
    //            echo "<pre>";
    //           print_r(explode(" ", trim($s_product_long_description )));
    //           $s_product_long_desc_count = count(explode(" ", $s_product_long_description));


    if ($vs['description'] !== null && trim($vs['description']) !== "") {
        $s_product_description = $vs['description'];
        $vs['description'] = preg_replace('/[^a-zA-Z0-9_ %\[\]\.\(\)%&-]/s', '', $vs['description']);
        $vs['description'] = preg_replace('/\s+/', ' ', $vs['description']);
        $vs['description'] = preg_replace('/[a-zA-Z]-/', ' ', $vs['description']);
        
        // $data_import['description'] = preg_replace('/[^A-Za-z0-9\. -!]/', ' ', $data_import['description']);
        $s_product_short_desc_count = count(explode(" ", $vs['description']));
    } else {
        $s_product_short_desc_count = 0;
        $s_product_description = '';
    }
    if ($vs['long_description'] !== null && trim($vs['long_description']) !== "") {
        $s_product_long_description = $vs['long_description'];
        $vs['long_description'] = preg_replace('/[^a-zA-Z0-9_ %\[\]\.\(\)%&-]/s', '', $vs['long_description']);
        $vs['long_description'] = preg_replace('/\s+/', ' ', $vs['long_description']);
        $vs['long_description'] = preg_replace('/[a-zA-Z]-/', ' ', $vs['long_description']);
        
        // $data_import['long_description'] = preg_replace('/[^A-Za-z0-9\. -!]/', ' ', $data_import['long_description']);
        $s_product_long_desc_count = count(explode(" ", $vs['long_description']));
    } else {
        $s_product_long_desc_count = 0;
        $s_product_long_description = '';
    }

    if ($i % 3 == 1) {
        echo '<div class="wrapper">';
    }
    //Max
    ?>


    <div id="grid_se_section_<?php echo $i; ?>"  class='grid_se_section <?php echo $class_left; ?> '>
        <?php if($i>1){?>
        <div class='has_stiky' id="h_<?php echo $i; ?>" class='h'>
            <input type="hidden" name='dd_customer' value="<?php echo $customer; ?>">
            <div id="an_grd_view_drop_gr<?php echo $i; ?>" class='an_grd_view_drop'></div>
            <img class='has_stiky_image' src="<?php echo base_url() ?>/img/pin-icon.png" title='Click to make sticky'>
        </div>
        <?php }else{?>
        <div id="h_<?php echo $i; ?>" class='h'>
            <input type="hidden" name='dd_customer' value="<?php echo $customer; ?>">
            <div id="an_grd_view_drop_gr<?php echo $i; ?>" class='an_grd_view_drop'></div>
            
        </div>
        <?php }?>
        <div id="<?php echo $customer;?>" class="grid">
        <div class='c'>
            <img class='preloader_grids_box' src="<?php echo base_url() ?>/img/grids_boxes_preloader.gif">
        <div class='c_content'>
				<!--                            //Denis-->
                <div class="p_name">
                    <!--<span class='analysis_content_head'>Product Name:</span>-->
                    <img class="assess_image product_image" src="<?php echo base_url() ?>/img/assess_grid/product.png">
                    <p style="min-height: 38px;" class='short_product_name name_bold'><?php echo $vs['product_name']; ?></p>
                </div>
			<div class="p_url">
                    <?php if ($ks > 0 && $mismatch_button==true) { ?>
                        <input data-value="<?php echo $vs['imported_data_id']; ?>"class="mismatch_image" style="float: right; margin-top: 0;" type="button" value="" title="Report mismatch">
                    <?php }
                    ?>
                    <!--<span class='analysis_content_head'>URL:</span>-->
                    <img class="assess_image product_image" src="<?php echo base_url() ?>/img/assess_grid/link.png">
                    <p class='short_product_name ellipsis'><a target="_blank" href="<?php echo $vs['url']; ?>"><?php echo $vs['url']; ?></a></p>
                </div>
                <div class="p_price1">
                    <?php
                    if (!empty($vs['three_last_prices'])) {
                        //echo "<span class='analysis_content_head'>Price:</span>";
                        echo '<table >';
                        foreach ($vs['three_last_prices'] as $last_price) {
                            ?>
                            <tr>
                                <td>									
                                    <p class='short_product_name short_product_date'>
										<img class="assess_image product_image" src="<?php echo base_url() ?>/img/assess_grid/cost_price_tag2.png">
										<?php //if($last_price->created!=''){echo date("m/d/Y", strtotime($last_price->created)).' - ';} ?>
										<?php if ($j != 0) { ?>
												<span <?php
													if (sprintf("%01.2f", floatval($last_price->price)) == $min_price) {
														echo "style='font-weight: bold;'";
													}
													?>class="product_price">$<?php echo sprintf("%01.2f", floatval($last_price->price)); ?></span>
											<?php
										} else {
											?>
												<span <?php
													if (sprintf("%01.2f", floatval($last_price->price)) > $min_price) {
														echo "class='not_min'";
													}
													?> class="product_price"><?php echo '$' . sprintf("%01.2f", floatval($last_price->price)); ?></span>
											<?php
										}
										?>
										<?php if($last_price->created!=''){echo "<span> - " . date("m/d/Y", strtotime($last_price->created)). "</span>";} ?>
									</p>
                                </td>
                                <?php /* if ($j != 0) { ?>
                                    <td>
                                        <!--    //Max-->
                                        <p  class='short_product_name'> <span <?php
                                            if (sprintf("%01.2f", floatval($last_price->price)) == $min_price) {
                                                echo "style='font-weight: bold;'";
                                            }
                                            ?>class="product_price">$<?php echo sprintf("%01.2f", floatval($last_price->price)); ?></span></p>
                                        <!--    //Max                            -->
                                    </td>
                                    <?php
                                } else {
                                    ?>
                                    <td>
                                        <p  class='short_product_name'> <span <?php
                                            if (sprintf("%01.2f", floatval($last_price->price)) > $min_price) {
                                                echo "class='not_min'";
                                            }
                                            ?> class="product_price"><?php echo '$' . sprintf("%01.2f", floatval($last_price->price)); ?></span></p>
                                    </td>
                                    <?php
                                }*/
                                ?>
                            </tr>
                            <?php
                        }
                        echo '</table>';
                    }else{
						echo "<span class='analysis_content_head'>Price:</span>";
						echo "<p>Special or not listed</p>";
					}
                    ?>
                </div>
                <div class="p_analusis cmp-area">
					<table id="analysis">
						<tbody>
						<tr>
							<td style="width: 194px;">
								<span class="short_product_name name_bold" style="float: none;">Analysis:</span>
								<select name="analysis">
									<option selected="selected">Product</option>
									<option>Page</option>
								</select>
							</td>
							<td>
								<span class="short" style="margin-right: 6px;">Short</span>
								<span class="short">Long</span>
							</td>
						</tr>
						<tr>
							<td>
								<img class="assess_image product_image" src="<?php echo base_url() ?>/img/assess_grid/page_number.png">
								Word count:
							</td>
							<td>
								<div class="words_count_short" style="float: left; width: 35px;"><?php echo $s_product_short_desc_count ?></div>
								<span style=""><?php echo $s_product_long_desc_count; ?></span>
							</td>
						</tr>
						<tr>
							<td style="height: 30px;">
								<!--<img class="assess_image product_image" src="<?php echo base_url() ?>/img/assess_grid/copy_documents_duplicate.png">-->
								<img class="assess_image product_image duplicate_content_img cmp-btn" test_page="1" src="<?php echo base_url() ?>/img/assess_grid/highlighter.png" title="Click to see duplicates words">
								<span class="duplicate-content">Duplicate content:</span>
							</td>
							<td>
								<div class="words_count_short" style="float: left; width: 35px;"><?php echo isset($vs['short_original']) && $vs['short_original'] != 'Insufficient data' && $vs['short_original'] != '%' ? $vs['short_original'] : '0%'; ?></div>
								<span class="words_count_short" style=""><?php echo isset($vs['long_original']) && $vs['long_original'] != 'Insufficient data' && $vs['short_original'] != '%' ? $vs['long_original'] : '0%'; ?></span>
							</td>
						</tr>
						</tbody>
					</table>
				</div>
				<div style="margin-top: 8px;">
					<img style="margin-top: 7px;" class="assess_image product_image percent_img" src="<?php echo base_url() ?>/img/assess_grid/percent.png">
					<span class="short_product_name keywords keywords_lable">Keywords:</span>
					<select class="keywords_select" name="analysis">
						<option selected="selected" value="title">Title</option>
						<option value="you">Custom</option>
					</select>
					<!--<img class="assess_image product_image keywords_img" src="<?php echo base_url() ?>/img/assess_grid/highlighter.png">-->
					<div class="clear"></div>
				</div>
				<div class="primary">
					<!--<div>-->
						<?php
						//echo count($vs['seo']['short']);
						if( count($vs['seo']['short']) > 0 ){
							/*foreach ($vs['seo']['short'] as $key => $value) {
								$v_ph = $value['ph'];
								?>
								<span style="white-space: normal;line-height: 20px;text-decoration: none;font-size: 14px !important;line-height: 21px;text-decoration: none;white-space: normal;"data-status='seo_link' onclick="wordGridModeHighLighter('section_<?php echo $i; ?>', '<?php echo $v_ph; ?>', 'short')" class='word_wrap_li_pr hover_en'>
									<?php echo $value['ph']; ?> <?php echo $value['prc'] . '%'; ?>
								</span>
								<?php
							}*/
							//echo"<pre>"; print_r( $vs['seo']['keyword'] ); echo"</pre>";
							fsort( $vs['seo']['short'], 'prc' );
							
							$ii = 1;
							$keyword_user = 0;
							$tertiary = 0;
							$secondary = 0;
							foreach ($vs['seo']['short'] as $key => $value) {
								$v_ph = $value['ph'];
								
								$keyword_count = substr_count($s_product_description, $v_ph);
								
								if( $ii == 4 ) break;
								if( $ii == '1' ) echo '<div class="keywords_lines"><span class="primary_name">Primary: </span>';
								if( $ii == '2' ){
									echo '<div class="keywords_lines"><span class="primary_name">Secondary: </span>';
									$secondary = 1;
								}
								if( $ii == '3' ){
									echo '<div class="keywords_lines"><span class="primary_name">Tertiary: </span>';
									$tertiary = 1;
								}
								$user_word = '';
								//$user_word = $vs['seo']['keyword'][$keyword_user]->keyword;
								foreach($vs['seo']['keyword'] as $kv){
									//echo '<br>'. $word_num = $kv->word_num . ' | ' . $kv->keyword . '<br/>';
									$word_num = $kv->word_num;
									if( $word_num == $ii ){
										$user_word = $kv->keyword;
										break;
									}
								}
								
								?>
								
									<span class='primary_speed'>
										<!--<div style="float: left;">[</div>--> <span class="title_words name_bold"><?php echo $value['ph']; ?></span>
										<span class="you_words you_words_input">
											<input class="keyword_input" imported_data_id="<?php echo $vs['imported_data_id']; ?>" name="keyword<?=$ii?>" keyword_num="<?=$ii?>" type="text" value="<?=$user_word?>" />
										</span>
										<!--<div style="float: right;">]</div>-->
									</span>
									<!--<img class="assess_image keyword_checkmark primary_image keywords_img" src="<?php echo base_url() ?>/img/assess_grid/check_circle_green.png" />-->
									
									<span class="keyword_percent">
										<span class="keyword_percent_text"><?php echo round($value['prc'], 1); ?></span>
										%
									</span>
									<span class="keyword_count"><?php echo $keyword_count ?></span>
								</div>
								<div class="clear"></div>
								<?php 
								$ii++;
								$keyword_user++;
							}
							foreach($vs['seo']['keyword'] as $kv){
								//echo '<br>'. $word_num = $kv->word_num . ' | ' . $kv->keyword . '<br/>';
								$word_num = $kv->word_num;
								if( $word_num == 1 ){
									$user_word1 = $kv->keyword;
								}
								if( $word_num == 2 ){
									$user_word2 = $kv->keyword;
								}
								if( $word_num == 3 ){
									$user_word3 = $kv->keyword;
								}
							}
							if( $secondary != 1 ){
								$user_word = $vs['seo']['keyword'][1]->keyword;
								echo '<div class="keywords_lines"><span class="primary_name">Secondary: </span>
										
										<span class="primary_speed">
											<!--<div style="float: left;">[</div>--> <span class="title_words"></span>
											<span class="you_words you_words_input">
												<input class="keyword_input" imported_data_id="'. $vs['imported_data_id'] .'" name="keyword2" keyword_num="2" type="text" value="'.$user_word2.'" />
											</span>&nbsp <!--<div style="float: right;">]</div>-->
										</span>
										<!--<img class="keyword_checkmark assess_image primary_image keywords_img" src="'. base_url() .'/img/assess_grid/check_circle_green.png" />-->
										
									</div>
									<div class="clear"></div>';
							}
							if( $tertiary != 1 ){
								//echo "<pre>";
								//print_r($vs['seo']['keyword']);
								//echo "</pre>";
								$user_word = $vs['seo']['keyword'][2]->keyword;
								echo '<div class="keywords_lines"><span class="primary_name">Tertiary: </span>
									
										<span class="primary_speed">
											<!--<div style="float: left;">[</div>-->
											<span class="title_words"></span>
											<span class="you_words you_words_input">
												<input class="keyword_input" imported_data_id="'. $vs['imported_data_id'] .'" name="keyword3" keyword_num="3" type="text" value="'.$user_word3.'" />
											</span> &nbsp<!--<div style="float: right;">]</div>-->
										</span>
										<!--<img class="assess_image keyword_checkmark primary_image keywords_img" src="'. base_url() .'/img/assess_grid/check_circle_green.png" />-->
									
									</div>
									<div class="clear"></div>';
							}
						}else{
							//echo '<span class="name_bold">None</span>';
							for( $jj = 1; $jj <= 3; $jj++ ){
								if( $jj == '1' ) echo '<div class="keywords_lines"><span class="primary_name">Primary: </span>';
								if( $jj == '2' )	echo '<div class="keywords_lines"><span class="primary_name">Secondary: </span>';
								if( $jj == '3' )	echo '<div class="keywords_lines"><span class="primary_name">Tertiary: </span>';
								
								//$user_word = $vs['seo']['keyword'][$jj-1]->keyword;
								foreach($vs['seo']['keyword'] as $kv){
									//echo '<br>'. $kv->word_num . ' | ' . $kv->keyword . '<br/>';
									$user_word = '';
									$word_num = $kv->word_num;
									if( $word_num == $jj ){
										$user_word = $kv->keyword;
									}
								}
								echo '<span class="primary_speed">
										<!--<div style="float: left;">[</div>--> <span class="title_words"></span>
										<span class="you_words you_words_input">
											<input class="keyword_input" imported_data_id="'. $vs['imported_data_id'] .'" name="keyword'.$jj.'" keyword_num="'.$jj.'" type="text" value="'.$user_word.'" />
										</span>&nbsp
										<!--<div style="float: right;">]</div>-->
									</span>
									<!--<img class="assess_image keyword_checkmark primary_image keywords_img" src="'. base_url() .'/img/assess_grid/check_circle_green.png" />-->									
									</div>
									<div class="clear"></div>';
							}
							/*
							echo '<div class="keywords_lines"><span class="primary_name">Secondary: </span>
									<span>
										<span class="primary_speed">
											<div style="float: left;">[</div> <span class="title_words"></span><span class="you_words you_words_input"><input class="keyword_input" imported_data_id="'. $vs['imported_data_id'] .'" name="keyword2" keyword_num="2" type="text" value="" /></span> <div style="float: right;">]</div>
										</span>
										<img class="assess_image primary_image keywords_img" src="'. base_url() .'/img/assess_grid/check_circle_green.png" />
									</span>
									</div>
									<div class="clear"></div>';
							echo '<div class="keywords_lines"><span class="primary_name">Tertiary: </span>
									<span>
										<span class="primary_speed">
											<div style="float: left;">[</div><span class="title_words"></span><span class="you_words you_words_input"><input class="keyword_input" imported_data_id="'. $vs['imported_data_id'] .'" name="keyword3" keyword_num="3" type="text" value="" /></span> <div style="float: right;">]</div>
										</span>
										<img class="assess_image primary_image keywords_img" src="'. base_url() .'/img/assess_grid/check_circle_green.png" />
									</span>
									</div>
									<div class="clear"></div>';*/
						}
						//echo"<pre>"; print_r( $vs['seo']['short'] ); echo"</pre>";
						//echo"<pre>"; print_r( $vs['seo']['long'] ); echo"</pre>";
						?>
					<!--	</span><img class="assess_image primary_image keywords_img" src="<?php echo base_url() ?>/img/assess_grid/check_circle_green.png" /><span></span>
					</div>
					<div class="clear"></div>
					<div>
						<span class="primary_name">Secondary: </span><span class="primary_speed">[10 Speed Blender] </span><img class="assess_image primary_image keywords_img" src="<?php echo base_url() ?>/img/assess_grid/check_circle_green.png" /><span></span>
					</div>
					<div class="clear"></div>
					<div>
						<span class="primary_name">Tertiary: </span><span class="primary_speed">[10 Speed Blender] </span><img class="assess_image primary_image keywords_img" src="<?php echo base_url() ?>/img/assess_grid/check_circle_green.png" /><span></span>
					</div>
					<div class="clear"></div>-->
				</div>
				
				<div class="description">
					<span class="short_product_name keywords name_bold description_label">Description:</span>
					<select class="description_select" name="description">
						<option <?php if($s_product_short_desc_count > 0) echo 'selected="selected"'?> value="short_desc_show" >Short</option>
						<option <?php if($s_product_long_desc_count > 0 && $s_product_short_desc_count == 0) echo 'selected="selected"';?> value="long_desc_show">Long</option>
					</select>
					<div class="clear"></div>
					<div>
						<?php 
						if( $s_product_short_desc_count > 0 ){
						?>
							<!--<p class="short_desc_show short_desc_con compare"><?php echo $s_product_description; ?></p>-->
							<p class="short_desc_show compare" <?php if($s_product_long_desc_count == 0 || $s_product_long_desc_count > 0 ) echo 'style="display: block;"';?> ><?php echo $s_product_description; ?></p>
						<?php 
						} 
						if( $s_product_long_desc_count > 0 ) { ?>
							<p class="long_desc_show compare" <?php if($s_product_short_desc_count == 0) echo 'style="display: block;"';?>><?php echo $s_product_long_description ?></p>
						<?php
						}
						if( $s_product_long_desc_count == 0 && $s_product_short_desc_count == 0 ) { ?>
							<span>No description on site</span>
						<?php } ?>
					</div>
				</div>


            </div>
             <p style="color: rgb(117, 114, 114);">Id: <?php echo $vs['imported_data_id']; ?></p>

            <!--            <div class='grid_seo'>
                            <ul>
                                <li><a href='javascript:void()'>SEO Phrases:</a></li>
                            </ul>
                            <ul class='gr_seo_short_ph' style='margin-top: 5px;'>
                                <li class='bold'>Short Description:</li>
            <?php if (count($vs['seo']['short']) > 0) { ?>
                <?php foreach ($vs['seo']['short'] as $key => $value) { ?>
                    <?php $v_ph = $value['ph']; ?>
                                                                                                                                                                                                                    <li style='margin-top: 5px;'>
                                                                                                                                                                                                                    <span data-status='seo_link' onclick="wordGridModeHighLighter('section_<?php echo $i; ?>', '<?php echo $v_ph; ?>', 'short')" class='word_wrap_li_pr hover_en'>
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
            <?php if (count($vs['seo']['long']) > 0) { ?>
                <?php foreach ($vs['seo']['long'] as $key => $value) { ?>
                    <?php $v_ph = $value['ph']; ?>
                    <?php echo $value['ph']; ?>
                                                                                                                                                                                                                    </li>
                <?php } ?>
            <?php } ?>
                            </ul>
                             <ul>
                                <li><a href='javascript:void()'>Attributes used (<span class='gr_attr_count'>0</span>):</a></li>
                                <li class='gr_attr_con'>no attributes</li>
                            </ul>
                        </div>-->
        </div>

        <?php if ($i % 3 == 0) { ?>
            <div style="clear:both"></div>
            <?php
        }
        ?>
    </div>      
    </div>
    <?php
    if ($i % 3 == 0) {
        echo '</div>';
    }
    ?>
    <?php
    $i++;
    $j++;
}
if (($i - 1) % 3 != 0) {
    echo '</div>';
}

?>

<div class="clear"></div>

<script type="text/javascript">
 rows_count="<?php echo $row=ceil(count($same_pr)/3);?>";
group_id = "<?php echo $same_pr[0]['imported_data_id']; ?>";




</script>
<script type='text/javascript'>
   function inArray(needle, haystack) {
    var length = haystack.length;
    for(var i = 0; i < length; i++) {
        if(haystack[i] == needle)
            return true;
    }
    return false;
  }
// function makeSticky(val){
     var stick_urls=[];
     $(".has_stiky_image").live('click',function(){
         var sticky_url=$(this).closest('.grid_se_section').find('select').val();
         $(this).css('background','black');
         $(this).attr('title','Click to unstick');
         if(!inArray(sticky_url,stick_urls)){
            stick_urls.push(sticky_url);
         }
         $.cookie('sticky_url', stick_urls);
         
     });
     var sticky_url= $.cookie('sticky_url');
       if(typeof(sticky_url)!=='undefined'){
           
       }
   
// }
 
    var count =<?php echo count($same_pr); ?>;
    var ddData_grids = [];
    var customers= [];
    function gridsCustomersListLoader() {

        for (var i = 1; i <= count + 1; i++) {

            //ddData_grids[i]['ddData_grid']=[];
            ddData_grids[i] = $("#grid_se_section_" + i + " input[type='hidden'][name='dd_customer']").val();
            if($("#grid_se_section_" + i + " input[type='hidden'][name='dd_customer']").val()!=undefined){

                customers.push($("#grid_se_section_" + i + " input[type='hidden'][name='dd_customer']").val());
            }
        }
        var newc_data=[];
        
        setTimeout(function() {
            selected_customers=[];
            var customers_list = $.post(base_url + 'index.php/measure/getsiteslist_new', { }, function(c_data) {
            //console.log(c_data);
            var j=0;
            for (var key in c_data){

               if(inArray(c_data[key].value,customers)){
                  //console.log(c_data[key].value);
                  newc_data[j]=c_data[key];
                  j++;
               }
            };

            for (var i = 1; i <= count; i++) {
                    var grid1 = $('#an_grd_view_drop_gr' + i).msDropDown({byJson: {data: newc_data}}).data("dd");
                    if (grid1 != undefined) {
                        grid1.setIndexByValue(ddData_grids[i]);
                    }
                }

            });
        }, 100);
    }
    gridsCustomersListLoader();
//    $("#drop_1").html($("#h_1").html());
    
//    $("#drop_2").html($("#h_2").html());
grid_listings=[];
$(".grid").each(function(){
    var site=$(this).attr('id');
    grid_listings[site]= $(this).html();
    
});
$(".an_grd_view_drop select").live('change', function(){
   
      $(this).closest('.grid_se_section').find('.grid').html(grid_listings[$(this).val()]);
      $(this).closest('.grid_se_section').find('.grid .c > img').css('display', 'none');
      $(this).closest('.grid_se_section').find('.grid .c > .c_content').css('display', 'block');
               
      fixGridHeights();
      $(".grid_se_section .c_content").each(function() {
          
            if ($(".grid_se_section .c_content").height() >= 700) {
                $(".grid_se_section .c_content").css('height', '700');
                $(".grid_se_section .c_content").css('overflow-y', 'auto');
                $(".grid_se_section .c_content").css('overflow-x', 'hidden');
                $(".grid_se_section .c_content .p_description").css('height','auto');
            }
        });
});

selectedCustomer();

$(document).ready(function(){
	$('.description_select').change(function(){
		show = $(this).val();
		if( show == 'long_desc_show' ){
			/*$(this).parent().find('.short_desc_show').fadeOut();
			$(this).parent().find('.long_desc_show').fadeIn();*/
			$(this).parent().find('.short_desc_show').hide();
			$(this).parent().find('.long_desc_show').show();
		}else if( show == 'short_desc_show' ){
			/*$(this).parent().find('.long_desc_show').fadeOut();
			$(this).parent().find('.short_desc_show').fadeIn();*/
			$(this).parent().find('.long_desc_show').hide();
			$(this).parent().find('.short_desc_show').show();
		}
	});
	
	function check_description(){
		show_desc = $('.description_select option:selected').val();
		$('.'+show_desc).show();
	}
	check_description();
	
	$('.keywords_select').change(function(){
		if( $(this).val() == 'you' ){
			$(this).parent().next('.primary:first').find('.title_words').hide();
			$(this).parent().next('.primary:first').find('.you_words').show();
			$(this).parent().next('.primary:first').find('.save_keywords').show();
			
			/*$(this).parent().next('.primary').find('.keyword_input').each(function(){
			
				keywords_count( $(this) );
			});*/
			
		}else if( $(this).val() == 'title' ){
			$(this).parent().next('.primary:first').find('.you_words').hide();
			$(this).parent().next('.primary:first').find('.save_keywords').hide();
			$(this).parent().next('.primary:first').find('.title_words').show();
		}
	});
	
	$(".keyword_input").keyup(function(event) {
		/*if( $(this).val().length >= 2 ) {
			imported_data_id = $(this).attr('imported_data_id');
			keyword = $(this).val();
			keyword_name = $(this).attr('name');
			keyword_num = $(this).attr('keyword_num');
			$.post(base_url + 'index.php/measure/save_new_words', {imported_data_id: imported_data_id, keywords: keyword, keyword_num: keyword_num, keyword_name: keyword_name}, function(data){});
		}*/
		/*var keyword = new Array();
		$(this).parent().parent().find('.keyword_input').each(function(){
			keyword.push( $(this).val() );
		});		
		$.post(base_url + 'index.php/measure/save_new_words', {keywords: keyword}, function(data){
			
		});*/
		keyword_save( $(this) );
		//keywords_count( $(this) );
	});
	
	$(".keyword_checkmark").click(function(){
		obj = $(this).parent().find('input:first');
		keyword_save( obj );
	});
	
	function keyword_save( obj ){
		//if( $(obj).val().length >= 2 ) {
			imported_data_id = $(obj).attr('imported_data_id');
			keyword = $(obj).val();
			keyword_name = $(obj).attr('name');
			keyword_num = $(obj).attr('keyword_num');
			$.post(base_url + 'index.php/measure/save_new_words', {imported_data_id: imported_data_id, keywords: keyword, keyword_num: keyword_num, keyword_name: keyword_name}, function(data){});
		//}
	}
	
	$('.percent_img').click(function(){
		var percent = $(this).parent().next('.primary:first').find('.keyword_percent');
		var count = $(this).parent().next('.primary:first').find('.keyword_count');
		if( $(percent).is(":visible") ){
			$(percent).hide();
			$(count).show();
		}else if( $(count).is(":visible") ){
			$(count).hide();
			$(percent).show();			
		}
	});
	
	$('.duplicate_content_img').click(function(){
		//$('.cmp-btn').click();
	});
	/*
	//$('.keyword_input').click(function(){
	function keywords_count(obj){
		var word = $(obj).val();
		if( word != '' ){
			content = $(obj).parent().parent().parent().parent().parent().parent().find('p.compare').text();
			reg = new RegExp(' '+word, 'gi')
			count = 0;
			while( (matches = reg.exec(content)) != null ){
				// var msg = "Done " + matches[0] + ".  ";
				//msg += "next from " + reg.lastIndex;
				//alert(msg);
				count++;
			}
			count_length = content.split(" ").length;
			percent = (count/count_length)*100;
			percent = percent.toFixed(1);
			$(obj).parent().parent().parent().find('.keyword_count').text(count);
			$(obj).parent().parent().parent().find('.keyword_percent_text').text(percent);
		}
	};*/
	
	/*$('.percent_img').mouseover(function(){
		$(this).parent().next('.primary:first').find('.keyword_percent').css({'text-decoration': 'underline'});
		$(this).parent().next('.primary:first').find('.keyword_count').css({'text-decoration': 'underline'});
	});
	
	$('.percent_img').mouseout(function(){
		$(this).parent().next('.primary:first').find('.keyword_percent').css({'text-decoration': 'none'});
		$(this).parent().next('.primary:first').find('.keyword_count').css({'text-decoration': 'none'});
	});*/
});

</script>

