<script>
    
    var measureAnalyzerAttrBaseUrl = "<?php echo base_url(); ?>index.php/measure/attributesmeasure";

    // --- GRIDS (START)
    var grid_status = 'list';

    function getSearchProductAttributes(s) {
        if(s !== "") {
            var analyzer_attr = $.post(measureAnalyzerAttrBaseUrl, { s: s }, 'json').done(function(data) {
                console.log('Attributes: ', data['search_results']);
                var res = 'no attributes';
                var count = 0;
                if(data['search_results'] !== "") {
                    res = data['search_results'];
                    count = res.split("<br />").length;
                }
                $("#grid_se_section_1 .gr_attr_count, #grid_se_section_2 .gr_attr_count, #grid_se_section_3 .gr_attr_count").text(count);
                $("#grid_se_section_1 .gr_attr_con, #grid_se_section_2 .gr_attr_con, #grid_se_section_3 .gr_attr_con").html(res);
            });
        }
    }

    function viewIconsReset() {
        $('#grid_sw_list, #grid_sw_grid').removeClass('btn-primary');
        $('#grid_sw_list > i').removeClass('icon-white');
        $('#grid_sw_grid > i').removeClass('icon-white');
    }
    function initGrid() {
        viewIconsReset();
        if(grid_status === 'list') {
            $('#grid_sw_list').addClass('btn-primary');
            $('#grid_sw_list > i').addClass('icon-white');
        } else if(grid_status === 'grid') {
            $('#grid_sw_grid').addClass('btn-primary');
            $('#grid_sw_grid > i').addClass('icon-white');
        }
        $('.grid_switcher').show();
    }

    function switchToListView() {
        viewIconsReset();
        $('#grid_sw_list').addClass('btn-primary');
        $('#grid_sw_list > i').addClass('icon-white');
        $("#compet_area_grid").hide();
        $("#attributes_metrics ul:not(.grid_switcher)").show();
        $("#measure_product_ind_wrap").show();
        grid_status = 'list';
    }

    function switchToGridView() {
        viewIconsReset();
        $('#grid_sw_grid').addClass('btn-primary');
        $('#grid_sw_grid > i').addClass('icon-white');
        $("#attributes_metrics ul:not(.grid_switcher)").hide();
        $("#measure_product_ind_wrap").hide();
        $("#compet_area_grid").show();
        grid_status = 'grid';
        // --- DEMO DATA FILL (START)
        var short_desc = $.trim($("#details-short-desc").text());
        var long_desc = $.trim($("#details-long-desc").text());
        var short_desc_count = 0;
        if(short_desc !== "") short_desc_count = short_desc.split(" ").length;
        var long_desc_count = 0;
        if(long_desc !== "") long_desc_count = long_desc.split(" ").length;
        var seo_short = $("ul[data-status='seo_an'][data-st-id='short_desc_seo']").html();
        var seo_long = $("ul[data-status='seo_an'][data-st-id='long_desc_seo']").html();
        $("#grid_se_section_1 .short_desc_wc, #grid_se_section_2 .short_desc_wc, #grid_se_section_3 .short_desc_wc").text(short_desc_count + " words");
        $("#grid_se_section_1 .short_desc_con, #grid_se_section_2 .short_desc_con, #grid_se_section_3 .short_desc_con").text(short_desc);
        $("#grid_se_section_1 .long_desc_wc, #grid_se_section_2 .long_desc_wc, #grid_se_section_3 .long_desc_wc").text(long_desc_count + " words");
        $("#grid_se_section_1 .long_desc_con, #grid_se_section_2 .long_desc_con, #grid_se_section_3 .long_desc_con").text(short_desc);
        $(".gr_seo_short_ph").html(seo_short);
        $(".gr_seo_long_ph").html(seo_long);
        getSearchProductAttributes($.trim($("#compare_text").val()));
        // --- DEMO DATA FILL (END)
    }
    // --- GRIDS (END)

    $("#compare_text").focus();

    // --- SCROLL UP / DOWN DETECTION (START)
    // if ($(window).scrollTop() == $(document).height() - $(window).height()) { alert('top re'); }
    // if (($(window).scrollTop()+document.body.clientHeight)==$(window).height()) { alert('bottom re'); }
    var mousewheelevt;
    mousewheelevt = (/Firefox/i.test(navigator.userAgent) ? "DOMMouseScroll" : "mousewheel");
    $("body").bind(mousewheelevt, function(e) {
        var delta, evt;
        evt = window.event || e;
        evt = (evt.originalEvent ? evt.originalEvent : evt);
        delta = (evt.detail ? evt.detail * (-40) : evt.wheelDelta);
        var mode = false;
        if($("#measure_product_ind_wrap").length > 0) {
            mode = true;
        }
        if(mode) {
            var step = 10;
            var current_margin = $("#measure_product_ind_wrap").css('margin-top');
            current_margin = parseInt(current_margin.substr(0, current_margin.length - 2));
            if (delta > 0) { // --- SCROLL UP EVENT
                // if ($(window).scrollTop() == $(document).height() - $(window).height()) {  
                //     $("#measure_product_ind_wrap").css('margin-top', '0px');
                // } else {
                //     if(current_margin > 0) {
                //         var new_margin = current_margin - step;
                //         $("#measure_product_ind_wrap").css('margin-top', new_margin + 'px');
                //     }
                // }
            } else { // --- SCROLL DOWN EVENT
                // if (($(window).scrollTop()+document.body.clientHeight)==$(window).height()) {} else {
                //     var new_margin = current_margin + step;
                //     $("#measure_product_ind_wrap").css('margin-top', new_margin + 'px');
                // }
            }
        }
    });

    // ---- METRICS (SEO PHRASES) (START)
    var measureAnalyzerBaseUrl = "<?php echo base_url(); ?>index.php/measure/analyzestring";
    var editorSearchBaseUrl = "<?php echo base_url(); ?>index.php/editor/searchmeasuredb";
    var keywordsAnalyzerBaseUrl = "<?php echo base_url(); ?>index.php/measure/analyzekeywords";
    
    var editorSearchAllBaseUrl = "<?php echo base_url(); ?>index.php/measure/searchmeasuredball";
    function startMeasureCompareV2() {
        var s = $.trim($("#compare_text").val());
        var sl = $.trim($(".dd-selected-value").val());
        var cat = $("#cats_an").val();
        var searcher_all = $.post(editorSearchAllBaseUrl, { s: s, sl: sl, cat: cat }, 'html').done(function(data) {
            $("#an_products_box").html(data);
            $("#an_products_box").fadeOut();
            $("#an_products_box").fadeIn();
        });
        initGrid();
        switchToListView();
        return false;
    }

    // function startMeasureCompare() {
    //     $("#measure_tab_pr_content_head .item_title b").html('No Title');
    //     var s = $.trim($("#compare_text").val());
    //     var sl = $.trim($(".dd-selected-value").val());
    //     var searcher = $.post(editorSearchBaseUrl, { s: s, sl: sl }, 'html').done(function(data) {
    //         if(typeof(data) !== "undefined" && data !== "") {
    //             $("#measure_tab_pr_content_body").html(data);
    //             var ms = $(data).find("#measure_res_status").val();

    //             if(ms === 'db') {

    //                 var title_dom = $(data).find("#link_m_title").val();
    //                 var url_dom = $(data).find("#link_m_url").val();
    //                 if(typeof(title_dom) !== 'undefined' && title_dom !== "") {
    //                     var title_section = title_dom;
    //                     if(typeof(url_dom) !== 'undefined' && url_dom !== "") {
    //                         title_section = "<a href='" + url_dom + "'>" + title_dom + "</a>";
    //                     }
    //                     $("#measure_tab_pr_content_head .item_title b").html(title_section);
    //                 }

    //                 // --- SHORT DESC ANALYZER (START)
    //                 var short_status = 'short';
    //                 var short_desc_an = $("#details-short-desc").html();
    //                 short_desc_an = short_desc_an.replace(/\s+/g, ' ');
    //                 short_desc_an = short_desc_an.trim();
    //                 var analyzer_short = $.post(measureAnalyzerBaseUrl, { clean_t: short_desc_an }, 'json').done(function(a_data) {
    //                     var seo_items = "<li class='long_desc_sep'>Short Description:</li>";
    //                     var top_style = "";
    //                     var s_counter = 0;
    //                     for(var i in a_data) {
    //                         if(typeof(a_data[i]) === 'object') {
    //                             s_counter++;
    //                             if(i == 0) {
    //                                 top_style = "style='margin-top: 5px;'";
    //                             }
    //                             seo_items += '<li ' + top_style + '>' + '<span data-status="seo_link" onclick="wordHighLighter(\''+a_data[i]['ph']+'\', \''+short_status+'\');" class="word_wrap_li_pr hover_en">' + a_data[i]['ph'] + '</span>' + ' <span class="word_wrap_li_sec">(' + a_data[i]['count'] + ')</span></li>';
    //                         }
    //                     }
    //                     if(s_counter > 0) $("ul[data-st-id='short_desc_seo']").html(seo_items);
    //                 });
    //                 // --- SHORT DESC ANALYZER (END)

    //                 // --- LONG DESC ANALYZER (START)
    //                 var long_status = 'long';
    //                 var long_desc_an = $("#details-long-desc").html();
    //                 long_desc_an = long_desc_an.replace(/\s+/g, ' ');
    //                 long_desc_an = long_desc_an.trim();
    //                 var analyzer_long = $.post(measureAnalyzerBaseUrl, { clean_t: long_desc_an }, 'json').done(function(a_data) {
    //                     var seo_items = "<li class='long_desc_sep'>Long Description:</li>";
    //                     var top_style = "";
    //                     var l_counter = 0;
    //                     for(var i in a_data) {
    //                         if(typeof(a_data[i]) === 'object') {
    //                             l_counter++;
    //                             if(i == 0) {
    //                                 top_style = "style='margin-top: 5px;'";
    //                             }
    //                             seo_items += '<li ' + top_style + '>' + '<span data-status="seo_link" onclick="wordHighLighter(\''+a_data[i]['ph']+'\', \''+long_status+'\');" class="word_wrap_li_pr hover_en">' + a_data[i]['ph'] + '</span>' + ' <span class="word_wrap_li_sec">(' + a_data[i]['count'] + ')</span></li>';
    //                             // seo_items += '<li ' + top_style + '>' + '<span data-status="seo_link" data-status-sv="long"  class="word_wrap_li_pr hover_en">' + a_data[i]['ph'] + '</span>' + ' <span class="word_wrap_li_sec">(' + a_data[i]['count'] + ')</span></li>';
    //                         }
    //                     }
    //                     if(l_counter > 0) $("ul[data-st-id='long_desc_seo']").html(seo_items);
    //                 });
    //                 // --- LONG DESC ANALYZER (END)

    //                 $("ul[data-status='seo_an']").fadeOut();
    //                 $("ul[data-status='seo_an']").fadeIn();

    //                 // ---- WORDS COUNTER (START)
    //                 var short_words_text = $.trim($("#details-short-desc").text());
    //                 var short_words_arr = short_words_text.split(" ");
    //                 var short_words_count = short_words_arr.length;
    //                 var long_words_text = $.trim($("#details-long-desc").text());
    //                 var long_words_arr = long_words_text.split(" ");
    //                 var long_words_count = long_words_arr.length;
    //                 var words_total = short_words_count + long_words_count;
    //                 $("li[data-status='words_an'] > span[data-st-id='short_desc']").text(short_words_count + " words");
    //                 $("li[data-status='words_an'] > span[data-st-id='long_desc']").text(long_words_count + " words");
    //                 $("li[data-status='words_an'] > span[data-st-id='total']").text(words_total + " words");
    //                 $("li[data-status='words_an']").fadeOut();
    //                 $("li[data-status='words_an']").fadeIn();
    //                 // ---- WORDS COUNTER (END)

    //             }

    //         }
    //     });
        
    //     return false;
        
    // }

    function removeTagsFromDescs() {
        var short_str = $("#details-short-desc").text();
        var long_str = $("#details-long-desc").text();
        var short_str_clean = short_str.replace(/<\/?[^>]+(>|$)/g, "");
        var long_str_clean = long_str.replace(/<\/?[^>]+(>|$)/g, "");
        $("#details-short-desc").html(short_str_clean);
        $("#details-long-desc").html(long_str_clean);
    }

    function wordHighLighter(w, status) {
        removeTagsFromDescs();
        var highlightStartTag = "<span class='hilite'>";
        var highlightEndTag = "</span>";
        var searchTerm = w;
        var bodyText = '';
        if(status === 'short') {
            bodyText = $("#details-short-desc").text();
        } else if(status === 'long') {
            bodyText = $("#details-long-desc").text();
        }

        var newText = "";
        var i = -1;
        var lcSearchTerm = searchTerm.toLowerCase();
        var lcBodyText = bodyText.toLowerCase();

        while (bodyText.length > 0) {
            i = lcBodyText.indexOf(lcSearchTerm, i+1);
            if (i < 0) {
              newText += bodyText;
              bodyText = "";
            } else {
              if (bodyText.lastIndexOf(">", i) >= bodyText.lastIndexOf("<", i)) {
                if (lcBodyText.lastIndexOf("/script>", i) >= lcBodyText.lastIndexOf("<script", i)) {
                  newText += bodyText.substring(0, i) + highlightStartTag + bodyText.substr(i, searchTerm.length) + highlightEndTag;
                  bodyText = bodyText.substr(i + searchTerm.length);
                  lcBodyText = bodyText.toLowerCase();
                  i = -1;
                }
              }
            }
        }

        if(status === 'short') {
            bodyText = $("#details-short-desc").html(newText);
            $.scrollTo("#details-short-desc", 400);
        } else if(status === 'long') {
            bodyText = $("#details-long-desc").html(newText);
            $.scrollTo("#details-long-desc", 400);
        }  
    }

    $("*").click(function(e) {
        var attr = $(e.target).attr('data-status');
        if(typeof(attr) !== 'undefined' && attr === 'seo_link') {} else { removeTagsFromDescs(); }
    });

    // --- KEYWORDS ANALYZER (START)
    function keywordsAnalizer() {
        var primary_ph = $.trim($("#km_primary_edit").val());
        var secondary_ph = $.trim($("#km_secondary_edit").val());
        var tertiary_ph = $.trim($("#km_tertiary_edit").val());
        if(primary_ph !== "") primary_ph.replace(/<\/?[^>]+(>|$)/g, "");
        if(secondary_ph !== "") secondary_ph.replace(/<\/?[^>]+(>|$)/g, "");
        if(tertiary_ph !== "") tertiary_ph.replace(/<\/?[^>]+(>|$)/g, "");

        if(primary_ph !== "" || secondary_ph !== "" || tertiary_ph !== "") {
            var short_desc = $.trim($("#details-short-desc").html());
            var long_desc = $.trim($("#details-long-desc").html());
            if(short_desc !== "") short_desc.replace(/<\/?[^>]+(>|$)/g, "");
            if(long_desc !== "") long_desc.replace(/<\/?[^>]+(>|$)/g, "");

            var kw_send_object = {
                primary_ph: primary_ph,
                secondary_ph: secondary_ph,
                tertiary_ph: tertiary_ph,
                short_desc: short_desc,
                long_desc: long_desc
            };

            var analyzer_kw = $.post(keywordsAnalyzerBaseUrl, kw_send_object, 'json').done(function(data) {
                $("#kw_primary_short_res").text(data['primary'][0].toPrecision(3) + "%");
                $("#kw_primary_long_res").text(data['primary'][1].toPrecision(3) + "%");

                $("#kw_secondary_short_res").text(data['secondary'][0].toPrecision(3) + "%");
                $("#kw_secondary_long_res").text(data['secondary'][1].toPrecision(3) + "%");

                $("#kw_tertiary_short_res").text(data['tertiary'][0].toPrecision(3) + "%");
                $("#kw_tertiary_long_res").text(data['tertiary'][1].toPrecision(3) + "%");

                $('.keywords_metrics_bl_res').fadeOut('fast', function() {
                    $('.keywords_metrics_bl_res').fadeIn();
                });
            });
        }
    }   
    // --- KEYWORDS ANALYZER (END)

</script>
<div class="main_content_other"></div>
<div class="main_content_editor">
<div class="row-fluid">
    <?php // echo form_open('', array('id'=>'measureFormMetrics')); ?>
    <form id="measureFormMetrics" accept-charset="utf-8" method="post" action="javascript:void()">
    <input type="text" name="compare_text" value="" id="compare_text" class="span8" placeholder=""/>
    <div id="measure_dropdown" class="ddslick_dropdown dropdowns"></div>
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
        <button type="submit" id="an_search" disabled='true' onclick="return startMeasureCompareV2()" class="btn pull-right">Search</button>
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
       <div style='margin-top: -40px; height: auto;' class="span8 search_area cursor_default an_sv_left">
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
                <li>Alexa: 156</li>
                <li>SKUs: 1,278,400</li>
                <li>&nbsp;</li>
                <li><a href="javascript:void(0)">Page Metrics</a></li>
                <li>SKU: KDL-55EX640</li>
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
        
        <div id='grid_se_section_1' class='grid_se_section'>
            <div class='h'>
                <select>
                    <?php if(count($customers_list) > 0) { ?>
                        <?php foreach ($customers_list as $key => $value) { ?>
                            <?php if($value == 'walmart.com') { $selected = 'selected'; } else { $selected = ''; } ?>
                            <option <?php echo $selected; ?> value="<?php echo $value; ?>"><?php echo $value; ?></option>
                        <?php } ?>
                    <?php } else { ?>
                    <option value='all'>All Sites</option>
                    <?php } ?>
                </select>
            </div>
            <div class='c'>
                <span class='analysis_content_head'>Short Description (<span class='short_desc_wc'>0 words</span>):</span>
                <p class='short_desc_con'>none</p>
                <span class='analysis_content_head'>Long Description (<span class='long_desc_wc'>0 words</span>):</span>
                <p class='long_desc_con'>none</p>
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
                <select>
                    <?php if(count($customers_list) > 0) { ?>
                        <?php foreach ($customers_list as $key => $value) { ?>
                            <?php if($value == 'staples.com') { $selected = 'selected'; } else { $selected = ''; } ?>
                            <option <?php echo $selected; ?> value="<?php echo $value; ?>"><?php echo $value; ?></option>
                        <?php } ?>
                    <?php } else { ?>
                    <option value='all'>All Sites</option>
                    <?php } ?>
                </select>
            </div>
            <div class='c'>
                <span class='analysis_content_head'>Short Description (<span class='short_desc_wc'>0 words</span>):</span>
                <p class='short_desc_con'>none</p>
                <span class='analysis_content_head'>Long Description (<span class='long_desc_wc'>0 words</span>):</span>
                <p class='long_desc_con'>none</p>
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
                <select>
                    <?php if(count($customers_list) > 0) { ?>
                        <?php foreach ($customers_list as $key => $value) { ?>
                            <?php if($value == 'overstock.com') { $selected = 'selected'; } else { $selected = ''; } ?>
                            <option <?php echo $selected; ?> value="<?php echo $value; ?>"><?php echo $value; ?></option>
                        <?php } ?>
                    <?php } else { ?>
                    <option value='all'>All Sites</option>
                    <?php } ?>
                </select>
            </div>
            <div class='c'>
                <span class='analysis_content_head'>Short Description (<span class='short_desc_wc'>0 words</span>):</span>
                <p class='short_desc_con'>none</p>
                <span class='analysis_content_head'>Long Description (<span class='long_desc_wc'>0 words</span>):</span>
                <p class='long_desc_con'>none</p>
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

    </div>
    <!-- GRID VIEW LAYOUT (END) -->

</div>
</div>
<!--- REAL CONTENT SECTION (END) -->

