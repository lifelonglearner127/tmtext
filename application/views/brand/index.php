<script>
    $(function() {
        $('head').find('title').text('Brand Rankings');
    });
</script>
<?php
$pervious_month = date("m", strtotime("first day of previous month"));
?>
<div class="main_content_other"></div>
<div class="tabbable">
    <div class="tab-content">
        <div class="tabbable">
            <div class="tab-content block_data_table">
                <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/smoothness/jquery-ui-1.8.2.custom.css" />
                <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/styles.css" />
                <!-- Table doesnt work without this jQuery include yet -->
                <script type="text/javascript" src="<?php echo base_url();?>js/jquery-templ.js"></script>
                <script type="text/javascript" src="<?php echo base_url();?>js/jquery.validate.min.js"></script>
                <script type="text/javascript" src="<?php echo base_url();?>js/jquery.dataTables.min.js"></script>
                <script type="text/javascript" src="<?php echo base_url();?>js/jquery.json-2.4.min.js"></script>
                <script type="text/javascript">
                    $(function() {
                        $( ".draggable" ).draggable();
                    });
                </script>
                <style type="text/css">
                    #brand_ranking {width: 100%; font-size: 1em;}
                    #brand_ranking th { font-weight: bold; }
                    .brand_filters { margin: 10px 0; }
                    .brand_filters select { float:left; margin-left: 5px; margin-top:5px; }
                    .brand_filters .brand_types { width:150px; }
                    .brand_filters .day { width:70px; }
                    .brand_filters .month { width:120px; }
                    .brand_filters .year { width:90px; }
                </style>
                <div>
                    <h3 class="pull-left">The 100 Most Social</h3>
                    <div class="brand_filters pull-left">
                        <select name="brand_types" id="brand_types" class="brand_types">
                            <?php foreach($brand_types as $brand_type) { ?>
                                    <option value="<?php echo $brand_type->id; ?>"><?php echo $brand_type->name.' Brands'; ?></option>
                            <?php } ?>
                        </select>
                        <select name="month" id="month" class="month">
                            <?php foreach($months as $key=>$month) { ?>
                                    <option value="<?php echo $key; ?>" <?php echo ($pervious_month == $key)?'selected="selected"':''; ?> >
                                        <?php echo $month; ?>
                                    </option>
                            <?php } ?>
                        </select>
                        <select name="year" id="year" class="year">
                            <?php foreach($years as $key=>$year) { ?> 
                                    <option value="<?php echo $key; ?>"><?php echo $year; ?></option>
                            <?php } ?>
                        </select>
                    </div>
                </div>
                <div class="clearfix"></div>
                <div id="research_tab2" class="tab-pane active">
                    <div class="row-fluid">
                        <div id="ajaxLoadAni">
                            <span>Loading...</span>
                        </div>
                        <div id="tabs" class="mt_10">
                            <div id="read">
                                <table id="brand_ranking">
                                    <thead>
                                    <tr>
                                        <th><div class="draggable">Social Rank</div></th>
                                        <th><div class="draggable">IR 500 Rank</div></th>
                                        <th><div class="draggable">Brand</div></th>
                                        <th><div class="draggable">Tweets</div></th>
                                        <th><div class="draggable">All Tweets</div></th>
                                        <th><div class="draggable">Followers</div></th>
                                        <th><div class="draggable">Youtube Videos</div></th>
                                        <th><div class="draggable">Views</div></th>
                                        <th><div class="draggable">All Views</div></th>
                                        <th><div class="draggable">Average</div></th>
                                        <th><div class="draggable">All Videos</div></th>
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