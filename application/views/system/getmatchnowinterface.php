<div class='sc_compare_selection_block' id='sc_compare_selection_block'>

	<div style='display: block;' class='sc_compare_block' id='sc_compare_block'>
		<div class='span5'>
			<div class='well'>
				<input type='hidden' name='get_pc' value="<?php echo $get_random_l['id']; ?>">
				<p class='centered'><span class="label label-success">PRODUCT FOR COMPARE</span></p>
				<p class='centered'><span class="label label-info"><?php echo $get_random_l['customer']; ?></span></p>
				<p class='centered'>
					<?php 
						switch ($get_random_l['customer']) {
							case 'bjs.com':
								$img_c_source = base_url()."/img/bjs-logo.gif";
								break;
							case 'sears.com':
								$img_c_source = base_url()."/img/sears-logo.png";
								break;
							case 'walmart.com':
								$img_c_source = base_url()."/img/walmart-logo.png";
								break;
							case 'staples.com':
								$img_c_source = base_url()."/img/staples-logo.png";
								break;
							case 'overstock.com':
								$img_c_source = base_url()."/img/overstock-logo.png";
								break;
							case 'tigerdirect.com':
								$img_c_source = base_url()."/img/tigerdirect-logo.jpg";
								break;
							
							default:
								$img_c_source = "";
								break;
						}
					?>
					<img src="<?php echo $img_c_source; ?>">
				</p>
				<ul class='nav nav-pills nav-stacked'>
					<li class='active'><a data-id="<?php echo $get_random_l['id']; ?>" href='javascript:void(0)'><?php echo $get_random_l['product_name']; ?></a></li>
				</ul>
				<p class='centered'><span class="label label-success">SHORT DESCRIPTION</span></p>
				<ul class='nav nav-pills nav-stacked'>
					<li><?php echo $get_random_l['description']; ?></li>
				</ul>
				<p class='centered'><span class="label label-success">LONG DESCRIPTION</span></p>
				<ul class='nav nav-pills nav-stacked'>
					<li><?php echo $get_random_l['long_description']; ?></li>
				</ul>
			</div>
		</div>

		<div class='span2'>
			<div class='well'>
				<p class='centered'><span class="label label-info">DECISION</span></p>
				<button id='sccb_notsure_btn' onclick="productCompareDecision(0);" type='button' disabled='true' class='btn btn-success icb_systme_compare_btn margin_bottom disabled'>New</button>
				<button id='sccb_yes_btn' onclick="productCompareDecision(2);" type='button' disabled='true' class='btn btn-primary icb_systme_compare_btn margin_bottom disabled'>Yes</button>
				<button id='sccb_not_btn' onclick="productCompareDecision(1);" type='button' disabled='true' class='btn btn-danger icb_systme_compare_btn disabled'>No</button>
			</div>
		</div>

		<div class='span5'>
			<div class='well'>
				<input type='hidden' name='get_pc' value="<?php echo $get_random_r['id']; ?>">
				<p class='centered'><span class="label label-success">PRODUCT FOR COMPARE</span></p>
				<p class='centered'><span class="label label-info"><?php echo $get_random_r['customer']; ?></span></p>
				<p class='centered'>
					<?php 
						switch ($get_random_r['customer']) {
							case 'bjs.com':
								$img_c_source = base_url()."/img/bjs-logo.gif";
								break;
							case 'sears.com':
								$img_c_source = base_url()."/img/sears-logo.png";
								break;
							case 'walmart.com':
								$img_c_source = base_url()."/img/walmart-logo.png";
								break;
							case 'staples.com':
								$img_c_source = base_url()."/img/staples-logo.png";
								break;
							case 'overstock.com':
								$img_c_source = base_url()."/img/overstock-logo.png";
								break;
							case 'tigerdirect.com':
								$img_c_source = base_url()."/img/tigerdirect-logo.jpg";
								break;
							
							default:
								$img_c_source = "";
								break;
						}
					?>
					<img src="<?php echo $img_c_source; ?>">
				</p>
				<ul class='nav nav-pills nav-stacked'>
					<li class='active'><a data-id="<?php echo $get_random_r['id']; ?>" href='javascript:void(0)'><?php echo $get_random_r['product_name']; ?></a></li>
				</ul>
				<p class='centered'><span class="label label-success">SHORT DESCRIPTION</span></p>
				<ul class='nav nav-pills nav-stacked'>
					<li><?php echo $get_random_r['description']; ?></li>
				</ul>
				<p class='centered'><span class="label label-success">LONG DESCRIPTION</span></p>
				<ul class='nav nav-pills nav-stacked'>
					<li><?php echo $get_random_r['long_description']; ?></li>
				</ul>
			</div>
		</div>

	</div>

</div>

<!-- <div class='sc_compare_block' id='sc_compare_block'>&nbsp;</div> -->

<script type='text/javascript'>

		var systemCompareProductsBaseUrl = base_url + 'index.php/system/getcompareproducts';
		var systemCompareProductsVoteBaseUrl = base_url + 'index.php/system/votecompareproducts';
		var systemCompareDeleteProductsVotedPairBaseUrl = base_url + 'index.php/system/deleteproductsvotedpair';

		function reComparePair(im_pr_f, im_pr_s) {
			cleanAndRestore();
			var ids = [im_pr_f, im_pr_s];
			var render_compare_section = $.post(systemCompareProductsBaseUrl, { ids: ids }, 'html').done(function(data) {
				$("#sc_compare_block").html(data);
				$("#sccb_yes_btn, #sccb_not_btn, #sccb_notsure_btn").removeClass('disabled');
				$("#sccb_yes_btn, #sccb_not_btn, #sccb_notsure_btn").removeAttr('disabled');
				$.scrollTo("#sc_compare_block", 400);
	        });
		}

		function deleteComparePair(id) {
			if(confirm('Are you sure?')) {
				var delete_products_votedpair = $.post(systemCompareDeleteProductsVotedPairBaseUrl, { id: id }, 'json').done(function(data) {

				});
			}
		}

		function productCompareDecision(dec) {
			var ids = [];
			$("input[type='hidden'][name='get_pc']").each(function(index, value) {
				ids.push($(value).val());
			});		
			if(ids.length === 2) {
				var product_compare_decision = $.post(systemCompareProductsVoteBaseUrl, { ids: ids, dec: dec }, 'json').done(function(data) {
					if(data) {
						cleanAndRestore();
						$.scrollTo("#sc_compare_selection_block", 400);
						$("#sc_compare_selection_block .limited_list").scrollTop(0);
					}
		        });
			}
		}

		function renderCompareSection() {
			var ids = [];
			$("#compare_pr_boxer > li > a").each(function(index, value) {
				ids.push($(value).data('id'));
			});
			var render_compare_section = $.post(systemCompareProductsBaseUrl, { ids: ids }, 'html').done(function(data) {
				$("#sc_compare_block").html(data);
				$("#sccb_yes_btn, #sccb_not_btn, #sccb_notsure_btn").removeClass('disabled');
				$("#sccb_yes_btn, #sccb_not_btn, #sccb_notsure_btn").removeAttr('disabled');
				$.scrollTo("#sc_compare_block", 400);
	        });
		}

		function cleanAndRestore() {
			$('#ibc_clean_btn').addClass('disabled');
			$('#ibc_clean_btn').attr('disabled', true);
			$('#ibc_start_btn').addClass('disabled');
			$('#ibc_start_btn').attr('disabled', true);
			$("#compare_pr_boxer").empty();
			$("#select_pr_boxer > li > a").bind('click', selectPrBoxerClickHandler);
			$("#sc_compare_block").empty();
		}

		function moveProductsToCompare() {
			var cli = $("#select_pr_boxer li.active").clone();
			$("#compare_pr_boxer").append(cli);
			$('#ibc_move_btn').addClass('disabled');
			$('#ibc_move_btn').attr('disabled', true);
			$('#ibc_clean_btn').removeClass('disabled');
			$('#ibc_clean_btn').removeAttr('disabled');
			$('#ibc_start_btn').removeClass('disabled');
			$('#ibc_start_btn').removeAttr('disabled');
			$("#select_pr_boxer > li").each(function(index, value) {
				$(value).removeClass('active');
			});
			$("#select_pr_boxer > li > a").unbind('click');
		}
		
		function checkMoveButtonStatus() {
			var act_count = $("#select_pr_boxer li.active").length;
			if(act_count === 2) {
				$('#ibc_move_btn').removeClass('disabled');
				$('#ibc_move_btn').removeAttr('disabled');
			} else {
				$('#ibc_move_btn').addClass('disabled');
				$('#ibc_move_btn').attr('disabled', true);
			}
		}

		$("#select_pr_boxer > li > a").bind('click', selectPrBoxerClickHandler);

		function selectPrBoxerClickHandler(e) {
			var act_count = $("#select_pr_boxer li.active").length;
			var act = $(this).parent('li').hasClass('active');
			if(act === false) { // select product attempt
				if(act_count < 2) {
					$(this).parent('li').addClass('active');
				}
			} else { // cancel selection
				$(this).parent('li').removeClass('active');
			}
			checkMoveButtonStatus();
		}
	
</script>