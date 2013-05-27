<script>
    
    // ---- METRICS (SEO PHRASES) (START)
    var tmp_dumm = 'Samsung UN40ES6500 40 Class LED 3D HDTV The Samsung UN40ES6500 40 Class LED 3D HDTV Samsung UN40ES6500 40 Class LED 3D HDTV The Samsung UN40ES6500 40 Class LED 3D HDTV';
    var measureAnalyzerBaseUrl = "<?php echo base_url(); ?>index.php/measure/analyzestring";
    var editorSearchBaseUrl = "<?php echo base_url(); ?>index.php/editor/searchmeasuredb";

    function startMeasureCompare() {
        $("#metrics_seo_phrases").nextAll().remove();
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

                    // --- LONG DESC ANALYZER
                    var long_desc_an = $("#details-long-desc").html();
                    long_desc_an = long_desc_an.replace(/\s+/g, ' ');
                    long_desc_an = long_desc_an.trim();
                    var analyzer_long = $.post(measureAnalyzerBaseUrl, { clean_t: long_desc_an }, 'json').done(function(a_data) {
                        var seo_items = "<li class='long_desc_sep'>Long Description:</li>";
                        var top_style = "";
                        for(var i in a_data) {
                            if(i == 0) {
                                top_style = "style='margin-top: 5px;'";
                            }
                            seo_items += "<li class='word_wrap_li' " + top_style + ">" + a_data[i]['ph'] + " (" + a_data[i]['count'] + ")</li>";
                        }
                        $(seo_items).insertAfter($("#metrics_seo_phrases"));
                    });

                    // --- SHORT DESC ANALYZER
                    var short_desc_an = $("#details-short-desc").html();
                    short_desc_an = short_desc_an.replace(/\s+/g, ' ');
                    short_desc_an = short_desc_an.trim();
                    var analyzer_short = $.post(measureAnalyzerBaseUrl, { clean_t: short_desc_an }, 'json').done(function(a_data) {
                        var seo_items = "<li class='long_desc_sep'>Short Description:</li>";
                        var top_style = "";
                        for(var i in a_data) {
                            if(i == 0) {
                                top_style = "style='margin-top: 5px;'";
                            }
                            seo_items += "<li class='word_wrap_li' " + top_style + ">" + a_data[i]['ph'] + " (" + a_data[i]['count'] + ")</li>";
                        }
                        $(seo_items).insertAfter($("#metrics_seo_phrases"));
                    });

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
    <?php echo form_open('', array('id'=>'measureForm')); ?>
        <!-- <input type="text" name="compare_text" value="UN40ES6500" id="compare_text" class="span8" placeholder=""/> -->
        <input type="text" name="compare_text" value="Samsung" id="compare_text" class="span8" placeholder=""/>
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
       <div class="span9 search_area uneditable-input cursor_default item_section">
            <div id='measure_tab_pr_content_body' class="item_section_content" >
                
            </div>
        </div>
        <div class="span3" style="width:195px; margin-top: -45px;" id="attributes_metrics">
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
                    <span>Primary:</span><textarea id="km_primary_edit"></textarea>
                </li>
                <li class='keywords_metrics_bl'>
                    <span>Secondary:</span><textarea id="km_secondary_edit"></textarea>
                </li>
                <li class='keywords_metrics_bl'>
                    <span>Tertiary:</span><textarea id="km_tertiary_edit"></textarea>
                </li>
                <li class='keywords_metrics_bl'><button type='button' class='btn btn-primary'>Update</button></li>
                <li>&nbsp;</li>
                <!-- <li id="metrics_seo_phrases"><a href='javascript:void(0)'>SEO Phrases</a>&nbsp;<button type='button' onclick="phrasesAnalysis()" class='btn btn-primary btn-small'>re-start</button></li> -->
                <li id="metrics_seo_phrases"><a href='javascript:void(0)'>SEO Phrases</a></li>
                <li>&nbsp;</li>
            </ul>
	    </div>
	</div>
</div>
</div>
<!--- REAL CONTENT SECTION (END) -->

