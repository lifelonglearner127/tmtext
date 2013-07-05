<div class="main_content_other"></div>
<div class="tabbable">
    <ul class="nav nav-tabs jq-measure-tabs">
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('measure');?>"><b>Home Pages</b></a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_departments');?>"><b>Departments & Categories</b></a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_products');?>"><b>Products</b></a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_gridview');?>"><b>Grid View</b></a></li>
    </ul>
    <div class="tab-content">
    	<div class="row-fluid home_pages">
    		
    		<div class='span12 head_section'>
	    		<p class='head_line1'>Home page reports are generated weekly. <a href="javascript:void(0)">Configure email reports.</a></p>
				<div class='head_line_2'>
					<div class="span2">View Reports for:</div>
					<div class="span2 w_100 ml_disable">
						<select class='year_s'>
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
								<li class="active"><a href="javascript:void(0)">1</a></li>
								<li><a href="javascript:void(0)">2</a></li>
								<li><a href="javascript:void(0)">3</a></li>
								<li><a href="javascript:void(0)">4</a></li>
								<li><a href="javascript:void(0)">5</a></li>
								<li><a href="javascript:void(0)">&raquo;</a></li>
							</ul>
						</div>
					</div>
				</div>
			</div>
			
			<div class='span12 body_section ml_disable mt_30'>

				<div class='span12 items_row ml_disable'>
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
				</div>
				<div class='span12 items_row ml_disable'>
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
				</div>
			</div>

		</div>
    </div>
</div>
