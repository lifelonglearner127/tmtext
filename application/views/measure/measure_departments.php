<style type="text/css">
.dropdown-menu {
	max-height: 350px;
	overflow: hidden;
	overflow-y: auto;
}
</style>
<div class="tabbable">
    <ul class="nav nav-tabs jq-measure-tabs">
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure');?>">Home Pages</a></li>
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('measure/measure_departments');?>">Categories</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_products');?>">Products</a></li>
        <!--<li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_social'); ?>">Social</a></li>-->
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_pricing'); ?>">Pricing</a></li>
    </ul>
    <div class="tab-content">
   
        <div class="row-fluid home_pages">
            <div class='span12 head_section'>

                <div class='head_line_2'>
                    <!--div class="span2">View Reports for:</div-->
                    <div >
                        <style type="text/css">
                            .tab-content{
                                min-height:400px;
                            }
                            .temp_li{
                                display: inline;
                                font-size: 18px;
                            }
                        </style>
                       <!-- <ul class="ml_10 pull-left" style="float:left">
                            <li class="temp_li"><a href="#" style="text-decoration: underline;">Your Watchlists</a></li>
                            <li class="temp_li ml_50"><a href="#">Best-sellers</a></li>
                            <li class="temp_li ml_50"><a href="#">Entire site</a></li>
                        </ul>
						-->
						
                        <?php
                        if($this->ion_auth->is_admin($this->ion_auth->get_user_id())){
                            if(count($customers_list) > 0) { ?>
                                <div id="hp_boot_drop" style="float:left;" class="btn-group <?php echo $dropup; ?> hp_boot_drop  mr_10">
                                    <button class="btn btn-danger btn_caret_sign" >Choose Site</button>
                                    <button class="btn btn-danger dropdown-toggle" data-toggle="dropdown">
                                        <span class="caret"></span>
                                    </button>
                                    <ul class="dropdown-menu">
                                        <?php foreach($customers_list as $val) { ?>
                                            <li><a data-item="<?php echo $val['id']; ?>" data-value="<?php echo $val['name_val']; ?>" href="javascript:void(0)"><?php echo $val['name']; ?></a></li>
                                        <?php } ?>
                                    </ul>
                                </div>
                            <?php }
                        }
                        ?>
                    </div>
					<div id="departmentDropdown"  class="btn-group">
                                    <button class="btn btn-danger btn_caret_sign1" >Choose Department</button>
                                    <button class="btn btn-danger dropdown-toggle" data-toggle="dropdown">
                                        <span class="caret"></span>
                                    </button>
                                    <ul class="dropdown-menu" >
                                    </ul>
                                </div>
					<!-- Compare with Begin-->
					
					
					<div id="departmentDropdownSec" style="float:right";  class="btn-group">
                                    <button class="btn btn-danger btn_caret_sign_sec1" >Choose Department</button>
                                    <button class="btn btn-danger dropdown-toggle" data-toggle="dropdown">
                                        <span class="caret"></span>
                                    </button>
                                    <ul class="dropdown-menu" >
                                    </ul>
                                </div>
					
					
					 <div  style="float:right;padding-right:3%;">
                        <style type="text/css">
                            .tab-content{
                                min-height:400px;
                            }
                            .temp_li{
                                display: inline;
                                font-size: 18px;
                            }
                        </style>
						
                        <?php
                        if($this->ion_auth->is_admin($this->ion_auth->get_user_id())){
                            if(count($customers_list) > 0) { ?>
                                <div id="hp_boot_drop_sec"  class="btn-group <?php echo $dropup; ?> hp_boot_drop_sec  mr_10">
                                    <button class="btn btn-danger btn_caret_sign_sec" >Choose Site</button>
                                    <button class="btn btn-danger dropdown-toggle" data-toggle="dropdown">
                                        <span class="caret"></span>
                                    </button>
                                    <ul class="dropdown-menu">
                                        <?php foreach($customers_list as $val) { ?>
                                            <li><a data-item="<?php echo $val['id']; ?>" data-value="<?php echo $val['name_val']; ?>" href="javascript:void(0)"><?php echo $val['name']; ?></a></li>
                                        <?php } ?>
                                    </ul>
                                </div>
                            <?php }
                        }
                        ?>
                    </div>
					<span style="float: right;font-weight: bold;">Compare with: </span>
					
					
					 <!--Compare with END -->
                </div>
            </div>
            <div class="clear"></div>
        </div>
		<div class="row-fluid home_pages">
            <!-- Table for results -->
                    <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/smoothness/jquery-ui-1.8.2.custom.css" />
                    <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/styles.css" />
                    <div class="table_results">
                        <div id="tabs"  class="mt_10" style="overflow: hidden;" >

                            <div id="dataTableDiv1" style="width: 48%;float: left;" >
                                <table id="records" >
                                    <thead>
										<tr>
											<th>Category()</th>
											<th>Items</th>
											<th>Category Description SEO</th>
											<th>Words</th>
										</tr>
                                    </thead>
                                    <tbody>
									</tbody>
                                </table>
								
                            </div>
							<!--div id="dataTableDiv2" style="width: 48%;float: left;margin-left: 35px;" >
								<table id="recordSec"  >
                                    <thead>
										<tr>
											<th>Category()</th>
											<th>Items</th>
											<th>Category Description SEO</th>
											<th>Words</th>
										</tr>
                                    </thead>
                                    <tbody>
									</tbody>
                                </table>
							</div-->

                        </div> <!-- end tabs -->

                        <div id="ajaxLoadAni">
                            <span>Loading...</span>
                        </div>                     <!-- message dialog box -->
                        <div id="msgDialog"><p></p></div>

                        <script type="text/javascript" src="<?php echo base_url();?>js/jquery-templ.js"></script>
                        <script type="text/javascript" src="<?php echo base_url();?>js/jquery.validate.min.js"></script>
                        <script type="text/javascript" src="<?php echo base_url();?>js/jquery.dataTables.min.js"></script>

                        <!--script type="text/template" id="readTemplate">
                            <tr id="${id}">
                                <td>${rank}</td>
                                <td>${product_name}</td>
                                <td>${url}</td>
                                <td nowrap><a class="updateBtn icon-edit" style="float:left;" href="${updateLink}"></a>
                                    <a class="deleteBtn icon-remove ml_5" href="${deleteLink}"></a>
                                </td>
                            </tr>
                        </script-->

                        <script type="text/javascript" src="<?php echo base_url();?>js/measure_department.js"></script>
                    </div>
            <!-- End of table for results -->
            <div class="clear"></div>
		</div>
    </div>
</div>