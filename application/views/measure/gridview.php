<?php //if(count($same_pr) === 3) { 
    $selectedUrl = $_POST['selectedUrl'];
    ?>
    <?php $i = 1; ?>
    <?php
    //Max
    $min_price= 1000000000;
    $j=0;
     foreach($same_pr as $ks => $vs) {
           foreach($vs['three_last_prices'] as $last_price){
                $price=sprintf("%01.2f", floatval($last_price->price));
                if($price<$min_price){
                    $min_price=$price;
                }
            }
            if($vs['url'] ==  $selectedUrl){
            if($ks!=0){
            $same_pr[]=$same_pr[0];
            $same_pr[0]=$vs;
            unset($same_pr[$ks]);
            }
        }
    }
 ?>
        
        <?php foreach($same_pr as $ks => $vs) { ?>
        <?php
        //Max
            $customer = $vs['customer'];
            $class_left = "";
            if($i%2 ==0 || $i%3 ==0) $class_left = 'left';
           // $s_product_description = $vs['description'];
 //           $s_product_long_description = $vs['long_description'];
//            $s_product_short_desc_count = count(explode(" ", $s_product_description));
//            echo "<pre>";
//           print_r(explode(" ", trim($s_product_long_description )));
 //           $s_product_long_desc_count = count(explode(" ", $s_product_long_description));
            
            
             if($vs['description'] !== null && trim($vs['description']) !== "") {
                $s_product_description = $vs['description'];
                $vs['description'] = preg_replace('/\s+/', ' ', $vs['description']);
                // $data_import['description'] = preg_replace('/[^A-Za-z0-9\. -!]/', ' ', $data_import['description']);
                $s_product_short_desc_count = count(explode(" ", $vs['description']));
            }
            else{
                $s_product_short_desc_count=0;
                $s_product_description='';
            }
            if($vs['long_description'] !== null && trim($vs['long_description']) !== "") {
                $s_product_long_description = $vs['long_description'];
                $vs['long_description'] = preg_replace('/\s+/', ' ', $vs['long_description']);
                // $data_import['long_description'] = preg_replace('/[^A-Za-z0-9\. -!]/', ' ', $data_import['long_description']);
                $s_product_long_desc_count = count(explode(" ", $vs['long_description']));
               
            }else{
                $s_product_long_desc_count=0; 
                $s_product_long_description='';
            }
             
            
        //Max    
            
            
        ?>
        <div id="grid_se_section_<?php echo $i; ?>" class='grid_se_section <?php echo $class_left; ?>'>
            <div class='h'>
                <input type="hidden" name='dd_customer' value="<?php echo $customer; ?>">
                <div id="an_grd_view_drop_gr<?php echo $i; ?>" class='an_grd_view_drop'></div>
            </div>
            <div class='c'>
                <img class='preloader_grids_box' src="<?php echo base_url() ?>/img/grids_boxes_preloader.gif">
                <div class='c_content'>
                 	<span class='analysis_content_head'>URL:</span>
<!--                        //Max-->
                    <p class='short_product_name ellipsis'><a target="_blank" href="<?php echo $vs['url']; ?>"><?php echo $vs['url']; ?></a></p>
<!--                            //Max-->
                    <span class='analysis_content_head'>Product Name:</span>
                    <p style="min-height: 38px;" class='short_product_name'><?php echo $vs['product_name']; ?></p>
                    <?php
                    if(!empty($vs['three_last_prices'])) {
                        echo "<span class='analysis_content_head'>Price:</span>";
                        echo '<table >';
                        foreach($vs['three_last_prices'] as $last_price) {
                            
                    ?>
                            <tr>
                                <td>
                                    <p class='short_product_name'><?php echo date("m/d/Y", strtotime($last_price->created)); ?>: </p>
                                </td>
                                <?php if($j!=0){ ?>
                                <td>
<!--    //Max-->
                                    <p  class='short_product_name'> <span <?php if(sprintf("%01.2f", floatval($last_price->price))==$min_price){ echo "style='font-weight: bold;'";} ?>class="product_price">$<?php echo sprintf("%01.2f", floatval($last_price->price)); ?></span></p>
<!--    //Max                            -->
                                </td>
                                <?php
                                }else{
                                ?>
                                    <td>
                                    <p  class='short_product_name'> <span <?php if(sprintf("%01.2f", floatval($last_price->price))>$min_price){echo "class='not_min'";} ?> class="product_price"><?php echo '$'.sprintf("%01.2f", floatval($last_price->price)); ?></span></p>
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
<!--                            //Max-->
        <?php if($s_product_short_desc_count>0){ ?>
                    <span class='analysis_content_head'><img style="height: 9px;width: 9px;background: rgb(207, 207, 207);padding: 2px;margin-top: -3px;margin-right: 4px;" src="<?php echo base_url() ?>/img/arrow-down.png"><?php if($s_product_description=='' || $s_product_long_description==''){ echo "Description";}else{ echo "Short Description"; } ?><span class='short_desc_wc'></span></span>
                         <p class="heading_text">Words: <b><?php echo $s_product_short_desc_count; ?></b></p>
                         <?php if(count($vs['seo']['short']) > 0) { ?>
                              <p class="heading_text">SEO: </p>
                              <ul class='gr_seo_short_ph' style='margin-top: -19px;margin-left: 40px;font-weight: bold;margin-bottom: 0px;'>
                                <?php foreach ($vs['seo']['short'] as $key => $value) { ?>
                                <?php $v_ph = $value['ph']; ?>
                                
                                <li >
                                    <span style="font-size: 14px !important;"data-status='seo_link' onclick="wordGridModeHighLighter('section_<?php echo $i; ?>', '<?php echo $v_ph; ?>', 'short')" class='word_wrap_li_pr hover_en'>
                                        <?php echo $value['ph']; ?>
                                        <?php echo '('.$value['count'].')'; ?>
                                    </span>
<!--                                    <span class='word_wrap_li_sec' style="margin-top: -16px;margin-left: 5px;"></span>-->
                                </li>
                                <?php } ?>
                                </ul>
                            <?php } else { ?>
                                
                                <p class="heading_text">SEO: <span style="font-weight: bold;">None</span></p>
                            <?php } ?>
                         <p>Original content: <b><?php echo $vs['short_original'];  ?></b></p>
                                                                          
                         <p  class='short_desc_con'><?php echo $s_product_description; ?></p>
        <?php }
            if($s_product_long_desc_count>0){ 
        ?>
                    
                    <span class='analysis_content_head'><img style="height: 9px;width: 9px;background: rgb(207, 207, 207);padding: 2px;margin-top: -3px;margin-right: 4px;" src="<?php echo base_url() ?>/img/arrow-down.png"><?php if($s_product_description=='' || $s_product_long_description==''){ echo "Description";}else{ echo "Long Description"; } ?><span class='long_desc_wc'></span></span>
                     <p class="heading_text">Words: <b><?php echo $s_product_long_desc_count; ?></b></p>
                     <?php if(count($vs['seo']['long']) > 0) { ?>
                              <p class="heading_text">SEO: </p>
                              <ul class='gr_seo_short_ph' style='margin-top: -19px;margin-left: 40px;font-weight: bold;margin-bottom: 0px;'>
                                <?php foreach ($vs['seo']['long'] as $key => $value) { ?>
                                <?php $v_ph = $value['ph']; ?>
                                
                                <li >
                                    <span style="font-size: 14px !important;"data-status='seo_link' onclick="wordGridModeHighLighter('section_<?php echo $i; ?>', '<?php echo $v_ph; ?>', 'long')" class='word_wrap_li_pr hover_en'>
                                        <?php echo $value['ph']; ?>
                                        <?php echo '('.$value['count'].')'; ?>
                                    </span>
<!--                                    <span class='word_wrap_li_sec' style="margin-top: -16px;margin-left: 5px;"></span>-->
                                </li>
                                <?php } ?>
                                </ul>
                            <?php } else { ?>
                                
                                <p class="heading_text">SEO: <span style="font-weight: bold;">None</span></p>
                            <?php } ?>
                         <p>Original content: <b><?php echo $vs['long_original'];  ?></b></p>
                        
                    
<!--                     //Max-->
            <p ><?php echo $s_product_long_description; }?></p>
           
            
                </div>
            </div>
            
<!--            <div class='grid_seo'>
                <ul>
                    <li><a href='javascript:void()'>SEO Phrases:</a></li>
                </ul>
                <ul class='gr_seo_short_ph' style='margin-top: 5px;'>
                    <li class='bold'>Short Description:</li>
                    <?php if(count($vs['seo']['short']) > 0) { ?>
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
                    <?php if(count($vs['seo']['long']) > 0) { ?>
                        <?php foreach ($vs['seo']['long'] as $key => $value) { ?>
                        <?php $v_ph = $value['ph']; ?>
                        <li style='margin-top: 5px;'>
                            <span data-status='seo_link' onclick="wordGridModeHighLighter('section_<?php echo $i; ?>', '<?php echo $v_ph; ?>', 'long')" class='word_wrap_li_pr hover_en'>
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
            </div>-->
        </div>
        <?php if ($i%3 == 0) { ?>
        <div style="clear:both"></div>
        <?php } ?>
<!--//Max-->
        <?php $i += 1; $j++;?>
    <?php } ?>

    <script type='text/javascript'>
        var count=<?php echo count($same_pr); ?>;
        var ddData_grids = [];
        function gridsCustomersListLoader() {
            
            for(var i=1;i<=count+1; i++){
              //ddData_grids[i]['ddData_grid']=[];
              ddData_grids[i] = $("#grid_se_section_"+i+" input[type='hidden'][name='dd_customer']").val();
              
            }
//            var ddData_grids_1 = [];
//            var ddData_grids_2 = [];
//            var ddData_grids_3 = [];
//            var ddData_grids_4 = [];
//            var ddData_grids_5 = [];
//
//            var grid_1_customer = $("#grid_se_section_1 input[type='hidden'][name='dd_customer']").val();
//            var grid_2_customer = $("#grid_se_section_2 input[type='hidden'][name='dd_customer']").val();
//            var grid_3_customer = $("#grid_se_section_3 input[type='hidden'][name='dd_customer']").val();
//            var grid_4_customer = $("#grid_se_section_4 input[type='hidden'][name='dd_customer']").val();
//            var grid_5_customer = $("#grid_se_section_5 input[type='hidden'][name='dd_customer']").val();

            setTimeout(function(){
                var customers_list = $.post(base_url + 'index.php/measure/getcustomerslist_new', {}, function(c_data) {
                  for(var i=1;i<=count; i++){
                      console.log(i);
                      var grid1 = $('#an_grd_view_drop_gr'+i).msDropDown({byJson:{data:c_data}}).data("dd");
                      if(grid1 != undefined){
                        grid1.setIndexByValue(ddData_grids[i]);
                      }
                  }
//                   var grid1 = $('#an_grd_view_drop_gr
//                   1').msDropDown({byJson:{data:c_data}}).data("dd");
//                    if(grid1 != undefined){
//                        grid1.setIndexByValue(grid_1_customer);
//                    }
//                    var grid2 = $('#an_grd_view_drop_gr2').msDropDown({byJson:{data:c_data}}).data("dd");
//                    if(grid2 != undefined){
//                        grid2.setIndexByValue(grid_2_customer);
//                    }
//                    var grid3 = $('#an_grd_view_drop_gr3').msDropDown({byJson:{data:c_data}}).data("dd");
//                    if(grid3 != undefined){
//                        grid3.setIndexByValue(grid_3_customer);
//                    }
//                    var grid4 = $('#an_grd_view_drop_gr4').msDropDown({byJson:{data:c_data}}).data("dd");
//                    if(grid4 != undefined){
//                        grid4.setIndexByValue(grid_4_customer);
//                    }
//                    var grid5 = $('#an_grd_view_drop_gr5').msDropDown({byJson:{data:c_data}}).data("dd");
//                    if(grid5 != undefined){
//                        grid5.setIndexByValue(grid_5_customer);
//                    }
                });
            }, 100);
        }
        gridsCustomersListLoader();
    </script>

<?php /* } else { ?>

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
                <span class='analysis_content_head'>Product Name:</span>
                <p class='short_product_name'><?php echo $s_product['product_name']; ?></p>
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
                <span class='analysis_content_head'>Product Name:</span>
                <p class='short_product_name'><?php echo $s_product['product_name']; ?></p>
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
                <span class='analysis_content_head'>Product Name:</span>
                <p class='short_product_name'><?php echo $s_product['product_name']; ?></p>
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

    <script type='text/javascript'>
        function gridsCustomersListLoader() {
            var ddData_grids_1 = [];
            var ddData_grids_2 = [];
            var ddData_grids_3 = [];
            var customers_list = $.post(base_url + 'index.php/measure/getcustomerslist', { }, 'json').done(function(c_data) {
                var cl_arr = [];
                for (var i = 0; i < c_data.length; i++) {
                    cl_arr.push(c_data[i]);
                }

                // --- GRID SECTION 1
                for (var i = 0; i < cl_arr.length; i++) {
                    var text_d = cl_arr[i];
                    var value_d = cl_arr[i];
                    var imageSrc_d = "";
                    var select_st = false;
                    if(cl_arr[i] == 'bjs.com') {
                        text_d = "";
                        imageSrc_d = base_url + "img/bjs-logo.gif";
                    } else if(cl_arr[i] == 'sears.com') {
                        text_d = "";
                        imageSrc_d = base_url + "img/sears-logo.png";
                    } else if(cl_arr[i] == 'walmart.com') {
                        text_d = "";
                        imageSrc_d = base_url + "img/walmart-logo.png";
                    } else if(cl_arr[i] == 'staples.com') {
                        text_d = "";
                        imageSrc_d = base_url + "img/staples-logo.png";
                    } else if(cl_arr[i] == 'overstock.com') {
                        text_d = "";
                        imageSrc_d = base_url + "img/overstock-logo.png";
                    } else if(cl_arr[i] == 'tigerdirect.com') {
                        text_d = "";
                        imageSrc_d = base_url + "img/tigerdirect-logo.png";
                    }
                    if(cl_arr[i] == $('input.dd-selected-value').val()){
                        select_st = true;
                    }
                    var mid = {
                        text: text_d,
                        value: value_d,
                        selected: select_st,
                        description: "",
                        imageSrc: imageSrc_d
                    };
                    ddData_grids_1.push(mid);
                };
                // --- GRID SECTION 2
                for (var i = 0; i < cl_arr.length; i++) {
                    var text_d = cl_arr[i];
                    var value_d = cl_arr[i];
                    var imageSrc_d = "";
                    var select_st = false;
                    if(cl_arr[i] == 'bjs.com') {
                        text_d = "";
                        imageSrc_d = base_url + "img/bjs-logo.gif";
                    } else if(cl_arr[i] == 'sears.com') {
                        text_d = "";
                        imageSrc_d = base_url + "img/sears-logo.png";
                    } else if(cl_arr[i] == 'walmart.com') {
                        text_d = "";
                        imageSrc_d = base_url + "img/walmart-logo.png";
                    } else if(cl_arr[i] == 'staples.com') {
                        text_d = "";
                        imageSrc_d = base_url + "img/staples-logo.png";
                        select_st = true;
                    } else if(cl_arr[i] == 'overstock.com') {
                        text_d = "";
                        imageSrc_d = base_url + "img/overstock-logo.png";
                    } else if(cl_arr[i] == 'tigerdirect.com') {
                        text_d = "";
                        imageSrc_d = base_url + "img/tigerdirect-logo.png";
                    }
                    var mid = {
                        text: text_d,
                        value: value_d,
                        selected: select_st,
                        description: "",
                        imageSrc: imageSrc_d
                    };
                    ddData_grids_2.push(mid);
                };
                // --- GRID SECTION 3
                for (var i = 0; i < cl_arr.length; i++) {
                    var text_d = cl_arr[i];
                    var value_d = cl_arr[i];
                    var imageSrc_d = "";
                    var select_st = false;
                    if(cl_arr[i] == 'bjs.com') {
                        text_d = "";
                        imageSrc_d = base_url + "img/bjs-logo.gif";
                    } else if(cl_arr[i] == 'sears.com') {
                        text_d = "";
                        imageSrc_d = base_url + "img/sears-logo.png";
                    } else if(cl_arr[i] == 'walmart.com') {
                        text_d = "";
                        imageSrc_d = base_url + "img/walmart-logo.png";
                    } else if(cl_arr[i] == 'staples.com') {
                        text_d = "";
                        imageSrc_d = base_url + "img/staples-logo.png";
                    } else if(cl_arr[i] == 'overstock.com') {
                        text_d = "";
                        imageSrc_d = base_url + "img/overstock-logo.png";
                        select_st = true;
                    } else if(cl_arr[i] == 'tigerdirect.com') {
                        text_d = "";
                        imageSrc_d = base_url + "img/tigerdirect-logo.png";
                    }
                    var mid = {
                        text: text_d,
                        value: value_d,
                        selected: select_st,
                        description: "",
                        imageSrc: imageSrc_d
                    };
                    ddData_grids_3.push(mid);
                };
                setTimeout(function(){
                    $('#an_grd_view_drop_gr1').ddslick({
                        data: ddData_grids_1,
                        width: 290,
                        truncateDescription: true,
                    });
                    $('#an_grd_view_drop_gr2').ddslick({
                        data: ddData_grids_2,
                        width: 290,
                        truncateDescription: true,
                    });
                    $('#an_grd_view_drop_gr3').ddslick({
                        data: ddData_grids_3,
                        width: 290,
                        truncateDescription: true,
                    });
                }, 500);
            });
        }
        gridsCustomersListLoader();
    </script>

<?php }*/ ?>