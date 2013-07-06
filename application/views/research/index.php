<script type="text/javascript">
var last_edition = '';
var box = new Array();
box['main_research_box_start'] = '<div class="span6" id="research" class="connectedMoved"><h3 class="handle">Research</h3>' +
        '<ul class="research_content connectedSortable" id="sortable1">';
box['main_research_box_end'] = '</ul></div>';
box['results'] = '<h3>Results</h3><div class="boxes_content"  style="height: 200px;padding:0px;">' +
        '<ul class="product_title"><li class="main"><span><b>Product Name</b></span><span><b>URL</b></span></li></ul>' +
        '<ul id="research_products" style="height: 170px; overflow: auto;"><li><span>&nbsp;</span><span>&nbsp;</span></li>' +
        '<li><span>&nbsp;</span><span>&nbsp;</span></li><li><span>&nbsp;</span><span>&nbsp;</span></li>' +
        '<li><span>&nbsp;</span><span>&nbsp;</span></li></ul><ul id="product_descriptions"></ul></div>';

box['related_keywords'] = '<h3>Related Keywords</h3><div class="boxes_content"><ul id="rel_keywords">' +
        '<li class="primary"><span>Televisions</span></li><li class="secondary"><span>TVs</span></li>' +
        '<li class="tertiary"><span>LCD TV</span></li><li class="primary"><span>LED TV</span></li>' +
        '<li class="secondary"><span>Digital TV</span></li><li class="tertiary"><span>Internet TV</span></li>' +
        '<li class="primary"><span>HDTV</span></li><li class="secondary"><span>3D</span></li>' +
        '<li class="tertiary"><span>HDMI</span></li><li class="primary"><span>2D</span></li>' +
        '<li class="secondary"><span>TFT</span></li><li class="tertiary"><span>USB</span></li></ul></div>';
box['seo_phrases'] = '<h3>SEO Phrases</h3><div class="boxes_content">' +
        '<ul class="less_b_margin ml_0" data-status="seo_an"></ul>' +
        '<ul class="less_b_margin ml_0" data-st-id="short_desc_seo" data-status="seo_an"></ul>' +
        '<ul class="less_b_margin ml_0" data-st-id="long_desc_seo" data-status="seo_an"></ul></div>';
box['main_edit_box_start'] = '<div class="span6" id="research_edit" class="connectedMoved">' +
            '<h3 class="handle">Edit</h3><ul class="research_content connectedSortable" id="sortable2">';
box['main_edit_box_end'] = '</ul></div>';
box['keywords'] = '<h3>Keywords</h3><div class="boxes_content"><p><span>Primary:</span>' +
        '<input class="keywords" type="text" name="primary" value="" /><a href="#" class="clear_all">x</a></p>' +
        '<p><span>Secondary:</span><input class="keywords" type="text" name="secondary" value="" />' +
        '<a href="#" class="clear_all">x</a></p><p><span>Tertiary:</span>' +
        '<input class="keywords" type="text" name="tertiary" value="" /><a href="#" class="clear_all">x</a></p></div>';
box['stylegide'] = '<h3>Style Guide</h3><div class="boxes_content"></div>';
box['page_elements'] = '<h3>Page Elements</h3><div class="boxes_content"><p>' +
        '<button id="generate_product" type="button" class="btn pull-right">Generate</button>' +
        '<label>Product name:</label><input type="text" class="span11 ml_0" name="product_name"/>' +
        '<input type="hidden" name="url"/><input type="hidden" name="revision"/></p><p><label>Meta title:</label>' +
        '<input type="text"  class="span11 ml_0" name="meta_title" /></p><p><label>Meta description:</label>' +
        '<textarea name="meta_description" style="height:100px;" ></textarea></p><p>' +
        '<button id="generate_keywords" type="button" class="btn pull-right">Generate</button>' +
        '<label>Meta keywords:</label><input type="text" class="span11 ml_0" name="meta_keywords" /></p></div>';
box['descriptions'] = '<h3>Descriptions</h3><div class="boxes_content"><div class="row-fluid">' +
        '<label>Short description:</label><label><span id="research_wc">0</span> words</label>' +
        '<button type="button" class="btn" style="float:left;">Generate</button>' +
        '<textarea type="text" name="short_description" class="span10 mt_10" style="height:100px;"></textarea></div>' +
        '<div class="row-fluid"><label>Long description:</label><label><span id="research_wc1">0</span> words</label>' +
        '<div class="search_area uneditable-input ml_10"  id="long_description" onClick="this.contentEditable=\'true\';" style="cursor: text; width: 365px;"></div></div>' +
        '<div class="row-fluid" id="research_density"><label>Density:</label><label>Primary:</label>' +
        '<input type="text" name="research_primary" class="span2" value="0" readonly="readonly" />' +
        '<span class="percent">%</span><label>Secondary:</label>' +
        '<input type="text" name="research_secondary" class="span2" value="0" readonly="readonly" />' +
        '<span class="percent" >%</span><label>Tertiary:</label>' +
        '<input type="text" name="research_tertiary" class="span2" value="0" readonly="readonly" />' +
        '<span class="percent" >%</span><button id="research_update_density" type="button" class="btn btn-primary ml_10">Update</button></p>' +
        '<p>Total words: <span id="research_total">0</span> words</p></div><div class="row-fluid mb_20">' +
        '<button id="validate" type="button" class="btn ml_10">Validate</button>' +
        '<button id="save_in_batch" type="button" class="btn ml_10 btn-success">Save</button>' +
        '<button id="save_next" type="button" class="btn ml_10 btn-success">Save & Next</button></div></div>';

function setMovement(){
    $('input[name="research_text"]').focus();
    $( "#sortable1, #sortable2" ).sortable({
        connectWith: ".connectedSortable",
        cursor: 'move',
        revert: "invalid",
        helper : 'clone',
        handle: "h3",
    });

    $("#research, #research_edit" ).draggable({
        containment: "#main",
        handle: ".handle",
        drag: function( event, ui ) {
                var isChrome = /Chrome/.test(navigator.userAgent) && /Google Inc/.test(navigator.vendor);
                var isSafari = /Safari/.test(navigator.userAgent) && /Apple Computer/.test(navigator.vendor);

                if (isChrome || isSafari){
                    if(ui.originalPosition.left-100 > ui.position.left){
                        if($(this).attr('id')=='research_edit'){
                            $('#research_edit').css({'z-index':'9999'});
                            $('#research').css({'z-index':'9998'});
                        } else {
                            $('#research_edit').css({'z-index':'9998'});
                            $('#research').css({'z-index':'9999'});
                        }
                    } else {
                        if($(this).attr('id')=='research_edit'){
                            $('#research_edit').css({'z-index':'9999'});
                            $('#research').css({'z-index':'9998'});
                        } else {
                            $('#research_edit').css({'z-index':'9998'});
                            $('#research').css({'z-index':'9999'});
                        }
                    }
                }else{
                    if(ui.originalPosition.left-100 > ui.position.left){
                        if($(this).attr('id')=='research_edit'){
                            $('#research').css({'left':'50%'});
                            $('#research_edit').css({'z-index':'9999'});
                            $('#research').css({'z-index':'9998'});
                        } else {
                            $('#research_edit').css({'z-index':'9998'});
                            $('#research').css({'z-index':'9999'});
                            $('#research_edit').css({'left':'0%'});
                        }
                    } else {
                        if($(this).attr('id')=='research_edit'){
                            $('#research_edit').css({'z-index':'9999'});
                            $('#research').css({'z-index':'9998'});
                            $('#research').css({'left':'0%'});
                        } else {
                            $('#research_edit').css({'left':'-50%'});
                            $('#research_edit').css({'z-index':'9998'});
                            $('#research').css({'z-index':'9999'});
                        }
                    }
                }
        },
    }).bind('click', function(){
            $(this).focus();
    });

    $( "ul#sortable1 li.boxes, ul#sortable2 li.boxes" ).resizable();
    $("#related_keywords").resizable({minWidth: 418, maxWidth:418});
}
$(document).ready(function() {
    $('title').text("Research & Edit");


    /*$.post(base_url + 'index.php/research/getBoxData', {}, function(data){
        var content = '';

        for(var i=0; i<data.length; i++){
            if(data[i]['position'] == 'left'){
                if(data[i]['box_id'].indexOf('main') > -1){
                    content += box[data[i]['box_id']+'_start'];
                } else {
                    content += '<li class="boxes mt_10">'+box[data[i]['box_id']]+'</li>';
                }
            }
            if(data[i]['position'] == 'right'){
                if(data[i]['box_id'].indexOf('main') > -1){
                    content += '</ul></div>';
                    content += box[data[i]['box_id']+'_start'];
                }else{
                    content += '<li class="boxes mt_10">'+box[data[i]['box_id']]+'</li>';
                }
            }
        }
        content += '</ul></div>';

    }, 'json');*/

    setMovement();



});
</script>
<div class="tabbable">
    <ul class="nav nav-tabs jq-research-tabs">
        <li class=""><a data-toggle="tab" href="<?php echo site_url('research/create_batch');?>">Create Batch</a></li>
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('research');?>">Edit</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('research/research_batches');?>">Review</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('research/research_reports');?>">Reports</a></li>
    </ul>
    <div class="tab-content">
    <div class="research">

        <div class="row-fluid">
            <div class="span6">
                Batch:
                <?php
                    $selected = array();
                    if(count($customer_list) == 2){
                        array_shift($customer_list);
                        $selected = array(0);
                    }
                    echo form_dropdown('customers', $customer_list, $selected, 'class="mt_10 category_list"'); ?>
                <?php echo form_dropdown('batches', $batches_list, array(), 'class="mt_10" style="width: 145px;"'); ?>
                <button id="export_batch" class="btn" type="button" style="margin-left:5px; margin-right: 10px;">Export</button>
            </div>
            <div class="span6">
                Add new: <input type="text" class="mt_10" style="width:180px" name="new_batch">
                <button id="new_batch" class="btn" type="button" style="margin-left:5px">New</button>
            </div>
        </div>
        
        <div class="clear"></div>

        <div id="research_tab1" class="tab-pane active">

            <!-- NEW STUFF (START) -->
            <div class="row-fluid">
                <p  style='width: 44px' class='inline_block float_l reset_mb_mt15'>Filter:</p>
                <?php echo form_open('', array('id'=>'measureForm', 'style' => 'float: left; width: 840px;')); ?>
                    <input type="text" id="research_text" name="research_text" value="" class="span5 w_300" placeholder=""/>
                    <div id="res_dropdown" class="ddslick_dropdown" style="width:90px;"></div>
                    <?php echo form_dropdown('category', $category_list, array(), 'class="category_list"'); ?>
                    <button id="research_search" type="button" class="btn btn-success" style="margin-top:-10px;">Search</button>
                    <p id="show_result">Show <select style="width:60px; margin-right:5px;margin-top: 9px;" name="result_amount">
                            <option value="10">10</option>
                            <option value="20">20</option>
                            <option value="50">50</option>
                            <option value="100">100</option>
                        </select>
                        results
                    </p >
                <?php echo form_close();?>
            </div>

            <div class="row-fluid" id="main">
                <div class="span6" id="research" class="connectedMoved">
                    <h3 class="handle"><a href="#" onclick="return false;" class="hideShow"><img style="width:15px;margin-right: 10px" src="<?php echo base_url();?>img/arrow-down.png" /></a>Research<a href="#" class="ml_10 research_arrow"><img src="<?php echo base_url(); ?>/webroot/img/arrow.png"></a></h3>
                    <ul class="research_content connectedSortable" id="sortable1">
                        <li class="boxes mt_10">
                            <h3><a href="#" onclick="return false;" class="hideShow"><img style="width:12px;margin-right: 10px" src="<?php echo base_url();?>img/arrow-down.png" /></a>Results<a href="#" class="ml_10 research_arrow"><img src="<?php echo base_url(); ?>/webroot/img/arrow.png"></a></h3>
                            <div class="boxes_content"  style="height: 200px;padding:0px;">
                                <ul class="product_title">
                                    <li class="main"><span><b>Product Name</b></span><span><b>URL</b></span></li>
                                </ul>
                                <ul id="research_products" style="height: 170px; overflow: auto;">
                                    <li><span>&nbsp;</span><span>&nbsp;</span></li>
                                    <li><span>&nbsp;</span><span>&nbsp;</span></li>
                                    <li><span>&nbsp;</span><span>&nbsp;</span></li>
                                    <li><span>&nbsp;</span><span>&nbsp;</span></li>
                                </ul>
                                <ul id="product_descriptions"></ul>
                            </div>
                        </li>
                        <li class="boxes mt_10" id="related_keywords">
                            <h3><a href="#" onclick="return false;" class="hideShow"><img style="width:12px;margin-right: 10px" src="<?php echo base_url();?>img/arrow-down.png" /></a>Related Keywords<a href="#" class="ml_10 research_arrow"><img src="<?php echo base_url(); ?>/webroot/img/arrow.png"></a></h3>
                            <div class="boxes_content" >
                                <ul id="rel_keywords" style="height: 170px; overflow: auto;">
                                    <li class="primary"><span>Televisions</span></li>
                                    <li class="secondary"><span>TVs</span></li>
                                    <li class="tertiary"><span>LCD TV</span></li>
                                    <li class="primary"><span>LED TV</span></li>
                                    <li class="secondary"><span>Digital TV</span></li>
                                    <li class="tertiary"><span>Internet TV</span></li>
                                    <li class="primary"><span>HDTV</span></li>
                                    <li class="secondary"><span>3D</span></li>
                                    <li class="tertiary"><span>HDMI</span></li>
                                    <li class="primary"><span>2D</span></li>
                                    <li class="secondary"><span>TFT</span></li>
                                    <li class="tertiary"><span>USB</span></li>
                                </ul>
                            </div>
                        </li>
                        <li class="boxes mt_10">
                            <h3><a href="#" onclick="return false;" class="hideShow"><img style="width:12px;margin-right: 10px" src="<?php echo base_url();?>img/arrow-down.png" /></a>SEO Phrases<a href="#" class="ml_10 research_arrow"><img src="<?php echo base_url(); ?>/webroot/img/arrow.png"></a></h3>
                            <div class="boxes_content">
                                <ul class='less_b_margin ml_0' data-status='seo_an'>
                                </ul>
                                <ul class='less_b_margin ml_0' data-st-id='short_desc_seo' data-status='seo_an'></ul>
                                <ul class='less_b_margin ml_0' data-st-id='long_desc_seo' data-status='seo_an'></ul>
                            </div>
                        </li>
                    </ul>
                </div>
                <div class="span6" id="research_edit" class="connectedMoved">
                    <h3 class="handle"><a href="#" onclick="return false;" class="hideShow"><img style="width:15px;margin-right: 10px" src="<?php echo base_url();?>img/arrow-down.png" /></a>Edit<a href="#" class="ml_10 research_arrow"><img src="<?php echo base_url(); ?>/webroot/img/arrow.png"></a></h3>
                    <ul class="research_content connectedSortable" id="sortable2">
                        
                        <li class="boxes mt_10" id="styleguide">
                            <h3><a href="#" onclick="return false;" class="hideShow"><img style="width:12px;margin-right: 10px" src="<?php echo base_url();?>img/arrow-down.png" /></a>Style Guide<a href="#" class="ml_10 research_arrow"><img src="<?php echo base_url(); ?>/webroot/img/arrow.png"></a></h3>
                            <div class="boxes_content">
                            </div>
                        </li>
                        
                        
                        <li class="boxes mt_10" id="keywords">
                            <h3><a href="#" onclick="return false;" class="hideShow"><img style="width:12px;margin-right: 10px" src="<?php echo base_url();?>img/arrow-down.png" /></a>Keywords<a href="#" class="ml_10 research_arrow"><img src="<?php echo base_url(); ?>/webroot/img/arrow.png"></a></h3>
                            <div class="boxes_content">
                                <p><span>Primary:</span><input class="keywords" type="text" name="primary" value="" /><a href="#" class="clear_all">x</a></p>
                                <p><span>Secondary:</span><input class="keywords" type="text" name="secondary" value="" /><a href="#" class="clear_all">x</a></p>
                                <p><span>Tertiary:</span><input class="keywords" type="text" name="tertiary" value="" /><a href="#" class="clear_all">x</a></p>
                            </div>
                        </li>

                        <li class="boxes mt_10" id="page_elements">
                            <h3><a href="#" onclick="return false;" class="hideShow"><img style="width:12px;margin-right: 10px" src="<?php echo base_url();?>img/arrow-down.png" /></a>Page Elements<a href="#" class="ml_10 research_arrow"><img src="<?php echo base_url(); ?>/webroot/img/arrow.png"></a></h3>
                            <div class="boxes_content">
                                <p><button id="generate_product" type="button" class="btn pull-right">Generate</button>
                                    <label>Product name:</label><input type="text" class="span11 ml_0" name="product_name"/>
                                    <input type="hidden" name="url"/>
                                    <input type="hidden" name="revision"/>
                                </p>
                                <p><label>Meta title:</label><input type="text"  class="span11 ml_0" name="meta_title" /></p>
                                <p><label>Meta description:</label><textarea name="meta_description" style="height:100px;" ></textarea></p>
                                <p><button id="generate_keywords" type="button" class="btn pull-right">Generate</button>
                                    <label>Meta keywords:</label><input type="text" class="span11 ml_0" name="meta_keywords" /></p>
                            </div>
                        </li>
                        <li class="boxes mt_10">
                            <h3><a href="#" onclick="return false;" class="hideShow"><img style="width:12px;margin-right: 10px" src="<?php echo base_url();?>img/arrow-down.png" /></a>Descriptions<a href="#" class="ml_10 research_arrow"><img src="<?php echo base_url(); ?>/webroot/img/arrow.png"></a></h3>
                            <div class="boxes_content">
                                <div class="row-fluid"><label>Short description:</label>
                                     <label><span id="research_wc">0</span> words<input type="hidden" name="short_description_wc" /></label>
                                     <button id="research_generate" type="button" class="btn" style="float:left;">Generate</button>
                                     <textarea type="text" name="short_description" class="span10 mt_10" style="height:100px;"></textarea>
                                     <div class="pagination">
                                         <ul id="pagination">
                                         </ul>
                                     </div>
                                </div>
                                <div class="row-fluid"><label>Long description:</label>
                                    <label><span id="research_wc1">0</span> words<input type="hidden" name="long_description_wc" /></label>
                                    <div class="search_area uneditable-input ml_10"  id="long_description" contenteditable="false" style="cursor: text; width: 365px; overflow: auto;"></div>
                                </div>
                                <div class="row-fluid" id="research_density">
                                    <label>Density:</label><label>Primary:</label><input type="text" name="research_primary" class="span2" value="0" readonly="readonly" /><span class="percent">%</span>
                                    <label>Secondary:</label><input type="text" name="research_secondary" class="span2" value="0" readonly="readonly" /><span class="percent" >%</span>
                                    <label>Tertiary:</label><input type="text" name="research_tertiary" class="span2" value="0" readonly="readonly" /><span class="percent" >%</span>
                                    <button id="research_update_density" type='button' class='btn btn-primary ml_10'>Update</button></p>
                                    <p>Total words: <span id="research_total">0</span> words</p>
                                </div>
                                <div class="row-fluid mb_20">
                                    <button id="validate" type="button" class="btn ml_10">Validate</button>
                                    <button id="save_in_batch" type="button" class="btn ml_10 btn-success">Save</button>
                                    <button id="save_next" type="button" class="btn ml_10 btn-success">Save & Next</button>
                                </div>
                            </div>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    </div>
</div>