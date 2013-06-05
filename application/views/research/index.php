<div class="main_content_other"></div>
<div class="main_content_editor research">
    <div class="row-fluid">
        <?php echo form_open('', array('id'=>'measureForm')); ?>
        <input type="text" id="research_text" name="research_text" value="" class="span8 " placeholder=""/>
        <div id="res_dropdown" class="ddslick_dropdown"></div>
        <button id="research_search" type="button" class="btn pull-right btn-success">Search</button>
        <?php echo form_close();?>
    </div>
    <div class="clear"></div>
    <div class="row-fluid">
        <div class="span6">
            Show <select class="mt_10" style="width:50px;" name="result_amount">
                <option value="10">10</option>
                <option value="20">20</option>
                <option value="50">50</option>
                <option value="100">100</option>
            </select>
            results in category
            <?php echo form_dropdown('category', $category_list, array(), 'class="mt_10"'); ?>
        </div>
        <div class="span6">
            Batch:
            <?php echo form_dropdown('batches', $batches_list, array(), 'class="mt_10" style="width: 100px;"'); ?>
            <button class="btn" type="button" style="margin-left:5px; margin-right: 10px;">Export</button>
            Add new: <input type="text" class="mt_10" style="width:80px" name="new_batch">
            <button id="new_batch" class="btn" type="button" style="margin-left:5px">New</button>
        </div>

    </div>
    <div class="row-fluid" id="main">
        <div class="span6" id="research" class="connectedMoved"> 
            <h3 class="handle">Research</h3>
            <ul class="research_content connectedSortable" id="sortable1">
                <li class="boxes">
                    <h3>Results</h3>
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
                    <h3>Related Keywords</h3>
                    <div class="boxes_content">
                        <ul id="rel_keywords">
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
                    <h3>SEO Phrases</h3>
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
            <h3 class="handle">Edit</h3>
            <ul class="research_content connectedSortable" id="sortable2">
                <li class="boxes" id="keywords">
                    <h3>Keywords</h3>
                    <div class="boxes_content">
                        <p><span>Primary:</span><input class="keywords" type="text" name="primary" value="" /><a href="#" class="clear_all">x</a></p>
                        <p><span>Secondary:</span><input class="keywords" type="text" name="secondary" value="" /><a href="#" class="clear_all">x</a></p>
                        <p><span>Tertiary:</span><input class="keywords" type="text" name="tertiary" value="" /><a href="#" class="clear_all">x</a></p>
                    </div>
                </li>

                <li class="boxes mt_10" id="page_elements">
                    <h3>Page Elements</h3>
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
                    <h3>Descriptions</h3>
                    <div class="boxes_content">
                        <div class="row-fluid"><label>Short description:</label>
                             <label><span id="research_wc">0</span> words</label>
                             <button type="button" class="btn" style="float:left;">Generate</button>
                             <textarea type="text" name="short_description" class="span10 mt_10" style="height:100px;"></textarea>
                        </div>
                        <div class="row-fluid"><label>Long description:</label>
                            <label><span id="research_wc1">0</span> words</label>
                            <div class="search_area uneditable-input ml_10"  id="long_description" onClick="this.contentEditable='true';" style="cursor: text; width: 365px;"></div>


                            <!--div class="search_area uneditable-input" id="long_description"
                                 onclick="this.focus(); " style="cursor: text;height:150px; width:380px;"></div-->
                           <!--textarea type="text" name="long_description" class="span10"  style="height:150px;display:none"></textarea-->
                        </div>
                        <div class="row-fluid" id="research_density">
                            <label>Persixy:</label><label>Primary:</label><input type="text" name="research_primary" class="span2" value="0" readonly="readonly" /><span class="percent">%</span>
                            <label>Secondary:</label><input type="text" name="research_secondary" class="span2" value="0" readonly="readonly" /><span class="percent" >%</span>
                            <label>Tertiary:</label><input type="text" name="research_tertiary" class="span2" value="0" readonly="readonly" /><span class="percent" >%</span></p>
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

