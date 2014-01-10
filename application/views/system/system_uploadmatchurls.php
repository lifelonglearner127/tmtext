<div class="tabbable">
    <ul class="nav nav-tabs jq-system-tabs">
           <li class=""><a data-toggle="tab" href="<?php echo site_url('system');?>">General</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/sites_view');?>">Sites</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('site_crawler');?>">Site Crawler</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('site_crawler/instances_list');?>">Crawler Instances <?php $this->load->helper("crawler_instances_helper"); echo crawler_instances_number();?></a></li>
            <li class="active"><a data-toggle="tab" href="<?php echo site_url('system/system_uploadmatchurls');?>">Upload Match URLs</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_dostatsmonitor');?>">Do_stats Monitor</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('brand/import');?>">Brands</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/batch_review');?>">Batch Review</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_compare');?>">Product Compare</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_productsmatch');?>">Product Match</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_reports');?>">Reports</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_logins');?>">Logins</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/keywords');?>">Keywords</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_rankings');?>">Rankings</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_pricing');?>">Pricing </a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/product_models');?>">Product models </a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/snapshot_queue');?>">Snapshot Queue</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/sync_keyword_status');?>">Sync Keyword Status</a></li> 
    </ul>
  <div class="tab-content">
      <div id="mathchurls" class="tab-pane active">
          <div id="matching"></div>
          <span class="btn btn-success fileinput-button pull-left" style="">
              Upload
              <i class="icon-plus icon-white"></i>
              <input type="file" multiple="" name="files[]" id="upload_urls">
          </span>
          <span class="btn btn-success fileinput-button pull-left" style="margin-left: 10px;">
              New Upload
              <i class="icon-plus icon-white"></i>
              <input type="file" multiple="" name="files[]" id="upload_urls_new">
          </span>
          <span class="btn btn-danger pull-left" id="stop_matches" style='margin-left: 10px;'>Stop</span>
          <input type="hidden" name="choosen_file" />
          <script>
			var match_ajax = "";
            var flag_stop_match = false;
            $(function () {
                var url = '<?php echo site_url('system/upload_match_urls'); ?>';
                $('#upload_urls').fileupload({
                  url: url,
                  dataType: 'json',
                  done: function (e, data) {
                    $('input[name="choosen_file"]').val(data.result.files[0].name);
                    var url = base_url+'index.php/system/check_urls';
                    var manu_file_upload_opts = $("#manu_upload_urls_check").is(":checked");
                    console.log("manu_file_upload_opts status: ", manu_file_upload_opts);
                    match_ajax = $.post(url, {'choosen_file': $('input[name="choosen_file"]').val(), 'manu_file_upload_opts': manu_file_upload_opts}, function(data) {
                  		console.log(data);
                    }, 'json');
		    matching_checking_int = setInterval(check_matching_status,5000);
		    flag_stop_match = false;
                  }
                });
            });
            
            // New loader
            $(function () {
                var url = '<?php echo site_url('system/upload_match_urls'); ?>';
                $('#upload_urls_new').fileupload({
                  url: url,
                  dataType: 'json',
                  done: function (e, data) {
                    $('input[name="choosen_file"]').val(data.result.files[0].name);
                    var url = base_url+'index.php/system/check_urls_threading';
                    var manu_file_upload_opts = $("#manu_upload_urls_check").is(":checked");
                    console.log("manu_file_upload_opts status: ", manu_file_upload_opts);
                    match_ajax = $.post(url, {'choosen_file': $('input[name="choosen_file"]').val(), 'manu_file_upload_opts': manu_file_upload_opts}, function(data) {
                  		console.log(data);
                    }, 'json');
                  }
                });
            });
            
          </script>
          <div style='float: left; width: 100%; clear: both; margin-top: 10px;'>
-          	<input type='checkbox' name='manu_upload_urls_check' id='manu_upload_urls_check'>
          	<label for='manu_upload_urls_check'>manufacturer match file</label>
          	<!-- <span class="btn btn-success fileinput-button pull-left" style="">
	              Upload manufacturer
	              <i class="icon-plus icon-white"></i>
	              <input type="file" multiple="" name="files[]" id="upload_urls_manu">
	          </span>
	          <span class="btn btn-danger pull-left" id="stop_matches_manu" style='margin-left: 10px;'>Stop</span>
		      	<input type="hidden" name="choosen_file_manu" /> -->
		      </div>
      </div>
  </div>
</div>

<!-- MODALS (START) -->
<div class="modal hide fade" id='system_modal_note'>
	<div class="modal-header">
		<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
		<h3>&nbsp;</h3>
	</div>
	<div class="modal-body">
		<p>&nbsp;</p>
	</div>
	<div class="modal-footer">
		<a href="javascript:void(0)" class="btn" data-dismiss="modal">Close</a>
	</div>
</div>
<!-- MODALS (END) -->

<script type='text/javascript'>
    var matching_checking_int = 0;

	function saveStateHandlerExt() {
		if(empty_check_validation_ext()) {
			$("#pm_tab_save_btn").removeClass('disabled');
			$("#pm_tab_save_btn").removeAttr('disabled');
			if(!$("#pm_tab_save_btn").hasClass('btn-success')) {
				$("#pm_tab_save_btn").addClass('btn-success');
			}
		}
	}

	function empty_check_validation_ext() {
		var res = false;
		$("#pm_data_table tr").each(function(index, value) {
			if(validate_url_ext($(value).find('.pmtt_url').val())) {
				res = true;
			}
		});
		return res;
	}

	function validate_url_ext(value) {
		return /^(https?|ftp):\/\/(((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?(((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?)(:\d*)?)(\/((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)?(\?((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\uE000-\uF8FF]|\/|\?)*)?(\#((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?$/i.test(value);
	}
        var old_data=false;
        function check_matching_status(){
            if(flag_stop_match){
                return clearInterval(matching_checking_int)
            }    
            if($("#matching").length==0)return false;
            var url = base_url+'index.php/system/get_matching_urls';
            $.ajax({
                type:'HEAD',
                url:url,
                success:function(data, status, xhr){
                    if(old_data!=xhr.getResponseHeader('Last-Change')){
                        old_data=xhr.getResponseHeader('Last-Change');
                        $.ajax({
                            url:url,
                            dataType:'json',
                            success:function(data){
                                $("#matching").html(data.response);
                                if(data.active)
                                {
                                    activeBtns('active');
                                } else
                                {
                                    activeBtns('unactive');
                                }
                            }
                        });
                    }
                }
            });
        }
        
        function activeBtns(type)
        {
            if(typeof(type) == 'undefined')
            {
                type = 'unactive';
            }
            if(type == 'active')
            {
                $('#upload_urls').attr('disabled',true);
                $('#mathchurls .btn-success:first').addClass('disabled');
                $('#mathchurls #stop_matches').removeClass('disabled');
            } else if(type == 'unactive')
             {
                 $('#upload_urls').removeAttr('disabled');
                 $('#mathchurls .btn-success:first').removeClass('disabled');
                 $('#mathchurls #stop_matches').addClass('disabled');
             }   
        }

	$(document).ready(function() {
            $('#stop_matches').on('click', function(){
                flag_stop_match = true;
                if(match_ajax != ""){
                    match_ajax.abort();
                }
		$.get(base_url+"index.php/system/stopChecking",function(d){ 
			activeBtns('unactive');
			$("#matching").html("Process has been stopped.");
		});
            })
            matching_checking_int = setInterval(check_matching_status,5000);
            $("#download_not_founds").click(function(){
                alert('works.');
                $.ajax({
                    url:base_url+"index.php/system/get_url_list",
                    success:function(data){
                        alert(data);
                    }
                });
            });

		// ---- UI tooltips (start)
		$("#pm_tab_newrow_btn").tooltip({
			placement: 'bottom',
			title: 'Maximum 10 rows'
		});
		$("#pm_tab_save_btn").tooltip({
			placement: 'right',
			title: 'Save Collection'
		});
		function destroyAndReinitTooltips() {
			$('#pm_tab_newrow_btn').tooltip('destroy');
			$('#pm_tab_save_btn').tooltip('destroy');
			$("#pm_tab_newrow_btn").tooltip({
				placement: 'bottom',
				title: 'Maximum 10 rows'
			});
			$("#pm_tab_save_btn").tooltip({
				placement: 'right',
				title: 'Save Collection'
			});
		}
		// ---- UI tooltips (end)

		function resetRowsInputs() {
			$('.pm_data_table_tinput').val('');
			$('.pm_data_table_tinput').removeClass('error');
			$("#pm_tab_save_btn").removeClass('btn-success');
			$("#pm_tab_save_btn").addClass('disabled');
			$("#pm_tab_save_btn").attr('disabled', true);
		}

		$("#pm_data_table .pm_data_table_tinput").bind('paste', function() {
			setTimeout(saveStateHandler, 200);
		});

		$("#pm_data_table .pm_data_table_tinput").bind('keypress', saveStateHandler);

		$("#pm_data_table .pm_data_table_tinput").bind('blur', saveStateHandler);

		function saveStateHandler() {
			if(empty_check_validation()) {
				$("#pm_tab_save_btn").removeClass('disabled');
				$("#pm_tab_save_btn").removeAttr('disabled');
				if(!$("#pm_tab_save_btn").hasClass('btn-success')) {
					$("#pm_tab_save_btn").addClass('btn-success');
				}
			}
		}

		function empty_check_validation() {
			var res = false;
			$("#pm_data_table tr").each(function(index, value) {
				if(validate_url($(value).find('.pmtt_url').val())) {
					res = true;
				}
			});
			return res;
		}

		function validate_url(value) {
			return /^(https?|ftp):\/\/(((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?(((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?)(:\d*)?)(\/((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)?(\?((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\uE000-\uF8FF]|\/|\?)*)?(\#((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?$/i.test(value);
		}

		function outputNotice(t, b) {
			$("#system_modal_note").modal('show');
			$("#system_modal_note .modal-header h3").text(t);
			$("#system_modal_note .modal-body p").text(b);
		}

		$("#pm_tab_newrow_btn").click(function() {
			if($("#pm_data_table tr").length < 10) {
				var new_line = "";
				new_line = "<tr>";
					new_line += "<td>";
						new_line += "<input type='text' onkeypress='saveStateHandlerExt()' onblur='saveStateHandlerExt()' class='pm_data_table_tinput pmtt_url' placeholder='Type URL' />";
					new_line += "</td>";
					new_line += "<td>";
						new_line += "<input type='text' onkeypress='saveStateHandlerExt()' onblur='saveStateHandlerExt()' class='pm_data_table_tinput pmtt_sku' placeholder='Type SKU' />";
					new_line += "</td>";
				new_line += "</tr>";
				$("#pm_data_table > tbody").append($(new_line));
			} else {
				outputNotice('Notice', 'Rows limit is reached. Maximum - 10 rows.');
			}
		});

		$("#pm_tab_save_btn").click(function() {
			$("#pm_data_table tr .pm_data_table_tinput").removeClass('error');
			var crawl_stack = [];
			$("#pm_data_table tr").each(function(index, value) {
				var url = $.trim($(value).find('.pmtt_url').val());
				var sku = $.trim($(value).find('.pmtt_sku').val());
				if(url === "") {
					
				} else {
					var mid = {
						'status_all': false,
						'status_url': false,
						'status_sku': true,
						'index': index,
						'url': '',
						'sku': ''
					};
					if(validate_url(url)) {
						mid['status_all'] = true;
						mid['url'] = url;
						mid['sku'] = sku;
						mid['status_url'] = true;
					}
					crawl_stack.push(mid);
				}
			});
			// --- travel through results (start)
			if(crawl_stack.length > 1) {
				var tr_res = true;
				for(var i = 0; i < crawl_stack.length; i++) {
					if(crawl_stack[i]['status_all'] !== true) {
						tr_res = false;
						break;
					}
				}
				if(tr_res) { // --- all ok, ready for send to backend
					$.ajax({
			              url: base_url + 'index.php/system/recordcollection',
			              dataType: "JSON",
			              async: false,
			              type: "POST",
			              data: {
			                crawl_stack: crawl_stack
			              },
			              success: function(res) {
			              	if(res === 1) { // --- all ok
			              		resetRowsInputs();
			              		destroyAndReinitTooltips();
			              		outputNotice('Success', 'Collection successfully saved.');
			              	} else if(res === 2) { // --- not enough valid collection items (must be 2>)
			              		outputNotice('Notice', 'Not enough valid collection items. Must be at least two.');
			              	} else if(res === 3) { // --- internal server error
			              		outputNotice('Warning', 'Internal Server Error');
			              	}
			              }
		            });
				} else { // ---- not ready, some mistakes in rows
					// --- highlight mistakes (start)
					for(var i=0; i < crawl_stack.length; i++) {
						if(crawl_stack[i]['status_all'] === false) {
							if(crawl_stack[i]['status_url'] === false) {
								var url_error = $("#pm_data_table tr")[crawl_stack[i]['index']];
								$(url_error).find('.pmtt_url').addClass('error');
							}
						}
					}
					// --- highlight mistakes (end)
					outputNotice('Fail', 'Check out some validation errors');
				} 
			} else {
				outputNotice('Notice', 'Not enough valid collection items.');
				// outputNotice('Notice', 'All rows are empty');
			}
			// --- travel through results (end)
		});

	});

</script>
