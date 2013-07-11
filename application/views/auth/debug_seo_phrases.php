<div class="row-fluid">
	<div class="span9 offset2">
		<div class="login_container">
			<div class="login_header">
				<h3 class="text-center">Seo Phrases Debugger</h3>
			</div>
			<div class="login_content">
				<div class='debug_seo_ph'>
					<div id="seo_edit_box" contenteditable='true' class='seod_edit_box'></div>
					<a href="javascript:void(0)" onclick="startSeoPhrasesDebugger()" class='btn btn-primary dsp_submit_btn'><i class='icon-tasks'></i>&nbsp;Start Seo Phrases Debug</a>
					<div class='debug_seo_ph_res'>
						<p class='h'>Results:</p>
						<ul id="res_seo_list"></ul>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>

<script type="text/javascript">
	function startSeoPhrasesDebugger() {
		var ph_text = $("#seo_edit_box").text();
		if($.trim(ph_text) !== "") {
			ph_text = ph_text.replace(/\s+/g, ' ');
			var analyzer_short = $.post(base_url+"index.php/measure/analyzestring", { clean_t: ph_text }, 'json').done(function(a_data) {
                console.log(a_data);
                var seo_items = "";
                var s_counter = 0;
                for(var i in a_data) {
                    if(typeof(a_data[i]) === 'object') {
                        s_counter++;
                        seo_items += '<li>' + '<span data-value="' + a_data[i]['ph'] + '" data-status="seo_link" onclick="wordHighLighterDebug(\''+a_data[i]['ph']+'\');" class="word_wrap_li_pr hover_en">' + a_data[i]['ph'] + '</span>' + ' <span class="word_wrap_li_sec">(' + a_data[i]['count'] + ')</span></li>';
                    }
                }
                if(s_counter > 0) $("ul#res_seo_list").html(seo_items);
            });
		} else {
			alert("Text for analyze is empty");
		}
	}

	function wordHighLighterDebug(w) {
		$(".word_wrap_li_pr").removeClass('act_select');
		$(".word_wrap_li_pr[data-value='" + w + "']").addClass('act_select');
		removeTagsFromDebugArea();
	    var highlightStartTag = "<span class='hilite'>";
	    var highlightEndTag = "</span>";
	    var searchTerm = w;
	    var bodyText = '';
	    bodyText = $("#seo_edit_box").text();

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

	    bodyText = $("#seo_edit_box").html(newText);
	}

	function removeTagsFromDebugArea() {
	    var debug_str = $("#seo_edit_box").text();
	    var debug_str_clean = debug_str.replace(/<\/?[^>]+(>|$)/g, "");
	    $("#seo_edit_box").html(debug_str_clean);
	}

	$(document).ready(function() {
		$("*").click(function(e) {
		    var attr = $(e.target).attr('data-status');
		    if(typeof(attr) !== 'undefined' && attr === 'seo_link') {} else {
	        	removeTagsFromDebugArea();
		    }
		});
	});

</script>