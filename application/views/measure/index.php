<script>
    
    // ---- METRICS (SEO PHRASES) (START)
    var tmp_dumm = 'Samsung UN40ES6500 40 Class LED 3D HDTV The Samsung UN40ES6500 40 Class LED 3D HDTV Samsung UN40ES6500 40 Class LED 3D HDTV The Samsung UN40ES6500 40 Class LED 3D HDTV';
    var measureAnalyzerBaseUrl = "<?php echo base_url(); ?>index.php/measure/analyzestring";
    var editorSearchBaseUrl = "<?php echo base_url(); ?>index.php/editor/searchmeasure";

    // function phrasesAnalysis() {
    //     var s = $.trim($("#search").val());
    //     var searcher = $.post(editorSearchBaseUrl, { s: s }, 'html').done(function(data) {
    //         if(typeof(data) !== "undefined" && data !== "") {
    //             var title_dom = $(data).find("#link_m_title");
    //             var title = "No Title";
    //             if(title_dom.length > 0) {
    //                 title = $(title_dom[0]).text();
    //             }
    //             var str = $(data).html();
    //             str = str.replace(/\s+/g, ' ');
    //             str = str.trim();
    //             $("#measure_tab_pr_content_body").html(data);
    //             $("#measure_tab_pr_content_head .item_title b").text(title);
    //             // ---- fill up DOM (end)
    //             var analyzer = $.post(measureAnalyzerBaseUrl, { clean_t: str }, 'json').done(function(a_data) {
    //                 $("#metrics_seo_phrases").nextAll().remove(); // --- clean up previous seo phrases
    //                 // --- collect and insert incoming seo phrases (start)
    //                 var seo_items = "";
    //                 if(a_data.length > 0) {
    //                     var top_style = "";
    //                     for(var i = 0; i < a_data.length; i++) {
    //                         if(i == 0) {
    //                             top_style = "style='margin-top: 5px;'";
    //                         }
    //                         seo_items += "<li class='word_wrap_li' " + top_style + ">" + a_data[i]['ph'] + " (" + a_data[i]['count'] + ")</li>";
    //                     }
    //                 }
    //                 $(seo_items).insertAfter($("#metrics_seo_phrases"));
    //                 // --- collect and insert incoming seo phrases (end)
    //             });
    //         }
    //     });
    // }

    // setTimeout(phrasesAnalysis, 1000);

    function startMeasureCompare() {
        var s = $.trim($("#compare_text").val());
        var searcher = $.post(editorSearchBaseUrl, { s: s }, 'html').done(function(data) {
            if(typeof(data) !== "undefined" && data !== "") {
                var title_dom = $(data).find("#link_m_title");
                var title = "No Title";
                if(title_dom.length > 0) {
                    title = $(title_dom[0]).text();
                }
                var str = $(data).html();
                str = str.replace(/\s+/g, ' ');
                str = str.trim();
                $("#measure_tab_pr_content_body").html(data);
                $("#measure_tab_pr_content_head .item_title b").text(title);
                // ---- fill up DOM (end)
                var analyzer = $.post(measureAnalyzerBaseUrl, { clean_t: tmp_dumm }, 'json').done(function(a_data) {
                    $("#metrics_seo_phrases").nextAll().remove(); // --- clean up previous seo phrases
                    // --- collect and insert incoming seo phrases (start)
                    var seo_items = "";
                    if(a_data.length > 0) {
                        var top_style = "";
                        for(var i = 0; i < a_data.length; i++) {
                            if(i == 0) {
                                top_style = "style='margin-top: 5px;'";
                            }
                            seo_items += "<li class='word_wrap_li' " + top_style + ">" + a_data[i]['ph'] + " (" + a_data[i]['count'] + ")</li>";
                        }
                    }
                    $(seo_items).insertAfter($("#metrics_seo_phrases"));
                    // --- collect and insert incoming seo phrases (end)
                });
            }
        });
    }

    // ---- METRICS (SEO PHRASES) (END)

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

    $(document).ready(function () {
        $('#websites_first').ddslick({
            data: ddData_first,
            defaultSelectedIndex: 0
        });
    });
</script>
<div class="main_content_other"></div>
<div class="main_content_editor">
<div class="row-fluid">
    <?php echo form_open('', array('id'=>'measureForm')); ?>
        <input type="text" name="compare_text" value="UN40ES6500" id="compare_text" class="span11" placeholder=""/>
        <button type="button" onclick="startMeasureCompare()" class="btn pull-right">Search</button>
    <?php echo form_close();?>
</div>
<div class="row-fluid">
    <div id="websites_first" class="dropdowns"></div>
</div>

<!--- REAL CONTENT SECTION (START) -->
<div id="measure_tab_pr_content">
    <div id="measure_tab_pr_content_head" class="row-fluid mt_10">
        <div class="span9 item_title"><b class='btag_elipsis'>No Title</b></div>
    </div>
	<div class="row-fluid">            
       <div id="measure_tab_pr_content_body" class="span9 search_area uneditable-input cursor_default item_section">
            <div class="item_section_content" >
                <div class='item_body'>
                    <div>
                        <span class="ql-details-short-desc">No description</span>
                    </div>
                </div>
                <!-- <div class="item_body">
                    <div>
                        <span class="ql-details-short-desc">
                        Enter a world of dazzling picture quality and unlimited entertainment. This elegantly slim LED TV boasts Full HD 1080p for incredible detail and Edge LED backlighting for boosted contrast. Internet connectivity is at your fingertips, so you can watch YouTube clips and access online HD movies, music and more.<br><br><b>Note:</b> You must have a source of HD programming in order to take full advantage of the Sony 55" HDTV. Contact your local cable or satellite TV provider for details on how to upgrade.
                        </span>
                    </div>
                    <div>
                        <br><b>Sony 55" Class LED 1080p 60Hz HDTV, KDL-55EX640:</b><ul><li>55" LCD panel<br>With a 1920 x 1080 Full HD resolution</li><li>True 16:9 aspect ratio<br>View your movies as the director intended</li><li>Wide 178-degree vertical and 178-degree horizontal angles<br>See a clear picture from anywhere in the room</li><li>Built-in digital tuner<br>Watch digital broadcasts, including HDTV programs where available</li><li>HDMI Inputs: 4<br>Enjoy a superior HD experience with HDMI one cable solution</li><li>54.6" screen measured diagonally from corner to corner</li><li>WiFi adaptor included<br>Connect your HDTV to the Internet and stream videos</li><li>BRAVIA Sync<br>Sync up all Sony devices</li><li>Wall mountable<br>VESA standard 300mm x 300mm</li></ul><br><b>ENERGY STAR<sup>&reg;</sup></b><br>Products that are ENERGY STAR-qualified prevent greenhouse gas emissions by meeting strict energy efficiency guidelines set by the U.S. Environmental Protection Agency and the U.S. Department of Energy. The ENERGY STAR name and marks are registered marks owned by the U.S. government, as part of their energy efficiency and environmental activities.
                    </div>
                </div>
                <div class="ProdQuestions prtHid" id="hideProductQuesLink">Do you have questions about this product? <a onclick="s_objectID=&quot;http://www.walmart.com/ip/Sony-55-Class-LED-1080p-60Hz-HDTV-2-3-8-ultra-slim-KDL-55EX640/20593825_36&quot;;return this.s_oc?this.s_oc(e):true" href="#Q%26A+Exchange">Ask a question</a>.</div> -->
            </div>
        </div>
        <div class="span3" style="width:195px; margin-top: -80px;" id="attributes_metrics">
            <h3>Metrics</h3>
            <ul>
                <li><a href="#">Site Metrics</a></li>
                <li>Alexa: 156</li>
                <li>SKUs: 1,278,400</li>
                <li>&nbsp;</li>
                <li><a href="#">Page Metrics</a></li>
                <li>SKU: KDL-55EX640</li>
                <li>&nbsp;</li>
                <li id="metrics_seo_phrases"><a href='javascript:void(0)'>SEO Phrases</a>&nbsp;<button type='button' onclick="phrasesAnalysis()" class='btn btn-primary btn-small'>re-start</button></li>
                <li>&nbsp;</li>
            </ul>
	    </div>
	</div>
</div>
</div>
<!--- REAL CONTENT SECTION (END) -->

