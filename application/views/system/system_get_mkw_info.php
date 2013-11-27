<?php if($results_stack['status']) { ?>

	<div id='meta_kw_pager_holder' class='row-fluid pagination'>
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
						<td><p class='ellipsis_p'><?php echo $v['product_name']; ?></p></td>
						<td>
							<?php if($v['long_seo_phrases']) { ?>
								<table>
										<tbody>
										<?php foreach($v['long_seo_phrases'] as $key => $val) { ?>
											<?php $kw = $val['ph']; $kw_prc = $val['prc']; $kw_count = $val['count']; ?>
											<tr>
												<td style='border-top: none; padding-left: 0px;'><?php echo $val['ph']." (".$val['count'].") - ".$val['prc']."%" ?></td>
												<td style='border-top: none;'><button type='button' onclick="addKeywordToKwSource('')" class='btn btn-primary'>Add</button></td>
											</tr>
										<?php } ?>
										</tbody>
									</table>
							<?php } ?>
							<?php if($v['short_seo_phrases']) { ?>
								<table>
										<tbody>
										<?php foreach($v['short_seo_phrases'] as $key => $val) { ?>
											<tr>
												<td style='border-top: none; padding-left: 0px;'><?php echo $val['ph']." (".$val['count'].") - ".$val['prc']."%" ?></td>
												<td style='border-top: none;'><button type='button' class='btn btn-primary'>Add</button></td>
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
</script>

<?php } else { ?>
	
	<div class='alert'><strong><?php echo $results_stack['msg']; ?></strong></div>

<?php } ?>
