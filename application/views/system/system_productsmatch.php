<div class="tabbable">
  <ul class="nav nav-tabs jq-system-tabs">
	<li class=""><a data-toggle="tab" href="<?php echo site_url('system');?>">General</a></li>
	<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_accounts');?>">New Accounts</a></li>
	<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_roles');?>">Roles</a></li>
	<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_users');?>">Users</a></li>
	<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_compare');?>">Product Compare Interface</a></li>
	<li class=""><a data-toggle="tab" href="<?php echo site_url('site_crawler');?>">Site Crawler</a></li>
    <li class=""><a data-toggle="tab" href="<?php echo site_url('system/batch_review');?>">Batch Review</a></li>
    <li class="active"><a data-toggle="tab" href="<?php echo site_url('system/system_productsmatch');?>">Product Match</a></li>
  </ul>
  <div class="tab-content">
    <div id="tab8" class="tab-pane active">
    	<table id='pm_data_table' class='pm_data_table'>
    		<tbody>
    			<tr>
    				<td><input class='pm_data_table_tinput pmtt_url' type='text' placeholder='Type URL'></td>
    				<td><input class='pm_data_table_tinput pmtt_sku' type='text' placeholder='Type SKU'></td>
				</tr>
				<tr>
    				<td><input class='pm_data_table_tinput pmtt_url' type='text' placeholder='Type URL'></td>
    				<td><input class='pm_data_table_tinput pmtt_sku' type='text' placeholder='Type SKU'></td>
				</tr>
				<tr>
    				<td><input class='pm_data_table_tinput pmtt_url' type='text' placeholder='Type URL'></td>
    				<td><input class='pm_data_table_tinput pmtt_sku' type='text' placeholder='Type SKU'></td>
				</tr>
				<tr>
    				<td><input class='pm_data_table_tinput pmtt_url' type='text' placeholder='Type URL'></td>
    				<td><input class='pm_data_table_tinput pmtt_sku' type='text' placeholder='Type SKU'></td>
				</tr>
				<tr>
    				<td><input class='pm_data_table_tinput pmtt_url' type='text' placeholder='Type URL'></td>
    				<td><input class='pm_data_table_tinput pmtt_sku' type='text' placeholder='Type SKU'></td>
				</tr>
			</tbody>
		</table>
		<table class='pm_data_table'>
			<tbody>
				<tr>
					<td>
						<button type='button' id="pm_tab_newrow_btn" class='btn btn-primary'>Add New Row</button>
    					<button type='button' id="pm_tab_save_btn" class='btn disabled' disabled='true'>Save</button>
					</td>
				</tr>
			</tbody>
		</table>
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

	$(document).ready(function() {

		$("#pm_data_table .pm_data_table_tinput").bind('keypress', keypressHandler);

		function keypressHandler() {
			if(empty_check_validation()) {
				$("#pm_tab_save_btn").removeClass('disabled');
				$("#pm_tab_save_btn").removeAttr('disabled');
				if(!$("#pm_tab_save_btn").hasClass('btn-success')) {
					$("#pm_tab_save_btn").addClass('btn-success');
				}
			}
		}

		$("#pm_data_table .pm_data_table_tinput").bind('blur', blurHandler);

		function blurHandler() {
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
				if( $.trim($("#pm_data_table tr").find('.pmtt_url').val()) !== "" && $.trim($("#pm_data_table tr").find('.pmtt_sku').val()) !== ""  ) {
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
						new_line += "<input type='text' class='pm_data_table_tinput pmtt_url' placeholder='Type URL' />";
					new_line += "</td>";
					new_line += "<td>";
						new_line += "<input type='text' class='pm_data_table_tinput pmtt_sku' placeholder='Type SKU' />";
					new_line += "</td>";
				new_line += "</tr>";
				$("#pm_data_table > tbody").append($(new_line));
				// --- BIND / UNBIND (START)
				// $("#pm_data_table input[type=text]").unbind('keypress');
				// $("#pm_data_table input[type=text]").unbind('blur');
				// setTimeout(function() {
				// 	$("#pm_data_table input[type=text]").bind('keypress', keypressHandler);
				// 	$("#pm_data_table input[type=text]").bind('blur', blurHandler);
				// }, 2000);
				// --- BIND / UNBIND (END)
			} else {
				alert('Rows limit is reached. Maximum - 10 rows.');
			}
		});

		$("#pm_tab_save_btn").click(function() {
			$("#pm_data_table tr .pm_data_table_tinput").removeClass('error');
			var crawl_stack = [];
			$("#pm_data_table tr").each(function(index, value) {
				var url = $.trim($(value).find('.pmtt_url').val());
				var sku = $.trim($(value).find('.pmtt_sku').val());
				if(url === "" && sku === "") {
					
				} else {
					var mid = {
						'status_all': false,
						'status_url': false,
						'status_sku': false,
						'index': index,
						'url': '',
						'sku': ''
					};
					if(validate_url(url) && sku !== "") {
						mid['status_all'] = true;
						mid['url'] = url;
						mid['sku'] = sku;
					}
					if(validate_url(url)) {
						mid['status_url'] = true;
					}
					if(sku !== "") {
						mid['status_sku'] = true;
					}
					crawl_stack.push(mid);
				}
			});
			// --- travel through results (start)
			if(crawl_stack.length > 0) {
				var tr_res = true;
				for(var i = 0; i < crawl_stack.length; i++) {
					if(crawl_stack[i]['status_all'] !== true) {
						tr_res = false;
						break;
					}
				}
				if(tr_res) { // --- all ok, ready for send to backend
					outputNotice('Success', 'Crawl objects ready for backend');
				} else { // ---- not ready, some mistakes in rows
					// --- highlight mistakes (start)
					for(var i=0; i < crawl_stack.length; i++) {
						if(crawl_stack[i]['status_all'] === false) {
							if(crawl_stack[i]['status_url'] === false) {
								var url_error = $("#pm_data_table tr")[crawl_stack[i]['index']];
								$(url_error).find('.pmtt_url').addClass('error');
							}
							if(crawl_stack[i]['status_sku'] === false) {
								var url_error = $("#pm_data_table tr")[crawl_stack[i]['index']];
								$(url_error).find('.pmtt_sku').addClass('error');
							}
						}
					}
					// --- highlight mistakes (end)
					outputNotice('Fail', 'Check out some validation errors');
				} 
			} else {
				outputNotice('Notice', 'All rows are empty');
			}
			// --- travel through results (end)
			// console.log("RESULT: ", crawl_stack);
		});

	});

</script>
