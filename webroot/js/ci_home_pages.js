function openScreensModalSlider() {
	$('#screens_slider').anythingSlider({
	    theme: 'default',
	    mode: 'horizontal',
	    expand: false,
	    resizeContents: true,
	    showMultiple: false,
	    easing: "swing",
	    buildArrows: true,
	    buildNavigation: true,
	    buildStartStop: true,
	    appendFowardTo: null,
	    appendBackTo: null,
	    appendControlsTo: null,
	    appendNavigationTo: null,
	    appendStartStopTo: null,
	    toggleArrows: false,
	    toggleControls: false,
	    startText: "Start",
	    stopText: "Stop",
	    forwardText: "&raquo;",
	    backText: "&laquo;",
	    tooltipClass: 'tooltip',
	    enableArrows: true,
	    enableNavigation: true,
	    enableStartStop: true,
	    enableKeyboard: true,
	    startPanel: 1,
	    changeBy: 1,
	    hashTags: true,
	    infiniteSlides: true,
	    navigationFormatter: function(index, panel) {
	        return "" + index;
	    },
	    navigationSize: false,
	    autoPlay: true,
	    autoPlayLocked: false,
	    autoPlayDelayed: false,
	    pauseOnHover: false,
	    stopAtEnd: false,
	    playRtl: false,
	    delay: 3000,
	    resumeDelay: 15000,
	    animationTime: 600,
	    delayBeforeAnimate  : 0,
	    onBeforeInitialize: function(e, slider) {},
	    onInitialized: function(e, slider) {},
	    onShowStart: function(e, slider) {},
	    onShowStop: function(e, slider) {},
	    onShowPause: function(e, slider) {},
	    onShowUnpause: function(e, slider) {},
	    onSlideInit: function(e, slider) {},
	    onSlideBegin: function(e, slider) {},
	    onSlideComplete: function(slider) {},
	    onSliderResize: function(e, slider) {},
	    clickForwardArrow: "click",
	    clickBackArrow: "click",
	    clickControls: "click focusin",
	    clickSlideshow: "click",
	    resumeOnVideoEnd: true,
	    resumeOnVisible: true,
	    addWmodeToObject: "opaque",
	    isVideoPlaying: function(base) {
	        return false;
	    }
	});
	$("#screens_modal_slider").modal('show');
}

function startAllCrawl() {
	$("#customers_screens_crawl_modal").modal('hide');
	$("#loading_crawl_modal").modal('show');
	var start_site_crawl = $.post(base_url + 'index.php/measure/webshootcrawlall', {}, function(data) {
		$("#loading_crawl_modal").modal('hide');
		console.log(data);
	});
}

function openCrawlLaunchPanelModal() {
	$("#customers_screens_crawl_modal").modal('show');
}

function removeCrawlSiteFromList(id) {
	$("#cl_cp_tbl_crawls tr[data-id='" + id + "']").remove();
	if($("#cl_cp_tbl_crawls tr").length == 1) {
		$("#cl_cp_crawl_modal").html("<p>No available sites for crawl</p>");
		$("#crawl_modal_sbm_btn").addClass("disabled");
		$("#crawl_modal_sbm_btn").attr("disabled", true);
		$("#crawl_modal_sbm_btn").attr("onclick", "return false");
	}
}

function openCrawlLaunchPanelModal(close_preview) {
	// if(close_preview) {
	// 	$("#preview_screenshot_modal").modal('hide');
	// }
	$("#customers_screens_crawl_modal").modal('show');
	var customers_list = $.post(base_url + 'index.php/measure/getcustomerslist_crawl', {}, function(c_data) {
		var tbl = "";
		tbl += "<table id='cl_cp_tbl_crawls' class='table table-striped'>";
			tbl += "<thead>";
				tbl += "<tr>";
					tbl += "<th>Sites</th>";
					tbl += "<th>Controls</th>";
				tbl += "</tr>";
			tbl += "</thead>";
			tbl += "<tbody>";
			for (var i = 0; i < c_data.length; i++) {
				tbl += "<tr data-id='" + c_data[i]['id']  + "'>";
					tbl += "<td>" + c_data[i]['name'] + "</td>";
					tbl += "<td>";
					if(c_data[i]['crawl_st']) {
						tbl += "<a style='margin-left: 10px;' onclick=\"previewScreenshotModal('" + c_data[i]['name'] + "');\" class='btn btn-primary'><i class='icon-refresh'></i>&nbsp;Refresh Screenshot</a>"
					} else {
						tbl += "<a style='margin-left: 10px;' onclick=\"previewScreenshotModal('" + c_data[i]['name'] + "');\" class='btn btn-primary'><i class='icon-picture'></i>&nbsp;Crawl Screenshot</a>";
					}
					if(c_data[i]['crawl_st']) {
						tbl += "<a style='margin-left: 10px;' onclick=\"flatPreviewScreenshotModal('" + c_data[i]['name'] + "');\" class='btn btn-success'><i class='icon-ok'></i>&nbsp;Screenshot Ready</a>";
					} else {
						tbl += "<a style='margin-left: 10px;' class='btn btn-warning disabled'><i class='icon-thumbs-down'></i>&nbsp;No Screenshot</a>";
					}
					tbl += "</td>";
				tbl += "</tr>";
			};
			tbl += "</tbody>";
		tbl += "</table>";
		$("#cl_cp_crawl_modal").html(tbl);
    }, 'json');
}

function flatPreviewScreenshotModal(url) {
	$("#customers_screens_crawl_modal").modal('hide');
	if(url === 'bloomingdales.com') { // --- static tmp screens for bloomingdales.com
		var tmp_thumb = base_url + "img/bloomingdales_com_wide_half.png";
		$("#preview_screenshot_modal #sc_preview").attr('src', tmp_thumb);
		$('#preview_screenshot_modal').lightbox();
	} else {
		var send_data = {
			url: url,
			year: $("#year_s > option:selected").val(),
			week: $(".pagination ul li.page.active").data('week')
		}
		var preview_img = $.post(base_url + 'index.php/measure/getwebshootdata', send_data, function(data) {
			$("#preview_screenshot_modal #sc_preview").attr('src', data[0]['img']);
			$('#preview_screenshot_modal').lightbox();
		});
	}
}

// function flatPreviewScreenshotModal(url) {
// 	$("#customers_screens_crawl_modal").modal('hide');
// 	$("#preview_screenshot_modal #sc_preview").css('width', '200');
// 	$("#preview_screenshot_modal #sc_preview").css('height', '150px');
// 	$("#preview_screenshot_modal").modal('show');
// 	if(url === 'bloomingdales.com') { // --- static tmp screens for bloomingdales.com
// 		var imagest = "";
// 		var tmp_thumb = base_url + "img/bloomingdales_com_wide_half.png";
// 		imagest += "<img id='s_img' onclick='openPreviewLarge()' src='" + tmp_thumb + "'>";
// 		imagest += "<img id='l_img' style='display: none;' src='" + tmp_thumb + "'>";
// 		$("#preview_screenshot_modal #sc_preview").html(imagest);
// 	} else {
// 		var send_data = {
// 			url: url,
// 			year: $("#year_s > option:selected").val(),
// 			week: $(".pagination ul li.page.active").data('week')
// 		}
// 		var preview_img = $.post(base_url + 'index.php/measure/getwebshootdata', send_data, function(data) {
// 			var imagest = "";
// 			imagest += "<img id='s_img' onclick='openPreviewLarge()' src='" + data[0]['thumb'] + "'>";
// 			imagest += "<img id='l_img' style='display: none;' src='" + data[0]['img'] + "'>";
// 			$("#preview_screenshot_modal #sc_preview").html(imagest);
// 		});
// 	}
// }

function previewScreenshotModal(url) {
	$("#customers_screens_crawl_modal").modal('hide');
	if(url === 'bloomingdales.com') { // --- static tmp screens for bloomingdales.com
		$("#loading_crawl_modal").modal('hide');
		$("#preview_screenshot_modal #sc_preview").css('width', '200');
		$("#preview_screenshot_modal #sc_preview").css('height', '150px');
		$("#preview_screenshot_modal").modal('show');
		var imagest = "";
		var tmp_thumb = base_url + "img/bloomingdales_com_wide_half.png";
		imagest += "<img id='s_img' onclick='openPreviewLarge()' src='" + tmp_thumb + "'>";
		imagest += "<img id='l_img' style='display: none;' src='" + tmp_thumb + "'>";
		$("#preview_screenshot_modal #sc_preview").html(imagest);
	} else {
		$("#loading_crawl_modal").modal('show');
		var send_data = {
			url: url,
			year: $("#year_s > option:selected").val(),
			week: $(".pagination ul li.page.active").data('week')
		}
		var start_site_crawl = $.post(base_url + 'index.php/measure/webshootcrawl', send_data, function(data) {
			$("#loading_crawl_modal").modal('hide');
			if(data['state']) {
				$("#preview_screenshot_modal #sc_preview").css('width', '200');
				$("#preview_screenshot_modal #sc_preview").css('height', '150px');
				$("#preview_screenshot_modal").modal('show');
				var imagest = "";
				imagest += "<img id='s_img' onclick='openPreviewLarge()' src='" + data['small_crawl'] + "'>";
				imagest += "<img id='l_img' style='display: none;' src='" + data['big_crawl'] + "'>";
				$("#preview_screenshot_modal #sc_preview").html(imagest);
			} else {
				alert('Internal Server Error');
			}
		});
	}
}

function openPreviewLarge() {
	$("#s_img").fadeOut('fast', function() {
		// $("#preview_screenshot_modal #sc_preview").css('width', '600px');
		// $("#preview_screenshot_modal #sc_preview").css('height', '450px');
		$("#preview_screenshot_modal #sc_preview").css('width', 'auto');
		$("#preview_screenshot_modal #sc_preview").css('height', 'auto');
		$("#l_img").fadeIn('fast');
	});
}

function openOverviewScreensCrawlModal() {
	$("#overview_screens_crawl_modal").modal('show');
}

function submitEmailReportsConfig() {
	var recs = $.trim($("#email_rec").val());
	var rec_day = $("#week_day_rep > option:selected").val();
	$("#email_rec").val("");
	$("#email_rec").blur("");
	$("#configure_email_reports").modal('hide');
	$("#configure_email_reports_success").modal('show');
}

function configureEmailReportsModal() {
	$("#configure_email_reports").modal('show');
}

function changeHomePageYersHandler() {
	var year = $("#year_s > option:selected").val();
	var week = $(".pagination ul li.page.active").data('week');
	$.ajax({
        url: base_url + 'index.php/measure/gethomepageyeardata',
        async: false,
        dataType: 'html',
        type: "POST",
        data: {
        	'year': year,
        	'week': week
        },
        success: function(res) {
        	$(".home_pages").fadeOut('medium', function() {
        		$(".home_pages").html(res);
        		$(".home_pages").fadeIn('medium');
        	});
        }
  	});
}

function detectNextPrevBtnPlace() {
	// --- activate all btns
	$("#page_next").removeClass('disabled');
	$("#page_next").find('a').attr('onclick', 'nextLocaHomePageWeekData()');
	$("#page_prev").removeClass('disabled');
	$("#page_prev").find('a').attr('onclick', 'prevLocaHomePageWeekData()');
	// --- configs
	var current_week_page = $(".pagination ul li.page.active").data('week');
	var next_sibling = $(".pagination ul li.page.active").next();
	var next_week_page = $(next_sibling).data('week');
	var prev_sibling = $(".pagination ul li.page.active").prev();
	var prev_week_page = $(prev_sibling).data('week');
	// --- next btn investigation
	var last_cwp = $(".pagination ul li.page:last").data('week');
	if(current_week_page == last_cwp) {
		$("#page_next").addClass('disabled');
		$("#page_next").find('a').attr('onclick', 'return false');
	}
	// --- prev btn investigation
	var first_cwp = $(".pagination ul li.page:first").data('week');
	if(current_week_page == first_cwp) {
		$("#page_prev").addClass('disabled');
		$("#page_prev").find('a').attr('onclick', 'return false');
	}
}

function get_home_page_week_data(week) {
	var year = $("#year_s > option:selected").val();
	var first_cwp = $(".pagination ul li.page:first").data('week');
	var last_cwp = $(".pagination ul li.page:last").data('week');
	$.ajax({
        url: base_url + 'index.php/measure/gethomepageweekdata',
        async: false,
        dataType: 'html',
        type: "POST",
        data: {
        	'year': year,
        	'week': week,
        	'first_cwp': first_cwp,
        	'last_cwp': last_cwp
        },
        success: function(res) {
        	$("#hp_ajax_content > div").slideUp('medium', function() {
        		$("#hp_ajax_content").html(res);
        	});
        }
  	});
}

function locaHomePageWeekData(week) {
	$(".pagination ul li").removeClass('active');
	$(".pagination ul li[data-week=" + week + "]").addClass('active');
	detectNextPrevBtnPlace();
	get_home_page_week_data(week);
}

function prevLocaHomePageWeekData() {
	var prev_sibling = $(".pagination ul li.page.active").prev();
	var prev_week_page = $(prev_sibling).data('week');
	locaHomePageWeekData(prev_week_page);
}

function nextLocaHomePageWeekData() {
	var next_sibling = $(".pagination ul li.page.active").next();
	var next_week_page = $(next_sibling).data('week');
	locaHomePageWeekData(next_week_page);
}


function slideTimeline(state) { // state: 'next', 'prev'
	var first_cwp = $(".pagination ul li.page:first").data('week');
	var last_cwp = $(".pagination ul li.page:last").data('week');
	$.ajax({
        url: base_url + 'index.php/measure/timelineblock',
        async: false,
        dataType: 'html',
        type: "POST",
        data: {
        	'first_cwp': first_cwp,
        	'last_cwp': last_cwp,
        	'state': state
        },
        success: function(res) {
        	$("#timeline_ctr").replaceWith(res);
        	get_home_page_week_data($("#timeline_ctr li.page.active").data('week'));
        }
  	});
}




