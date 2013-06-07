<script src="http://code.jquery.com/ui/1.10.3/jquery-ui.js"></script>
<script type="text/javascript">
	$(document).ready(function() {
		$('head').find('title').text('Validate');

		// ---- search string cookie (auto mode search launcher) (start)
	    var auto_mode_search_str = "";
	    var validate_search_str = $.cookie('validate_search_str');
	    if(typeof(validate_search_str) !== 'undefined' && validate_search_str !== null && validate_search_str !== "") {
	        auto_mode_search_str = validate_search_str;
	    }
	    if(auto_mode_search_str !== "") {
	        $("input[type='text'][name='search_validate']").val(auto_mode_search_str);
	        $("#validate_s_submit_btn").attr('disabled', true);
	        setTimeout(function() {
	            $("#searchForm").trigger('submit');
	            $("#validate_s_submit_btn").removeAttr('disabled');
	        }, 1000);
	    }
	    // ---- search string cookie (auto mode search launcher) (end)

	});
</script>
<div class="row-fluid">
	<?php
		echo form_open('editor/attributes', array('id'=>'attributesForm')).form_close();
		echo form_open('editor/search', array('id'=>'searchForm'));
	?>
	<input type="text" name="s" value="UN40ES6500" id="search" name='search_validate' class="span11" placeholder="Search (SKU, Model #, Manufacturer, or URL) from CSV, DB or files"/>
	<button id='validate_s_submit_btn' type="submit" class="btn pull-right">Search</button>
	<input type='hidden' id='form_id' name='form_id' value='validate_form'>
	<?php echo form_close();?>
</div>
<div class="row-fluid">
	<div class="span search_area uneditable-input" style="overflow : auto;" id="attributes">
	    Product attributes
	</div>		                
</div>