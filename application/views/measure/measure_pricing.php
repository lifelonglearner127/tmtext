<div class="main_content_other"></div>
<div class="tabbable">
	<ul class="nav nav-tabs jq-system-tabs">
                    <li class=""><a data-toggle="tab" href="<?php echo site_url('system');?>">General</a></li>
                    <li class=""><a data-toggle="tab" href="<?php echo site_url('system/sites_view');?>">Sites</a></li>
                    <li class=""><a data-toggle="tab" href="<?php echo site_url('site_crawler');?>">Site Crawler</a></li>
                    <li class=""><a data-toggle="tab" href="<?php echo site_url('brand/import');?>">Brands</a></li>
                    <li class=""><a data-toggle="tab" href="<?php echo site_url('system/batch_review');?>">Batch Review</a></li>
                    <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_compare');?>">Product Compare</a></li>
                    <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_productsmatch');?>">Product Match</a></li>
                    <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_reports');?>">Reports</a></li>
                    <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_logins');?>">Logins</a></li>
                    <li class=""><a data-toggle="tab" href="<?php echo site_url('system/keywords');?>">Keywords</a></li>
                    <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_rankings');?>">Rankings</a></li>
                    <li class="active"><a data-toggle="tab" href="<?php echo site_url('measure/measure_pricing');?>">Pricing </a></li>
                    <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/product_models');?>">Product models </a></li>
                    <li class=""><a data-toggle="tab" href="<?php echo site_url('system/snapshot_queue');?>">Snapshot Queue</a></li>
                    <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_uploadmatchurls');?>">Upload Match URLs</a></li>
                    <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_dostatsmonitor');?>">Do_stats Monitor</a></li>
                    <li class=""><a data-toggle="tab" href="<?php echo site_url('system/sync_keyword_status');?>">Sync Keyword Status</a></li>
		</ul>
    <div class="tab-content">
        <div class="tabbable">
            <div class="tab-content block_data_table">
                <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/smoothness/jquery-ui-1.8.2.custom.css" />
                <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/styles.css" />
                <script>
                    $(function() {
                        $( ".draggable" ).draggable();
                    });
                </script>
                <div id="research_tab2" class="tab-pane active">
                    <div class="row-fluid">
                        <div id="ajaxLoadAni">
                            <span>Loading...</span>
                        </div>

                        <div id="tabs" class="mt_10">
                            <div id="read">
                                <table id="records">
                                    <thead>
                                    <tr>
                                        <th><div class="draggable">Date</div></th>
                                        <th><div class="draggable">Site</div></th>
                                        <th><div class="draggable">Model</div></th>
                                        <th><div class="draggable">Product</div></th>
                                        <th><div class="draggable">Price</div></th>
                                    </tr>
                                    </thead>
                                    <tbody></tbody>
                                </table>
                            </div>
                            <div id="create">
                            </div>
                        </div> <!-- end tabs -->

                        <!-- message dialog box -->
                        <div id="msgDialog"><p></p></div>

                        <!-- Table doesnt work without this jQuery include yet -->
                        <!-- <script type="text/javascript" src="<?php echo base_url();?>js/jquery-1.4.2.min.js"></script>
                        <script type="text/javascript" src="<?php echo base_url();?>js/jquery-ui-1.8.2.min.js"></script> -->
                        <script type="text/javascript" src="<?php echo base_url();?>js/jquery-templ.js"></script>
                        <script type="text/javascript" src="<?php echo base_url();?>js/jquery.validate.min.js"></script>
                        <script type="text/javascript" src="<?php echo base_url();?>js/jquery.dataTables.min.js"></script>
                        <script type="text/javascript" src="<?php echo base_url();?>js/jquery.json-2.4.min.js"></script>

                        <script type="text/template" id="readTemplate">
                            <tr>
                                <td class="column_created"></td>
								<td class="column_url"></td>
                                <td class="column_model"></td>
                                <td class="column_product_name"></td>
                                <td class="column_price"></td>
                            </tr>
                        </script>

                        <script type="text/javascript" src="<?php echo base_url();?>js/competitive_intelligence.js"></script>
                    </div>
                    <div class="clear mt_40"></div>
                </div>
            </div>
        </div>
    </div>
</div>
<script>
            $(function() {
                $('head').find('title').text('System');
            });
 </script>