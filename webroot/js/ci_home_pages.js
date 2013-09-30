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
	    hashTags: false,
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

function activateDepRepPreview() {
	$("#dcsr_control_panel_modal").modal('hide');
	$.post(base_url + 'index.php/measure/activate_dep_rep_preview_list', {}, function(data) {
		$("#dep_rep_preview_list_modal").html(data);
		$("#dep_rep_preview_list_modal").modal('show');
	});
}

function drop_selecction_scan() {
	// --- screens dropdowns selections scanner (start)
    var send_data = {
		year: $("#year_s > option:selected").val(),
		week: $(".pagination ul li.page.active").data('week')
	}
    var drop_selection_scan = $.post(base_url + 'index.php/measure/dropselectionscan', send_data, function(data) {
    	for(var i=0; i < data.length; i++) {
    		if(data[i]['cell'] !== false) {
    			if(data[i]['cell']['reset'] == 0) {
    				var data_cell_img = base_url + "webshoots/" + data[i]['cell']['shot_name'];
	    			var item_id = $(".hp_boot_drop[data-pos='" + data[i]['pos'] + "']").data('itemid'); 
	    			$("#screen_lightbox_img_" + item_id).attr('src', data_cell_img);
						$("#art_img_" + item_id).html("<a href='#screen_lightbox_" + item_id  + "' data-toggle='lightbox' style='background-image: url(" + data_cell_img + "); background-position: top left; background-repeat: no-repeat;'></a>");
						var t = moment(data[i]['cell']['screen_stamp']).format('MMMM Do, YYYY');
						$("#crawl_date_" + item_id).text(t);
						$("#hp_boot_drop_" + item_id + " .btn_caret_sign").text(data[i]['cell']['label']);
				} else {
						var item_id = $(".hp_boot_drop[data-pos='" + data[i]['pos'] + "']").data('itemid'); 
						$("#art_img_" + item_id).html("");
						$("#crawl_date_" + item_id).text("");
						$("#hp_boot_drop_" + item_id + " .btn_caret_sign").text("[ Choose site ]");
				}
    		}
    	}
    	$("#loading_crawl_modal").modal('hide');
    });
    // --- screens dropdowns selections scanner (end)
}

function viewCatsScreensCp() {
	$("#dep_rep_preview_list_modal").modal('hide');
	$("#dcsr_control_panel_modal").modal('show');
	// --- refresh listing (start)
	var send_data = {};
	var rec = $.post(base_url + 'index.php/measure/get_cats_screens_rep', send_data, function(data) {
		$("#dcsr_control_panel_modal").html(data);
	});
	// -- refresh listing (end)
}

function resetScreenDrop(uid, pos, year, week) {
	var send_data = {
		uid: uid,
		pos: pos,
		year: year,
		week: week
	};
	$.post(base_url + 'index.php/measure/reset_screen_drop', send_data, function(data) {
		drop_selecction_scan();
	});
}

function sendEmailScreensToSelected() {
	var gerr_user_id = $("#gerr_user_id").val();
	var gerr_c_week = $("#gerr_c_week").val();
	var gerr_c_year = $("#gerr_c_year").val();
	var selected_data = [];
	var selected_items = $("input[type='checkbox'][name='send_report_ch']:checked").length;
	if(selected_items > 0) {
		$(".report_bean_line.selected").each(function(index, value) {
			var mid = {
				'id': $(value).data('id'),
				'email': $(value).data('email'),
				'day': $(value).data('day')
			};
			selected_data.push(mid);
		});
		var send_data = {
			selected_data: selected_data,
			c_week: gerr_c_week,
			c_year: gerr_c_year,
			uid: gerr_user_id,
			c_week_up_confirm: $("#c_week_up_confirm").is(":checked")
		};
		$("#recipients_control_panel_modal").modal('hide');
		$("#loader_emailsend_modal").modal('show');
		var send_recipient_report_sel = $.post(base_url + 'index.php/measure/send_recipient_report_selected', send_data, function(data) {
			$("#loader_emailsend_modal").modal('hide');
			$("#success_emailsend_modal").modal('show');
		});
	} else {
		alert('None of emails is selected');
	}
}

function sendEmailScreensToAll() {
	var gerr_user_id = $("#gerr_user_id").val();
	var gerr_c_week = $("#gerr_c_week").val();
	var gerr_c_year = $("#gerr_c_year").val();
	var selected_data = [];
	$(".report_bean_line").each(function(index, value) {
		var mid = {
			'id': $(value).data('id'),
			'email': $(value).data('email'),
			'day': $(value).data('day')
		};
		selected_data.push(mid);
	});
	var send_data = {
		selected_data: selected_data,
		c_week: gerr_c_week,
		c_year: gerr_c_year,
		uid: gerr_user_id,
		c_week_up_confirm: $("#c_week_up_confirm").is(":checked")
	};
	$("#recipients_control_panel_modal").modal('hide');
	$("#loader_emailsend_modal").modal('show');
	var send_recipient_report_sel = $.post(base_url + 'index.php/measure/send_recipient_report_selected', send_data, function(data) {
		$("#loader_emailsend_modal").modal('hide');
		$("#success_emailsend_modal").modal('show');
	});
}

function sendRecipientReport(id, email, day, c_week, c_year, uid) {
	var send_data = {
		id: id,
		email: email,
		day: day,
		c_week: c_week,
		c_year: c_year,
		uid: uid,
		c_week_up_confirm: $("#c_week_up_confirm").is(":checked")
	};
	$("#recipients_control_panel_modal").modal('hide');
	$("#loader_emailsend_modal").modal('show');
	var send_recipient_report = $.post(base_url + 'index.php/measure/send_recipient_report', send_data, function(data) {
		console.log(data);
		$("#loader_emailsend_modal").modal('hide');
		$("#success_emailsend_modal").modal('show');
	});
}

function deleteRecipient(id) {
	if(confirm('Are you sure?')) {
		var send_data = {
			id: id
		};
		var remove_rec = $.post(base_url + 'index.php/measure/delete_recipient', send_data, function(data) {
			$("#recipients_control_panel_body > table tr[data-id='" + id + "']").remove();
			// $("#recipients_control_panel_modal").modal('hide');
		});
	}
}

function startAllCrawl() {
	$("#customers_screens_crawl_modal").modal('hide');
	$("#loading_crawl_modal").modal('show');
	var start_site_crawl = $.post(base_url + 'index.php/measure/webshootcrawlall', {}, function(data) {
		drop_selecction_scan();
	});
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
					tbl += "<a onclick=\"previewScreenshotModal('" + c_data[i]['url'] + "');\" class='btn btn-primary'><i class='icon-refresh'></i>&nbsp;Refresh Screenshot</a>";
                } else {
					tbl += "<a onclick=\"previewScreenshotModal('" + c_data[i]['url'] + "');\" class='btn btn-primary'><i class='icon-picture'></i>&nbsp;Crawl Screenshot</a>";
                }
                if(c_data[i]['crawl_st']) {
						tbl += "<a style='margin-left: 3px;' onclick=\"flatPreviewScreenshotModal('" + c_data[i]['url'] + "');\" class='btn btn-success'><i class='icon-ok'></i>&nbsp;Screenshot Ready</a>";
					} else {
						tbl += "<a style='margin-left: 3xpx;' class='btn btn-warning disabled'><i class='icon-thumbs-down'></i>&nbsp;No Screenshot</a>";
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
	// if(url === 'bloomingdales.com') {
	// 	var tmp_thumb = base_url + "img/bloomingdales_com_wide_half.png";
	// 	$("#preview_screenshot_modal #sc_preview").attr('src', tmp_thumb);
	// 	$('#preview_screenshot_modal').lightbox();
	// } else {
	// 	var send_data = {
	// 		url: url,
	// 		year: $("#year_s > option:selected").val(),
	// 		week: $(".pagination ul li.page.active").data('week')
	// 	}
	// 	var preview_img = $.post(base_url + 'index.php/measure/getwebshootdata', send_data, function(data) {
	// 		$("#preview_screenshot_modal #sc_preview").attr('src', data[0]['img']);
	// 		$('#preview_screenshot_modal').lightbox();
	// 	});
	// }
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

function previewScreenshotModal(url) {
	$("#customers_screens_crawl_modal").modal('hide');
	$("#loading_crawl_modal").modal('show');
	var send_data = {
		url: url,
		year: $("#year_s > option:selected").val(),
		week: $(".pagination ul li.page.active").data('week')
	}
	var start_site_crawl = $.post(base_url + 'index.php/measure/webshootcrawl', send_data, function(data) {
		drop_selecction_scan();
		if(data['state']) {
			flatPreviewScreenshotModal(url);
		} else {
			alert('Internal Server Error');
		}
	});
}

function openPreviewLarge() {
	$("#s_img").fadeOut('fast', function() {
		$("#preview_screenshot_modal #sc_preview").css('width', 'auto');
		$("#preview_screenshot_modal #sc_preview").css('height', 'auto');
		$("#l_img").fadeIn('fast');
	});
}

function openOverviewScreensCrawlModal() {
	$("#overview_screens_crawl_modal").modal('show');
}

function redirectToRecipientsListAfterAdd() {
	$("#configure_email_reports_success").modal('hide');
	viewRecipientsList();
}

function viewRecipientsList() {
	$("#recipients_control_panel_modal").modal('show');
	// --- refresh listing (start)
	var send_data = {
		c_week: $(".pagination ul li.page.active").data('week'),
		c_year: $("#year_s > option:selected").val()
	};
	var rec = $.post(base_url + 'index.php/measure/get_emails_reports_recipient', send_data, function(data) {
		$("#recipients_control_panel_modal").html(data);
	});
	// -- refresh listing (end)
}

function capitaliseFirstLetter(string)
{
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function internalRecipientFunc(){
    $('.delete_rec').click(function(){
        if(confirm('Are you sure?')) {
            var send_data = {
                id: $('#delete_rec').attr('id')
            };
            var remove_rec = $.post(base_url + 'index.php/measure/delete_recipient', send_data, function(data) {
                $("#recipients_control_panel_modal").modal('hide');
            });
        }
    });
    $('.fire_rec').click(function(){
    	var gerr_user_id = $("#gerr_user_id").val();
		var gerr_c_week = $("#gerr_c_week").val();
		var gerr_c_year = $("#gerr_c_year").val();
        var send_data = {
            id: $('.fire_rec').attr('id'),
            email: $(this).parent().parent().data('email'),
            day: $(this).parent().parent().data('day'),
            c_week: gerr_c_week,
			c_year: gerr_c_year,
			uid: gerr_user_id,
			c_week_up_confirm: $("#c_week_up_confirm").is(":checked")
        };
        var send_recipient_report = $.post(base_url + 'index.php/measure/send_recipient_report', send_data, function(data) {
            $("#recipients_control_panel_modal").modal('hide');
        });
    });
    var checked_count = $("input[type='checkbox'][name='send_report_ch']").length;
    $("input[type='checkbox'][name='send_report_ch']").on('change', function(e) {
        setTimeout(function() {
            // ---- mark / unmark tr line as selected (start)
            if($(e.target).is(":checked")) {
                $(e.target).parent().parent().addClass('selected');
            } else {
                $(e.target).parent().parent().removeClass('selected');
            }
            // ---- mark / unmark tr line as selected (end)
            var count_s = 0;
            $("input[type='checkbox'][name='send_report_ch']").each(function(index, val) {
                if($(val).is(':checked')) count_s++;
            });
            if(checked_count == count_s) $("#send_report_ch_all").attr('checked', true);
            if(count_s == 0) $("#send_report_ch_all").removeAttr('checked');
        }, 100);
    });
}

function submitEmailReportsConfig() {
    $('tr.no_recipients').remove();
    // --- collect data (start)
    var email_pattern = /^([a-z0-9_\-]+\.\+)*[a-z0-9_\-\+]+@([a-z0-9][a-z0-9\-]*[a-z0-9]\.)+[a-z]{2,4}$/i;
    var recs_arr = [];
    var recs = $.trim($('input[name="recipients_rec"]').val());
    if(recs !== "") {
        recs_arr = recs.split(',');
        var recs_arr_checked = [];
        for(var i = 0; i < recs_arr.length; i++) {
            if(email_pattern.test($.trim(recs_arr[i]))) {
                recs_arr_checked.push($.trim(recs_arr[i]));
            }
        }
    }
    var rec_day = $("#recipients_week_day > option:selected").val();
    // --- collect data (end)
    var send_data = {
        recs_arr: recs_arr_checked,
        rec_day: rec_day
    }
    var rec = $.post(base_url + 'index.php/measure/rec_emails_reports_recipient', send_data, function(data) {
        if(data.length > 0) {
            for(var i=0; i<data.length; i++){
                $("<tr class='report_bean_line' data-id="+data[i][0].id+" data-email="+data[i][0].email+" data-day="+data[i][0].day+" >" +
                    "<td><input type='checkbox' name='send_report_ch' id='send_report_ch_"+data[i][0].id+"'>" +
                    "</td><td><span class='recipients_control_panel_txt'>"+data[i][0].email+"</span></td>" +
                    "<td><span class='recipients_control_panel_txt'>"+capitaliseFirstLetter(data[i][0].day)+"</span></td>" +
                    "<td nowrap><button type='button' class='btn btn-success btn-rec-ind-send fire_rec' id="+data[i][0].id+"><i class='icon-fire'></i></button>" +
                    " <button type='button' class='btn btn-danger btn-rec-remove' onclick=\"deleteRecipient('" + data[i][0].id + "');\" id='"+data[i][0].id+"'><i class='icon-remove'></i></button>" +
                    "</td></tr>").insertBefore('#new_row');
            }
            $('input[name="recipients_rec"]').val('');
            $('input[name="recipients_rec"]').blur('');
            internalRecipientFunc();
        } else {
            alert('Validation or internal server error');
        }
    });

}
var num=0;
function newRecipient() {
    num++;
        $('tr.no_recipients').remove();
        $('table.table-striped').append('<tr id="new_row_'+num+'">' +
            '<td>&nbsp;</td><td><input type="text" placeholder="New email" name="new_recipients_'+num+'" style="width:150px;">' +
            '</td><td><select name="new_week_day_rep_'+num+'">' +
            '<option value="monday" selected>Monday</option>' +
            '<option value="tuesday">Tuesday</option>' +
            '<option value="wednesday">Wednesday</option>' +
            '<option value="thursday">Thursday</option>' +
            '<option value="friday">Friday</option>' +
            '<option value="saturday">Saturday</option>' +
            '<option value="sunday">Sunday</option></select></td>' +
            '<td><a href="javascript:void(0)" class="btn btn-success new_rec" id="new_rec'+num+'">' +
            '<i class="icon-plus"></i></a></td></tr>');


        $("#new_rec"+num).click(function(){
            // --- collect data (start)
            var email_pattern = /^([a-z0-9_\-]+\.\+)*[a-z0-9_\-\+]+@([a-z0-9][a-z0-9\-]*[a-z0-9]\.)+[a-z]{2,4}$/i;
            var recs_arr = [];
            var recs = $.trim($('input[name="new_recipients_'+num+'"]').val());
            if(recs !== "") {
                recs_arr = recs.split(',');
                var recs_arr_checked = [];
                for(var i = 0; i < recs_arr.length; i++) {
                    if(email_pattern.test($.trim(recs_arr[i]))) {
                        recs_arr_checked.push($.trim(recs_arr[i]));
                    }
                }
            }
            var rec_day = $("select[name='new_week_day_rep_"+num+"'] > option:selected").val();
            // --- collect data (end)
            var send_data = {
                recs_arr: recs_arr_checked,
                rec_day: rec_day
            }
            var rec = $.post(base_url + 'index.php/measure/rec_emails_reports_recipient', send_data, function(data) {
                if(data.length > 0) {
                    $("#new_row_"+num).remove();
                    for(var i=0; i<data.length; i++){
                        $("<tr class='report_bean_line' data-id="+data[i][0].id+" data-email="+data[i][0].email+" data-day="+data[i][0].day+" >" +
                            "<td><input type='checkbox' name='send_report_ch' id='send_report_ch_"+data[i][0].id+"'>" +
                            "</td><td><span class='recipients_control_panel_txt'>"+data[i][0].email+"</span></td>" +
                            "<td><span class='recipients_control_panel_txt'>"+capitaliseFirstLetter(data[i][0].day)+"</span></td>" +
                            "<td><button type='button' class='btn btn-success btn-rec-ind-send fire_rec' id="+data[i][0].id+"><i class='icon-fire'></i></button>" +
                            "<button type='button' class='btn btn-danger btn-rec-remove' onclick=\"deleteRecipient('" + data[i][0].id + "');\" id='"+data[i][0].id+"'><i class='icon-remove'></i></button>" +
                            "</td></tr>").insertBefore('#new_row');
                    }
                    internalRecipientFunc();
                } else {
                    alert('Validation or internal server error');
                }
            });
        });
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

function get_screenshots_slider_data(week, year) {
	var send_data = {
		week: week,
		year: year
	}
	var sc_slider_data = $.post(base_url + 'index.php/measure/get_screenshots_slider_data', send_data, function(data) {
		$("#screens_images_slider_wrap").html(data);
	});
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

function redetectTimelineTooltips() {
	$("#timeline_ctr .page:not(.disabled, .active) a:not(.have_screen, .current_week, .mixed_screen)").tooltip('destroy');
	$("#timeline_ctr .page:not(.disabled) a.current_week:not(.have_screen, .mixed_screen)").tooltip('destroy');
	$("#timeline_ctr .page:not(.disabled) a.have_screen:not(.current_week, .mixed_screen)").tooltip('destroy');
	$("#timeline_ctr .page:not(.disabled) a.mixed_screen").tooltip('destroy');
	$("#timeline_ctr .page.active:not(.disabled) a:not(.have_screen, .current_week, .mixed_screen)").tooltip('destroy');
	$("#timeline_ctr .page:not(.disabled, .active) a:not(.have_screen, .current_week, .mixed_screen)").tooltip({
		placement: 'bottom',
		title: 'regular week / no screenshots'
	});
	$("#timeline_ctr .page:not(.disabled) a.current_week:not(.have_screen, .mixed_screen)").tooltip({
		placement: 'bottom',
		title: 'current week / no screenshots'
	});
	$("#timeline_ctr .page:not(.disabled) a.have_screen:not(.current_week, .mixed_screen)").tooltip({
		placement: 'bottom',
		title: 'regular week / available screenshots'
	});
	$("#timeline_ctr .page:not(.disabled) a.mixed_screen").tooltip({
		placement: 'bottom',
		title: 'current week / available screenshots'
	});
	$("#timeline_ctr .page.active:not(.disabled) a:not(.have_screen, .current_week, .mixed_screen)").tooltip({
		placement: 'bottom',
		title: 'selected week / no screenshots'
	});
}

function locaHomePageWeekData(week) {
	var year = $("#year_s > option:selected").val();
	$(".pagination ul li").removeClass('active');
	$(".pagination ul li[data-week=" + week + "]").addClass('active');
	detectNextPrevBtnPlace();
	get_home_page_week_data(week);
	get_screenshots_slider_data(week, year);
	setTimeout(function() {
		redetectTimelineTooltips();
	}, 500);
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
        	'state': state,
        	'year': $("#year_s > option:selected").val()
        },
        success: function(res) {
        	$("#timeline_ctr").replaceWith(res);
        	get_home_page_week_data($("#timeline_ctr li.page.active").data('week'));
        	get_screenshots_slider_data($("#timeline_ctr li.page.active").data('week'), $("#year_s > option:selected").val());
        }
  	});
}
