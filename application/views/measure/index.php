<div class="main_content_other"></div>
<div class="main_content_editor">
<div class="row-fluid">
    <?php // echo form_open('', array('id'=>'measureFormMetrics')); ?>
    <form id="measureFormMetrics" accept-charset="utf-8" method="post" action="javascript:void(0)">
    <input type="text" name="compare_text" value="" id="compare_text" class="span8" placeholder="" autocomplete="off"/>
    <!-- <div id="measure_dropdown" class="ddslick_dropdown dropdowns"></div> -->
    <div id="ci_dropdown" class="ddslick_dropdown"></div>
        <select class='cats_an_select' id='cats_an' name='cats_an'>
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
        </select>
        <button type="submit" id="an_search" disabled='true' onclick="return startMeasureCompareV2()" class="btn btn-success pull-right">Search</button>
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
	<div id='compet_area_list' class="row-fluid">            
       <!-- <div style='margin-top: -40px;' class="span8 search_area cursor_default item_section an_sv_left"> -->
       <div style='margin-top: -40px; margin-left: -10px; height: auto;' class="span8 search_area cursor_default an_sv_left">
            <div id="an_products_box" style='display: none;' class="span8 an_sv_left connectedSortable">&nbsp;</div>
            <div id='measure_tab_pr_content_body' class="item_section_content">&nbsp;</div>
        </div> 
        <div class="span3 an_sv_right" id="attributes_metrics">
            <ul class='grid_switcher' data-status='grid-switch'>
                <li>
                    <h3>View:</h3n>
                    <button class='btn' onclick="switchToListView();" id='grid_sw_list' type='button'><i class="icon-th-list"></i>&nbsp;List</button>
                    <button class='btn' onclick="switchToGridView();" id='grid_sw_grid' type='button'><i class="icon-th-large"></i>&nbsp;Grid</button>
                </li>
            </ul>
            <!-- <h3>Metrics</h3> -->
            <ul>
                <li><h3>Metrics</h3></li>
                <li><a href="javascript:void(0)">Site Metrics</a></li>
                <li>Alexa: &nbsp;</li>
                <li>SKUs: &nbsp;</li>
                <li>&nbsp;</li>
                <li><a href="javascript:void(0)">Page Metrics</a></li>
                <li>SKU: &nbsp;</li>
                <li>&nbsp;</li>
                <li style='margin-bottom: 5px;'><a href="javascript:void(0)">Keyword Metrics</a></li>
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
  
    // ---- new CI term typeahead (start) (NEW)
    $(document).ready(function() {
      
      var autocomplete_ci_baseurl = base_url + 'index.php/measure/cisearchteram';
      var gTime, ci_search_name;
      ci_search_name = "";
      
      $("#compare_text").keyup(function(e) {
        if (e.which === 13) ci_search_name = $("#compare_text").val();
      });

      $('#compare_text').keyup(function(e) {
          ci_search_name = $("#compare_text").val();
          if(e.which == 13) {
            setTimeout(function() {
              $("#measureFormMetrics").submit();
            }, 1000);
          }

      });

      $("#compare_text").typeahead({
        items: 4,
        minLength: 3,
        matcher: function() {
          return true;
        },
        updater: function(item) {
          if(typeof(item) === "undefined") {
            return ci_search_name; 
          } else {
            return item;
          }
        },
        source: function(query, process) {
          clearTimeout(gTime);
          gTime = setTimeout(function() {
            var xhr;
            if (xhr && xhr.readystate !== 4) xhr.abort();
            xhr = $.ajax({
              url: autocomplete_ci_baseurl,
              dataType: "JSON",
              data: {
                q: query,
                sl: $("#ci_dropdown .dd-selected-value").val(),
                cat: $("#cats_an > option:selected").val()
              },
              success: function(response) {
                if(typeof(response) !== 'undefined' && response !== null) {
                  var labelsTitles;
                  labelsTitles = [];
                  $.each(response, function(i, item) {
                    labelsTitles.push(item.value);
                  });
                  process(_.uniq(labelsTitles));
                }
              }
            });
          }, 300);
        }
      });

    });
    // ---- new CI term typeahead (end) (NEW)

    // --- CI search term autocomplete (start) (OLD)
    // setTimeout(function() {
    //     var autocomplete_ci_baseurl = base_url + 'index.php/measure/cisearchteram';
    //     $("#compare_text").autocomplete({
    //         source: autocomplete_ci_baseurl + "?sl=" + $("#ci_dropdown .dd-selected-value").val() + "&cat=" +  $("#cats_an > option:selected").val(),
    //         minChars: 3,
    //         deferRequestBy: 300,
    //         select: function(event, ui) { 
    //             startMeasureCompareV2();
    //         }
    //     });
    // }, 1000);
    // --- CI search term autocomplete (end) (OLD)

    // ---- search string cookie (auto mode search launcher) (start)
    var auto_mode_search_str = "";
    var cookie_search_str = $.cookie('com_intel_search_str');
    if(typeof(cookie_search_str) !== 'undefined' && cookie_search_str !== null && cookie_search_str !== "") {
        auto_mode_search_str = cookie_search_str;
    }
    if(auto_mode_search_str !== "") {
        $("#compare_text").val(auto_mode_search_str);
        setTimeout(function() {
            $("#an_search").removeAttr('disabled');
            startMeasureCompareV2();
        }, 2500);
    }
    // ---- search string cookie (auto mode search launcher) (end)

</script>

