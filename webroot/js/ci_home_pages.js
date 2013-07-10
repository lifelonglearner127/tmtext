/* --- shrinktheweb.com API keys (start) --- */
var stwaccesskeyid = "28c77fca6deb748";
/* --- shrinktheweb.com API keys (end) --- */

function test_screenshot() {
	var customers_list = $.post(base_url + 'index.php/measure/testscreenshot', {}, function(data) {
		console.log(data);
	});
}

function openCrawlLaunchPanelModal() {
	$("#customers_screens_crawl_modal").modal('show');
}
function startCrawl() {
	console.log("start crawl");
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
	if(close_preview) {
		$("#preview_screenshot_modal").modal('hide');
	}
	$("#customers_screens_crawl_modal").modal('show');
	var customers_list = $.post(base_url + 'index.php/measure/getcustomerslist_general', {}, function(c_data) {
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
					tbl += "<a onclick=\"removeCrawlSiteFromList('" + c_data[i]['id'] + "');\" class='btn btn-danger'><i class='icon-remove-sign'></i>&nbspRemove</a>";
					tbl += "<a style='margin-left: 10px;' onclick=\"previewScreenshotModal('" + c_data[i]['name'] + "');\" class='btn btn-primary'><i class='icon-picture'></i>&nbsp;Preview Screen</a>"
					tbl += "</td>";
				tbl += "</tr>";
			};
			tbl += "</tbody>";
		tbl += "</table>";
		$("#cl_cp_crawl_modal").html(tbl);
		$("#crawl_modal_sbm_btn").removeClass("disabled");
		$("#crawl_modal_sbm_btn").removeAttr("disabled");
		$("#crawl_modal_sbm_btn").attr("onclick", "startCrawl()");
    }, 'json');
}

function previewScreenshotModal(url) {
	$("#customers_screens_crawl_modal").modal('hide');
	var link_img = "http://images.shrinktheweb.com/xino.php?stwembed=1&stwaccesskeyid=" + stwaccesskeyid + "&stwsize=lg&stwurl=http://www." + url;
	$("#preview_screenshot_modal").modal('show');
	$("#preview_screenshot_modal #sc_preview > img").attr('src', link_img);
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
	$(".page_next").removeClass('disabled');
	$(".page_next").find('a').attr('onclick', 'nextLocaHomePageWeekData()');
	$(".page_prev").removeClass('disabled');
	$(".page_prev").find('a').attr('onclick', 'prevLocaHomePageWeekData()');
	// --- configs
	var current_week_page = $(".pagination ul li.page.active").data('week');
	var next_sibling = $(".pagination ul li.page.active").next();
	var next_week_page = $(next_sibling).data('week');
	var prev_sibling = $(".pagination ul li.page.active").prev();
	var prev_week_page = $(prev_sibling).data('week');
	// --- next btn investigation
	if(current_week_page == '5') {
		$(".page_next").addClass('disabled');
		$(".page_next").find('a').attr('onclick', 'return false');
	}
	// --- prev btn investigation
	if(current_week_page == '1') {
		$(".page_prev").addClass('disabled');
		$(".page_prev").find('a').attr('onclick', 'return false');
	}
}

function locaHomePageWeekData(week) {
	var year = $("#year_s > option:selected").val();
	$(".pagination ul li").removeClass('active');
	$(".pagination ul li[data-week=" + week + "]").addClass('active');
	detectNextPrevBtnPlace();
	$.ajax({
        url: base_url + 'index.php/measure/gethomepageweekdata',
        async: false,
        dataType: 'html',
        type: "POST",
        data: {
        	'year': year,
        	'week': week
        },
        success: function(res) {
        	$("#hp_ajax_content > div").slideUp('medium', function() {
        		$("#hp_ajax_content").html(res);
        	});
        }
  	});
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