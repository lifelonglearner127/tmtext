<script src="http://code.jquery.com/ui/1.10.3/jquery-ui.js"></script>
<script type="text/javascript">
	$(document).ready(function() {
		$('head').find('title').text('Validate');
	});
</script>
<div class="row-fluid">
	<?php
		echo form_open('editor/attributes', array('id'=>'attributesForm')).form_close();
		echo form_open('editor/search', array('id'=>'searchForm'));
	?>
	<input type="text" name="s" value="UN40ES6500" id="search" class="span11" placeholder="Search (SKU, Model #, Manufacturer, or URL) from CSV, DB or files"/>
	<button type="submit" class="btn pull-right">Search</button>
	<?php echo form_close();?>
</div>
<div class="row-fluid">
	<div class="span search_area uneditable-input" style="overflow : auto;" id="attributes">
	    Product attributes
	</div>		                
</div>