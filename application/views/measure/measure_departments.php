<div class="tabbable">
    <ul class="nav nav-tabs jq-measure-tabs">
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure');?>">Home Pages</a></li>
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('measure/measure_departments');?>">Departments & Categories</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_products');?>">Products</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_pricing'); ?>">Pricing</a></li>
    </ul>
    <div class="tab-content">
		<div class="row-fluid home_pages">

			<div class='span12 head_section'>

				<div class='head_line_2'>
					<div class="span2">View Reports for:</div>
					<div class="span2 w_100 ml_disable">
						<select id='year_s' class='year_s' onchange="changeHomePageYersHandler()">
							<?php for($i = 1980; $i <= 2013; $i++) { ?>
								<?php $selected = ""; if($i == 2013) $selected = 'selected'; ?>
								<option <?php echo $selected; ?> value="<?php echo $i; ?>"><?php echo $i; ?></option>
							<?php } ?>
						</select>
					</div>
					<div class="span1 ml_disable">week:</div>
					<div class='span6 ml_disable'>
						<div class="pagination">
							<ul>
								<li class="page_prev disabled"><a onclick="prevLocaHomePageWeekData()" href="javascript:void(0)">&laquo;</a></li>
								<li data-week='1' class="page active"><a href="javascript:void(0)" onclick="locaHomePageWeekData('1')">1</a></li>
								<li data-week='2' class='page'><a href="javascript:void(0)" onclick="locaHomePageWeekData('2')">2</a></li>
								<li data-week='3' class='page'><a href="javascript:void(0)" onclick="locaHomePageWeekData('3')">3</a></li>
								<li data-week='4' class='page'><a href="javascript:void(0)" onclick="locaHomePageWeekData('4')">4</a></li>
								<li data-week='5' class='page'><a href="javascript:void(0)" onclick="locaHomePageWeekData('5')">5</a></li>
								<li class='page_next'><a onclick="nextLocaHomePageWeekData()" href="javascript:void(0)">&raquo;</a></li>
							</ul>
						</div>
					</div>
				</div>
			</div>

			<div style='margin-left: 0px;' class='span12 mt_10'>
				<span class='inline_block lh_30 mr_10 span2'>Department:</span>
				<input type="text" id="department" name="department" value="" class="inline_block lh_30 w_375 mb_reset" placeholder=""/>
				<button id="department_show" type="button" class="btn ml_10" >Show</button>
				<button id="department_next" type="button" class="btn ml_10" >Next</button>
			</div>

			<div style='margin-left: 0px;' class='span12 mt_10'>
				<span class='inline_block lh_30 mr_10 span2'>Category:</span>
				<input type="text" id="category" name="category" value="" class="inline_block lh_30 w_375 mb_reset" placeholder=""/>
				<button id="category_show" type="button" class="btn ml_10" >Show</button>
				<button id="category_next" type="button" class="btn ml_10" >Next</button>
			</div>

			<div id='hp_ajax_content' class='span12 body_section ml_disable mt_30'>
				<div class='ph_placeholder' data-week='1'>
					<?php
					$items_count = 6;
					$item_per_row = 3;
					$items_rows = ceil($items_count/$item_per_row);
					?>

					<?php for($i = 1; $i <= $items_rows; $i++) { ?>
						<div class='span12 items_row ml_disable'>
							<?php
							$position = $item_per_row*($i-1);
							// $row_items = getRowItemsRowFromBackend($item_per_row, $position); // -- method template to get items from backend // designed in such way that row will not have more than 3 items
							$row_items = array(rand(), rand(), rand()); // tmp for mockup
							?>
							<?php if($i == $items_rows) $dropup = 'dropup'; else $dropup = ''; ?>
							<?php foreach($row_items as $k=>$v) { ?>
								<div class='span4 item'>
									<?php if(count($customers_list) > 0) { ?>
										<div id="hp_boot_drop_<?php echo $v; ?>" class="btn-group <?php echo $dropup; ?> hp_boot_drop">
											<button class="btn btn-danger btn_caret_sign">[ Choose site ]</button>
											<button class="btn btn-danger dropdown-toggle" data-toggle="dropdown">
												<span class="caret"></span>
											</button>
											<ul class="dropdown-menu">
												<?php foreach($customers_list as $val) { ?>
													<li><a data-item="<?php echo $v; ?>" data-value="<?php echo $val['name_val']; ?>" href="javascript:void(0)"><?php echo $val['name']; ?></a></li>
												<?php } ?>
											</ul>
										</div>
									<?php } ?>
									<div>
										<div class='w_100' style='background: none repeat scroll 0 0 #333333; height: 150px; width: 150px;'>&nbsp;</div>
										<div class='mt_10'>
                                            <span class="btn mr_10">
                                                <i class="icon-align-justify"></i>
                                            </span>
											Keywords: .... (5)
										</div>
                                        <div class='mt_10'>
                                            <span class="btn mr_10">
                                                <i class="icon-align-justify"></i>
                                            </span>
                                            Text: (... words) ...
                                        </div>
									</div>
								</div>
							<?php } ?>
						</div>
					<?php } ?>
				</div>
			</div>
		</div>
    </div>
</div>



<script type="text/javascript">
	$(document).ready(function() {
		$(".hp_boot_drop .dropdown-menu > li > a").bind('click', function(e) {
			var new_caret = $.trim($(this).text());
			var item_id = $(this).data('item');
			$("#hp_boot_drop_" + item_id + " .btn_caret_sign").text(new_caret);
		});
	});
</script>