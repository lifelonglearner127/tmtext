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
						<select id='year_s' class='year_s'>
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
								<li class="disabled"><a href="javascript:void(0)">&laquo;</a></li>
								<li data-week='1' class="active"><a href="javascript:void(0)" onclick="locaHomePageWeekData('1')">1</a></li>
								<li data-week='2'><a href="javascript:void(0)" onclick="locaHomePageWeekData('2')">2</a></li>
								<li data-week='3'><a href="javascript:void(0)" onclick="locaHomePageWeekData('3')">3</a></li>
								<li data-week='4'><a href="javascript:void(0)" onclick="locaHomePageWeekData('4')">4</a></li>
								<li data-week='5'><a href="javascript:void(0)" onclick="locaHomePageWeekData('5')">5</a></li>
								<li><a href="javascript:void(0)">&raquo;</a></li>
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
							$row_items = array('1', '2', '3'); // tmp for mockup
						?>
						<?php foreach($row_items as $k=>$v) { ?>
							<div class='span4 item'>
								<div class='art_hp_select_item'>&nbsp;</div>
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

<script type='text/javascript'>
	function locaHomePageWeekData(week) {
		var year = $("#year_s > option:selected").val();
		$(".pagination ul li").removeClass('active');
		$(".pagination ul li[data-week=" + week + "]").addClass('active');
		$.ajax({
            url: base_url + 'index.php/system/gethomepageweekdata',
            async: false,
            dataType: 'html',
            type: "POST",
            data: {
            	'year': year,
            	'week': week
            },
            success: function(res) {
            	$("#hp_ajax_content > div").slideUp('medium', function() {
            		$("#hp_ajax_content").html(res);
            	});
            }
          });
	}
</script>
