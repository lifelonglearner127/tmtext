<div class="row-fluid">
	<div class="span9 offset2">
		<div class="login_container" style="margin-top: 5%;">
			<div class="login_header">
				<h3 class="text-center">Ranking API Debugger</h3>
			</div>
			<div class="login_content">
				<div class='debug_seo_ph'>

					<form id='add_rank_form' class="form-horizontal" method='post' action='' enctype="multipart/form-data">
			      <div class="control-group">
			        <label class="control-label" for="ar_url">Url</label>
			        <div class="controls">
			          <input type="text" id="ar_url" placeholder="Email">
			          <p id='fe_ar_url' class='help-block form_error'>&nbsp;</p>
			        </div>
			      </div>
			      <div class="control-group">
			        <label class="control-label" for="ar_keyw">Keyword</label>
			        <div class="controls">
			          <input type="text" id="ar_keyw" placeholder="Password">
			          <p id='fe_ar_keyw' class='help-block form_error'>&nbsp;</p>
			        </div>
			      </div>
			      <div class="control-group">
			        <div class="controls">
			          <button type="submit" onclick='return addRankingData()' class="btn btn-primary">Add keyword/url pair</button>
			        </div>
			      </div>
			    </form>
					<div class='debug_seo_ph_res'>
						<p class='h'>Current tracking www.serpranktracker.com data:</p>
						<?php if(isset($track_data) && isset($track_data->data) && count($track_data->data) > 0) { ?>
							<?php foreach($track_data->data as $k => $v) { ?>
								<div class="alert"><?php echo $v->site; ?> <?php if(!isset($v->keywords) || count($v->keywords) == 0) { ?>(no data)<?php } ?></div>
								<?php if(isset($v->keywords) && count($v->keywords) > 0) { ?>
									<table class='table'>
										<thead>
											<tr>
												<th>keyword</th>
												<th>location</th>
												<th>engine</th>
												<th>ranking</th>
												<th>control</th>
											</tr>
										</thead>
										<tbody>
											<?php foreach($v->keywords as $ks => $kv) { ?>
												<tr>
													<td><?php echo $kv->keyword; ?></td>
													<td><?php echo $kv->location; ?></td>
													<td><?php echo $kv->searchengine; ?></td>
													<td>
														<?php if(isset($kv->rankings) && count($kv->rankings) > 0) { ?>
															<?php foreach($kv->rankings as $ks => $vs) { ?>
																<p><span>Ranking: </span><span><?php echo $vs->ranking ?></span></p>
																<p><span>Ranked url: </span><span><?php echo $vs->rankedurl ?></span></p>
																<p><span>Date: </span><span><?php echo date('F jS, Y', $vs->datetime) ?></span></p>
															<?php } ?>
															<?php } else { ?>
																<p>no ranking data</p>
															<?php } ?>
													</td>
													<td><button type='button' class='btn btn-danger'>Delete</button></td>
												</tr>
											<?php } ?>
										</tbody>
									</table>
								<?php } ?>
							<?php } ?>
						<?php } ?>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>

<script type="text/javascript">
	function addRankingData() {
		$("#add_rank_form .form_error").text("");
		$("#add_rank_form .form_error").hide();
		var url_regex = /^(https?|ftp):\/\/(((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?(((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?)(:\d*)?)(\/((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)?(\?((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\uE000-\uF8FF]|\/|\?)*)?(\#((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?$/i;
		var url = $.trim($("#ar_url").val());
		var key_word = $.trim($("#ar_keyw").val());
		if(!url_regex.test(url) || key_word === "") {
			if(!url_regex.test(url)) {
				$("#fe_ar_url").text("Incorrect url format");
				$("#fe_ar_url").fadeOut('medium', function() {
					$("#fe_ar_url").fadeIn('medium');
				})
			}
			if(key_word === "") {
				$("#ar_keyw").text("Incorrect url format");
				$("#ar_keyw").fadeOut('medium', function() {
					$("#ar_keyw").fadeIn('medium');
				})
			}
		} else {
			var send_data = {
				url: url,
				key_word: key_word
			} 
			$.post(base_url + "index.php/measure/debug_ranking_data", send_data, 'json').done(function(a_data) {
				location.reload();
				// console.log('DEBUG RANKING DATA : ', a_data);
      });
		}
		return false;
	}
</script>