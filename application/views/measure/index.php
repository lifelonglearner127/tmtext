<div class="main_content_other"></div>
<div class="tabbable">
    <ul class="nav nav-tabs jq-measure-tabs">
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('measure');?>">Home Pages</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_departments');?>">Departments & Categories</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_products');?>">Products</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_gridview');?>">Grid View</a></li>
    </ul>
    <div class="tab-content">
    	<div class="row-fluid home_pages">
    		
    		<div class='span12 head_section'>
	    		<p class='head_line1'>Home page reports are generated weekly. <a href="javascript:void(0)">Configure email reports.</a></p>
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
			
			<div id='hp_ajax_content' class='span12 body_section ml_disable mt_30'>
				<div class='ph_placeholder' data-week='1'>
					<?php 
						$items_count = 9;
						$item_per_row = 3;
						$items_rows = ceil($items_count/$item_per_row);
					?>

					<?php for($i = 1; $i <= $items_rows; $i++) { ?>
						<div class='span12 items_row ml_disable'>
						<?php 
							$position = $item_per_row*($i-1); 
							// $row_items = getRowItemsRowFromBackend($item_per_row, $position); // -- method template to get items from backend // designed in such way that row will not have more than 3 items  
							$row_items = array('1', '2', '3'); // tmp for mockup
						?>
						<?php if($i == $items_rows) $dropup = 'dropup'; else $dropup = ''; ?>
						<?php foreach($row_items as $k=>$v) { ?>
							<div class='span4 item'>
								<?php if(count($customers_list) > 0) { ?>
								    <div class="btn-group <?php echo $dropup; ?> hp_boot_drop">
									    <button class="btn btn-primary">All customers</button>
									    <button class="btn btn-primary dropdown-toggle" data-toggle="dropdown">
									    	<span class="caret"></span>
									    </button>
									    <ul class="dropdown-menu">
									    	<?php foreach($customers_list as $k=>$v) { ?>
									    		<li><a href="javascript:void(0)"><?php echo $v['name']; ?></a></li>
									    	<?php } ?>
									    </ul>
								    </div>
							    <?php } ?>
								<div class='art_hp_item'>
									<div class='art_img'>&nbsp;</div>
									<div class='art_oview'>
										<p class='h'>Overview</p>
										<p class='t'>text sample</p>
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

<script src="<?php echo base_url();?>js/ci_home_pages.js"></script>
