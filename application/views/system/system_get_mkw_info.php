<?php if($results_stack['status']) { ?>

<div id='meta_kw_pager_holder' class='row-fluid pagination'>
	<div style='margin-bottom: 10px;'>
		<button type='button' onclick="kwSyncAll()" class='btn btn-success'>Sync all</button>&nbsp;&nbsp;&nbsp;<button type='button' onclick="kwSyncCurrentPage()" class='btn btn-success'>Sync current page</button>
	</div>
	<ul id='meta_kw_pager'>
		<?php for($p = 1; $p < $results_stack['pages']; $p++) { ?>
			<?php if($p == $results_stack['cpage']) { ?>
				<li class='active'><a style='border: none' href='javascript:void(0)' data-page="<?php echo $p; ?>"><?php echo $p; ?></a></li>
			<?php } else { ?>
				<li><a style='border: none' href='javascript:void(0)' data-page="<?php echo $p; ?>"><?php echo $p; ?></a></li>
			<?php } ?>
		<?php } ?>
	</ul>
</div>

<div class='row-fluid' id='sk_batches_list_data'>
	<table class='table'>
		<thead>
			<tr>
				<th>Product name</th>
				<th>Keywords</th>
			</tr>
		</thead>
		<tbody>
			<?php foreach($results_stack['data_pager'] as $k => $v) { ?>
				<?php $id = $v['id']; $batch_id = $v['batch_id']; ?>
				<tr>
					<td>
						<?php $url = $v['url']; $imported_data_id = $v['imported_data_id']; ?>
						<p class='ellipsis_p' style='font-size: 12px; font-weight: bold'><?php echo $v['product_name']; ?></p>
						<p class='ellipsis_p' style='font-size: 12px; font-weight: bold'><a target="_blank" href="<?php echo $url ?>"><?php echo $url; ?></a></p>
					</td>
					<td>
						<div <?php if($v_mode_option === 'title') { ?> style='display: block;' <?php } ?> class='title_keys_kw_section n_visible'>
						<p style='font-size: 14px; font-weight: bold;'>Title Keywords:</p>
						<?php if($v['long_seo_phrases']) { ?>
							<table>
								<tbody>
								<?php foreach($v['long_seo_phrases'] as $key => $val) { ?>
									<?php $kw = $val['ph']; $kw_prc = $val['prc']; $kw_count = $val['count']; ?>
									<?php $check_meta_status = $statistics_new_model->check_keyword_kw_source($id, $batch_id, $kw); ?>
									<input type='hidden' value="<?php echo $check_meta_status; ?>">
									<tr>
										<?php 
											$pkey_class = 'ellipsis_pkey';
											if($check_meta_status['status']) $pkey_class = 'ellipsis_pkey';
										?>
										<td style='border-top: none; padding-left: 0px;'><p class="<?php echo $pkey_class; ?>"><span style='font-size: 12px; font-weight: bold'><?php echo $val['ph']." (".$val['count'].") - ".$val['prc']."%" ?></span></p></td>
										<td style='border-top: none;'>
										<div class='overall_controls_holder'>
											<?php if($check_meta_status['status']) { ?>
											<?php $last_id = $check_meta_status['last_id']; ?>
											<div style='display: inline-block; margin-bottom: 5px;' class='action_btn_holder'><button type='button' disabled class='btn btn-success disabled'>Inside</button></div>
											<div style='display: inline-block; margin-bottom: 5px;'>
                                                                                            <button type='button' onclick="kwSyncMetaPersonal('<?php echo $last_id; ?>', this)" class='btn btn-success'>Sync</button>
                                                                                            <button type="button" onclick="kwSyncMetaPersonalQueue('<?php echo $last_id; ?>','<?php echo $kw; ?>' ,'<?php echo $url; ?>' , this)" class="btn btn-success" style="height: 30px;" ><i class="icon-plus icon-white"></i></button>
                                                                                        </div>
											<div style='display: inline-block; margin-bottom: 5px;'><button type='button' onclick="kwExploreMetaPersonal('<?php echo $last_id; ?>')" class='btn btn-success'>Explore</button></div>
											<div style='display: inline-block;'><button type='button' onclick="kwDeleteMetaPersonal('<?php echo $last_id; ?>', this)" class='btn btn-danger'>Delete</button></div>
											<?php } else { ?>
											<div class='action_btn_holder'><button type='button' onclick="addKeywordToKwSource(this, '<?php echo $id; ?>', '<?php echo $batch_id; ?>', '<?php echo $kw; ?>', '<?php echo $kw_prc; ?>', '<?php echo $kw_count; ?>', '<?php echo $url; ?>', '<?php echo $imported_data_id; ?>')" class='btn btn-primary'>Add</button></div>
											<?php } ?>
										</div>
										</td>
									</tr>
								<?php } ?>
								</tbody>
							</table>
						<?php } ?>
						<?php if($v['short_seo_phrases']) { ?>
							<table>
								<tbody>
								<?php foreach($v['short_seo_phrases'] as $key => $val) { ?>
									<?php $kw = $val['ph']; $kw_prc = $val['prc']; $kw_count = $val['count']; ?>
									<?php $check_meta_status = $statistics_new_model->check_keyword_kw_source($id, $batch_id, $kw); ?>
									<input type='hidden' value="<?php echo $check_meta_status; ?>">
									<tr>
										<?php 
											$pkey_class = 'ellipsis_pkey';
											if($check_meta_status['status']) $pkey_class = 'ellipsis_pkey';
										?>
										<td style='border-top: none; padding-left: 0px;'><p class="<?php echo $pkey_class; ?>"><span style='font-size: 12px; font-weight: bold'><?php echo $val['ph']." (".$val['count'].") - ".$val['prc']."%" ?></span></p></td>
										<td style='border-top: none;'>
											<div class='overall_controls_holder'>
												<?php if($check_meta_status['status']) { ?>
												<?php $last_id = $check_meta_status['last_id']; ?>
												<div style='display: inline-block; margin-bottom: 5px;' class='action_btn_holder'><button type='button' disabled class='btn btn-success disabled'>Inside</button></div>
												<div style='display: inline-block; margin-bottom: 5px;'>
                                                                                                    <button type='button' onclick="kwSyncMetaPersonal('<?php echo $last_id; ?>', this)" class='btn btn-success'>Sync</button>
                                                                                                    <button type="button" onclick="kwSyncMetaPersonalQueue('<?php echo $last_id; ?>', this)" class="btn btn-success" style="height: 30px;" ><i class="icon-plus icon-white"></i></button>
                                                                                                </div>
												<div style='display: inline-block; margin-bottom: 5px;'><button type='button' onclick="kwExploreMetaPersonal('<?php echo $last_id; ?>', this)" class='btn btn-success'>Explore</button></div>
												<div style='display: inline-block;'><button type='button' onclick="kwDeleteMetaPersonal('<?php echo $last_id; ?>', this)" class='btn btn-danger'>Delete</button></div>
												<?php } else { ?>
												<div class='action_btn_holder'><button type='button' onclick="addKeywordToKwSource(this, '<?php echo $id; ?>', '<?php echo $batch_id; ?>', '<?php echo $kw; ?>', '<?php echo $kw_prc; ?>', '<?php echo $kw_count; ?>', '<?php echo $url; ?>', '<?php echo $imported_data_id; ?>')" class='btn btn-primary'>Add</button></div>
												<?php } ?>
											</div>
										</td>
									</tr>
								<?php } ?>
								</tbody>
							</table>
						<?php } ?>
						</div>

						<div <?php if($v_mode_option === 'meta') { ?> style='display: block;' <?php } ?> class='meta_keys_kw_section n_visible'>
						<p style='font-size: 14px; font-weight: bold;'>Meta Keywords:</p>
						<?php if($v['meta']['short_meta']) { ?>
							<table>
								<tbody>
								<?php foreach($v['meta']['short_meta'] as $key => $val) { ?>
									<?php $kw = $val['ph']; $kw_prc = $val['prc']; $kw_count = $val['count']; ?>
									<?php $check_meta_status = $statistics_new_model->check_keyword_kw_source($id, $batch_id, $kw); ?>
									<input type='hidden' value="<?php echo $check_meta_status; ?>">
									<tr>
										<?php 
											$pkey_class = 'ellipsis_pkey';
											if($check_meta_status['status']) $pkey_class = 'ellipsis_pkey';
										?>
										<td style='border-top: none; padding-left: 0px;'><p class="<?php echo $pkey_class; ?>"><span style='font-size: 12px; font-weight: bold'><?php echo $val['ph']." (".$val['count'].") - ".$val['prc']."%" ?></span></p></td>
										<td style='border-top: none;'>
											<div class='overall_controls_holder'>
												<?php if($check_meta_status['status']) { ?>
												<?php $last_id = $check_meta_status['last_id']; ?>
												<div style='display: inline-block; margin-bottom: 5px;' class='action_btn_holder'><button type='button' disabled class='btn btn-success disabled'>Inside</button></div>
												<div style='display: inline-block; margin-bottom: 5px;'>
                                                                                                    <button type='button' onclick="kwSyncMetaPersonal('<?php echo $last_id; ?>', this)" class='btn btn-success'>Sync</button>
                                                                                                    <button type="button" onclick="kwSyncMetaPersonalQueue('<?php echo $last_id; ?>', this)" class="btn btn-success" style="height: 30px;" ><i class="icon-plus icon-white"></i></button>
                                                                                                </div>
												<div style='display: inline-block; margin-bottom: 5px;'><button type='button' onclick="kwExploreMetaPersonal('<?php echo $last_id; ?>', this)" class='btn btn-success'>Explore</button></div>
												<div style='display: inline-block;'><button type='button' onclick="kwDeleteMetaPersonal('<?php echo $last_id; ?>', this)" class='btn btn-danger'>Delete</button></div>
												<?php } else { ?>
												<div class='action_btn_holder'><button type='button' onclick="addKeywordToKwSource(this, '<?php echo $id; ?>', '<?php echo $batch_id; ?>', '<?php echo $kw; ?>', '<?php echo $kw_prc; ?>', '<?php echo $kw_count; ?>', '<?php echo $url; ?>', '<?php echo $imported_data_id; ?>')" class='btn btn-primary'>Add</button></div>
												<?php } ?>
											</div>
										</td>
									</tr>
								<?php } ?>
								</tbody>
							</table>
						<?php } ?>
						<?php if($v['meta']['long_meta']) { ?>
							<table>
								<tbody>
								<?php foreach($v['meta']['long_meta'] as $key => $val) { ?>
									<?php $kw = $val['ph']; $kw_prc = $val['prc']; $kw_count = $val['count']; ?>
									<?php $check_meta_status = $statistics_new_model->check_keyword_kw_source($id, $batch_id, $kw); ?>
									<input type='hidden' value="<?php echo $check_meta_status; ?>">
									<tr>
										<?php 
											$pkey_class = 'ellipsis_pkey';
											if($check_meta_status['status']) $pkey_class = 'ellipsis_pkey';
										?>
										<td style='border-top: none; padding-left: 0px;'><p class="<?php echo $pkey_class; ?>"><span style='font-size: 12px; font-weight: bold'><?php echo $val['ph']." (".$val['count'].") - ".$val['prc']."%" ?></span></p></td>
										<td style='border-top: none;'>
											<div class='overall_controls_holder'>
												<?php if($check_meta_status['status']) { ?>
												<?php $last_id = $check_meta_status['last_id']; ?>
												<div style='display: inline-block; margin-bottom: 5px;' class='action_btn_holder'><button type='button' disabled class='btn btn-success disabled'>Inside</button></div>
												<div style='display: inline-block; margin-bottom: 5px;'>
                                                                                                    <button type='button' onclick="kwSyncMetaPersonal('<?php echo $last_id; ?>', this)" class='btn btn-success'>Sync</button>
                                                                                                    <button type="button" onclick="kwSyncMetaPersonalQueue('<?php echo $last_id; ?>', this)" class="btn btn-success" style="height: 30px;" ><i class="icon-plus icon-white"></i></button>
                                                                                                </div>
												<div style='display: inline-block; margin-bottom: 5px;'><button type='button' onclick="kwExploreMetaPersonal('<?php echo $last_id; ?>', this)" class='btn btn-success'>Explore</button></div>
												<div style='display: inline-block;'><button type='button' onclick="kwDeleteMetaPersonal('<?php echo $last_id; ?>', this)" class='btn btn-danger'>Delete</button></div>
												<?php } else { ?>
												<div class='action_btn_holder'><button type='button' onclick="addKeywordToKwSource(this, '<?php echo $id; ?>', '<?php echo $batch_id; ?>', '<?php echo $kw; ?>', '<?php echo $kw_prc; ?>', '<?php echo $kw_count; ?>', '<?php echo $url; ?>', '<?php echo $imported_data_id; ?>')" class='btn btn-primary'>Add</button></div>
												<?php } ?>
											</div>
										</td>
									</tr>
								<?php } ?>
								</tbody>
							</table>
						<?php } ?> 
						</div>

					</td>
				</tr>
			<?php } ?>
		</tbody>
	</table>
</div>

<div class="modal hide fade ci_hp_modals crawl_launch_panel" id='recipients_control_panel_modal'></div>

<div class="modal hide fade ci_hp_modals crawl_launch_panel" id='explore_meta_personal_modal'>
	<div class="modal-header">
		<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
		<h3>Rankings Explore Panel</h3>
	</div>
	<div class="modal-body">
		<div id='explore_meta_personal_data_holder'>

		</div>
	</div>
	<div class="modal-footer">
		<a href="javascript:void(0)" class="btn" data-dismiss="modal">Close</a>
	</div>
</div>

<script type='text/javascript'>
	
	function kwSyncAll() {
		$("#explore_meta_personal_modal").modal('show');
		$.post(base_url + 'index.php/system/kw_sync_all', function(data) {
			$("#explore_meta_personal_modal").modal('hide');
		});
	}

	function kwSyncCurrentPage() {
		var cpage = $("#meta_kw_pager > li.active > a").attr('data-page');
		$("#explore_meta_personal_modal").modal('show');
		
		$.post(base_url + 'index.php/system/kw_sync_current_page', {'cpage': cpage}, function(data) {
			$("#explore_meta_personal_modal").modal('hide');
		});
	}

	function kwExploreMetaPersonal(id, e) {
		$.post(base_url + 'index.php/system/explore_meta_personal', {'id': id}, function(data) {
        if(data.status) {
        	$("#explore_meta_personal_modal").modal('show');
        	$("#explore_meta_personal_modal #explore_meta_personal_data_holder").html("");
        	var rank_json_encode = $.parseJSON(data.res.rank_json_encode);
        	var highest_rank = $.parseJSON(data.res.highest_rank);
        	// ===== RENDER HIGHEST RANKING DATA (START)
        	var highest_rank_content = "";
        	if(typeof(highest_rank) !== 'undefined' && highest_rank !== null && _.isObject(highest_rank)) {
        		highest_rank_content += "<p class='font-size: 14px; font-weight: bold'>Highest ranking:</p>";
        		highest_rank_content += "<table class='table'>";
	        	highest_rank_content += "<thead>";
	        	highest_rank_content += "<tr>";
	        	highest_rank_content += "<th>Ranking</th>";
	        	highest_rank_content += "<th>Rankedurl</th>";
	        	highest_rank_content += "<th>Datetime</th>";
	        	highest_rank_content += "</tr>";
	        	highest_rank_content += "</thead>";
	        	highest_rank_content += "<tbody>";
	        	highest_rank_content += "<tr>";
	        	var hrc_ranking = highest_rank.ranking;
	        	if(hrc_ranking == null) hrc_ranking = "not indexed";
	        	var hrc_rankedurl = highest_rank.rankedurl;
	        	if(hrc_rankedurl == null) hrc_rankedurl = "no data";
	        	highest_rank_content += "<td>" + hrc_ranking + "</td>";
	        	highest_rank_content += "<td>" + hrc_rankedurl + "</td>";
	        	highest_rank_content += "<td>" + moment.unix(highest_rank.datetime).format('MMMM Do, YYYY') + "</td>";
	        	highest_rank_content += "</tr>";
	        	highest_rank_content += "</tbody></table>";
        	} else {
        		highest_rank_content += "<p class='font-size: 14px; font-weight: bold'>Highest ranking:</p>";
        		highest_rank_content += "<p>no data</p>";
        	}
        	$("#explore_meta_personal_modal #explore_meta_personal_data_holder").append(highest_rank_content);
        	// ===== RENDER HIGHEST RANKING DATA (END)
        	// ===== RENDER OVERALL RANKING DATA (START)
        	var regular_rank_content = "";
        	if(typeof(rank_json_encode) !== 'undefined' && rank_json_encode !== null && (rank_json_encode.length > 0 || _.isObject(rank_json_encode))) {
        		regular_rank_content += "<p class='font-size: 14px; font-weight: bold'>Overall rankings:</p>";
        		regular_rank_content += "<table class='table'>";
	        	regular_rank_content += "<thead>";
	        	regular_rank_content += "<tr>";
	        	regular_rank_content += "<th>Ranking</th>";
	        	regular_rank_content += "<th>Rankedurl</th>";
	        	regular_rank_content += "<th>Datetime</th>";
	        	regular_rank_content += "</tr>";
	        	regular_rank_content += "</thead>";
	        	regular_rank_content += "<tbody>";
	        	for(var i = 0; i < rank_json_encode.length; i++) {
	        		regular_rank_content += "<tr>";
	        		var rrc_ranking = rank_json_encode[i].ranking;
	        		if(rrc_ranking == null) rrc_ranking = "not indexed";
	        		regular_rank_content += "<td>" + rrc_ranking + "</td>";
	        		var rrc_rankedurl = rank_json_encode[i].rankedurl;
		        	if(rrc_rankedurl == null) rrc_rankedurl = "no data";
		        	regular_rank_content += "<td>" + rrc_rankedurl + "</td>";
		        	regular_rank_content += "<td>" + moment.unix(rank_json_encode[i].datetime).format('MMMM Do, YYYY') + "</td>";
	        		regular_rank_content += "</tr>";
	        	}
	        	regular_rank_content += "</tbody></table>";
        	} else {
        		regular_rank_content += "<p class='font-size: 14px; font-weight: bold'>Overall rankings:</p>";
        		regular_rank_content += "<p>no data</p>";
        	}
        	$("#explore_meta_personal_modal #explore_meta_personal_data_holder").append(regular_rank_content);
        	// ===== RENDER OVERALL RANKING DATA (END)
        } else {
        	alert('Keyword ranking source not finded');
        }
    });
	}

	function kwSyncMetaPersonal(id, e) {
		$(e).addClass('disabled');
		$(e).attr('disabled', true);
		$.post(base_url + 'index.php/system/sync_meta_personal', {'id': id}, function(data) {
        $(e).removeClass('disabled');
        $(e).removeAttr('disabled');
        console.log(data);
    });
	}

	function kwDeleteMetaPersonal(id, e) {
		if(confirm('Are you sure?')) {
			$.post(base_url + 'index.php/system/delete_keyword_from_kw_source', {'id': id}, function(data) {
	        $(e).parent().remove();
	    });
		}
	}

	function getMetaKeysBatchData(bid, cpage) {
      cpage = parseInt(cpage);
      var v_mode_option = $("#kw_show_words_mode > option:selected").val();
      $.post(base_url + 'index.php/system/system_get_mkw_info', {'bid': bid, 'cpage': cpage, 'v_mode_option': v_mode_option}, function(d) {
          $("#loading_kw_meta_selection").modal('hide');
          $("#overall_meta_kw_pager_holder").html(d);
      });
  }
	$("#meta_kw_pager > li > a:not('active')").click(function(e) {
			$("#loading_kw_meta_selection").modal('show');
      var pi = $(e.target).data('page');
      var bid = $("#sk_batches_list > option:selected").val();
      getMetaKeysBatchData(bid, pi);
  });
	function addKeywordToKwSource(e, id, batch_id, kw, kw_prc, kw_count, url, imported_data_id) {
		var btn_holder = $(e).parent().parent();
		var send_object = {
			'id': id,
			'batch_id': batch_id,
			'kw': kw,
			'kw_prc': kw_prc,
			'kw_count': kw_count,
			'url': url,
			'imported_data_id': imported_data_id
		};
		$.post(base_url + 'index.php/system/add_keyword_to_kw_source', send_object, function(data) {
        console.log(data);
        if(data.status) {
        	btn_holder.html('<div style="display: inline-block; margin-bottom: 5px;" class="action_btn_holder"><button type="button" disabled class="btn btn-success disabled">Inside</button></div>&nbsp;<div style="display: inline-block; margin-bottom: 5px;"><button type="button" onclick="kwSyncMetaPersonal(\''+data.last_id+'\', this)" class="btn btn-success">Sync</button><button type="button" onclick="kwSyncMetaPersonalQueue(\''+data.last_id+'\', this)" class="btn btn-success" style="height: 30px;" ><i class="icon-plus icon-white"></i></button></div>&nbsp;<div style="display: inline-block; margin-bottom: 5px;"><button type="button" onclick="kwExploreMetaPersonal(\''+data.last_id+'\', this)" class="btn btn-success">Explore</button></div>&nbsp;<div style="display: inline-block;"><button type="button" onclick="kwDeleteMetaPersonal(\''+data.last_id+'\', this)" class="btn btn-danger">Delete</button></div>');
        } else {
        	alert(data.msg);
        }
    });
	}
         function kwSyncMetaPersonalQueue(id, kw, url,obj){
            $.ajax({
                type: 'POST',
                url: base_url + 'index.php/system/set_kwsync_queue',
                data: {id: id, kw: kw, url: url}
            }).done(function(data){
                console.log(data);
            });
         }

</script>

<?php } else { ?>
	
	<div class='alert'><strong><?php echo $results_stack['msg']; ?></strong></div>

<?php } ?>
