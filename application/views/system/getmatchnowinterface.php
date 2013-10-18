<div class='sc_compare_selection_block' id='sc_compare_selection_block'>

	<!-- <div style='margin-bottom: 20px;'>
		<input type='text' id='pci_attr_test_s' name='pci_attr_test_s'><br>
		<button type='button' class='btn' onclick="testAttributesExt();" >Test Attributes Extractor</button>
	</div> -->

	<div style='display: block;' class='sc_compare_block' id='sc_compare_block'>
		<div id='pci_l_section' class='span5'>
			<!-- <div id="dd_drop_random_l"></div> -->
			<div class='well'>
				<input type='hidden' name='random_l_hidden_c' value="<?php echo $get_random_l['customer']; ?>">
				<input type='hidden' id='get_pc_l' name='get_pc' value="<?php echo $get_random_l['id']; ?>">
				<p class='centered'><span class="label label-success">PRODUCT FOR COMPARE</span></p>
				<p class='centered'><span class="label label-info"><?php echo $get_random_l['customer']; ?></span></p>
				<p class='centered'>
					<?php 
						switch ($get_random_l['customer']) {
							case 'bjs.com':
								$img_c_source = base_url()."img/bjs-logo.gif";
								break;
							case 'sears.com':
								$img_c_source = base_url()."img/sears-logo.png";
								break;
							case 'walmart.com':
								$img_c_source = base_url()."img/walmart-logo.png";
								break;
							case 'staples.com':
								$img_c_source = base_url()."img/staples-logo.png";
								break;
							case 'overstock.com':
								$img_c_source = base_url()."img/overstock-logo.png";
								break;
							case 'tigerdirect.com':
								$img_c_source = base_url()."img/tigerdirect-logo.jpg";
								break;
                            case 'amazon.com':
                                $img_c_source = base_url(). "img/amazon-logo.jpg";
                                break;
							
							default:
								$img_c_source = "";
								break;
						}
					?>
					<img src="<?php echo $img_c_source; ?>">
				</p>
				<ul class='nav nav-pills nav-stacked'>
					<li class='active'><a class='pfc_link_l' data-id="<?php echo $get_random_l['id']; ?>" target="_blank" href="<?php echo $get_random_l['url']; ?>"><?php echo $get_random_l['product_name']; ?></a></li>
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
				<button id='sccb_newset_btn' onclick="productCompareNewSet();" type='button' class='btn btn-success icb_systme_compare_btn margin_bottom'>New</button>
				<button id='sccb_yes_btn' onclick="productCompareDecision(2);" type='button' class='btn btn-primary icb_systme_compare_btn margin_bottom'>Yes</button>
				<button id='sccb_not_btn' onclick="productCompareDecision(1);" type='button' class='btn btn-danger icb_systme_compare_btn'>No</button>
			</div>
		</div>

		<div id='pci_r_section' class='span5'>
			<!-- <div id="dd_drop_random_r"></div> -->
			<div class='well'>
				<input type='hidden' name='random_r_hidden_c' value="<?php echo $get_random_r['customer']; ?>">
				<input type='hidden' id='get_pc_r' name='get_pc' value="<?php echo $get_random_r['id']; ?>">
				<p class='centered'><span class="label label-success">PRODUCT FOR COMPARE</span></p>
				<p class='centered'><span class="label label-info"><?php echo $get_random_r['customer']; ?></span></p>
				<p class='centered'>
					<?php 
						switch ($get_random_r['customer']) {
							case 'bjs.com':
								$img_c_source = base_url()."img/bjs-logo.gif";
								break;
							case 'sears.com':
								$img_c_source = base_url()."img/sears-logo.png";
								break;
							case 'walmart.com':
								$img_c_source = base_url()."img/walmart-logo.png";
								break;
							case 'staples.com':
								$img_c_source = base_url()."img/staples-logo.png";
								break;
							case 'overstock.com':
								$img_c_source = base_url()."img/overstock-logo.png";
								break;
							case 'tigerdirect.com':
								$img_c_source = base_url()."img/tigerdirect-logo.jpg";
								break;
                            case 'amazon.com':
                                $img_c_source = base_url(). "img/amazon-logo.jpg";
                                break;
							default:
								$img_c_source = "";
								break;
						}
					?>
					<img src="<?php echo $img_c_source; ?>">
				</p>
				<ul class='nav nav-pills nav-stacked'>
					<li class='active'><a class='pfc_link_r' data-id="<?php echo $get_random_r['id']; ?>" target="_blank" href="<?php echo $get_random_r['url']; ?>"><?php echo $get_random_r['product_name']; ?></a></li>
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

<script type='text/javascript'>

		// function testAttributesExt() {
		// 	var desc = $("#pci_attr_test_s").val();
		// 	var test_attr_ext = $.post(base_url + 'index.php/system/testattributesext', { desc: desc }, 'json').done(function(data) {
		// 		console.log("ATTRIBUTES EXT TEST RES: ", data);
		// 	});
		// }

		$(document).ready(function(e) {
			// ---- UI tooltips (start)
			$("#sccb_newset_btn").tooltip({
				placement: 'left',
				title: 'Load new set'
			});
			$("#sccb_yes_btn").tooltip({
				placement: 'left',
				title: 'Mark as similar'
			});
			$("#sccb_not_btn").tooltip({
				placement: 'bottom',
				title: 'Mark as different'
			});
			$(".pfc_link_l").tooltip({
				placement: 'left',
				title: 'Press to visit product page'
			});
			$(".pfc_link_r").tooltip({
				placement: 'right',
				title: 'Press to visit product page'
			});
			// ---- UI tooltips (end)
		});

		var systemCompareProductsBaseUrl = base_url + 'index.php/system/getcompareproducts';
		var systemCompareProductsVoteBaseUrl = base_url + 'index.php/system/votecompareproducts';
		var systemCompareDeleteProductsVotedPairBaseUrl = base_url + 'index.php/system/deleteproductsvotedpair';
		var reNewCompareRightSideBaseUrl = base_url + 'index.php/system/renewcomparerightside';
		var reNewAllCompareSidesBaseUrl = base_url + 'index.php/system/renewallcomparesides';
		var reNewCompareRightSideFromDropdownBaseUrl = base_url + 'index.php/system/renewcomparerightsidefromdropdown';

		function initCustomersPciDropdownRight() {
			var ddData_grids_r_current = $("input[type='hidden'][name='random_r_hidden_c']").val();
			setTimeout(function(){
                var customers_list = $.post(base_url + 'index.php/measure/getcustomerslist_new', {}, function(c_data) {
                    var dd_right = $('#dd_drop_random_r').msDropDown({byJson:{data:c_data}}).data("dd");
                    if(dd_right != undefined){
                        dd_right.setIndexByValue(ddData_grids_r_current);
                    }
                });
            }, 500);

		}

		function initCustomersPciDropdowns() {
			var ddData_grids_l_current = $("input[type='hidden'][name='random_l_hidden_c']").val();
			var ddData_grids_r_current = $("input[type='hidden'][name='random_r_hidden_c']").val();
            var ddData_grids_r_current = $("input[type='hidden'][name='random_r_hidden_c']").val();
            setTimeout(function(){
                var customers_list = $.post(base_url + 'index.php/measure/getcustomerslist_new', {}, function(c_data) {
                    var dd_left = $('#dd_drop_random_l').msDropDown({byJson:{data:c_data}}).data("dd");
                    if(dd_left != undefined){
                        dd_left.setIndexByValue(ddData_grids_l_current);
                    }
                    var dd_right = $('#dd_drop_random_r').msDropDown({byJson:{data:c_data}}).data("dd");
                    if(dd_right != undefined){
                        dd_right.setIndexByValue(ddData_grids_r_current);
                    }
                });
            }, 500);
		}
		// initCustomersPciDropdowns();

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

		function productCompareNewSet() {
			var renew_all_compare_sides = $.post(reNewAllCompareSidesBaseUrl, {}, 'html').done(function(data) {
				if(data) {
					$("#sc_compare_block").html(data);
					setTimeout(function() {
						initCustomersPciDropdowns();
					}, 500);
				}
	        });
		}

		function productCompareDecision(dec) { // 2- yes, 1 - no 
			var ids = [];
			$("input[type='hidden'][name='get_pc']").each(function(index, value) {
				ids.push($(value).val());
			});		
			if(ids.length === 2) {
				var product_compare_decision = $.post(systemCompareProductsVoteBaseUrl, { ids: ids, dec: dec }, 'json').done(function(data) {
					if(data) {
						var customer_l = $("input[type='hidden'][name='random_l_hidden_c']").val();
						var id_l = $("input[type='hidden'][name='get_pc'][id='get_pc_l']").val();
						reNewCompareRightSide(customer_l, id_l);
					}
		        });
			}
		}

		function reNewCompareRightSide(customer_l, id_l) {
			// $(".preloader_grids_box_pci").show();
			var renew_compare_rightside = $.post(reNewCompareRightSideBaseUrl, { customer_l: customer_l, id_l: id_l }, 'html').done(function(data) {
				if(data) {
					$("#pci_r_section").html(data);
					// initCustomersPciDropdownRight();
				}
	        });
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