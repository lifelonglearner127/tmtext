<?php
//if(count($same_pr) === 3) {
//$selectedUrl = $_POST['selectedUrl'];
//echo $selectedUrl;
?>
<?php $i = 1; $bold = 0;?>
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
$row = 1;
foreach ($same_pr as $ks => $vs) {
    $marg = 0;
   
    $row = ceil($i / 3);
    foreach ($vs['three_last_prices'] as $key => $last_price) {
        if (count($vs['three_last_prices']) > 1) {
            foreach ($vs['three_last_prices'] as $key1 => $last_price1) {
                if (($key1 != $key) && (date("m/d/Y", strtotime($last_price->created)) === date("m/d/Y", strtotime($last_price1->created)))) {

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

   // if (!isset($vs['short_description_wc'])) {
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
//    } else {
//        $s_product_short_desc_count = $vs['short_description_wc'];
//        $s_product_long_desc_count = $vs['long_description_wc'];
//        $s_product_description = $vs['short_description_wc'] != 0 ? $vs['description'] : '';
//        $s_product_long_description = $vs['long_description_wc'] != 0 ? $vs['long_description'] : '';
//    }

    if ($i % 3 == 1) {
        echo '<div class="wrapper">';
    }
 ?>


    <div id="grid_se_section_<?php echo $i; ?>"  class='grid_se_section <?php echo $class_left; ?> '>
    <?php if ($i > 1) { ?>
            <div class='has_stiky' id="h_<?php echo $i; ?>" class='h'>
                <input type="hidden" name='dd_customer' value="<?php echo $customer; ?>">
                <div id="an_grd_view_drop_gr<?php echo $i; ?>" class='an_grd_view_drop'></div>
                <img class='has_stiky_image' src="<?php echo base_url() ?>/img/pin-icon.png" title='Click to make sticky'>
            </div>
    <?php } else { ?>
            <div id="h_<?php echo $i; ?>" class='h'>
                <input type="hidden" name='dd_customer' value="<?php echo $customer; ?>">
                <div id="an_grd_view_drop_gr<?php echo $i; ?>" class='an_grd_view_drop'></div>

            </div>
    <?php } ?>
        <div id="<?php echo $customer; ?>" class="grid">
            <div class='c'>
                <img class='preloader_grids_box' src="<?php echo base_url() ?>/img/grids_boxes_preloader.gif">
                <div class='c_content'>
                    <div class="p_url">
    <?php if ($ks > 0 && $mismatch_button == true) { ?>
                            <input data-value="<?php echo $vs['imported_data_id']; ?>"class="mismatch_image" style="float: right; margin-top: 0;position: relative;z-index: 200;" type="button" value="" title="">
                            <div class='missmatch_popup'style="display: none;">
                             <span class="first_line">Mark as incorrect match  </span><br/>
                             <span class="second_line">Enter URL of match... </span>
                            </div>
                        <?php }

                    if ($ks ==0 && $mismatch_button == true) { ?>
                            <input data-value="<?php echo $vs['imported_data_id']; ?>"class="missmatch_first" style="float: right; margin-top: 0;" type="button" value="" title="Report mismatch">
                        <?php }

                        ?>
                        <span class='analysis_content_head'>URL:</span>
                        <!--                        //Max-->
                        <p class='short_product_name ellipsis'><a target="_blank" href="<?php echo $vs['url']; ?>"><?php echo $vs['url']; ?></a></p>
                    </div>
                    <!--                            //Max-->
                    <div class="p_name"  <?php //if($marg == 0) echo "style='margin-bottom:25px;'";?>>
                        <span class='analysis_content_head'>Product Name:</span>
                        <p style="float:none;" class='short_product_name grid_product_name'  ><?php echo $vs['product_name'];?></p>
                    </div>
                    <div class="p_price">
    <?php
    if (!empty($vs['three_last_prices'])) {
        echo "<span class='analysis_content_head'>Price:</span>";
        echo '<table >';
        foreach ($vs['three_last_prices'] as $last_price) {
            ?>
                                <tr>
                                    <td>
                                        <p class='short_product_name'><?php
                    if ($last_price->created != '') {
                        echo date("m/d/Y", strtotime($last_price->created)) . ':';
                    }
            ?> </p>
                                    </td>
                                            <?php if ($j != 0) { ?>
                                        <td>
                                            <!--    //Max-->
                                            <p  class='short_product_name'> <span <?php
                                                if (sprintf("%01.2f", floatval($last_price->price)) == $min_price) {
                                                    if ($bold != 1) {
                                                        echo "style='font-weight: bold;'";
                                                        $bold = 1;
                                                    }
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
                        } elseif (sprintf("%01.2f", floatval($last_price->price)) == $min_price) {
                            if ($bold != 1) {
                                echo "style='font-weight: bold;'";
                                $bold = 1;
                            }
                        }
                ?> class="product_price"><?php echo '$' . sprintf("%01.2f", floatval($last_price->price)); ?></span></p>
                                        </td>
                                                    <?php
                                                }
                                                ?>
                                    <?php
                                }
                                echo '</table>';
                            } else {
                                echo "<span class='analysis_content_head'>Price:</span>";
                                echo "<p>Special or not listed</p>";
                            }
                            ?>
                    </div>
                    <!--                            //Max-->
                    <div class="p_description" style="overflow:hidden;">
    <?php if ($s_product_short_desc_count > 0) { ?>
                            <span class='analysis_content_head' style="width: 100%;"><img style="height: 9px;width: 9px;background: rgb(207, 207, 207);padding: 2px;margin-top: -3px;margin-right: 4px;" src="<?php echo base_url() ?>/img/arrow-down.png"><?php
                            if ($s_product_long_description == '') {
                                echo "Description";
                            } else {
                                //echo $s_product_long_description."!!!!";
                                echo "Short Description";
                            }
                            ?>
                            <?php $snap_data = $this->webshoots_model->scanForProductSnap($vs['imported_data_id']); ?>
                            <?php if($snap_data['img_av_status']) { ?>
                                <i style='float: right;' class='snap_ico_gridview icon-picture' data-snap="<?php echo $snap_data['snap']; ?>"></i>
                            <?php } ?>
                            <span class='short_desc_wc' style="float:left;width: 100%;"></span></span>
                            <p class="heading_text">Words: <b><?php echo $s_product_short_desc_count; ?></b></p>
                            <div class="p_seo<?php echo $row; ?>short seo_container" style="clear:left;">

                                   <div style="float: left;width: 100%;"> <p class="heading_text">SEO Keywords: </p>
                                        <select class="keywords_select" name="analysis" style="margin-top: -20px;float: right;width: 95px;margin-right: 50px;">
                                                    <option  value="title">Title</option>
                                                    <option value="custom">Custom</option>
<!--                                                    Maxik-->
                                                    <?php if(isset($vs['short_meta'])){?>
                                                    <option value="meta">Meta</option>   
                                                    <?php }?>
<!--                                                     Maxik-->
                                        </select>
                                   </div>
                                <div class="primary" style="height: 100%;width: 100%;">
                                    <div class=""><span class="primary_name">Primary: </span>
                                        <span>
                                            <span class="primary_speed">
                                                    <span class="title_words" style="display: none;"></span>
                                                    <span class="you_words you_words_input" style="display: inline;">
                                                        <input class="keyword_input" data-value="<?php echo $vs['imported_data_id']; ?>" name="keyword1" keyword_num="1" type="text" value="<?php if(count($vs['custom_seo'])>0){ echo $vs['custom_seo']['primary']; }?>">
                                                        <span id="keyword1_density"></span>
                                                    </span>
                                            </span>
                                        </span>
                                    </div>
                                    <div class="clear"></div>
                                    <div class=""><span class="primary_name">Secondary: </span>
                                        <span>
                                            <span class="primary_speed">
                                                    <span class="title_words" style="display: none;"></span>
                                                    <span class="you_words you_words_input" style="display: inline;">
                                                        <input class="keyword_input" data-value="<?php echo $vs['imported_data_id']; ?>" name="keyword2" keyword_num="2" type="text" value="<?php if(count($vs['custom_seo'])>0){ echo $vs['custom_seo']['secondary']; }?>">
                                                        <span id="keyword2_density"></span>
                                                    </span>
                                            </span>
                                        </span>
                                    </div>
                                    <div class="clear"></div>
                                    <div class=""><span class="primary_name">Tertiary: </span>
                                        <span>
                                            <span class="primary_speed">
                                                    <span class="title_words" style="display: none;"></span>
                                                    <span class="you_words you_words_input" style="display: inline;">
                                                        <input class="keyword_input" data-value="<?php echo $vs['imported_data_id']; ?>" name="keyword3" keyword_num="2" type="text" value="<?php if(count($vs['custom_seo'])>0){ echo $vs['custom_seo']['tertiary']; }?>">
                                                        <span id="keyword3_density"></span>
                                                    </span>
                                            </span>
                                        </span>
                                    </div>
                                    <div class="clear"></div>
				</div>
<!--                                Maxik-->
                                <div class="seo_meta">
                                    <ul class='gr_seo_short_ph seo_meta_section' style='font-weight: bold;float:left;'>
            <?php if(isset($vs['short_meta'])){foreach ($vs['short_meta'] as $key => $value) { ?>

                                            <?php $v_ph = $value['value']; ?>

                                            <li >
                                                <span style="white-space: normal;line-height: 20px;text-decoration: none;font-size: 14px !important;line-height: 21px;text-decoration: none;white-space: normal;"data-status='seo_link' onclick="wordGridModeHighLighter('section_<?php echo $i; ?>', '<?php echo $v_ph; ?>', 'short')" class='word_wrap_li_pr hover_en'>
                <?php echo $value['value']; ?>
                                                    <?php echo '(' . $value['count'] . ') - ' . $value['prc']. '%'; ?>
                                                </span>
                            <!--                                    <span class='word_wrap_li_sec' style="margin-top: -16px;margin-left: 5px;"></span>-->
                                            </li>
    <?php } }?>
                                    </ul>
                                </div>
<!--Maxik-->
            <?php if (count($vs['seo']['short']) > 0) { ?>
                                    <ul class='gr_seo_short_ph list_section' style='font-weight: bold;float:left;'>
            <?php foreach ($vs['seo']['short'] as $key => $value) { ?>

                                            <?php $v_ph = $value['ph']; ?>

                                            <li >
                                                <span style="white-space: normal;line-height: 20px;text-decoration: none;font-size: 14px !important;line-height: 21px;text-decoration: none;white-space: normal;"data-status='seo_link' onclick="wordGridModeHighLighter('section_<?php echo $i; ?>', '<?php echo $v_ph; ?>', 'short')" class='word_wrap_li_pr hover_en'>
                <?php echo $value['ph']; ?>
                                                    <?php echo '(' . $value['count'] . ') - ' . $value['prc'] . '%'; ?>
                                                </span>
                            <!--                                    <span class='word_wrap_li_sec' style="margin-top: -16px;margin-left: 5px;"></span>-->
                                            </li>
            <?php } ?>
                                    </ul>
                                    <?php } else { ?>

                                    <p style="float: left;width: 100%;" class="heading_text list_section"><span style="font-weight: bold;">None</span></p>
        <?php } ?>
                            </div>
                            <div class="cmp-area" style="float: left;">
        <?php if (isset($vs['short_original']) && $vs['short_original'] != "Insufficient data") { ?>
                                    <p><img class="cmp-btn" src="<?php echo base_url() ?>/img/icon.png" title='Click to see dublicates words'>Duplicate content: <b><?php echo $vs['short_original']; ?> </b></p>
                                <?php } else { ?>
                                    <p>Duplicate content: <b><?php echo $vs['short_original']; ?> </b></p>
                                <?php } ?>
                                <p class="short_desc_con compare"><?php echo $s_product_description; ?></p>
                            </div>
        <?php
    }
    if ($s_product_long_desc_count > 0) {
        ?>

                            <span class='analysis_content_head' style="width: 100%;float:left;"><img style="height: 9px;width: 9px;background: rgb(207, 207, 207);padding: 2px;margin-top: -3px;margin-right: 4px;" src="<?php echo base_url() ?>/img/arrow-down.png"><?php
                    if ($s_product_description == '') {
                        echo "Description";
                    } else {
                        echo "Long Description";
                    }
        ?><span class='long_desc_wc'style="float:left;width: 100%;" ></span></span>
                            <p class="heading_text">Words: <b><?php echo $s_product_long_desc_count; ?></b></p>
                            <div class="p_seo<?php
                        if ($s_product_description == '') {
                            echo $row . 'short';
                        } else {
                            echo $row . 'long';
                        }
        ?> seo_container">
                           <?php if ($s_product_description == '') { ?>
                                   <div style="float: left;width: 100%;"><p class="heading_text">SEO Keywords: </p>
                                   <select class="keywords_select" name="analysis" style="float: right;margin-top: -20px;width: 95px;margin-right: 50px;">
						<option  value="title">Title</option>
						<option value="custom">Custom</option>
<!--                                                Maxik-->
                                                <?php if(isset($vs['long_meta'])){?>
                                                    <option value="meta">Meta</option>   
                                                <?php }?>
<!--                                                    Maxik-->
				   </select>
                                   </div>

                                     <div class="primary" style="height: 100%;width: 100%;">
                                    <div class=""><span class="primary_name">Primary: </span>
                                        <span>
                                            <span class="primary_speed">
                                                    <span class="title_words" style="display: none;"></span>
                                                    <span class="you_words you_words_input" style="display: inline;">
                                                        <input class="keyword_input" data-value="<?php echo $vs['imported_data_id']; ?>" name="keyword1" keyword_num="1" type="text" value="<?php if(count($vs['custom_seo'])>0){ echo $vs['custom_seo']['primary']; }?>">
                                                        <span id="keyword1_density"></span>
                                                    </span>
                                            </span>
                                        </span>
                                    </div>
                                    <div class="clear"></div>
                                    <div class=""><span class="primary_name">Secondary: </span>
                                        <span>
                                            <span class="primary_speed">
                                                    <span class="title_words" style="display: none;"></span>
                                                    <span class="you_words you_words_input" style="display: inline;">
                                                        <input class="keyword_input" data-value="<?php echo $vs['imported_data_id']; ?>" name="keyword2" keyword_num="2" type="text" value="<?php if(count($vs['custom_seo'])>0){ echo $vs['custom_seo']['secondary']; }?>">
                                                        <span id="keyword2_density"></span>
                                                    </span>
                                            </span>
                                        </span>
                                    </div>
                                    <div class="clear"></div>
                                    <div class=""><span class="primary_name">Tertiary: </span>
                                        <span>
                                            <span class="primary_speed">
                                                    <span class="title_words" style="display: none;"></span>
                                                    <span class="you_words you_words_input" style="display: inline;">
                                                        <input class="keyword_input" data-value="<?php echo $vs['imported_data_id']; ?>" name="keyword3" keyword_num="2" type="text" value="<?php if(count($vs['custom_seo'])>0){ echo $vs['custom_seo']['tertiary']; }?>">
                                                        <span id="keyword3_density"></span>
                                                    </span>
                                            </span>
                                        </span>
                                    </div>
                                    <div class="clear"></div>
				</div>
                                <?php }else{ ?>
                                <!--<div class="primary" style="height: 100%;width: 100%;">
                                   <p style="float: left;width: 100%;" class="heading_text list_section"><span style="font-weight: bold;">Primary: <?php if(count($vs['custom_seo'])>0){ echo $vs['custom_seo']['primary']; }?></span></p>
                                   <p style="float: left;width: 100%;" class="heading_text list_section"><span style="font-weight: bold;">Secondary: <?php if(count($vs['custom_seo'])>0){ echo $vs['custom_seo']['secondary']; }?></span></p>
                                   <p style="float: left;width: 100%;" class="heading_text list_section"><span style="font-weight: bold;">Tertiary: <?php if(count($vs['custom_seo'])>0){ echo $vs['custom_seo']['tertiary'];}?></span></p>
                                </div>-->
                                <div style="float: left;width: 100%;"><p class="heading_text">SEO Keywords: </p></div>
                                <div class="primary" style="height: 100%; width: 100%; display: block;">
                                    <div class=""><span class="primary_name1">Primary: </span>
                                        <span>
                                            <span class="primary_speed">
                                                    <span class="title_words" style="display: none;"></span>
                                                    <span class="you_words you_words_input" style="display: inline;">
                                                        <span class='prim_1 primary_name_long'> <?php if(count($vs['custom_seo'])>0){ echo $vs['custom_seo']['primary']; }?></span><span class='prim_1_prc'></span>
                                                    </span>
                                            </span>
                                        </span>
                                    </div>
                                    <div class="clear"></div>
                                    <div class=""><span class="primary_name1">Secondary: </span>
                                        <span>
                                            <span class="primary_speed">
                                                    <span class="title_words" style="display: none;"></span>
                                                    <span class="you_words you_words_input" style="display: inline;">
                                                        <span class='prim_2 primary_name_long'><?php if(count($vs['custom_seo'])>0){ echo $vs['custom_seo']['secondary']; }?></span><span class='prim_2_prc'></span>
                                                    </span>
                                            </span>
                                        </span>
                                    </div>
                                    <div class="clear"></div>
                                    <div class=""><span class="primary_name1">Tertiary: </span>
                                        <span>
                                            <span class="primary_speed">
                                                    <span class="title_words" style="display: none;"></span>
                                                    <span class="you_words you_words_input" style="display: inline;">
                                                        <span class='prim_3 primary_name_long'><?php if(count($vs['custom_seo'])>0){ echo $vs['custom_seo']['tertiary']; }?></span><span class='prim_3_prc'></span>
                                                    </span>
                                            </span>
                                        </span>
                                    </div>
                                    <div class="clear"></div>
				</div>
<!--                                Maxik-->
                                <div class="seo_meta">
                                    <ul class='gr_seo_short_ph seo_meta_section' style='font-weight: bold;float:left;'>
            <?php if(isset($vs['short_meta'])){foreach ($vs['long_meta'] as $key => $value) { ?>

                                            <?php $v_ph = $value['value']; ?>

                                            <li >
                                                <span style="white-space: normal;line-height: 20px;text-decoration: none;font-size: 14px !important;line-height: 21px;text-decoration: none;white-space: normal;"data-status='seo_link' onclick="wordGridModeHighLighter('section_<?php echo $i; ?>', '<?php echo $v_ph; ?>', 'long')" class='word_wrap_li_pr hover_en'>
                <?php echo $value['value']; ?>
                                                    <?php echo '(' . $value['count'] . ') - ' . $value['prc']. '%'; ?>
                                                </span>
                            <!--                                    <span class='word_wrap_li_sec' style="margin-top: -16px;margin-left: 5px;"></span>-->
                                            </li>
            <?php }} ?>
                                    </ul>
                               </div>
<!--Maxik-->
                                <?php }?>
 <?php if (count($vs['seo']['long']) > 0) { ?>
                                    <ul class='gr_seo_short_ph list_section' style='font-weight: bold;float:left;'>
            <?php foreach ($vs['seo']['long'] as $key => $value) { ?>
                                            <?php $v_ph = $value['ph']; ?>

                                            <li >
                                                <span style="font-size: 14px !important;white-space: normal;line-height: 20px;text-decoration: none;"data-status='seo_link' onclick="wordGridModeHighLighter('section_<?php echo $i; ?>', '<?php echo $v_ph; ?>', 'long')" class='word_wrap_li_pr hover_en'>
                <?php echo $value['ph']; ?>
                                                    <?php echo '(' . $value['count'] . ') - ' . $value['prc'] . '%'; ?>
                                                </span>
                            <!--                                    <span class='word_wrap_li_sec' style="margin-top: -16px;margin-left: 5px;"></span>-->
                                            </li>
            <?php } ?>
                                    </ul>
                                    <?php } else { ?>

                                    <p style="float: left;width: 100%;" class="heading_text list_section"><span style="font-weight: bold;">None</span></p>
        <?php } ?>
                            </div>
                            <div class="cmp-area" style="float: left;">
        <?php if (isset($vs['long_original']) && $vs['long_original'] != "Insufficient data") { ?>
                                    <p><img class="cmp-btn" src="<?php echo base_url() ?>/img/icon.png" title='Click to see dublicates words'>Duplicate content: <b><?php echo $vs['long_original']; ?> </b></p>
                                <?php } else { ?>
                                    <p>Duplicate content: <b><?php echo $vs['long_original']; ?> </b></p>
                                <?php } ?>

                                <!--                     //Max-->
        <?php echo '<p class="compare compare_long">' . $s_product_long_description . '</p>'; ?>

                            </div>
        <?php
    }
    if ($s_product_long_desc_count == 0 && $s_product_short_desc_count == 0) {
        ?>
                            <span class='analysis_content_head'>Description: </span>
                            <span>No description on site</span>

        <?php
    }
    ?>

                    </div>

                    <div>

                        <!--     dublicate the short text           -->

                        <!--?php
                        if (isset($vs['short_original_text'])) {
                            echo "<p>short dublicate text</p>";
                            //var_dump($vs['short_original_text']);
                            echo "<b>" . implode(',', $vs['short_original_text']) . "</b>";
                        }
                        ?>
                        <!--   end  dublicate the short text           -->
                        <!--     dublicate the long text           -->

                        <!--?php
                        if (isset($vs['long_original_text'])) {
                            echo "<p>long dublicate text</p>";
                            //var_dump($vs['short_original_text']);
                            echo "<b>" . implode(',', $vs['long_original_text']) . "</b>";
                        }
                        ?>
                        <!--   end  dublicate the long text           -->

                    </div>
                </div>

                <p  style="color: rgb(117, 114, 114);">Id: <span class="imported_data_id"><?php echo $vs['imported_data_id']; ?></span></p>

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

<script type="text/javascript">
                                    rows_count = "<?php echo $row = ceil(count($same_pr) / 3); ?>";
                                    group_id = "<?php echo $same_pr[0]['imported_data_id']; ?>";


//                                    short_long_dublicate();

</script>
<script type='text/javascript'>
 function gridKeywordDensity( selected_item){
        var grid_primary_ph = $.trim($(selected_item+' input[name="keyword1"]').val());
        var grid_secondary_ph = $.trim($(selected_item+' input[name="keyword2"]').val());
        var grid_tertiary_ph = $.trim($(selected_item+' input[name="keyword3"]').val());
        if(grid_primary_ph !== "") grid_primary_ph.replace(/<\/?[^>]+(>|$)/g, "");
        if(grid_secondary_ph !== "") grid_secondary_ph.replace(/<\/?[^>]+(>|$)/g, "");
        if(grid_tertiary_ph !== "") grid_tertiary_ph.replace(/<\/?[^>]+(>|$)/g, "");

        if(grid_primary_ph !== "" || grid_secondary_ph !== "" || grid_tertiary_ph !== "") {
            var grid_short_desc = $.trim($(selected_item+' .short_desc_con').html());
            if(grid_short_desc  !== "") grid_short_desc.replace(/<\/?[^>]+(>|$)/g, "");
            var grid_long_desc = $.trim($(selected_item+' .compare_long').html());
            if(grid_long_desc  !== "") grid_short_desc.replace(/<\/?[^>]+(>|$)/g, "");

            var grid_send_object = {
                primary_ph: grid_primary_ph,
                secondary_ph: grid_secondary_ph,
                tertiary_ph: grid_tertiary_ph,
                short_desc: grid_short_desc,
                long_desc: grid_long_desc
            };

            $.post(base_url+'index.php/measure/analyzekeywords', grid_send_object, function(data) {
                var first = (data['primary'][0].toPrecision(3)*100).toFixed(2);
                var second = (data['secondary'][0].toPrecision(3)*100).toFixed(2);
                var third = (data['tertiary'][0].toPrecision(3)*100).toFixed(2);
                var first1 = (data['primary'][1].toPrecision(3)*100).toFixed(2);
                var second1 = (data['secondary'][1].toPrecision(3)*100).toFixed(2);
                var third1 = (data['tertiary'][1].toPrecision(3)*100).toFixed(2);
                if(grid_short_desc!=''){
                if($(selected_item+" input[name='keyword1']").val()!=''){
                    $(selected_item+' span#keyword1_density').html(' - '+first+'%');
                }
                if($.trim($(selected_item+" input[name='keyword2']").val())!=''){
                    $(selected_item+' span#keyword2_density').html(' - '+second+'%');
                }
                if($.trim($(selected_item+" input[name='keyword3']").val())!=''){
                    $(selected_item+' span#keyword3_density').html(' - '+third+'%');
                }
                
                
                
                
                if($.trim($(selected_item+' .prim_1').text()!='')){
                    $(selected_item+' .prim_1_prc').html(' - '+first1+'%');
                }
                if($(selected_item+' .prim_2').text()!=''){
                    $(selected_item+' .prim_2_prc').html(' - '+second1+'%');
                }
                if($(selected_item+' .prim_3').text()!=''){
                    $(selected_item+' .prim_3_prc').html(' - '+third1+'%');
                }
                
                
            }
            if(grid_short_desc=='' && grid_long_desc!='' ){
                 if($(selected_item+" input[name='keyword1']").val()!=''){
                    $(selected_item+' span#keyword1_density').html(' - '+first1+'%');
                }
                if($.trim($(selected_item+" input[name='keyword2']").val())!=''){
                    $(selected_item+' span#keyword2_density').html(' - '+second1+'%');
                }
                if($.trim($(selected_item+" input[name='keyword3']").val())!=''){
                    $(selected_item+' span#keyword3_density').html(' - '+third1+'%');
                }
            }
            }, 'json');
        }
        return false;
    }
    function inArray(needle, haystack) {
        var length = haystack.length;
        for (var i = 0; i < length; i++) {
            if (haystack[i] == needle)
                return true;
        }
        return false;
    }
    // function makeSticky(val){
    var stick_urls = [];
    $(".has_stiky_image").live('click', function() {
        var sticky_url = $(this).closest('.grid_se_section').find('select').val();
        $(this).css('background', 'black');
        $(this).attr('title', 'Click to unstick');
        if (!inArray(sticky_url, stick_urls)) {
            stick_urls.push(sticky_url);
        }
        $.cookie('sticky_url', stick_urls);

    });
    var sticky_url = $.cookie('sticky_url');
    if (typeof(sticky_url) !== 'undefined') {

    }

    // }

    var count =<?php echo count($same_pr); ?>;
    var ddData_grids = [];
    var customers = [];
    function gridsCustomersListLoader() {

        for (var i = 1; i <= count + 1; i++) {

            //ddData_grids[i]['ddData_grid']=[];
            ddData_grids[i] = $("#grid_se_section_" + i + " input[type='hidden'][name='dd_customer']").val();
            if ($("#grid_se_section_" + i + " input[type='hidden'][name='dd_customer']").val() != undefined) {

                customers.push($("#grid_se_section_" + i + " input[type='hidden'][name='dd_customer']").val());
            }
        }
        var newc_data = [];

        setTimeout(function() {
            selected_customers = [];
            var customers_list = $.post(base_url + 'index.php/measure/getsiteslist_new', {}, function(c_data) {
                //console.log(c_data);
                var j = 0;
                for (var key in c_data) {

                    if (inArray(c_data[key].value, customers)) {
                        //console.log(c_data[key].value);
                        newc_data[j] = c_data[key];
                        j++;
                    }
                }
                ;

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
    grid_listings = [];
    $(".grid").each(function() {
        var site = $(this).attr('id');
        grid_listings[site] = $(this).html();

    });
    $(".an_grd_view_drop select").live('change', function() {

        $(this).closest('.grid_se_section').find('.grid').html(grid_listings[$(this).val()]);
        $(this).closest('.grid_se_section').find('.grid .c > img').css('display', 'none');
        $(this).closest('.grid_se_section').find('.grid .c > .c_content').css('display', 'block');

        fixGridHeights();
        $(".grid_se_section .c_content").each(function() {

            if ($(".grid_se_section .c_content").height() >= 700) {
                $(".grid_se_section .c_content").css('height', '700');
                $(".grid_se_section .c_content").css('overflow-y', 'auto');
                $(".grid_se_section .c_content").css('overflow-x', 'hidden');
                $(".grid_se_section .c_content .p_description").css('height', 'auto');
            }
        });
    });

    selectedCustomer();

 $(document).ready(function(){
   $(".grid_se_section").each(function() {
       var selected_item='#'+$(this).closest('.grid_se_section').attr('id');
       gridKeywordDensity(selected_item);

    });
   
   $(".mismatch_image").live('mouseover', function() {

        var item = "<div class='missmatch_popup'>Aaaaaaaaaa</div>";
        $(".missmatch_popup").css('display', 'block');

    });

    $(".missmatch_popup").live('mouseleave', function() {
        $(".missmatch_popup").css('display', 'none');
    });
// Maxik
    $(".primary").css('display', 'none');
    $(".seo_meta_section").css('display', 'none');

    $(".keywords_select").live('change', function() {

        if ($(this).val() === 'title') {
            $(this).closest('.grid_se_section').find(".primary").css('display', 'none');
            $(this).closest('.grid_se_section').find(".seo_meta_section").css('display', 'none');
            $(this).closest('.grid_se_section').find(".list_section").css('display', 'block');
        }
        if($(this).val() === 'meta'){
            
            $(this).closest('.grid_se_section').find(".primary").css('display', 'none');
            $(this).closest('.grid_se_section').find(".list_section").css('display', 'none');
            $(this).closest('.grid_se_section').find(".seo_meta_section").css('display', 'block');
              
        }
        
        if($(this).val() === 'custom'){

            $(this).closest('.grid_se_section').find(".list_section").css('display', 'none');
            $(this).closest('.grid_se_section').find(".seo_meta_section").css('display', 'none');
            $(this).closest('.grid_se_section').find(".primary").css('display', 'block');

        }
        fixGridHeights();
    });
//Maxik
    $(".keyword_input").change(function() {
        
    selected_item='#'+$(this).closest('.grid_se_section').attr('id');
        gridKeywordDensity(selected_item);
    });
    
    //on keyup, start the countdown
    $(".keyword_input").keyup(function(){
        selected_item='#'+$(this).closest('.grid_se_section').attr('id');
                  
        var primary=$(selected_item).find("input[name='keyword1']").val();
        var secondary=$(selected_item).find("input[name='keyword2']").val();
        var tertiary=$(selected_item).find("input[name='keyword3']").val();
        $(selected_item).find('.prim_1').text(primary);
        $(selected_item).find('.prim_2').text(secondary);
        $(selected_item).find('.prim_3').text(tertiary);
        $(selected_item).find('.keyword_input').each(function(){
             if($.trim($(this).val())==''){
             $(this).next('span').text('');
        }  
        });
        $(selected_item).find('.primary_name_long').each(function(){
             if($.trim($(this).val())==''){
             $(this).next('span').text('');
        }  
        });            
         setTimeout(function(){ gridKeywordDensity(selected_item);}, '1000');
    });

    $(".snap_ico_gridview").on('mouseover', function(e) {
        var snap = $(e.target).data('snap');
        var img_target = base_url + "webshoots/" + snap;
        var data = "<img src='" + img_target + "'>";
        $("#preview_crawl_snap_modal").modal('show');
        $("#preview_crawl_snap_modal .snap_holder").html(data);
    });

$('.primary input').change(function() {
        $(this).closest('.primary').find('.keyword_input').addClass('currentFocused');
    });

$(document).click(function(e) {
        if ($('.currentFocused').length>0 && !($(e.target).hasClass('keyword_input') && $(e.target).hasClass('currentFocused'))) {
            var primary=$('.currentFocused').closest('.primary').find("input[name='keyword1']").val();
            var secondary=$('.currentFocused').closest('.primary').find("input[name='keyword2']").val();
            var tertiary=$('.currentFocused').closest('.primary').find("input[name='keyword3']").val();
            var imported_data_id= $('.currentFocused').closest('.primary').find("input[name='keyword1']").attr('data-value');
            $('.currentFocused').closest('.grid_se_section').find('.prim_1').text(primary);
            $('.currentFocused').closest('.grid_se_section').find('.prim_2').text(secondary);
            $('.currentFocused').closest('.grid_se_section').find('.prim_3').text(tertiary);
    $.post(add_seo, {primary: primary, secondary: secondary, tertiary: tertiary, imported_data_id: imported_data_id}, 'json').done(function(data) {

    });
        $('.currentFocused').removeClass('currentFocused');
        }
    });


  $('.primary input').keydown(function (e){

    if(e.keyCode == '13' || e.keyCode == '32'){

        var primary=$(this).closest('.primary').find("input[name='keyword1']").val();
        var secondary=$(this).closest('.primary').find("input[name='keyword2']").val();
        var tertiary=$(this).closest('.primary').find("input[name='keyword3']").val();
        var imported_data_id= $(this).closest('.primary').find("input[name='keyword1']").attr('data-value');
        $(this).closest('.grid_se_section').find('.prim_1').text(primary);
        $(this).closest('.grid_se_section').find('.prim_2').text(secondary);
        $(this).closest('.grid_se_section').find('.prim_3').text(tertiary);
        $.post(add_seo, {primary: primary, secondary: secondary, tertiary: tertiary, imported_data_id: imported_data_id}, 'json').done(function(data) {

        });

        $('.currentFocused').removeClass('currentFocused')

    }

  });
   });



</script>

<style>
    #compet_area_grid .you_words_input input {
        margin-top: 0px !important;
        width: 120px !important;
    }
    .primary{
        height: auto !important;

    }
    .primary_speed{
        float: left;
        margin-left: 5px;
        width: 180px;
        margin-bottom: 2px;
    }
</style>