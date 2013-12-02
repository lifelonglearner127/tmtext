<?php if($results_stack['status']) { ?>

	<div id='meta_kw_pager_holder' class='row-fluid pagination'>
		<div style='margin-bottom: 10px;'>
			<button type='button' class='btn btn-success'>Sync all</button>&nbsp;&nbsp;&nbsp;<button type='button' class='btn btn-success'>Sync current page</button>
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
							<?php $url = $v['url']; ?>
							<p class='ellipsis_p' style='font-size: 12px; font-weight: bold'><?php echo $v['product_name']; ?></p>
							<p class='ellipsis_p' style='font-size: 12px; font-weight: bold'><a target="_blank" href="<?php echo $url ?>"><?php echo $url; ?></a></p>
						</td>
						<td>
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
													<div style='display: inline-block; margin-bottom: 5px;'><button type='button' onclick="kwSyncMetaPersonal('<?php echo $last_id; ?>', this)" class='btn btn-success'>Sync</button></div>
													<div style='display: inline-block; margin-bottom: 5px;'><button type='button' onclick="kwExploreMetaPersonal('<?php echo $last_id; ?>')" class='btn btn-success'>Explore</button></div>
													<div style='display: inline-block;'><button type='button' onclick="kwDeleteMetaPersonal('<?php echo $last_id; ?>', this)" class='btn btn-danger'>Delete</button></div>
													<?php } else { ?>
													<div class='action_btn_holder'><button type='button' onclick="addKeywordToKwSource(this, '<?php echo $id; ?>', '<?php echo $batch_id; ?>', '<?php echo $kw; ?>', '<?php echo $kw_prc; ?>', '<?php echo $kw_count; ?>', '<?php echo $url; ?>')" class='btn btn-primary'>Add</button></div>
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
														<div style='display: inline-block; margin-bottom: 5px;'><button type='button' onclick="kwSyncMetaPersonal('<?php echo $last_id; ?>', this)" class='btn btn-success'>Sync</button></div>
														<div style='display: inline-block; margin-bottom: 5px;'><button type='button' onclick="kwExploreMetaPersonal('<?php echo $last_id; ?>')" class='btn btn-success'>Explore</button></div>
														<div style='display: inline-block;'><button type='button' onclick="kwDeleteMetaPersonal('<?php echo $last_id; ?>', this)" class='btn btn-danger'>Delete</button></div>
														<?php } else { ?>
														<div class='action_btn_holder'><button type='button' onclick="addKeywordToKwSource(this, '<?php echo $id; ?>', '<?php echo $batch_id; ?>', '<?php echo $kw; ?>', '<?php echo $kw_prc; ?>', '<?php echo $kw_count; ?>', '<?php echo $url; ?>')" class='btn btn-primary'>Add</button></div>
														<?php } ?>
													</div>
												</td>
											</tr>
										<?php } ?>
										</tbody>
									</table>
							<?php } ?>
						</td>
					</tr>
				<?php } ?>
			</tbody>
		</table>
	</div>

<script type='text/javascript'>
	
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
      $.post(base_url + 'index.php/system/system_get_mkw_info', {'bid': bid, 'cpage': cpage}, function(d) {
          $("#loading_kw_meta_selection").modal('hide');
          $("#overall_meta_kw_pager_holder").html(d);
      });
  }
	$("#meta_kw_pager > li > a:not('active')").click(function(e) {
      var pi = $(e.target).data('page');
      var bid = $("#sk_batches_list > option:selected").val();
      getMetaKeysBatchData(bid, pi);
  });
	function addKeywordToKwSource(e, id, batch_id, kw, kw_prc, kw_count, url) {
		var btn_holder = $(e).parent().parent();
		var send_object = {
			'id': id,
			'batch_id': batch_id,
			'kw': kw,
			'kw_prc': kw_prc,
			'kw_count': kw_count,
			'url': url
		};
		$.post(base_url + 'index.php/system/add_keyword_to_kw_source', send_object, function(data) {
        console.log(data);
        if(data.status) {
        	btn_holder.html('<div style="display: inline-block; margin-bottom: 5px;" class="action_btn_holder"><button type="button" disabled class="btn btn-success disabled">Inside</button></div>&nbsp;<div style="display: inline-block; margin-bottom: 5px;"><button type="button" onclick="kwSyncMetaPersonal(\''+data.last_id+'\', this)" class="btn btn-success">Sync</button></div>&nbsp;<div style="display: inline-block; margin-bottom: 5px;"><button type="button" onclick="kwExploreMetaPersonal(\''+data.last_id+'\')" class="btn btn-success">Explore</button></div>&nbsp;<div style="display: inline-block;"><button type="button" onclick="kwDeleteMetaPersonal(\''+data.last_id+'\', this)" class="btn btn-danger">Delete</button></div>');
        } else {
        	alert(data.msg);
        }
    });
	}

</script>

<?php } else { ?>
	
	<div class='alert'><strong><?php echo $results_stack['msg']; ?></strong></div>

<?php } ?>
