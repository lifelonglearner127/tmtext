<div class="main_content_other"></div>
<div class="tabbable">
    <ul class="nav nav-tabs jq-measure-tabs">
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure'); ?>">Home Pages</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_departments'); ?>">Departments & Categories</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_products'); ?>">Products</a></li>
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('measure/measure_pricing'); ?>">Pricing</a></li>
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
                        <script type="text/javascript" src="<?php echo base_url();?>js/jquery-1.4.2.min.js"></script>
                        <script type="text/javascript" src="<?php echo base_url();?>js/jquery-ui-1.8.2.min.js"></script>
                        <script type="text/javascript" src="<?php echo base_url();?>js/jquery-templ.js"></script>
                        <script type="text/javascript" src="<?php echo base_url();?>js/jquery.validate.min.js"></script>
                        <script type="text/javascript" src="<?php echo base_url();?>js/jquery.dataTables.min.js"></script>
                        <script type="text/javascript" src="<?php echo base_url();?>js/jquery.json-2.4.min.js"></script>

                        <script type="text/template" id="readTemplate">
                            <tr>
                                <td class="column_created"></td>
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
