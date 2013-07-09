<div class='span12 head_section'>
	<p class='head_line1'>Home page reports are generated weekly. <a onclick="configureEmailReportsModal()" href="javascript:void(0)">Configure email reports.</a></p>
	<div class='head_line_2'>
		<div class="span2">View Reports for:</div>
		<div class="span2 w_100 ml_disable">
			<select id='year_s' class='year_s' onchange="changeHomePageYersHandler()">
				<?php for($i = 1980; $i <= 2013; $i++) { ?>
				<?php $selected = ""; if($i == $year) $selected = 'selected'; ?>
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
						    <button class="btn btn-danger btn_caret_sign">All customers</button>
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

<a id='customers_screens_crawl' class='btn btn-warning'><i class='icon-file'></i>&nbsp;Crawl customers screenshots</a>

<script type="text/javascript">
	$(document).ready(function() {
		$(".hp_boot_drop .dropdown-menu > li > a").bind('click', function(e) {
			var new_caret = $.trim($(this).text());
			var item_id = $(this).data('item');
			$("#hp_boot_drop_" + item_id + " .btn_caret_sign").text(new_caret);
		});

		$("#customers_screens_crawl").tooltip({
			placement: 'right',
			title: 'Test Customers Screens Crawl'
		});
	});
</script>
