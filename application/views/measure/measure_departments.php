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
                    <!--div class="span2">View Reports for:</div-->
                    <div class="span10">
                        <style type="text/css">
                            .temp_li{
                                display: inline;
                                font-size: 18px;
                            }
                            .rank_table{
                                width: 660px;
                                border: 2px solid #000;
                            }
                            .rank_table td, .rank_table th{
                                border: 1px solid #000;
                                padding:7px;
                                color:#000;
                            }
                            .rank_table thead{
                                background: #ccc;
                            }
                        </style>
                        <ul class="ml_10 pull-left" style="float:left">
                            <li class="temp_li"><a href="#" style="text-decoration: underline;">Your Watchlists</a></li>
                            <li class="temp_li ml_50"><a href="#">Best-sellers</a></li>
                            <li class="temp_li ml_50"><a href="#">Entire site</a></li>
                        </ul>
                        <?php
                        if($this->ion_auth->is_admin($this->ion_auth->get_user_id())){
                            if(count($customers_list) > 0) { ?>
                                <div id="hp_boot_drop_<?php echo $v; ?>" class="btn-group <?php echo $dropup; ?> hp_boot_drop pull-right mr_10">
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
                            <?php }
                        }
                        ?>
                    </div>
                    <div class="span2 w_100 ml_disable">
                        <select id='year_s' class='year_s' onchange="changeHomePageYersHandler()">
                            <?php for($i = 1980; $i <= 2013; $i++) { ?>
                                <?php $selected = ""; if($i == 2013) $selected = 'selected'; ?>
                                <option <?php echo $selected; ?> value="<?php echo $i; ?>"><?php echo $i; ?></option>
                            <?php } ?>
                        </select>
                    </div>

                    <!--div class="span1 ml_disable">week:</div>
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
					</div-->
                </div>
            </div>
            <div style='margin-left: 0px;' class='span12 mt_10'>
                <span class='inline_block lh_30 mr_10 span2'>Department:</span>
                <?php //var_dump($departmens_list);?>
                <?php  echo form_dropdown('department', $departmens_list, null, 'class="inline_block lh_30 w_375 mb_reset"'); ?>
                <!-- <input type="text" id="department" name="department" value="" class="inline_block lh_30 w_375 mb_reset" placeholder=""/>-->
                <button id="department_show" type="button" class="btn ml_10" >Show</button>
                <button id="department_next" type="button" class="btn ml_10" >Next</button>
                <button id="department_go" type="button" class="btn ml_10" >Go</button>
            </div>

            <div style='margin-left: 0px;' class='span12 mt_10'>
                <span class='inline_block lh_30 mr_10 span2'>Category:</span>
                <?php  echo form_dropdown('category', $category_list, null, 'class="inline_block lh_30 w_375 mb_reset"'); ?>
                <button id="category_show" type="button" class="btn ml_10" >Show</button>
                <button id="category_next" type="button" class="btn ml_10" >Next</button>
                <button id="category_go" type="button" class="btn ml_10" >Go</button>
            </div>
            <div class="clear"></div>
        </div>
		<div class="row-fluid home_pages">
            <!-- Table for results -->
                    <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/smoothness/jquery-ui-1.8.2.custom.css" />
                    <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/styles.css" />
                    <div class="table_results">
                        <div id="tabs" class="mt_10">

                            <div id="read">
                                <table id="records">
                                    <thead>
                                    <tr>
                                        <th>Rank</th>
                                        <th>Product Name</th>
                                        <th>URL</th>
                                        <th><div class="draggable">Actions</div></th>
                                    </tr>
                                    </thead>
                                    <tbody></tbody>
                                </table>
                            </div>

                        </div> <!-- end tabs -->

                        <div id="ajaxLoadAni">
                            <span>Loading...</span>
                        </div>                     <!-- message dialog box -->
                        <div id="msgDialog"><p></p></div>

                        <script type="text/javascript" src="<?php echo base_url();?>js/jquery-templ.js"></script>
                        <script type="text/javascript" src="<?php echo base_url();?>js/jquery.validate.min.js"></script>
                        <script type="text/javascript" src="<?php echo base_url();?>js/jquery.dataTables.min.js"></script>

                        <script type="text/template" id="readTemplate">
                            <tr id="${id}">
                                <td>${rank}</td>
                                <td>${product_name}</td>
                                <td>${url}</td>
                                <td nowrap><a class="updateBtn icon-edit" style="float:left;" href="${updateLink}"></a>
                                    <a class="deleteBtn icon-remove ml_5" href="${deleteLink}"></a>
                                </td>
                            </tr>
                        </script>

                        <script type="text/javascript" src="<?php echo base_url();?>js/measure_department.js"></script>
                    </div>
            <!-- End of table for results -->

            <!--div class='span12 mt_10'>
                <table class="rank_table mt_30">
                    <thead>
                        <th>Rank</th>
                        <th>Site</th>
                        <th>Score</th>
                    </thead>
                    <tbody>
                        <tr>
                            <td>1</td>
                            <td>Amazon.com</td>
                            <td>92</td>
                        </tr>
                        <tr>
                            <td>2</td>
                            <td>Staples.com</td>
                            <td>85</td>
                        </tr>
                        <tr>
                            <td>3</td>
                            <td>Waltmart.com</td>
                            <td>78</td>
                        </tr>
                    </tbody>
                <table>
            </div-->
            <div class="clear"></div>
            <img  src="../../img/marketing.jpg"  class="mt_30" >
            <img  src="../../img/pricing.jpg"  class="mt_30 ml_120">
            <img  src="../../img/inventory.jpg"  class="mt_30 ml_120">
			<!--div id='hp_ajax_content' class='span12 body_section ml_disable mt_30'>
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
			</div-->
		</div>
    </div>
</div>



<script type="text/javascript">
	$(document).ready(function() {
		$(".hp_boot_drop .dropdown-menu > li > a").bind('click', function(e) {
			var new_caret = $.trim($(this).text());
			var item_id = $(this).data('item');
			$("#hp_boot_drop_" + item_id + " .btn_caret_sign").text(new_caret);
            $.post(base_url + 'index.php/measure/getDepartmentsByCustomer', {'customer_name': new_caret}, function(data) {
                $("select[name='department']").empty();
                if(data.length > 0){
                    for(var i=0; i<data.length; i++){
                        $("select[name='department']").append("<option value='"+data[i].id+"'>"+data[i].text+"</option>");
                    }
                }
            });
            $.post(base_url + 'index.php/measure/getCategoriesByCustomer', {'customer_name': new_caret}, function(data) {
                $("select[name='category']").empty();
                if(data.length > 0){
                    for(var i=0; i<data.length; i++){
                        $("select[name='category']").append("<option value='"+data[i].id+"'>"+data[i].text+"</option>");
                    }
                }
            });
		});
        $('button#department_go').click(function(e){
            // use success flag
            var success = false;
            var url = '';
            e.preventDefault();
            $.post(base_url + 'index.php/measure/getUrlByDepartment', {
                'department_id': $('select[name="department"]').find("option:selected").val()
            }, function(data) {
                if(data.length > 0){
                    window.success = true;
                    if(data[0].url!='' && data[0].url!=undefined){
                        window.url = data[0].url;
                    }
                }
            });
            setTimeout(function(){
                if (window.success == true) { // and read the flag here
                    window.open(window.url);
                }
            }, 100);


        });
        $('button#category_go').click(function(e){
            // use success flag
            var success = false;
            var url = '';
            e.preventDefault();
            $.post(base_url + 'index.php/measure/getUrlByCategory', {
                'category_id': $('select[name="category"]').find("option:selected").val()
            }, function(data) {
                if(data.length > 0){
                    window.success = true;
                    if(data[0].url!='' && data[0].url!=undefined){
                        window.url = data[0].url;
                    }
                }
            });
            setTimeout(function(){
                if (window.success == true) { // and read the flag here
                    window.open(window.url);
                }
            }, 100);
        });
	});
</script>