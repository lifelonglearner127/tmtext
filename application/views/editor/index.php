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
		                <div class="span8 search_area uneditable-input" style="width: 597px; overflow : auto;" id="items">
		                Original product descriptions
		                </div>
		            	<div class="span4 search_area uneditable-input" style="overflow : auto;" id="attributes">
		                Product attributes
		                </div>
					</div>
<?php //echo form_open('editor/save'); ?>
					<div class="row-fluid auto_title">
                		<input type="text" class="span12" id = 'title'/>
						<div class="chars_content title_length">
							<input type="text" name="title_length" value="128" class="span3"/>
							<label>Chars: <span id="tc">0</span> of </label>
						</div>
					</div>
					<div class="row-fluid new_product">
						<textarea class="span12 search_area" name='description'></textarea>
						<div class="pull-left">
							<button class="btn new_btn btn-primary"><i class="icon-white icon-file"></i>&nbsp;New</button>
							<div class="pagination">
			                    <ul id="pagination">
			                    </ul>
						    </div>
						</div>
						<div class="chars_content">
							<input type="text" name="description_length" value="150" class="span3"/>
							<label>Words: <span id="wc">0</span> of </label>
						</div>
						<button class="btn new_btn_fr ml_15"><i class="icon-ok-sign"></i>&nbsp;Validate</button>
						<button class="btn new_btn_fr btn-danger ml_15"><i class="icon-white icon-ok"></i>&nbsp;Save</button>

					</div>
<?php //echo form_close(); ?>




<?php if(0) {?>
	<!--Website Content Starts-->

	<div class="wrapper">

		<div class="navigation">

            <div class="system_nav">
                <ul>
                    <li><a class="active" href="" title="">EDITOR</a></li>
                    <li><a href="" title="">CUSTOMER</a></li>
                </ul>
            </div>

            <div class="admin_nav">
                <label>admin: </label>
                <ul>
                    <li><a href="" title="">SYSTEM</a></li>
                    <li><a href="" title="">CUSTOMER</a></li>
                    <li><a href="" title="">EDITORS</a></li>
                </ul>
            </div>
            <div class="clear"></div>
        </div>

<?php
echo form_open('editor/attributes', array('id'=>'attributesForm'))
	.form_close();

echo form_open('editor/search', array('id'=>'searchForm')); ?>

        <div class="search_part">

            <div class="search_field">
                <input type="text" name="s" value="UN40ES6500" id="search" class="search_product" placeholder = 'Search (SKU, Model #, Manufacturer, or URL) from CSV, DB or ﬁles'/>
            </div>

            <button class="search_but">search</button>

        </div>
<?php echo form_close();?>

        <div class="product_des">

            <div class="description">
                <div  style="width:580px; height:200px; background-color: white; border: 1px solid; margin: 2px; padding: 2px;overflow : auto;" id="items">
                Product descriptions listing
                </div>
            </div>

            <div class="attribute_list">
            	<div  style="width:308px; height:200px; background-color: white; border: 1px solid; margin: 2px; padding: 2px;overflow : auto;" id="attributes">
                Product attributes
                </div>
            </div>

        </div>
        <div class="clear"> </div>
        <div class="product_title">

            <div class="auto_title">
                <input type="text" class="" id = 'title', disabled = 'disabled'/>
            </div>

            <div class="title_length">
                <label>Chars: </label>
                <span id="tc"></span>
                <label> </label>
                <label class="label1">of </label>
                <input type="text" class="length"/>
            </div>

        </div>

<?php echo form_open('editor/save'); ?>
        <div class="new_product">

            <div class="new_des">
                <textarea cols="111" rows="12" name = 'description' disabled = 'disabled'></textarea>
            </div>

            <div class="bottom_nav">
                <div class="sequence">
                    <button class="new">new</button>
                    <ul id="pagination">
                    </ul>
                </div>

                <div class="applying">
                    <button class="validate">validate</button>
                    <button class="save">save</button>
                    <label>Words: </label>
                    <span id="wc"></span>
                    <label> </label>
                    <label class="label2">of </label>
                    <input type="text" class=""/>
                </div>
            </div>

        </div>
<?php echo form_close(); ?>
	</div> <!-- wrapper -->

	<!--Website Content Ends-->


<!--
<?php
echo form_open('editor/attributes', array('id'=>'attributesForm'))
	.form_close();


echo form_open('editor/search', array('id'=>'searchForm'))
	.form_input(array(
			'name'=>'search',
			'id' =>'s',
			'placeholder' => 'Search (SKU, Model #, Manufacturer, or URL) from CSV, DB or ﬁles'
		))
	.form_submit(array('name'=>'search', 'id' => 'search'),'Search')
	.br();
?>
	<div id="items" class="block block60">
		Product descriptions listing
	</div>
	<div id="attributes" class="block block20">
		Product attributes
	</div>

	<div style="clear:both"></div>
<?php
echo form_open('editor/search')
	.form_input(array(
			'name'=>'title',
			'id' =>'title',
			'disabled' => 'disabled'
		))
	.br()
	.form_textarea(array(
			'name' => 'description',
			'disabled' => 'disabled'
		))
	.br()
	.form_button('validate','Validate')
	.form_submit('form_save', 'Save')
	.form_close();
?> //-->

<?php } ?>