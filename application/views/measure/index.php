<script>
    
    // ---- METRICS (SEO PHRASES) (START)
    var tmp_dumm = 'Samsung UN40ES6500 40 Class LED 3D HDTV The Samsung UN40ES6500 40 Class LED 3D HDTV Samsung UN40ES6500 40 Class LED 3D HDTV The Samsung UN40ES6500 40 Class LED 3D HDTV';
    var measureAnalyzerBaseUrl = "<?php echo base_url(); ?>index.php/measure/analyzestring";
    var editorSearchBaseUrl = "<?php echo base_url(); ?>index.php/editor/searchmeasuredb";

    function startMeasureCompare() {
        // $("#metrics_seo_phrases").nextAll().remove();
        $("#measure_tab_pr_content_head .item_title b").html('No Title');
        var s = $.trim($("#compare_text").val());
        var searcher = $.post(editorSearchBaseUrl, { s: s }, 'html').done(function(data) {
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
                    var short_desc_an = $("#details-short-desc").html();
                    short_desc_an = short_desc_an.replace(/\s+/g, ' ');
                    short_desc_an = short_desc_an.trim();
                    var analyzer_short = $.post(measureAnalyzerBaseUrl, { clean_t: short_desc_an }, 'json').done(function(a_data) {
                        var seo_items = "<li class='long_desc_sep'>Short Description:</li>";
                        var top_style = "";
                        for(var i in a_data) {
                            if(typeof(a_data[i]) === 'object') {
                                if(i == 0) {
                                    top_style = "style='margin-top: 5px;'";
                                }
                                seo_items += "<li " + top_style + ">" + "<span class='word_wrap_li_pr hover_en'>" + a_data[i]['ph'] + "</span>" + " <span class='word_wrap_li_sec'>(" + a_data[i]['count'] + ")</span></li>";
                            }
                        }
                        // $(seo_items).insertAfter($("#metrics_seo_phrases"));
                        $("ul[data-st-id='short_desc_seo']").html(seo_items);
                    });
                    // --- SHORT DESC ANALYZER (END)

                    // --- LONG DESC ANALYZER (START)
                    var long_desc_an = $("#details-long-desc").html();
                    long_desc_an = long_desc_an.replace(/\s+/g, ' ');
                    long_desc_an = long_desc_an.trim();
                    var analyzer_long = $.post(measureAnalyzerBaseUrl, { clean_t: long_desc_an }, 'json').done(function(a_data) {
                        var seo_items = "<li class='long_desc_sep'>Long Description:</li>";
                        var top_style = "";
                        for(var i in a_data) {
                            if(typeof(a_data[i]) === 'object') {
                                if(i == 0) {
                                    top_style = "style='margin-top: 5px;'";
                                }
                                seo_items += "<li " + top_style + ">" + "<span class='word_wrap_li_pr hover_en'>" + a_data[i]['ph'] + "</span>" + " <span class='word_wrap_li_sec'>(" + a_data[i]['count'] + ")</span></li>";
                            }
                        }
                        // $(seo_items).insertAfter($("#metrics_seo_phrases"));
                        $("ul[data-st-id='long_desc_seo']").html(seo_items);
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

    // ---- METRICS (SEO PHRASES) (END)
    $(document).ready(function () {
        var ddData_first = [
            {
                text: "",
                value: "Walmart.com",
                description: "",
                imageSrc: "<?php echo base_url(); ?>img/walmart-logo.png"
            },
            {
                text: "",
                value: "Sears.com",
                description: "",
                imageSrc: "<?php echo base_url(); ?>img/sears-logo.png"
            },
            {
                text: "",
                value: "TigerDirect.com",
                description: "",
                imageSrc: "<?php echo base_url(); ?>img/tigerdirect-logo.png"
            },
        ];
        $('#measure_dropdown').ddslick({
            data: ddData_first,
            defaultSelectedIndex: 0
        });
    });
</script>
<div class="main_content_other"></div>
<div class="main_content_editor">
<div class="row-fluid">
    <?php echo form_open('', array('id'=>'measureFormMetrics')); ?>
        <!-- <input type="text" name="compare_text" value="UN40ES6500" id="compare_text" class="span8" placeholder=""/> -->
        <input type="text" name="compare_text" value="UN40ES6500" id="compare_text" class="span8" placeholder=""/>
        <div id="measure_dropdown" class="dropdowns"></div>
        <button type="submit" onclick="return startMeasureCompare()" class="btn pull-right">Search</button>
    <?php echo form_close();?>
</div>

<!--- REAL CONTENT SECTION (START) -->
<div id="measure_tab_pr_content">
    <div id="measure_tab_pr_content_head" class="row-fluid mt_10">
        <div class="span8 item_title"><b class='btag_elipsis'>No Title</b></div>
    </div>
	<div class="row-fluid">            
       <div class="span8 search_area uneditable-input cursor_default item_section">
            <div id='measure_tab_pr_content_body' class="item_section_content" >
                
            </div>
        </div>
        <div class="span3" style="width: 290px; margin-left: 5px; margin-top: -45px;" id="attributes_metrics">
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
                <li data-status='words_an'><a href='javascript:void(0)'>Words Analysis:</a></li>
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

