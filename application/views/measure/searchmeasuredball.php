<?php if(count($search_results) > 0) { ?>

	<script type='text/javascript'>
		$(document).ready(function () {

			$("#an_products_box").sortable({
	            connectWith: ".connectedSortable"
	        });
	        $(document).on("click", '#products li', function() {
	        	$("#products li").each(function(){
                    $(this).css({'background':'none'});
                    $(this).attr('data-status', 'standart');
                });
                $(this).css({'background':'#CAEAFF'});
                $(this).attr('data-status', 'selected');
                // ---- START DISTINCT PRODUCT METRICS (START)
                var im_data_id = $(this).attr('data-value');
                startMeasureCompare(im_data_id);
                // ---- START DISTINCT PRODUCT METRICS (END)
        	});
        	setTimeout(function() {
        		$('#products li:eq(0)').trigger('click');
        	}, 500);


        	function startMeasureCompare(im_data_id) {
		        var searcher = $.post(editorSearchBaseUrl, { im_data_id: im_data_id, search_data: $.trim($("#compare_text").val()) }, 'html').done(function(data) {
		            if(typeof(data) !== "undefined" && data !== "") {
		                $("#measure_tab_pr_content_body").html(data);
		                var ms = $(data).find("#measure_res_status").val();
		                if(ms === 'db') {
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

		                    keywordsAnalizer();

		                    initGrid();

		                    if(grid_status === 'list') {
		                    	switchToListView();
		                    } else if(grid_status === 'grid') {
		                    	switchToGridView();
		                    }

		                }

		            }
		        });
		    }

            // click on table row for expand or shrink
            $("#products span").click(function() {
                if($(this).css('white-space') == 'normal') {
                    $(this).parent().find('span').css('white-space', 'nowrap');
                } else {
                    $(this).parent().find('span').css('white-space', 'normal');
                }
            });
		});
	</script>

	<div id='an_sort_search_box' class='boxes_content' style='margin-bottom: 15px;'>
		<ul class='product_title'>
			<li class='main'>
				<span><b>Product Name</b></span>
				<span><b>URL</b></span>
			</li>
		</ul>
		<ul id="products" class='products_an_search'>
			<?php foreach($search_results as $k => $v) { ?>
				<li data-status='standart' data-value="<?php echo $v['imported_data_id']; ?>">
					<span><?php echo $v['product_name']; ?></span>
					<span><?php echo $v['url']; ?></span>
				</li>
			<?php } ?>
		</ul>
	</div>

<?php } else { ?>
	<p>search results are empty</p>
<?php } ?>