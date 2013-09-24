<div class="modal-header">
	<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
	<h3>Categories screenshot reports</h3>
</div>
<div class="modal-body">
	<table id='dcsr_control_panel_tabel' class='table table-striped'>
		<thead>
			<tr>
				<th><input type='checkbox' name="cat_report_ch_all" id="cat_report_ch_all"></th>
				<th>Choose Department</th>
				<th>Competitors</th>
			</tr>
		</thead>
		<tbody>
			<tr>
				<td><input type='checkbox' class='cat_report_ch'></td>
				<td>
					<?php if (count($sites_list) > 0) { ?>
						<select class='main_site_chooser' onchange="mainSiteChooserHandler(this)">
							<option value='0'>Choose Site</option>
							<?php foreach ($sites_list as $val) { ?>
							<option value="<?php echo $val['id']; ?>" data-value="<?php echo $val['name_val']; ?>"><?php echo $val['name']; ?></option>
							<?php } ?>
						</select>
						<select style='display: none;' class='main_dep_chooser'></select>
					<?php } ?>
				</td>
				<td>
					<div class='comparison_row'>
						<select class='sec_site_chooser' onchange="secSiteChooserHandler(this)">
							<option value='0'>Choose comparison site</option>
							<?php foreach ($sites_list as $val) { ?>
							<option value="<?php echo $val['id']; ?>" data-value="<?php echo $val['name_val']; ?>"><?php echo $val['name']; ?></option>
							<?php } ?>
						</select>
						<select style='display: none;' class='sec_dep_chooser'></select>
						<label style='display: none; margin-top: 0px !important;' class="checkbox"><input type="checkbox"> Select competitor</label>
						<div style='display: none; margin-bottom: 10px;' class='comparison_row_cnt'>
							<button type='button' class='btn btn-success' onclick="addCompetitorRow(this)">Add Competitor</button>
						</div>
					</div>
				</td>
			</tr>
		</tbody>
	</table>
</div>
<div class="modal-footer">
	<button class="btn" onclick="addNewFullRow()" type="button">New row</button>
	<button id='btn_dep_rep_preview_set' class="btn btn-success btn-rec-all-send" disabled="" type="button">Preview saved sets</button>
	<button id='btn_dep_rep_save_set' class="btn btn-primary btn-rec-all-send" disabled="" type="button">Save sets</button>
</div>

<script type='text/javascript'>
	
	$(document).ready(function() {
		$("#cat_report_ch_all").on('change', function(e) {
			if($(e.target).is(":checked")) {
				$('.cat_report_ch').attr('checked', true);
				$('#btn_dep_rep_save_set').removeAttr('disabled');
			} else {
				$('.cat_report_ch').removeAttr('checked');
				$('#btn_dep_rep_save_set').attr('disabled', true);
			}
		});

		$(".cat_report_ch").on('change', function(e) {
			var checked_count = $(".cat_report_ch").length;
			setTimeout(function() {
				var count_s = 0;
				$(".cat_report_ch").each(function(index, val) {
					if($(val).is(':checked')) count_s++;
				});
				if(checked_count == count_s) {
					$("#cat_report_ch_all").attr('checked', true);
				} else {
					$("#cat_report_ch_all").removeAttr('checked');
				}
				if(count_s == 0) {
					$("#cat_report_ch_all").removeAttr('checked');
					$("#btn_dep_rep_save_set").attr('disabled', true);
				} else {
					$('#btn_dep_rep_save_set').removeAttr('disabled');
				} 
			}, 100);
		});

	});

	function addNewFullRow() {
		$.post(base_url + 'index.php/measure/get_full_dep_rep_comparison_row', {}, function(data) {
			$("#dcsr_control_panel_tabel tbody").append(data);
			$("#cat_report_ch_all").removeAttr('checked');
		});
	}

	function removeFullRow(e) {
		if(confirm('Are you sure?')) {
			var full_row = $(e).parent().parent();
			full_row.remove();
		}
	}

	function removeCompetitorRow(e) {
		var comparison_row = $(e).parent().parent();
		comparison_row.remove();
	}

	function addCompetitorRow(e) {
		var comparison_row = $(e).parent().parent();
		$.post(base_url + 'index.php/measure/get_dep_rep_comparison_row', {}, function(data) {
			$(e).replaceWith("<button class='btn btn-danger' onclick='removeCompetitorRow(this)'>Remove Competitor</button>");
			$(data).insertAfter(comparison_row);
			var rows_count = $('.comparison_row').length;
			if(rows_count == 5) {
				$('.comparison_row').last().find('.comparison_row_cnt').remove();
			}
		}); 
	}

	function secSiteChooserHandler(e) {
		var site_id = $(e).val();
		// ==== elements detection (start)
		var sec_dep_dropdown = $(e).next();
		var sec_dep_checkbox = $(e).next().next();
		var sec_dep_cnt = $(e).next().next().next();
		// ==== elements detection (end)
		sec_dep_dropdown.empty();
		$.post(base_url + 'index.php/measure/getDepartmentsByCustomerNew', {site_id: site_id}, function(data) {
			if(data.length > 0) {
				var dep_options = "";
				for(var i = 0; i < data.length; i++) {
					dep_options += "<option value='" + data[i]['id'] + "'>" + data[i]['text'] + "</option>"
				}
				sec_dep_dropdown.append(dep_options);
				sec_dep_dropdown.show();
				sec_dep_checkbox.show();
				sec_dep_cnt.show();
			} else {
				sec_dep_dropdown.hide();
				sec_dep_checkbox.hide();
				sec_dep_cnt.hide();
			}
		});
	}

	function mainSiteChooserHandler(e) {
		var site_id = $(e).val();
		// ==== elements detection (start)
		var sec_dep_dropdown = $(e).next();
		// ==== elements detection (end)
		sec_dep_dropdown.empty();
		$.post(base_url + 'index.php/measure/getDepartmentsByCustomerNew', {site_id: site_id}, function(data) {
			if(data.length > 0) {
				var dep_options = "";
				for(var i = 0; i < data.length; i++) {
					dep_options += "<option value='" + data[i]['id'] + "'>" + data[i]['text'] + "</option>"
				}
				sec_dep_dropdown.append(dep_options);
				sec_dep_dropdown.show();
			} else {
				sec_dep_dropdown.hide();
			}
		});
	}

</script>