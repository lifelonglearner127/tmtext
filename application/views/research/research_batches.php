<div class="tabbable">
    <ul class="nav nav-tabs jq-research-tabs">
        <li class=""><a data-toggle="tab" href="<?php echo site_url('research');?>">General</a></li>
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('research/research_batches');?>">Batches</a></li>
    </ul>
    <div class="tab-content research_batches">
        <div id="research_tab2" class="tab-pane active">
            <div class="row-fluid">
                <div class="span6">
                    Batches: <?php echo form_dropdown('research_batches', $batches_list, array(), 'class="mt_10 mr_10" style="width: 100px;"'); ?>
                    Edit Name:<input type="text" class="mt_10 ml_10" name="batche_name" />
                    <button id="research_batches_save" type="button" class="btn pull-right btn-success mt_10">Save</button>
                    <input type="text" id="research_batches_text" name="research_batches_text" value="" class="span8 ml_0" placeholder=""/>
                    <button id="research_batches_search" type="button" class="btn ml_10">Search</button>
                </div>
                <div class="span6">
                    <div class="control-group">
                        <label class="control-label mt_10" for="customer_name" style="width:70px; float: left">Columns:</label>
                        <div class="controls mt_10">
                            <ul id="gallery" class="product_title_content gallery span10">
                                <li><span>Text1</span><a hef="#" class="ui-icon-trash">x</a></li>
                                <li><span>Text2</span><a hef="#" class="ui-icon-trash">x</a></li>
                                <li><span>Text3</span><a hef="#" class="ui-icon-trash">x</a></li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row-fluid">
                <table id="research_results">
                    <thead>
                       <tr>
                           <td>Date</td>
                           <td>Editor</td>
                           <td>Product</td>
                           <td>URL</td>
                           <td>Meta Title</td>
                           <td>Meta Description</td>
                           <td>Short Description</td>
                           <td>Long Description</td>
                       </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>&nbsp;</td>
                            <td>&nbsp;</td>
                            <td>&nbsp;</td>
                            <td>&nbsp;</td>
                            <td>&nbsp;</td>
                            <td>&nbsp;</td>
                            <td>&nbsp;</td>
                            <td>&nbsp;</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="row-fluid mt_20">
                <button id="research_batches_delete" type="button" class="btn btn-danger ml_10">Delete</button>
                <button id="research_batches_undo" type="button" class="btn ml_10">Undo</button>
            </div>
            <div class="clear mt_40"></div>
        </div>
    </div>
</div>