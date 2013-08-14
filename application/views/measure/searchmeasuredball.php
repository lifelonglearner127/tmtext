<?php if (count($search_results) > 0) { ?>

    <script type='text/javascript'>

        var alldata =<?php echo json_encode($search_results); ?>;

        $(document).ready(function() {
           selectedCustomer();  
            setTimeout(function() {
                   $('#products li:eq(0)').trigger('click');
                   
            }, 500);
            
    
            $(document).click(function(e) {
                if ($(e.target).hasClass('products_an_search') || $(e.target).parents('.products_an_search').length > 0) {
                $('select').blur();        
            $('.products_an_search').addClass('active');
                } else {
                    $('.products_an_search').removeClass('active');
                }
            });

            $(document).keydown(function(e) {
                var linesCount = $('#products li').length;
                var currentLine = $('#products li[data-status=selected]').index();

                if (e.keyCode == 38) {
                    if (currentLine > 0 && $('.products_an_search').hasClass('active')) {
                        e.preventDefault();
                        var currentElem = $('#products li').eq(currentLine - 1);

                        $('#products li').attr('data-status', 'standart').css({
                            'background-color': '#fff',
                            'background-image': 'none',
                            'background-position': 'initial initial',
                            'background-repeat': 'initial initial'
                        });
                        $('#products li span').css('white-space', 'nowrap');
                        currentElem.attr('data-status', 'selected').css({
                            'background-color': 'rgb(202, 234, 255)',
                            'background-position': 'initial initial',
                            'background-repeat': 'initial initial'
                        });
                        currentElem.find('span').css('white-space', 'normal');
                        var im_data_id = currentElem.attr('data-value');
                        startMeasureCompare(im_data_id);

                        var lineTop = currentElem.offset().top;
                        var blockTop = $('.products_an_search').offset().top;
                        var scrollPos = lineTop - blockTop;
                        $('.products_an_search').scrollTop((currentLine - 1)*23);

                    }
                }
                if (e.keyCode == 40) {
                    if (currentLine < linesCount - 1 && $('.products_an_search').hasClass('active')) {
                        e.preventDefault();
                        var currentElem = $('#products li').eq(currentLine + 1);

                        $('#products li').attr('data-status', 'standart').css({
                            'background-color': '#fff',
                            'background-image': 'none',
                            'background-position': 'initial initial',
                            'background-repeat': 'initial initial'
                        });
                        $('#products li span').css('white-space', 'nowrap');
                        currentElem.attr('data-status', 'selected').css({
                            'background-color': 'rgb(202, 234, 255)',
                            'background-position': 'initial initial',
                            'background-repeat': 'initial initial'
                        });
                        currentElem.find('span').css('white-space', 'normal');
                        var im_data_id = currentElem.attr('data-value');

                        startMeasureCompare(im_data_id);
                        
                        var lineTop = currentElem.height();
                        var blockTop = $('.products_an_search').offset().top;
                        var scrollPos = lineTop - blockTop;
                        $('.products_an_search').scrollTop((currentLine + 1)*23);
                        //console.log(lineTop +'-'+ blockTop +'-'+ scrollPos);
                    }
                }
            });

            $("#an_products_box").sortable({
                connectWith: ".connectedSortable"
            });
            $(document).on("click", '#products li', function() {
                $("#products li").each(function() {
                    $(this).css({'background': 'none'});
                    $(this).attr('data-status', 'standart');
                });
                 $("#products li span").each(function() {
                    $(this).css('white-space', 'nowrap');
                   
                });
                
                $(this).css({'background': '#CAEAFF'});
                $(this).attr('data-status', 'selected');
                $(this).find('span').css('white-space', 'normal');
                // ---- START DISTINCT PRODUCT METRICS (START)
                var im_data_id = $(this).attr('data-value');

                startMeasureCompare(im_data_id);
                var ci_product_item_view = $.cookie('ci_product_item_view');
                if (typeof(ci_product_item_view) !== 'undefined') {
                    $.removeCookie('ci_product_item_view', {path: '/'}); // destroy
                    $.cookie('ci_product_item_view', im_data_id , {expires: 7, path: '/'}); // re-create
                } else {
                    $.cookie('ci_product_item_view', im_data_id, {expires: 7, path: '/'}); // create
                }

                //Max
                // ---- START DISTINCT PRODUCT METRICS (END)
            });
            //max

            function startMeasureCompare(im_data_id) {
                var searcher = $.post(editorSearchBaseUrl, {im_data_id: im_data_id, search_data: $.trim($("#compare_text").val())}, 'html').done(function(data) {
                    if (typeof(data) !== "undefined" && data !== "") {
                        $("#measure_tab_pr_content_body").html(data);
                        var ms = $(data).find("#measure_res_status").val();
                        if (ms === 'db') {
                            // --- SHORT DESC ANALYZER (START)
                            var short_status = 'short';
                            var short_desc_an = $("#details-short-desc").html();
                            short_desc_an = short_desc_an.replace(/\s+/g, ' ');
                            short_desc_an = short_desc_an.trim();
                            var analyzer_short = $.post(measureAnalyzerBaseUrl, {clean_t: short_desc_an}, 'json').done(function(a_data) {
                                var seo_items = "<li class='long_desc_sep'>Short Description:</li>";
                                var top_style = "";
                                var s_counter = 0;
                                for (var i in a_data) {
                                    if (typeof(a_data[i]) === 'object') {
                                        s_counter++;
                                        if (i == 0) {
                                            top_style = "style='margin-top: 5px;'";
                                        }
                                        seo_items += '<li ' + top_style + '>' + '<span data-status="seo_link" onclick="wordHighLighter(\'' + a_data[i]['ph'] + '\', \'' + short_status + '\');" class="word_wrap_li_pr hover_en">' + a_data[i]['ph'] + '</span>' + ' <span class="word_wrap_li_sec">(' + a_data[i]['count'] + ')</span></li>';
                                    }
                                }
                                if (s_counter > 0)
                                    $("ul[data-st-id='short_desc_seo']").html(seo_items);
                            });
                            // --- SHORT DESC ANALYZER (END)

                            // --- LONG DESC ANALYZER (START)
                            var long_status = 'long';
                            var long_desc_an = $("#details-long-desc").html();
                            long_desc_an = long_desc_an.replace(/\s+/g, ' ');
                            long_desc_an = long_desc_an.trim();
                            var analyzer_long = $.post(measureAnalyzerBaseUrl, {clean_t: long_desc_an}, 'json').done(function(a_data) {
                                var seo_items = "<li class='long_desc_sep'>Long Description:</li>";
                                var top_style = "";
                                var l_counter = 0;
                                for (var i in a_data) {
                                    if (typeof(a_data[i]) === 'object') {
                                        l_counter++;
                                        if (i == 0) {
                                            top_style = "style='margin-top: 5px;'";
                                        }
                                        seo_items += '<li ' + top_style + '>' + '<span data-status="seo_link" onclick="wordHighLighter(\'' + a_data[i]['ph'] + '\', \'' + long_status + '\');" class="word_wrap_li_pr hover_en">' + a_data[i]['ph'] + '</span>' + ' <span class="word_wrap_li_sec">(' + a_data[i]['count'] + ')</span></li>';
                                    }
                                }
                                if (l_counter > 0)
                                    $("ul[data-st-id='long_desc_seo']").html(seo_items);
                            });
                            // --- LONG DESC ANALYZER (END)

                            // $("ul[data-status='seo_an']").fadeOut();
                            // $("ul[data-status='seo_an']").fadeIn();
                            $("ul[data-status='seo_an']").show();

                            // ---- WORDS COUNTER (START)
                            var short_words_text = $.trim($("#details-short-desc").text());
                            var short_words_arr = short_words_text.split(" ");
                            //Max
                            var short_words_count = 0;
                            var long_words_count = 0;
                            if (short_words_arr[0] != '') {

                                short_words_count = short_words_arr.length;

                            }
                            var long_words_text = $.trim($("#details-long-desc").text());
                            var long_words_arr = long_words_text.split(" ");
                            if (long_words_arr[0] != '') {
                                long_words_count = long_words_arr.length;

                            }
                            var words_total = short_words_count + long_words_count;
                            if (short_words_count > 0) {
                                $("li[data-status='words_an'] > span[data-st-id='short_desc']").text(short_words_count + " words");
                            } else {
                                $("li[data-status='words_an'] > span[data-st-id='short_desc']").text('none');
                            }
                            if (long_words_count > 0) {
                                $("li[data-status='words_an'] > span[data-st-id='long_desc']").text(long_words_count + " words");
                            } else {
                                $("li[data-status='words_an'] > span[data-st-id='long_desc']").text('none');
                            }
                            //Max  
                            $("li[data-status='words_an'] > span[data-st-id='total']").text(words_total + " words");
                            // $("li[data-status='words_an']").fadeOut();
                            // $("li[data-status='words_an']").fadeIn();
                            $("li[data-status='words_an']").show();
                            // ---- WORDS COUNTER (END)

                            keywordsAnalizer();

                            initGrid();

                            if (grid_status === 'list') {
                                switchToListView();
                            }
                            if(grid_status === 'table'){
                                 switchToTableView();
                            }
                            if (grid_status === 'grid') {
                                switchToGridView();
                            }

                        }

                    }
                });
            }

            // click on table row for expand or shrink
            $("#products span").click(function() {
                if ($(this).css('white-space') == 'normal') {
                    $(this).parent().find('span').css('white-space', 'nowrap');
                } else {
                    $(this).parent().find('span').css('white-space', 'normal');
                }
                var im_data_id = $(this).parent().attr('data-value');
                var ci_product_item_view = $.cookie('ci_product_item_view');
                if (typeof(ci_product_item_view) !== 'undefined') {
                    $.removeCookie('ci_product_item_view', {path: '/'}); // destroy
                    $.cookie('ci_product_item_view', im_data_id , {expires: 7, path: '/'}); // re-create
                } else {
                    $.cookie('ci_product_item_view', im_data_id, {expires: 7, path: '/'}); // create
                }
            });

            var auto_mode_item_view = "";
            var product_item_view = $.cookie('ci_product_item_view');

            if (typeof(product_item_view) !== 'undefined' && product_item_view !== null && product_item_view !== "") {
                auto_mode_item_view = product_item_view ;
            }
            setTimeout(function() {
                if(auto_mode_item_view!==""){
//                    $("#products li").each(function() {
//                        $(this).css({'background': 'none'});
//                        $(this).attr('data-status', 'standart');
//                    });
//                    $("#products li").each(function() {
//                        if($(this).attr('data-value')==auto_mode_item_view) {
//                            $(this).css({'background': '#CAEAFF'});
//                            $(this).attr('data-status', 'selected');
//                            startMeasureCompare(auto_mode_item_view);
//                        }
//                    });
                } else {
                    $('#products li:eq(0)').trigger('click');
                }
            }, 500);
        });
    </script>
    <!--//Max-->
    <div id='an_sort_search_box' class='boxes_content' style='margin-top: -20px;'>
        <ul class='product_title'>
            <li class='main'>
                <span><b>Product Name</b></span>
                <span><b>URL</b></span>
            </li>
        </ul>
        <ul id="products" class='products_an_search'>

            <?php foreach ($search_results as $k => $v) { ?>
                <li data-status='standart' data-value="<?php echo $v['imported_data_id']; ?>">
                    <span><?php echo $v['product_name']; ?></span>
                    <span><?php echo $v['url']; ?></span>
                </li>
            <?php } ?>
        </ul>
    </div>

<?php } else { ?>

    <div id='an_sort_search_box' class='boxes_content' style='margin-bottom: 15px;'>
        <p id="search-result_" class="ml_10">search results are empty</p>
    </div>
    <script>
        $("#measure_product_ind_wrap").html('');
        $("#compet_area_grid").html('');
        $(".grid_switcher").hide();
        $(".keywords_metrics_bl_res").hide();
        $('li.keywords_metrics_bl_res, li.keywords_metrics_bl_res ~ li, ul.less_b_margin').hide();

    </script>
<?php } ?>