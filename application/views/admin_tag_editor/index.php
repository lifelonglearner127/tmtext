<form class="form-horizontal" id="tag_editor">
    <div>
        <div id="products">

        </div>
    </div>
<div class="row-fluid">
     <div class="span5" style="width: 327px;">
         <?php echo form_dropdown('filename', $files ); ?>
         <a href="#popup" id="delete_category" class="btn btn-danger ml_10 fancybox"><i class="icon-white icon-ok"></i>&nbsp;Delete</a>
         <div id="popup">
             <p>This will delete <span id="category_name"></span> category and all associated rules permanently. Are you sure you want to continue?</p>
             <button id="yes" class="btn new_btn ml_15"><i class="icon-ok-sign"></i>&nbsp;Yes</button>
             <button id="no" class="btn new_btn ml_15"><i class="icon-ok-sign"></i>&nbsp;No</button>
         </div>
     </div>
     <div class="span6 admin_tageditor_content">
        <p>New category:</p>
         <input type="text" name="new_file" class="span6" />       
        <button id="create" class="btn new_btn ml_15"><i class="icon-white icon-file"></i>&nbsp;Create</button>
     </div>
</div>
    <div>
        <div  id="tageditor_content" class="row-fluid mt_20 admin_tageditor_content">
            <div id="items" class="span10 search_area uneditable-input" style="overflow : auto; height:250px;">
                <?php
                echo ul($tagrules_data,
                    array('id' => 'items_list')
                );
                ?>
            </div>
            <button id="test" class="btn new_btn ml_15"><i class="icon-ok-sign"></i>&nbsp;Test</button>
            <button id="next" class="btn new_btn mt_10 ml_15"><i class="icon-white icon-ok"></i>&nbsp;Next</button>
            <button id="new" class="btn new_btn btn-primary mt_10 ml_15"><i class="icon-white icon-ok"></i>&nbsp;New</button>
            <button id="delete" class="btn new_btn btn-danger mt_10 ml_15"><i class="icon-white icon-ok"></i>&nbsp;Delete</button>            
            <button id="undo" class="btn new_btn btn-warning mt_10 ml_15"><i class="icon-white icon-ok"></i>&nbsp;Undo</button>
            <button id="save_data" class="btn new_btn btn-success mt_10 ml_15"><i class="icon-white icon-ok"></i>&nbsp;Save</button>
        </div>

    </div>
    <div class="row-fluid matches_message">
        <span class="matches_found"></span>
    </div>
<div class="row-fluid mt_10 admin_tageditor_content">
    <div class="search_area uneditable-input span10" onClick="this.contentEditable='true';" style="cursor: text; width: 765px; height: 250px; overflow : auto;" id="tageditor_description">
        <?php
            echo ul($description,
                array()
            );
        ?>
    </div>
    <button id="new_desc" class="btn new_btn btn-primary mt_10 ml_15"><i class="icon-white icon-ok"></i>&nbsp;New</button>
    <button id="save_desc" class="btn new_btn btn-success mt_10 ml_15"><i class="icon-white icon-ok"></i>&nbsp;Save</button>
    <button id="delete_desc" class="btn new_btn btn-danger mt_10 ml_15"><i class="icon-white icon-ok"></i>&nbsp;Delete</button>
    <div id="standart_description" style="display:none">
        <?php
        echo ul($description,
            array()
        );
        ?>
    </div>
</div>
</form>



