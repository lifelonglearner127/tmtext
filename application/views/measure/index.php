<script>
    
    $("#compare_text").focus();

    // ---- METRICS (SEO PHRASES) (START)

    var measureAnalyzerBaseUrl = "<?php echo base_url(); ?>index.php/measure/analyzestring";
    var editorSearchBaseUrl = "<?php echo base_url(); ?>index.php/editor/searchmeasuredb";
    var customersListBaseUrl = "<?php echo base_url(); ?>index.php/measure/getcustomerslist";

    function startMeasureCompare() {
        $("#measure_tab_pr_content_head .item_title b").html('No Title');
        var s = $.trim($("#compare_text").val());
        var sl = $.trim($(".dd-selected-value").val());
        var searcher = $.post(editorSearchBaseUrl, { s: s, sl: sl }, 'html').done(function(data) {
            if(typeof(data) !== "undefined" && data !== "") {
                $("#measure_tab_pr_content_body").html(data);
                var ms = $(data).find("#measure_res_status").val();

                if(ms === 'db') {

                    var title_dom = $(data).find("#link_m_title").val();
                    var url_dom = $(data).find("#link_m_url").val();
                    if(typeof(title_dom) !== 'undefined' && title_dom !== "") {
                        var title_section = title_dom;
                        if(typeof(url_dom) !== 'undefined' && url_dom !== "") {
                            title_section = "<a href='" + url_dom + "'>" + title_dom + "</a>";
                        }
                        $("#measure_tab_pr_content_head .item_title b").html(title_section);
                    }

                    // --- SHORT DESC ANALYZER (START)
                    var short_status = 'short';
                    var short_desc_an = $("#details-short-desc").html();
                    short_desc_an = short_desc_an.replace(/\s+/g, ' ');
                    short_desc_an = short_desc_an.trim();
                    var analyzer_short = $.post(measureAnalyzerBaseUrl, { clean_t: short_desc_an }, 'json').done(function(a_data) {
                        var seo_items = "<li class='long_desc_sep'>Short Description:</li>";
                        var top_style = "";
                        var s_counter = 0;
                        for(var i in a_data) {
                            if(typeof(a_data[i]) === 'object') {
                                s_counter++;
                                if(i == 0) {
                                    top_style = "style='margin-top: 5px;'";
                                }
                                seo_items += '<li ' + top_style + '>' + '<span data-status="seo_link" onclick="wordHighLighter(\''+a_data[i]['ph']+'\', \''+short_status+'\');" class="word_wrap_li_pr hover_en">' + a_data[i]['ph'] + '</span>' + ' <span class="word_wrap_li_sec">(' + a_data[i]['count'] + ')</span></li>';
                            }
                        }
                        if(s_counter > 0) $("ul[data-st-id='short_desc_seo']").html(seo_items);
                    });
                    // --- SHORT DESC ANALYZER (END)

                    // --- LONG DESC ANALYZER (START)
                    var long_status = 'long';
                    var long_desc_an = $("#details-long-desc").html();
                    long_desc_an = long_desc_an.replace(/\s+/g, ' ');
                    long_desc_an = long_desc_an.trim();
                    var analyzer_long = $.post(measureAnalyzerBaseUrl, { clean_t: long_desc_an }, 'json').done(function(a_data) {
                        var seo_items = "<li class='long_desc_sep'>Long Description:</li>";
                        var top_style = "";
                        var l_counter = 0;
                        for(var i in a_data) {
                            if(typeof(a_data[i]) === 'object') {
                                l_counter++;
                                if(i == 0) {
                                    top_style = "style='margin-top: 5px;'";
                                }
                                seo_items += '<li ' + top_style + '>' + '<span data-status="seo_link" onclick="wordHighLighter(\''+a_data[i]['ph']+'\', \''+long_status+'\');" class="word_wrap_li_pr hover_en">' + a_data[i]['ph'] + '</span>' + ' <span class="word_wrap_li_sec">(' + a_data[i]['count'] + ')</span></li>';
                                // seo_items += '<li ' + top_style + '>' + '<span data-status="seo_link" data-status-sv="long"  class="word_wrap_li_pr hover_en">' + a_data[i]['ph'] + '</span>' + ' <span class="word_wrap_li_sec">(' + a_data[i]['count'] + ')</span></li>';
                            }
                        }
                        if(l_counter > 0) $("ul[data-st-id='long_desc_seo']").html(seo_items);
                    });
                    // --- LONG DESC ANALYZER (END)

                    $("ul[data-status='seo_an']").fadeOut();
                    $("ul[data-status='seo_an']").fadeIn();

                    // ---- WORDS COUNTER (START)
                    var short_words_text = $.trim($("#details-short-desc").text());
                    var short_words_arr = short_words_text.split(" ");
                    var short_words_count = short_words_arr.length;
                    var long_words_text = $.trim($("#details-long-desc").text());
                    var long_words_arr = long_words_text.split(" ");
                    var long_words_count = long_words_arr.length;
                    var words_total = short_words_count + long_words_count;
                    $("li[data-status='words_an'] > span[data-st-id='short_desc']").text(short_words_count + " words");
                    $("li[data-status='words_an'] > span[data-st-id='long_desc']").text(long_words_count + " words");
                    $("li[data-status='words_an'] > span[data-st-id='total']").text(words_total + " words");
                    $("li[data-status='words_an']").fadeOut();
                    $("li[data-status='words_an']").fadeIn();
                    // ---- WORDS COUNTER (END)

                }

            }
        });
        
        return false;
        
    }

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


    // ---- METRICS (SEO PHRASES) (END)
    $(document).ready(function () {

        var customers_list = $.post(customersListBaseUrl, { }, 'json').done(function(c_data) {
            var cl_arr = [];
            var ddData_second = [];
            cl_arr.push("All Sites");
            for(i in c_data) {
                cl_arr.push(c_data[i]);
            }
            for (var i = 0; i < cl_arr.length; i++) {
                if(i == 0) {
                    var mid = {
                        text: cl_arr[i],
                        value: "all",
                        description: ""
                    };    
                } else {
                    var text_d = cl_arr[i];
                    var value_d = cl_arr[i];
                    var imageSrc_d = "";
                    if(cl_arr[i] == 'bjs.com') {
                        text_d = "";
                        imageSrc_d = "<?php echo base_url(); ?>img/bjs-logo.gif";
                    } else if(cl_arr[i] == 'sears.com') {
                        text_d = "";
                        imageSrc_d = "<?php echo base_url(); ?>img/sears-logo.png";
                    } else if(cl_arr[i] == 'walmart.com') {
                        text_d = "";
                        imageSrc_d = "<?php echo base_url(); ?>img/walmart-logo.png";
                    } else if(cl_arr[i] == 'staples.com') {
                        text_d = "";
                        imageSrc_d = "<?php echo base_url(); ?>img/staples-logo.png";
                    } else if(cl_arr[i] == 'overstock.com') {
                        text_d = "";
                        imageSrc_d = "<?php echo base_url(); ?>img/overstock-logo.png";
                    } else if(cl_arr[i] == 'tigerdirect.com') {
                        text_d = "";
                        imageSrc_d = "<?php echo base_url(); ?>img/tigerdirect-logo.png";
                    }

                    var mid = {
                        text: text_d,
                        value: value_d,
                        description: "",
                        imageSrc: imageSrc_d
                    };
                }
                ddData_second.push(mid);
            };
            $('#measure_dropdown').ddslick({
                data: ddData_second,
                width: 104,
                defaultSelectedIndex: 0
            });
        });

    });
</script>
<div class="main_content_other"></div>
<div class="main_content_editor">
<div class="row-fluid">
    <?php echo form_open('', array('id'=>'measureFormMetrics')); ?>
        <input type="text" name="compare_text" value="" id="compare_text" class="span8" placeholder=""/>
        <div id="measure_dropdown" class="dropdowns"></div>
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
        <button type="submit" onclick="return startMeasureCompare()" class="btn pull-right">Search</button>
    <?php echo form_close();?>
</div>

<!--- REAL CONTENT SECTION (START) -->
<div id="measure_tab_pr_content">
    <div id="measure_tab_pr_content_head" class="row-fluid mt_10">
        <div class="span8 item_title an_sv_left"><b class='btag_elipsis'>No Title</b></div>
    </div>
	<div class="row-fluid">            
       <div class="span8 search_area uneditable-input cursor_default item_section an_sv_left">
            <div id='measure_tab_pr_content_body' class="item_section_content" >
                
            </div>
        </div> 
        <div class="span3 an_sv_right" id="attributes_metrics">
            <h3>Metrics</h3>
            <ul>
                <li><a href="javascript:void(0)">Site Metrics</a></li>
                <li>Alexa: 156</li>
                <li>SKUs: 1,278,400</li>
                <li>&nbsp;</li>
                <li><a href="javascript:void(0)">Page Metrics</a></li>
                <li>SKU: KDL-55EX640</li>
                <li>&nbsp;</li>
                <li><a href="javascript:void(0)">Keywords Metrics</a></li>
                <li class='keywords_metrics_bl'>
                    <span>Primary:</span><textarea id="km_primary_edit" disabled='true'>X% Y%</textarea>
                </li>
                <li class='keywords_metrics_bl'>
                    <span>Secondary:</span><textarea id="km_secondary_edit" disabled='true'>X% Y%</textarea>
                </li>
                <li class='keywords_metrics_bl'>
                    <span>Tertiary:</span><textarea id="km_tertiary_edit" disabled='true'>X% Y%</textarea>
                </li>
                <li class='keywords_metrics_bl'><button type='button' class='btn btn-primary'>Update</button></li>
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
</div>
</div>
<!--- REAL CONTENT SECTION (END) -->

