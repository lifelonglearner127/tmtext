<script type="text/javascript">
    $("select[name='category']").trigger("change");
    $("#tageditor_description").trigger("ready");
</script>
<form class="form-horizontal" id="tag_editor">
    <div>
        <div id="products">

        </div>
    </div>
    <div class="row-fluid">
         <div class="span5" style="width: 327px;">
             <?php echo form_dropdown('category', $category_list ); ?>
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
            </div>
            <button id="test" class="btn new_btn ml_15"><i class="icon-ok-sign"></i>&nbsp;Test</button>
            <button id="next" class="btn new_btn mt_10 ml_15"><i class="icon-white icon-ok"></i>&nbsp;Next</button>
            <button id="new" class="btn new_btn btn-primary mt_10 ml_15"><i class="icon-white icon-ok"></i>&nbsp;New</button>
            <button id="delete" class="btn new_btn btn-danger mt_10 ml_15"><i class="icon-white icon-ok"></i>&nbsp;Delete</button>
            <button id="undo" class="btn new_btn btn-warning mt_10 ml_15"><i class="icon-white icon-ok"></i>&nbsp;Undo</button>
            <button id="save_data" class="btn new_btn btn-success mt_10 ml_15"><i class="icon-white icon-ok"></i>&nbsp;Save</button>
            <span class="btn btn-success fileinput-button mt_10 ml_15 btn-mini">Import<i class="icon-plus icon-white"></i>
			        <input id="fileupload" type="file" name="files[]" multiple>
            </span>
            <div id="files"></div>
            <script>
                $(function () {
                    var url = '<?php echo site_url('admin_tag_editor/upload_dat');?>';
                    $('#fileupload').fileupload({
                        url: url,
                        dataType: 'json',
                        done: function (e, data) {
                            $.each(data.result.files, function (index, file) {
                                $.post('<?php echo site_url('admin_tag_editor/import_rules');?>', function(data) {
                                });
                            });

                        }
                    });
                });
            </script>
        </div>
    </div>
    <div class="row-fluid">
    	<div class="span2">
        	<button id="new_test_set" class="btn new_btn"><i class="icon-ok-sign"></i>&nbsp;New Test Set</button>
        </div>
         <div class="span6 admin_tageditor_content">
            <p>Number of descriptions:</p>
			<div>
				<i class="icon-chevron-up" id="input_fln_up"></i>
	            <input id="description_limit" type="text" class="span2 input_fln" value="15"/>
	            <i class="icon-chevron-down" id="input_fln_down"></i>
            </div>
         </div>
    </div>
    <div class="row-fluid matches_message">
        <span class="matches_found"></span>
        <button id="export" class="btn btn-success pull-right btn-mini" style="margin-right:60px"><i class="icon-white icon-ok"></i>&nbsp;Export</button>
    </div>
    <div class="row-fluid mt_10 admin_tageditor_content">
        <div class="search_area uneditable-input span10" onClick="this.contentEditable='true';" style="cursor: text; width: 765px; height: 250px; overflow : auto;" id="tageditor_description">
        </div>
        <button id="new_desc" class="btn new_btn btn-primary mt_10 ml_15"><i class="icon-white icon-ok"></i>&nbsp;New</button>
        <button id="save_desc" class="btn new_btn btn-success mt_10 ml_15"><i class="icon-white icon-ok"></i>&nbsp;Save</button>
        <button id="delete_desc" class="btn new_btn btn-danger mt_10 ml_15"><i class="icon-white icon-ok"></i>&nbsp;Delete</button>
        <div id="standart_description" style="display:none">
        </div>
    </div>
</form>



