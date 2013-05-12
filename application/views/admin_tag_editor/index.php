<form class="form-horizontal" id="tag_editor">
    <div>
        <div id="products">

        </div>
    </div>
<div class="row-fluid span10">
     <div class="span4"><?php echo form_dropdown('filename', $files ); ?></div>
     <div class="span6 admin_tageditor_content">
        <p>New category:</p>
         <input type="text" name="new_file" class="span8" />
       </div>
        <button class="btn new_btn"><i class="icon-white icon-file"></i>&nbsp;Create</button>
</div>
    <div>
<div  id="tageditor_content" class="row-fluid mt_20 admin_tageditor_content">
    <div id="items" class="span10 search_area uneditable-input" style="overflow : auto;">
        <?php
        echo ul($tagrules_data,
            array('id' => 'items_list')
        );
        ?>
    </div>
    <button id="test" class="btn new_btn ml_15"><i class="icon-ok-sign"></i>&nbsp;Test</button>
    <button id="save_data" class="btn new_btn btn-success mt_10 ml_15"><i class="icon-white icon-ok"></i>&nbsp;Save</button>
</div>
        </div>
<div class="row-fluid mt_30 admin_tageditor_content">
    <div class="search_area uneditable-input span10" style="width: 765px; height: 250px; overflow : auto;" id="tageditor_description">
        <?php
            echo ul($description,
                array()
            );
        ?>
    </div>
    <div id="standart_description" style="display:none">
        <?php
        echo ul($description,
            array()
        );
        ?>
    </div>
</div>
</form>