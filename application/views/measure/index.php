<script type='text/javascript'>
jQuery(document).ready(function($) {
    $("#compare_text").focus();

});
    $('#grid_sw_grid').click(function(){
        //$('#shadow').css('display','block');
        //$('#drop_cat').css('display','block');
        //$('.drop_cat').css('display','block');
        switchToGridView();
    });

    $(function() {
        if($('.jq-measure').parent().hasClass('active'))
            $('.jq-measure').trigger( "click" );
    });

</script>
<div class="main_content_other"></div>
<div class="tabbable">
    <h2> Competitive Research
        <span>
            <a href="#myModal" style="float:right; "role="button"  data-toggle="modal"><img  style="width:30px; heihgt: 30px;"src ="<?php echo base_url() ?>/img/ico-gear.png"></a>
            <button class='btn' style="float:right;" onclick="switchToListView();" id='grid_sw_list' type='button'><i class="icon-th-list"></i>&nbsp;SEO</button>
            <button style="float:right;" class='btn' id='grid_sw_grid' type='button'><i class="icon-th-large"></i>&nbsp;COMPARISION</button>
        </span>
    </h2>
    <div class="tab-content">
        <div class="measure-products">
            <div class="row-fluid mb_20">
                <div class="span6">

                    <div id="product_customers" class="customer_dropdown"></div>
                    <?php  echo form_dropdown('product_batches_hidden', $batches_list, array(), 'class="mt_10 mr_10" id="batchess_hidden" style="width: 145px; display: none;"');//max ?>
                    <?php  echo form_dropdown('product_batches', $batches_list, array(), 'class="mt_10 mr_10" id="batchess" style="width: 145px;"');//max ?>
                    <span class="product_batches_items"></span>
                </div>
               
                    
                    <!--button class="drop_cat" style="margin-right: 9px;display:none;float:right;">Save changes</button-->
                    <!--button style="margin-right: 9px" class='btn' onclick="switchToTableView();" id='table_grid' type='button'><i class="icon-th-table"></i>&nbsp;Summary</button-->
                  
                  
                

 
<!-- Modal -->
<div id="myModal" class="modal hide fade" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
    <h3 id="myModalLabel">Display Options</h3>
  </div>
  <div class="modal-body">
    <input  style="margin-top: -4px; margin-right: 3px;" type="radio" name="show_results" value="all"><span>Show all results</span><br>
    <input style="margin-top: -4px;margin-right: 3px;" type="radio" name="show_results" value="one_match"><span>Show results for which there is at least one match <span><Br> 
    <input style="margin-top: -4px;margin-right: 3px;" type="radio" name="show_results" value="no_match"><span>Show results for which there are no matches <span><Br> 
    <input style="margin-top: -4px;margin-right: 3px;" type="radio" name="show_results" value="matchon"><span>Only show items if there is a match on: <span><Br> 
    
    <form >
    <select size="10" id="popup_sites" multiple="multiple" style="margin-left:15px;margin-top: 5px;">
                         <?php
                         
                            foreach($sites as $cite){
                                
                                 ?>
                                 <option value="<?php echo $cite->name; ?>"><?php echo $cite->name; ?></option>
                                <?php
                            }
                         ?>
    </select>
        <div id="for_text">
            <p>Use Shift to select multiple consecutive sites</p>
            <p>Use CTRL (Windows) or Command (Mac) to select multiple individual sites</p>
        </div>
        
        
      
  </form> 
            
  </div>
  <div class="modal-footer">
    <div style ="float: left;margin-top: 4px;">
        <input style="margin-top: -4px;margin-left: 3px;" type="checkbox" name="scroll" id="scroll_all" value="scroll"><span> Scroll all columns at same time <span>
    </div>
    <button class="btn" data-dismiss="modal" aria-hidden="true">Cancel</button>
    <button id="popup_save"class="btn btn-primary">Save changes</button>
     
  </div>
</div>
<script>
$(document).ready(function(){

                        $('#scroll_all').attr('checked',true).addClass('check');
                        $("#popup_save").live('click',function(){
                       $.removeCookie('status_showing_results', {path: '/'});
                       $.removeCookie('selected_cites_cookie', {path: '/'})
                        selected_cites=$("#popup_sites").val();
                        
                        //$("input['name=show_results']").val();
                        
                        if(!$("#scroll_all").is(':checked'))
                            $("#scroll_all").removeAttr('checked').removeClass('check');
                        else
                            $('#scroll_all').attr('checked',true).addClass('check');
//<<<<<<< Updated upstream

                        var status=$("input[name='show_results']:checked").val();

                        var status_showing_results = $.cookie('status_showing_results');
                        var selected_cites_cookie = $.cookie('selected_cites_cookie');

                        if (typeof(status_showing_results) !== 'undefined') {
                            $.removeCookie('status_showing_results', {path: '/'}); // destroy
                            $.cookie('status_showing_results', status, {expires: 7, path: '/'}); // re-create
                            if(status!=='all'){
                                $.cookie("selected_cites_cookie", selected_cites);
                            }else{

                                $.cookie("selected_cites_cookie",null);

                            }

                        } else {
                            $.cookie('status_showing_results', status, {expires: 7, path: '/'}); // create
                            
                            if(status==='matchon'){
                                $.cookie("selected_cites_cookie", selected_cites);
                                selected_cites_cookie = $.cookie('selected_cites_cookie');
                                var dataarray=selected_cites_cookie.split(",");
                                $("#drop_cat").val(dataarray);
                            }else{

                                $.cookie("selected_cites_cookie",null);

                            }
                        }
                        if(status!=='matchon'){
                                $.cookie("selected_cites_cookie",null);
                         }
                        batch_title= $("#batchess").val();
                        if(batch_title!=0){
                            show_from_butches();
                            $('#products li:eq(0)').trigger('click');
                        }
                        
                       $('#myModal').modal('hide');
                    });
                    
                    
                    
                       
        

                        
                        $('#shadow').click(function(){
                               var status=$("input[name='show_results']:checked").val();
                                var selected_cites_drop = $("#drop_cat").val();
                                //selected_cites_drop = $.cookie('selected_cites_cookie')
                                if(selected_cites_drop !='All'){
                                    
                                     $("input[name='show_results']:checked").removeAttr('checked');
                                     $.cookie('status_showing_results', 'matchon', {expires: 7, path: '/'});
                                     $.cookie("selected_cites_cookie", selected_cites_drop);
                                     status_showing_results= $.cookie('status_showing_results');
                                      
                                    if (typeof( status_showing_results) !== 'undefined' ){

                                        status_showing_results = $.cookie('status_showing_results');

                                        $('input[value="'+status_showing_results+'"]').attr('checked',true);
                                        if(status_showing_results=='matchon'){
                                            selected_cites_cookie = $.cookie('selected_cites_cookie');
                                            var dataarray=selected_cites_cookie.split(",");
                                            $("#popup_sites").val(dataarray);
                                            $("#drop_cat").val(dataarray);

                                        }
                                    }else{
                                      $('input[value="all"]').attr('checked',true);  
                                    }
                                     
     
                                     
                                     
                                 }else{
                                     $('input[value="all"]').attr('checked',true); 
                                     $.cookie("selected_cites_cookie",null);
                                     $.cookie('status_showing_results', 'undefined', {expires: 7, path: '/'});
                                 }
                             $('#shadow').css('display','none');
                             $('#drop_cat').css('display','none');
                             
                            batch_title= $("#batchess").val();
                                if(batch_title!=0){
                                show_from_butches();
                                $('#products li:eq(0)').trigger('click');
                            }

                        });
                        
                        
                        
                        
                        status_showing_results= $.cookie('status_showing_results');
                       
                        if (typeof( status_showing_results) != 'undefined' ){ 
                          
                            //status_showing_results = $.cookie('status_showing_results');

                            $('input[value="'+status_showing_results+'"]').attr('checked',true);
                            if(status_showing_results=='matchon'){
                                
                                selected_cites_cookie = $.cookie('selected_cites_cookie');
                                if(selected_cites_cookie){                              
                                    var dataarray=selected_cites_cookie.split(",");
                                    $("#popup_sites").val(dataarray);
                                }
                            }
                        }else{ 
                          $('input[value="all"]').attr('checked',true);  
                        }
                    });
                </script>
<!--//<<<<<<< Updated upstream-->
            </div>
     </div>
        <div class="row-fluid">
            <?php // echo form_open('', array('id'=>'measureFormMetrics')); ?>
            <form id="measureFormMetrics" accept-charset="utf-8" method="post" action="javascript:void(0)">
            <input type="text" name="compare_text" value="" id="compare_text" class="span8" placeholder="" autocomplete="off"/>
            <div id="ci_dropdown" class="website_dropdown"></div>
                <!--select class='cats_an_select' id='cats_an' name='cats_an'>
                    <?php if(count($category_list) > 0) { ?>
                        <?php foreach ($category_list as $key => $value) { ?>
                            <?php if($value->name == "All") { ?>
                            <option value="all">All Categories</option>
                            <?php } else { ?>
                            <option value="<?php echo $value->id; ?>"><?php echo $value->name; ?></option>
                            <?php } ?>
                        <?php } ?>
                    <?php } else { ?>
                    <option value='all'>All Categories</option>
                    <?php } ?>
                </select-->
                <!--?php  echo form_dropdown('cats_an', $departmens_list, null, 'id="cat_an" class="inline_block lh_30 w_375 mb_reset" style="width:135px!important"'); ?-->
                <button type="submit" id="an_search" style="float:left;" onclick="return startMeasureCompareV2()" class="btn btn-search pull-right">SEARCH</button>
                <!-- <button type="submit" id="an_search" class="btn btn-success pull-right">Search</button> -->
            <?php // echo form_close();?>
            </form>
        </div>

        <!--- REAL CONTENT SECTION (START) -->
        <div id="measure_tab_pr_content">
            <div id="measure_tab_pr_content_head" class="row-fluid mt_10">
                <!-- <div class="span8 an_sv_left" style='height: 30px;'><b class='btag_elipsis'>No Title</b></div> -->
                <div class="span8 an_sv_left" style='height: 30px;'>&nbsp;</div>
            </div>
            <div id='compet_area_list' class="row-fluid" style="margin-top: -40px; ">
               <!-- <div style='margin-top: -40px;' class="span8 search_area cursor_default item_section an_sv_left"> -->
               <div style='margin-left: -10px; height: auto;' class="span8 search_area cursor_default an_sv_left">
                    <div id="an_products_box" style='display: none;' class="span8 an_sv_left connectedSortable">&nbsp;</div>
                    <div id='measure_tab_pr_content_body' class="item_section_content">&nbsp;</div>
                </div>
                <div class="span3 an_sv_right" id="attributes_metrics" style="margin-top: -5px; ">
                    <!-- <h3>Metrics</h3> -->
                    <ul>
                        <li><h3>Metrics</h3></li>
<!--                        <li><a href="javascript:void(0)">Site Metrics</a></li>
                        <li>Alexa: &nbsp;</li>
                        <li>SKUs: &nbsp;</li>
                        <li>&nbsp;</li>
                        <li><a href="javascript:void(0)">Page Metrics</a></li>
                        <li>SKU: &nbsp;</li>
                        <li>&nbsp;</li>-->
                        <li style='margin-bottom: 5px;'><a href="javascript:void(0)">Analyze Keyword Density</a></li>
                        <li class='keywords_metrics_bl'>
                            <table class='keywords_metrics_tbl'>
                                <tbody>
                                    <tr>
                                        <td><span>Primary:</span></td>
                                        <td><input type='text' name='km_primary_edit' id="km_primary_edit"></td>
                                    </tr>
                                    <tr>
                                        <td><span>Secondary:</span></td>
                                        <td><input type='text' name='km_secondary_edit' id="km_secondary_edit"></td>
                                    </tr>
                                    <tr>
                                        <td><span>Tertiary:</span></td>
                                        <td><input type='text' name='km_tertiary_edit' id="km_tertiary_edit"></td>
                                    </tr>
                                </tbody>
                            </table>
                        </li>
                        <li class='keywords_metrics_bl'><button type='button' onclick="keywordsAnalizer()" class='btn btn-primary'>Update</button></li>
                        <li>&nbsp;</li>
                        <li class='keywords_metrics_bl_res'>
                            <table class='keywords_metrics_bl_res_tbl'>
                                <tbody>
                                    <tr>
                                        <td><span>Description Density:</span></td>
                                        <td><span>Short</span></td>
                                        <td><span>Long</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>Primary:</span></td>
                                        <td><span id='kw_primary_short_res'>0%</span></td>
                                        <td><span id='kw_primary_long_res'>0%</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>Secondary:</td>
                                        <td><span id='kw_secondary_short_res'>0%</span></td>
                                        <td><span id='kw_secondary_long_res'>0%</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>Tertiary:</td>
                                        <td><span id='kw_tertiary_short_res'>0%</span></td>
                                        <td><span id='kw_tertiary_long_res'>0%</span></td>
                                    </tr>
                                </tbody>
                            </table>
                        </li>
                        <li>&nbsp;</li>
                        <li data-status='words_an'><a href='javascript:void(0)'>Word Analysis:</a></li>
                        <li data-status='words_an' class='bold_li li_top_margin'>Short Description: <span class='normal_font_w' data-st-id='short_desc'>0</span></li>
                        <li data-status='words_an' class='bold_li li_top_margin'>Long Description: <span class='normal_font_w' data-st-id='long_desc'>0</span></li>
                        <li data-status='words_an' class='bold_li li_top_margin'>Total: <span class='normal_font_w' data-st-id='total'>0</span></li>
                    </ul>
                    <ul class='less_b_margin' data-status='seo_an'>
                        <li><a href='javascript:void(0)'>SEO Phrases</a></li>
                    </ul>
                    <ul class='less_b_margin' data-st-id='short_desc_seo' data-status='seo_an'></ul>
                    <ul class='less_b_margin' data-st-id='long_desc_seo' data-status='seo_an'></ul>
                </div>
            </div>

            <!-- GRID VIEW LAYOUT (START) -->
            <div id='compet_area_grid' class='row-fluid'>

                <!-- <div id='grid_se_section_1' class='grid_se_section'>
                    <div class='h'>
                        <div id='an_grd_view_drop_gr1' class='an_grd_view_drop'></div>
                    </div>
                    <div class='c'>
                        <img class='preloader_grids_box' src="<?php echo base_url() ?>/img/grids_boxes_preloader.gif">
                        <div class='c_content'>
                            <span class='analysis_content_head'>Short Description (<span class='short_desc_wc'>0 words</span>):</span>
                            <p class='short_desc_con'>none</p>
                            <span class='analysis_content_head'>Long Description (<span class='long_desc_wc'>0 words</span>):</span>
                            <p class='long_desc_con'>none</p>
                        </div>
                    </div>
                    <div class='grid_seo'>
                        <ul>
                            <li><a href='javascript:void()'>SEO Phrases:</a></li>
                        </ul>
                        <ul class='gr_seo_short_ph' style='margin-top: 5px;'>
                            <li class='bold'>Short Description:</li>
                        </ul>
                        <ul class='gr_seo_long_ph' style='margin-top: 5px;'>
                            <li class='bold'>Long Description:</li>
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
                            <span class='analysis_content_head'>Short Description (<span class='short_desc_wc'>0 words</span>):</span>
                            <p class='short_desc_con'>none</p>
                            <span class='analysis_content_head'>Long Description (<span class='long_desc_wc'>0 words</span>):</span>
                            <p class='long_desc_con'>none</p>
                        </div>
                    </div>
                    <div class='grid_seo'>
                        <ul>
                            <li><a href='javascript:void()'>SEO Phrases:</a></li>
                        </ul>
                        <ul class='gr_seo_short_ph' style='margin-top: 5px;'>
                            <li class='bold'>Short Description:</li>
                        </ul>
                        <ul class='gr_seo_long_ph' style='margin-top: 5px;'>
                            <li class='bold'>Long Description:</li>
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
                            <span class='analysis_content_head'>Short Description (<span class='short_desc_wc'>0 words</span>):</span>
                            <p class='short_desc_con'>none</p>
                            <span class='analysis_content_head'>Long Description (<span class='long_desc_wc'>0 words</span>):</span>
                            <p class='long_desc_con'>none</p>
                        </div>
                    </div>
                    <div class='grid_seo'>
                        <ul>
                            <li><a href='javascript:void()'>SEO Phrases:</a></li>
                        </ul>
                        <ul class='gr_seo_short_ph' style='margin-top: 5px;'>
                            <li class='bold'>Short Description:</li>
                        </ul>
                        <ul class='gr_seo_long_ph' style='margin-top: 5px;'>
                            <li class='bold'>Long Description:</li>
                        </ul>
                        <ul>
                            <li><a href='javascript:void()'>Attributes used (<span class='gr_attr_count'>0</span>):</a></li>
                            <li class='gr_attr_con'>no attributes</li>
                        </ul>
                    </div>
                </div> -->

            </div>
            <!-- GRID VIEW LAYOUT (END) -->

        </div>
        </div>
        <!--- REAL CONTENT SECTION (END) -->

        <script type='text/javascript'>
            // ---- search string cookie (auto mode search launcher) (start)
            var auto_mode_search_str = "";
            var auto_mode_product_batch ="";
            var auto_mode_product_batch_items ="";
            var auto_mode_status_view = "";
            var cookie_search_str = $.cookie('com_intel_search_str');
            var product_batch = $.cookie('product_batch');
            var product_batch_items = $.cookie('product_batch_items');
            var status_view = $.cookie('status_view');
            if (typeof(cookie_search_str) !== 'undefined' && cookie_search_str !== null && cookie_search_str !== "") {
                auto_mode_search_str = cookie_search_str;
            }
            if (typeof(product_batch) !== 'undefined' && product_batch !== null && product_batch !== "") {
                auto_mode_product_batch = product_batch;
            }
            if (typeof(product_batch_items) !== 'undefined' && product_batch_items !== null && product_batch_items !== "") {
                auto_mode_product_batch_items = product_batch_items;
            }
            if (typeof(status_view) !== 'undefined' && status_view !== null && status_view !== "") {
                auto_mode_status_view = status_view;
            }
            if (auto_mode_search_str !== "") {
                $("#compare_text").val(auto_mode_search_str);
                setTimeout(function() {
                    $("#an_search").removeAttr('disabled');
                    startMeasureCompareV2();
                }, 2500);
            }
            if(auto_mode_product_batch!==""){
                $('select#batchess').val(auto_mode_product_batch).prop('selected',true);
                show_from_butches();
            }
            if(auto_mode_product_batch_items!==""){
                $("span.product_batches_items").html(auto_mode_product_batch_items);
            }
            if(auto_mode_status_view!==""){
                if(auto_mode_status_view == 'list'){
                    switchToListView();
                }
                if(auto_mode_status_view == 'table'){
                    switchToTableView();
                }
                if(auto_mode_status_view == 'grid') {
                    switchToGridView();
                }
            }
$('#myModal').modal('hide');
            // ---- search string cookie (auto mode search launcher) (end)
       </script>
</div>
</div>

<!-- MODALS (START) -->
<div class="modal hide fade ci_hp_modals" id='preview_crawl_snap_modal'>
    <div class="modal-body" style='overflow: hidden'>
        <div class='snap_holder'>&nbsp;</div>
    </div>
    <div class="modal-footer">
        <a href="javascript:void(0)" class="btn" data-dismiss="modal">Close</a>
    </div>
</div>
<div id="shadow">
</div>
<select size="10" id="drop_cat" multiple="multiple" style="float:left;margin-top: 5px;">
     <?php

        foreach($site_names_list as $cite){

             ?>
             <option value="<?php echo $cite; ?>"><?php echo $cite; ?></option>
            <?php
        }
     ?>
</select>
<style>
    #shadow {
  width:100%;
  height:100%;
  /*background:black;*/
  position:absolute;
  top:0;
  left:0;
  /*opacity:0.4;
  filter: alpha (apacity=40);*/
  display:none;
 
 }
    #drop_cat {
width:180px;
  height:220px;
  position:absolute;
  top:225px;
  left:828px;
  z-index: 1;
background-repeat:no-repeat;
/*background-position:center center;*/
  display:none;
}
</style>
<!-- MODALS (END) -->
<script>
            $(function() {
                $('head').find('title').text('Competitive Research');
            });

 </script>  
  