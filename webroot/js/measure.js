var grid_id = 0;

var editorGridViewBaseUrl = base_url + 'index.php/measure/gridview';
// ---- search string cookie (auto mode search launcher) (start)
// var auto_mode_search_str = "";
// var cookie_search_str = $.cookie('com_intel_search_str');
// if(typeof(cookie_search_str) !== 'undefined' && cookie_search_str !== null && cookie_search_str !== "") {
//     auto_mode_search_str = cookie_search_str;
// }
// if(auto_mode_search_str !== "") {
//     $("#compare_text").val(auto_mode_search_str);
//     $("#an_search").attr('disabled', true);
//     setTimeout(function() {
//         $("#measureFormMetrics").trigger('submit');
//         $("#an_search").removeAttr('disabled');
//     }, 2500);
// }
// ---- search string cookie (auto mode search launcher) (end)

var measureAnalyzerAttrBaseUrl = base_url + "index.php/measure/attributesmeasure";

// --- GRIDS (START)
var grid_status = 'list';

function startGridsBoxesContentAnalyzer(s) {
    if (s !== "") {
        $(".grid_se_section .c_content").hide();
        $(".preloader_grids_box").show();
        var analyzer_attr = $.post(measureAnalyzerAttrBaseUrl, {s: s}, 'json').done(function(data) {
            var res = {
                'search': [],
                'count': 0
            };
            if (data['search_results'] !== "") {
                var incoming = data['search_results'];
                var sr_stack = incoming.split("<br />");
                // --- map attributes array to clean it up (start)
                sr_stack = $.map(sr_stack, function(val, index) {
                    val = val.replace(/\n/g, "")
                    val = val.replace(/\s+/g, ' ');
                    return val;
                });
                // --- map attributes array to clean it up (end)
                if (sr_stack.length > 0)
                    res.search = sr_stack;
                res.count = sr_stack.length;
            }

            // next analyzer step (using getted attributes) (start)
            console.log("MIDDLEWARE (SELECTED ITEM ATTRIBUTES): ", res);
            // next analyzer step (using getted attributes) (end)

            // output attributes list (rendering) (start)
            $("#grid_se_section_1 .gr_attr_count, #grid_se_section_2 .gr_attr_count, #grid_se_section_3 .gr_attr_count").text(res.count);
            if (res.search.length > 0) {
                var attr_output = "";
                for (var i = 0; i < res.search.length; i++) {
                    attr_output += res.search[i] + "<br/>";
                }
                $("#grid_se_section_1 .gr_attr_con, #grid_se_section_2 .gr_attr_con, #grid_se_section_3 .gr_attr_con").html(attr_output);
            }
            // output attributes list (rendering) (end)

            $(".preloader_grids_box").hide();
            $(".grid_se_section .c_content").show();
        });
    }
}

// function getSearchProductAttributes(s) {
//     if(s !== "") {
//         var analyzer_attr = $.post(measureAnalyzerAttrBaseUrl, { s: s }, 'json').done(function(data) {
//             var res = 'no attributes';
//             var count = 0;
//             if(data['search_results'] !== "") {
//                 res = data['search_results'];
//                 count = res.split("<br />").length;
//             }
//             $("#grid_se_section_1 .gr_attr_count, #grid_se_section_2 .gr_attr_count, #grid_se_section_3 .gr_attr_count").text(count);
//             $("#grid_se_section_1 .gr_attr_con, #grid_se_section_2 .gr_attr_con, #grid_se_section_3 .gr_attr_con").html(res);
//         });
//     }
// }

function viewIconsReset() {
    $('#grid_sw_list, #grid_sw_grid').removeClass('btn-primary');
    $('#grid_sw_list > i').removeClass('icon-white');
    $('#grid_sw_grid > i').removeClass('icon-white');
}

function initGrid() {
    viewIconsReset();
    if (grid_status === 'list') {
        $('#grid_sw_list').addClass('btn-primary');
        $('#grid_sw_list > i').addClass('icon-white');
    } else if (grid_status === 'grid') {
        $('#grid_sw_grid').addClass('btn-primary');
        $('#grid_sw_grid > i').addClass('icon-white');
    }
    $('.grid_switcher').show();
}

function switchToListView() {
    viewIconsReset();
    $('#grid_sw_list').addClass('btn-primary');
    $('#grid_sw_list > i').addClass('icon-white');
    $("#compet_area_grid").empty();
    $("#compet_area_grid").hide();
    $("#attributes_metrics ul").show();
    $("#measure_product_ind_wrap").show();
    $("#an_products_box").removeClass('grid_results_show');
    $(".main span:first-child,#products li span:first-child ").removeClass('new_width');
    grid_status = 'list';

}
//Max
function switchToGridView() {

    viewIconsReset();

    $('#grid_sw_grid').addClass('btn-primary');
    $('#grid_sw_grid > i').addClass('icon-white');
    $("#attributes_metrics ul:not(.grid_switcher)").hide();
    $("#measure_product_ind_wrap").hide();
    // AJAX CALL TO GET GRID VIEW CONTENT (START) (NEW STUFF)
    var im_data_id = $("#an_sort_search_box > #products > li[data-status='selected']").attr('data-value');

    var strict = 0;
    if ($("input[name='strict_grid']:checked").val() !== undefined) {
        strict = 1;
    }

    var grid_view = $.post(editorGridViewBaseUrl, {selectedUrl: $('#products li[data-status=selected] span').eq(1).text(), im_data_id: im_data_id, s_term: $.trim($("#compare_text").val()), strict: strict}, 'html').done(function(data) {
        $("#compet_area_grid").html(data);
        $("#compet_area_grid").show();
        $(".preloader_grids_box").hide();
        $(".grid_se_section .c_content").show();
        fixGridHeights();
        // gridsCustomersListLoader();
    });

    $("#an_products_box").addClass('grid_results_show');
    $(".main span:first-child, #products li span:first-child ").addClass('new_width');

//    #grid_se_section_1 .c .c_content table 
    grid_status = 'grid';

}
//Max
// ------------- !!!! OLD STUFF (START) -------------
// $("#compet_area_grid").show();
// grid_status = 'grid';
// --- DEMO DATA FILL (START)
// var short_desc = $.trim($("#details-short-desc").text());
// var long_desc = $.trim($("#details-long-desc").text());
// var short_desc_count = 0;
// if(short_desc !== "") short_desc_count = short_desc.split(" ").length;
// var long_desc_count = 0;
// if(long_desc !== "") long_desc_count = long_desc.split(" ").length;
// var seo_short = $("ul[data-status='seo_an'][data-st-id='short_desc_seo']").html();
// var seo_long = $("ul[data-status='seo_an'][data-st-id='long_desc_seo']").html();
// $("#grid_se_section_1 .short_desc_wc, #grid_se_section_2 .short_desc_wc, #grid_se_section_3 .short_desc_wc").text(short_desc_count + " words");
// $("#grid_se_section_1 .short_desc_con, #grid_se_section_2 .short_desc_con, #grid_se_section_3 .short_desc_con").text(short_desc);
// $("#grid_se_section_1 .long_desc_wc, #grid_se_section_2 .long_desc_wc, #grid_se_section_3 .long_desc_wc").text(long_desc_count + " words");
// $("#grid_se_section_1 .long_desc_con, #grid_se_section_2 .long_desc_con, #grid_se_section_3 .long_desc_con").text(long_desc);
// $(".gr_seo_short_ph").html(seo_short);
// $(".gr_seo_long_ph").html(seo_long);
// --- DEMO DATA FILL (END)
// $.scrollTo("#compet_area_grid", 400);
// startGridsBoxesContentAnalyzer($.trim($("#compare_text").val()));
// --- TMP (in cause slow files attribtes fetch) (start)
// $(".preloader_grids_box").hide();
// $(".grid_se_section .c_content").show();
// --- TMP (in cause slow files attribtes fetch) (end)
// gridsCustomersListLoader();
// ------------- !!!! OLD STUFF (END) -------------
// --- GRIDS (END)

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
    if ($("#measure_product_ind_wrap").length > 0) {
        mode = true;
    }
    if (mode) {
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
var measureAnalyzerBaseUrl = base_url + "index.php/measure/analyzestring";
var editorSearchBaseUrl = base_url + "index.php/editor/searchmeasuredb";
var keywordsAnalyzerBaseUrl = base_url + "index.php/measure/analyzekeywords";

var editorSearchAllBaseUrl = base_url + "index.php/measure/searchmeasuredball";
function startMeasureCompareV2() {
    // ---- LIMIT DETECTION (START) (OLD)
    // var limit = 0;
    // if($(".ui-autocomplete").is(':visible')) {
    //     limit = $(".ui-autocomplete > li").length;
    // }
    // ---- LIMIT DETECTION (END) (OLD)

    // ---- LIMIT DETECTION (START) (NEW)
    $("#batchess").val("0");//max
    var limit = 20;
    if ($(".typeahead").is(':visible')) {
        limit = $(".typeahead > li").length;
    }
    // ---- LIMIT DETECTION (END) (NEW)

    // $(".ui-autocomplete").hide();
    $(".typeahead").hide();
    var s = $.trim($("#compare_text").val());
    var oDropdown = $("#ci_dropdown").msDropdown().data("dd");
    var sl = $.trim(oDropdown.getData().data.value);
    var cat = $("#cats_an").val();
    // --- record search term to cookie storage (start)
    if (s !== "") {
        var cookie_search_str = $.cookie('com_intel_search_str');
        if (typeof(cookie_search_str) !== 'undefined') {
            $.removeCookie('com_intel_search_str', {path: '/'}); // destroy
            $.cookie('com_intel_search_str', s, {expires: 7, path: '/'}); // re-create
        } else {
            $.cookie('com_intel_search_str', s, {expires: 7, path: '/'}); // create
        }
    }
    // --- record search term to cookie storage (end)
    var searcher_all = $.post(editorSearchAllBaseUrl, {s: s, sl: sl, cat: cat, limit: limit}, 'html').done(function(data) {
        $("#an_products_box").html(data);
        // $("#an_products_box").fadeOut();
        // $("#an_products_box").fadeIn();
        $("#an_products_box").show();
        var w = $('ul#products li:first-child span:first-child').width();
        $('#an_sort_search_box .product_title .main span:first-child').width(w);
        setTimeout(function() {
            // if($(".ui-autocomplete").is(':visible')) $(".ui-autocomplete").hide(); // OLD
            if ($(".typeahead").is(':visible'))
                $(".typeahead").hide(); // NEW
        }, 1000);
    });

    return false;
}
function show_from_butches() {//max
    var batch_id = $("#batchess").val();

    var searcher_all = $.post(editorSearchAllBaseUrl, {batch_id: batch_id}, 'html').done(function(data) {
        $("#an_products_box").html(data);
        // $("#an_products_box").fadeOut();
        // $("#an_products_box").fadeIn();
        $("#an_products_box").show();
        var w = $('ul#products li:first-child span:first-child').width();
        $('#an_sort_search_box .product_title .main span:first-child').width(w);
        setTimeout(function() {
            // if($(".ui-autocomplete").is(':visible')) $(".ui-autocomplete").hide(); // OLD
            if ($(".typeahead").is(':visible'))
                $(".typeahead").hide(); // NEW
        }, 1000);
    });

    return false;

}


//max
function removeTagsFromDescs() {
    var short_str = $("#details-short-desc").text();
    var long_str = $("#details-long-desc").text();
    var short_str_clean = short_str.replace(/<\/?[^>]+(>|$)/g, "");
    var long_str_clean = long_str.replace(/<\/?[^>]+(>|$)/g, "");
    $("#details-short-desc").html(short_str_clean);
    $("#details-long-desc").html(long_str_clean);
}

function removeTagsFromAllGridDescs() {
    var short_str = $("#grid_se_section_1 .short_desc_con").text();
    var long_str = $("#grid_se_section_1 .long_desc_con").text();
    var short_str_clean = short_str.replace(/<\/?[^>]+(>|$)/g, "");
    var long_str_clean = long_str.replace(/<\/?[^>]+(>|$)/g, "");
    $("#grid_se_section_1 .short_desc_con").html(short_str_clean);
    $("#grid_se_section_1 .long_desc_con").html(long_str_clean);

    var short_str = $("#grid_se_section_2 .short_desc_con").text();
    var long_str = $("#grid_se_section_2 .long_desc_con").text();
    var short_str_clean = short_str.replace(/<\/?[^>]+(>|$)/g, "");
    var long_str_clean = long_str.replace(/<\/?[^>]+(>|$)/g, "");
    $("#grid_se_section_2 .short_desc_con").html(short_str_clean);
    $("#grid_se_section_2 .long_desc_con").html(long_str_clean);

    var short_str = $("#grid_se_section_3 .short_desc_con").text();
    var long_str = $("#grid_se_section_3 .long_desc_con").text();
    var short_str_clean = short_str.replace(/<\/?[^>]+(>|$)/g, "");
    var long_str_clean = long_str.replace(/<\/?[^>]+(>|$)/g, "");
    $("#grid_se_section_3 .short_desc_con").html(short_str_clean);
    $("#grid_se_section_3 .long_desc_con").html(long_str_clean);
}

function wordGridModeHighLighter(section, w, status) {
    removeTagsFromAllGridDescs();
    var highlightStartTag = "<span class='hilite'>";
    var highlightEndTag = "</span>";
    var searchTerm = w;
    var bodyText = '';
    if (status === 'short') {
        bodyText = $("#grid_se_" + section + " .short_desc_con").text();
    } else if (status === 'long') {
        bodyText = $("#grid_se_" + section + " .long_desc_con").text();
    }

    var newText = "";
    var i = -1;
    var lcSearchTerm = searchTerm.toLowerCase();
    var lcBodyText = bodyText.toLowerCase();

    while (bodyText.length > 0) {
        i = lcBodyText.indexOf(lcSearchTerm, i + 1);
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

    if (status === 'short') {
        $("#grid_se_" + section + " .short_desc_con").html(newText);
        $.scrollTo("#grid_se_" + section + " .short_desc_con", 400);
    } else if (status === 'long') {
        $("#grid_se_" + section + " .long_desc_con").html(newText);
        $.scrollTo("#grid_se_" + section + " .long_desc_con", 400);
    }
}

// function stackWordsHighLighterMainContent(words, status) {
//     removeTagsFromDescs();
//     var highlightStartTag = "<span class='hilite'>";
//     var highlightEndTag = "</span>";
//     if(words.length > 0) {
//         for(var j=0; j < words.length; j++) {
//             var searchTerm = words[j];
//             var bodyText = '';
//             if(status === 'short') {
//                 bodyText = $("#details-short-desc").text();
//             } else if(status === 'long') {
//                 bodyText = $("#details-long-desc").text();
//             }

//             var newText = "";
//             var i = -1;
//             var lcSearchTerm = searchTerm.toLowerCase();
//             var lcBodyText = bodyText.toLowerCase();

//             while (bodyText.length > 0) {
//                 i = lcBodyText.indexOf(lcSearchTerm, i+1);
//                 if (i < 0) {
//                     newText += bodyText;
//                     bodyText = "";
//                 } else {
//                     if (bodyText.lastIndexOf(">", i) >= bodyText.lastIndexOf("<", i)) {
//                         if (lcBodyText.lastIndexOf("/script>", i) >= lcBodyText.lastIndexOf("<script", i)) {
//                             newText += bodyText.substring(0, i) + highlightStartTag + bodyText.substr(i, searchTerm.length) + highlightEndTag;
//                             bodyText = bodyText.substr(i + searchTerm.length);
//                             lcBodyText = bodyText.toLowerCase();
//                             i = -1;
//                         }
//                     }
//                 }
//             }

//             if(status === 'short') {
//                 bodyText = $("#details-short-desc").html(newText);
//             } else if(status === 'long') {
//                 bodyText = $("#details-long-desc").html(newText);
//             }
//         }
//     }
// }

function stackWordsHighLighterMainContent(words) {
    removeTagsFromDescs();
    var highlightStartTag = "<span class='hilite'>";
    var highlightEndTag = "</span>";
    if (words.length > 0) {
        for (var j = 0; j < words.length; j++) {
            var searchTerm = words[j];
            var bodyText = '';
            bodyText = $("#measure_product_ind_wrap").html();

            var newText = "";
            var i = -1;
            var lcSearchTerm = searchTerm.toLowerCase();
            var lcBodyText = bodyText.toLowerCase();

            while (bodyText.length > 0) {
                i = lcBodyText.indexOf(lcSearchTerm, i + 1);
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

            $("#measure_product_ind_wrap").html(newText);
        }
    }
}

function wordHighLighter(w, status) {
    removeTagsFromDescs();
    var highlightStartTag = "<span class='hilite'>";
    var highlightEndTag = "</span>";
    var searchTerm = w;
    var bodyText = '';
    if (status === 'short') {
        bodyText = $("#details-short-desc").text();
    } else if (status === 'long') {
        bodyText = $("#details-long-desc").text();
    }

    var newText = "";
    var i = -1;
    var lcSearchTerm = searchTerm.toLowerCase();
    var lcBodyText = bodyText.toLowerCase();

    while (bodyText.length > 0) {
        i = lcBodyText.indexOf(lcSearchTerm, i + 1);
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

    if (status === 'short') {
        bodyText = $("#details-short-desc").html(newText);
        $.scrollTo("#details-short-desc", 400);
    } else if (status === 'long') {
        bodyText = $("#details-long-desc").html(newText);
        $.scrollTo("#details-long-desc", 400);
    }
}

$("*").click(function(e) {
    var attr = $(e.target).attr('data-status');
    if (typeof(attr) !== 'undefined' && attr === 'seo_link') {
    } else {
        removeTagsFromDescs();
        if ($("#compet_area_grid .grid_se_section").length > 0) {
            removeTagsFromAllGridDescs();
        }
    }
});

// --- KEYWORDS ANALYZER (START)
function keywordsAnalizer() {
    var primary_ph = $.trim($("#km_primary_edit").val());
    var secondary_ph = $.trim($("#km_secondary_edit").val());
    var tertiary_ph = $.trim($("#km_tertiary_edit").val());
    if (primary_ph !== "")
        primary_ph.replace(/<\/?[^>]+(>|$)/g, "");
    if (secondary_ph !== "")
        secondary_ph.replace(/<\/?[^>]+(>|$)/g, "");
    if (tertiary_ph !== "")
        tertiary_ph.replace(/<\/?[^>]+(>|$)/g, "");

    if (primary_ph !== "" || secondary_ph !== "" || tertiary_ph !== "") {
        var short_desc = $.trim($("#details-short-desc").html());
        var long_desc = $.trim($("#details-long-desc").html());
        if (short_desc !== "")
            short_desc.replace(/<\/?[^>]+(>|$)/g, "");
        if (long_desc !== "")
            long_desc.replace(/<\/?[^>]+(>|$)/g, "");

        var kw_send_object = {
            primary_ph: primary_ph,
            secondary_ph: secondary_ph,
            tertiary_ph: tertiary_ph,
            short_desc: short_desc,
            long_desc: long_desc
        };

        var analyzer_kw = $.post(keywordsAnalyzerBaseUrl, kw_send_object, 'json').done(function(data) {
            var kw_primary_short_res = data['primary'][0].toPrecision(3) * 100;
            var kw_primary_long_res = data['primary'][1].toPrecision(3) * 100;
            $("#kw_primary_short_res").text(kw_primary_short_res.toPrecision(2) + "%");
            $("#kw_primary_long_res").text(kw_primary_long_res.toPrecision(2) + "%");

            var kw_secondary_short_res = data['secondary'][0].toPrecision(3) * 100;
            var kw_secondary_long_res = data['secondary'][1].toPrecision(3) * 100;
            $("#kw_secondary_short_res").text(kw_secondary_short_res.toPrecision(2) + "%");
            $("#kw_secondary_long_res").text(kw_secondary_long_res.toPrecision(2) + "%");

            var kw_tertiary_short_res = data['tertiary'][0].toPrecision(3) * 100;
            var kw_tertiary_long_res = data['tertiary'][1].toPrecision(3) * 100;
            $("#kw_tertiary_short_res").text(kw_tertiary_short_res.toPrecision(2) + "%");
            $("#kw_tertiary_long_res").text(kw_tertiary_long_res.toPrecision(2) + "%");

            // --- figure out highlighter stack (start)
            var hl_stack_short = [];
            var hl_stack_long = [];
            var hl_stack_common = [];
            var tmp = [];
            if (kw_primary_short_res > 0) {
                tmp = primary_ph.split(" ");
                if (tmp.length > 0) {
                    for (var i = 0; i < tmp.length; i++) {
                        hl_stack_common.push(tmp[i]);
                        // hl_stack_short.push(tmp[i]);
                    }
                }
                tmp = [];
            }
            if (kw_primary_long_res > 0) {
                tmp = primary_ph.split(" ");
                if (tmp.length > 0) {
                    for (var i = 0; i < tmp.length; i++) {
                        hl_stack_common.push(tmp[i]);
                        // hl_stack_long.push(tmp[i]);
                    }
                }
                tmp = [];
            }
            if (kw_secondary_short_res > 0) {
                tmp = secondary_ph.split(" ");
                if (tmp.length > 0) {
                    for (var i = 0; i < tmp.length; i++) {
                        hl_stack_common.push(tmp[i]);
                        // hl_stack_short.push(tmp[i]);
                    }
                }
                tmp = [];
            }
            if (kw_secondary_long_res > 0) {
                tmp = secondary_ph.split(" ");
                if (tmp.length > 0) {
                    for (var i = 0; i < tmp.length; i++) {
                        hl_stack_common.push(tmp[i]);
                        // hl_stack_long.push(tmp[i]);
                    }
                }
                tmp = [];
            }
            if (kw_tertiary_short_res > 0) {
                tmp = tertiary_ph.split(" ");
                if (tmp.length > 0) {
                    for (var i = 0; i < tmp.length; i++) {
                        hl_stack_common.push(tmp[i]);
                        // hl_stack_short.push(tmp[i]);
                    }
                }
                tmp = [];
            }
            if (kw_tertiary_long_res > 0) {
                tmp = tertiary_ph.split(" ");
                if (tmp.length > 0) {
                    for (var i = 0; i < tmp.length; i++) {
                        hl_stack_common.push(tmp[i]);
                        // hl_stack_long.push(tmp[i]);
                    }
                }
                tmp = [];
            }
            hl_stack_common = _.uniq(hl_stack_common);
            stackWordsHighLighterMainContent(hl_stack_common);
            // hl_stack_short = _.uniq(hl_stack_short);
            // hl_stack_long = _.uniq(hl_stack_long);
            // stackWordsHighLighterMainContent(hl_stack_short, 'short');
            // stackWordsHighLighterMainContent(hl_stack_long, 'long');
            // --- figure out highlighter stack (end)

            $('.keywords_metrics_bl_res').fadeOut('fast', function() {
                $('.keywords_metrics_bl_res').fadeIn();
            });
        });
    }
}
// --- KEYWORDS ANALYZER (END)

$(document).ready(function() {
    //Max

    $(".mismatch_image").live('click', function() {
        $(this).closest('.grid_se_section').hide();
        var im_data_id = $(this).data('value');
        var aaa = $.post(base_url + 'index.php/measure/report_mismatch', {group_id: group_id, im_data_id: im_data_id}, 'json').done(function(data) {
       
        });
    });

    $("#an_search").live('click', function() {//max
        var dropdown = $("select[name='customers_list']").msDropdown().data("dd");
        dropdown.destroy();
        $('#product_customers .ddcommon').remove();
        $("select[name='customers_list'] option[value='All Customers']").prop('selected', true);

        dropdown = $("select[name='customers_list']").msDropdown().data("dd");
    });
    //Max
    $('title').text("Competitive Intelligence");

    $("#measureFormMetrics").submit(function(e) {
        e.preventDefault();
        startMeasureCompareV2();
    });

    var autocomplete_ci_baseurl = base_url + 'index.php/measure/cisearchteram';
    var gTime, ci_search_name;
    ci_search_name = "";

    $('#compare_text').keyup(function(e) {
        if (e.which == 13) {
            ci_search_name = $("#compare_text").val();
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
            if (typeof(item) === "undefined") {
                return ci_search_name;
            } else {
                return item;
            }
        },
        source: function(query, process) {
            clearTimeout(gTime);
            gTime = setTimeout(function() {
                var xhr;
                if (xhr && xhr.readystate !== 4)
                    xhr.abort();
                xhr = $.ajax({
                    url: autocomplete_ci_baseurl,
                    dataType: "JSON",
                    data: {
                        q: query,
                        sl: $("#ci_dropdown .dd-selected-value").val(),
                        cat: $("#cats_an > option:selected").val()
                    },
                    success: function(response) {
                        if (typeof(response) !== 'undefined' && response !== null) {
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

    $("#batchess").live('change', function() {//max

        $.post(base_url + 'index.php/research/filterCustomerByBatch', {'batch': $("#batchess").val()}, function(data) {
            if (data !='') {

                $("select[name='customers_list'] option").each(function() {

                    if (data == $(this).val()) {
                        var dropdown = $("select[name='customers_list']").msDropdown().data("dd");
                        dropdown.destroy();
                        $('#product_customers .ddcommon').remove();
                        $(this).prop('selected', true);
                        //$("select[name='customers_list']").val($(this).val());
                        dropdown = $("select[name='customers_list']").msDropdown().data("dd");

                    }
                });
            } else {
                $("select[name='customers_list'] option").each(function() {
                    if($(this).val() == 'All Customers'){
                        var dropdown = $("select[name='customers_list']").msDropdown().data("dd");
                        dropdown.destroy();
                        $('#product_customers .ddcommon').remove();
                        $(this).prop('selected', true);
                        dropdown = $("select[name='customers_list']").msDropdown().data("dd");
                    }
                });
            }
        });
        if ($("#batchess").val() !== '0') {
            //alert($("#batchess").val());
            show_from_butches();
        } else {
            $("#measure_product_ind_wrap").html('');
            $("#compet_area_grid").html('');
            $("#an_sort_search_box").html('');
            $(".grid_switcher").hide();
            $(".keywords_metrics_bl_res").hide();
            $('li.keywords_metrics_bl_res, li.keywords_metrics_bl_res ~ li, ul.less_b_margin').hide();
        }

         });

    $('li.temp_li a').live('click', function() {
        $('li.temp_li a').each(function() {
            $(this).css({'text-decoration': 'none'});
        });
        $(this).css({'text-decoration': 'underline'});
        return false;
    });
});//max
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
if (typeof(cookie_search_str) !== 'undefined' && cookie_search_str !== null && cookie_search_str !== "") {
    auto_mode_search_str = cookie_search_str;
}
if (auto_mode_search_str !== "") {
    $("#compare_text").val(auto_mode_search_str);
    setTimeout(function() {
        $("#an_search").removeAttr('disabled');
        startMeasureCompareV2();
    }, 2500);
}
// ---- search string cookie (auto mode search launcher) (end)

Array.max = function(array) {
    return Math.max.apply(Math, array);
};

// Function to get the Min value in Array
Array.min = function(array) {
    return Math.min.apply(Math, array);
};
function fixGridHeights() {
    var selectors = new Array('.p_url', '.p_name', '.p_price', '.p_seo', '.p_description');
    var wrapper = $('.wrapper');
    if (wrapper.length > 0) {
        $.each(wrapper, function(k, v) {
            var thisEl = $(this);
            var section = thisEl.find('.grid_se_section');
            if (section.length > 1) {
                $.each(selectors, function(k1, v1) {
                    var heights = thisEl.find(v1).map(function() {
                        return $(this).height();
                    }).get();
                    thisEl.find(v1).height(Array.max(heights));
                });
            }
        });
    }
}