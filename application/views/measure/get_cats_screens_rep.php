<div class="modal-header">
	<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
	<h3>Configure Screenshots Report</h3>
</div>
<div class="modal-body">
	<table id='dcsr_control_panel_tabel' class='table table-striped'>
		<thead>
			<tr>
				<th>&nbsp;</th>
				<th>Choose Department</th>
				<th>Competitors</th>
			</tr>
		</thead>
		<tbody>
			<tr data-id="<?php echo $helpers_model->random_string_gen(11); ?>">
				<td>&nbsp;</td>
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
	<?php 
		$sets_disabled_state = "disabled";
		if(count($user_dep_rep_sets) > 0) {
			$sets_disabled_state = "";
		}
	?>
	<button id='btn_dep_rep_preview_set' <?php echo $sets_disabled_state; ?> onclick="activateDepRepPreview()" class="btn btn-success btn-rec-all-send" type="button">Preview</button>
	<button id='btn_dep_rep_save_set' class="btn btn-primary btn-rec-all-send" disabled="" type="button" onclick="saveSets()">Save</button>
</div>

<script type='text/javascript'>
	
	function saveSetButtonStateScaner() {
		var sets = [];
		// === prepare selected sets data for analyzer (start)
		$("#dcsr_control_panel_modal table > tbody > tr").each(function(index, value) {
			var mid = {
				id: $(value).data('id'),
				main_choose_site: '0',
				main_choose_dep: '0',
				competitors: [],
				valid: false
			};
			mid.main_choose_site = $(value).find('.main_site_chooser > option:selected').val();
			if( $(value).find('.main_dep_chooser').is(':visible') ) {
				mid.main_choose_dep = $(value).find('.main_dep_chooser > option:selected').val();
			}
			$(value).find('.comparison_row').each(function(index, value) {
				if( $(value).find('.sec_site_chooser > option:selected').val() != 0 && $(value).find('.sec_dep_chooser').is(':visible') && $(value).find('.sec_dep_chooser > option:selected').val() != 0 ) {
					var com_mid = {
						sec_site_chooser: $(value).find('.sec_site_chooser > option:selected').val(),
						sec_dep_chooser: $(value).find('.sec_dep_chooser > option:selected').val()
					};
					mid.competitors.push(com_mid);
				}
			});
			sets.push(mid);  
		});
		// === prepare selected sets data for analyzer (end)

		// === sets validation (start)
		var v_status = false;
		for(var i = 0; i < sets.length; i++) {
			if( sets[i]['main_choose_site'] != "0" && sets[i]['main_choose_dep'] != "0" && sets[i]['competitors'].length > 0 ) {
				sets[i]['valid'] = true;
			}
		}
		// === sets validation (end)
		var overall_valid = true;
		for(var j = 0; j < sets.length; j++) {
			if(!sets[j]['valid']) {
				overall_valid = false;
				break;
			}
		}
		if(overall_valid) {
			$("#btn_dep_rep_save_set").removeAttr('disabled');
		} else {
			$("#btn_dep_rep_save_set").attr('disabled', true);
		}
	}

	// function activateDepRepPreview() {
	// 	$("#dcsr_control_panel_modal").modal('hide');
	// 	$.post(base_url + 'index.php/measure/activate_dep_rep_preview_list', {}, function(data) {
	// 		$("#dep_rep_preview_list_modal").html(data);
	// 		$("#dep_rep_preview_list_modal").modal('show');
	// 	});
	// }

	function saveSets() {
		var sets = [];
		// === prepare selected sets data for backend analyzer (start)
		$("#dcsr_control_panel_tabel > tbody > tr").each(function(index, value) {
			var mid = {
				id: $(value).data('id'),
				main_choose_site: '0',
				main_choose_dep: '0',
				competitors: [],
				valid: false
			};
			mid.main_choose_site = $(value).find('.main_site_chooser > option:selected').val();
			if( $(value).find('.main_dep_chooser').is(':visible') ) {
				mid.main_choose_dep = $(value).find('.main_dep_chooser > option:selected').val();
			}
			$(value).find('.comparison_row').each(function(index, value) {
				if( $(value).find('.sec_site_chooser > option:selected').val() != 0 && $(value).find('.sec_dep_chooser').is(':visible') && $(value).find('.sec_dep_chooser > option:selected').val() != 0 ) {
					var com_mid = {
						sec_site_chooser: $(value).find('.sec_site_chooser > option:selected').val(),
						sec_dep_chooser: $(value).find('.sec_dep_chooser > option:selected').val()
					};
					mid.competitors.push(com_mid);
				}
			});
			sets.push(mid);  
		});
		// === prepare selected sets data for backend analyzer (end)

		// === initial sets validation (start)
		console.log("COLLECTED SETS DATA : ", sets);
		var v_status = false;
		for(var i = 0; i < sets.length; i++) {
			if( sets[i]['main_choose_site'] != "0" && sets[i]['main_choose_dep'] != "0" && sets[i]['competitors'].length > 0 ) {
				sets[i]['valid'] = true;
			}
		}
		console.log("COLLECTED SETS DATA AFTER VALIDATION : ", sets);
		// === initial sets validation (end)

		$("#dcsr_control_panel_modal").modal('hide');
		$("#loader_dep_saving_sets").modal('show');
		$.post(base_url + 'index.php/measure/save_dep_rep_comparison_sets', {sets: sets}, function(data) {
			$("#loader_dep_saving_sets").modal('hide');
			console.log("SETS SAVING RESPONSE : ", data);
		});

	}

	function addNewFullRow() {
		$.post(base_url + 'index.php/measure/get_full_dep_rep_comparison_row', {}, function(data) {
			$("#dcsr_control_panel_tabel tbody").append(data);
			saveSetButtonStateScaner();
		});
	}

	function removeFullRow(e) {
		if(confirm('Are you sure?')) {
			var full_row = $(e).parent().parent();
			full_row.remove();
			saveSetButtonStateScaner();
		}
	}

	function removeCompetitorRow(e) {
		var comparison_row = $(e).parent().parent();
		comparison_row.remove();
		saveSetButtonStateScaner();
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
			saveSetButtonStateScaner();
		}); 
	}

	function secSiteChooserHandler(e) {
		var site_id = $(e).val();
		// ==== elements detection (start)
		var sec_dep_dropdown = $(e).next();
		var sec_dep_cnt = $(e).next().next();
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
				sec_dep_cnt.show();
			} else {
				sec_dep_dropdown.hide();
				sec_dep_cnt.hide();
			}
			saveSetButtonStateScaner();
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
			saveSetButtonStateScaner();
		});
	}

</script>