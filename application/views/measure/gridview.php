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

foreach ($same_pr as $ks => $vs) {
    //Max
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
        $vs['description'] = preg_replace('/\s+/', ' ', $vs['description']);
        // $data_import['description'] = preg_replace('/[^A-Za-z0-9\. -!]/', ' ', $data_import['description']);
        $s_product_short_desc_count = count(explode(" ", $vs['description']));
    } else {
        $s_product_short_desc_count = 0;
        $s_product_description = '';
    }
    if ($vs['long_description'] !== null && trim($vs['long_description']) !== "") {
        $s_product_long_description = $vs['long_description'];
        $vs['long_description'] = preg_replace('/\s+/', ' ', $vs['long_description']);
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
        <div class='h'>
            <input type="hidden" name='dd_customer' value="<?php echo $customer; ?>">
            <div id="an_grd_view_drop_gr<?php echo $i; ?>" class='an_grd_view_drop'></div>
        </div>
        <div class='c'>
            <img class='preloader_grids_box' src="<?php echo base_url() ?>/img/grids_boxes_preloader.gif">
            <div class='c_content'>
                <div class="p_url">
                    <?php if ($ks > 0 && $mismatch_button==true) { ?>
                        <input data-value="<?php echo $vs['imported_data_id']; ?>"class="mismatch_image" style="float: right; margin-top: 0;" type="button" value="" title="Report mismatch">
                    <?php }
                    ?>
                    <span class='analysis_content_head'>URL:</span>
                    <!--                        //Max-->
                    <p class='short_product_name ellipsis'><a target="_blank" href="<?php echo $vs['url']; ?>"><?php echo $vs['url']; ?></a></p>
                </div>
                <!--                            //Max-->
                <div class="p_name">
                    <span class='analysis_content_head'>Product Name:</span>
                    <p style="min-height: 38px;" class='short_product_name'><?php echo $vs['product_name']; ?></p>
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
                                    <p class='short_product_name'><?php echo date("m/d/Y", strtotime($last_price->created)); ?>: </p>
                                </td>
                                <?php if ($j != 0) { ?>
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
                                }
                                ?>
                            </tr>
                            <?php
                        }
                        echo '</table>';
                    }
                    ?>
                </div>
                <!--                            //Max-->
                <div class="p_description" style="overflow:hidden;">
                    <?php if ($s_product_short_desc_count > 0) { ?>
                        <span class='analysis_content_head'><img style="height: 9px;width: 9px;background: rgb(207, 207, 207);padding: 2px;margin-top: -3px;margin-right: 4px;" src="<?php echo base_url() ?>/img/arrow-down.png"><?php
                            if ($s_product_description == '' || $s_product_long_description == '') {
                                echo "Description";
                            } else {
                                echo "Short Description";
                            }
                            ?><span class='short_desc_wc'></span></span>
                        <p class="heading_text">Words: <b><?php echo $s_product_short_desc_count; ?></b></p>
                        <div class="p_seo">
                            <?php if (count($vs['seo']['short']) > 0) { ?>
                                <p class="heading_text">SEO: </p>
                                <ul class='gr_seo_short_ph' style='margin-top: -19px;margin-left: 40px;font-weight: bold;margin-bottom: 0px;'>
                                    <?php foreach ($vs['seo']['short'] as $key => $value) { ?>
                                        <?php $v_ph = $value['ph']; ?>

                                        <li >
                                            <span style="font-size: 14px !important;line-height: 21px;text-decoration: none;white-space: normal;"data-status='seo_link' onclick="wordGridModeHighLighter('section_<?php echo $i; ?>', '<?php echo $v_ph; ?>', 'short')" class='word_wrap_li_pr hover_en'>
                                                <?php echo $value['ph']; ?>
                                                <?php echo '(' . $value['count'] . ')'; ?>
                                            </span>
                        <!--                                    <span class='word_wrap_li_sec' style="margin-top: -16px;margin-left: 5px;"></span>-->
                                        </li>
                                    <?php } ?>
                                </ul>
                            <?php } else { ?>

                                <p class="heading_text">SEO: <span style="font-weight: bold;">None</span></p>
                            <?php } ?>
                        </div>
                        <p>Duplicate content: <b><?php echo isset($vs['short_original']) ? $vs['short_original'] : ''; ?></b></p>

                        <p  class='short_desc_con'><?php echo $s_product_description; ?></p>
                        <?php
                    }
                    
 elseif($s_product_long_desc_count > 0){
                        ?>

                        <span class='analysis_content_head'><img style="height: 9px;width: 9px;background: rgb(207, 207, 207);padding: 2px;margin-top: -3px;margin-right: 4px;" src="<?php echo base_url() ?>/img/arrow-down.png"><?php
                            if ($s_product_description == '' || $s_product_long_description == '') {
                                echo "Description";
                            } else {
                                echo "Long Description";
                            }
                            ?><span class='long_desc_wc'></span></span>
                        <p class="heading_text">Words: <b><?php echo $s_product_long_desc_count; ?></b></p>
                        <div class="p_seo">
                            <?php if (count($vs['seo']['long']) > 0) { ?>
                                <p class="heading_text">SEO: </p>
                                <ul class='gr_seo_short_ph' style='margin-top: -19px;margin-left: 40px;font-weight: bold;margin-bottom: 0px;'>
                                    <?php foreach ($vs['seo']['long'] as $key => $value) { ?>
                                        <?php $v_ph = $value['ph']; ?>

                                        <li >
                                            <span style="font-size: 14px !important;"data-status='seo_link' onclick="wordGridModeHighLighter('section_<?php echo $i; ?>', '<?php echo $v_ph; ?>', 'long')" class='word_wrap_li_pr hover_en'>
                                                <?php echo $value['ph']; ?>
                                                <?php echo '(' . $value['count'] . ')'; ?>
                                            </span>
                        <!--                                    <span class='word_wrap_li_sec' style="margin-top: -16px;margin-left: 5px;"></span>-->
                                        </li>
                                    <?php } ?>
                                </ul>
                            <?php } else { ?>

                                <p class="heading_text">SEO: <span style="font-weight: bold;">None</span></p>
                            <?php } ?>
                        </div>
                        <p>Duplicate content: <b><?php echo isset($vs['long_original']) ? $vs['long_original'] : ''; ?></b></p>


                        <!--                     //Max-->
                        <?php
                        echo '<p>' . $s_product_long_description . '</p>';
                    }else{
                       ?>
                        <span class='analysis_content_head'>Description: </span>
                        <span>No description on site</span>
                        
                       <?php
                    }
                    ?>

                </div>


            </div>

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
</script>

