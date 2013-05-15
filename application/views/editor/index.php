<script src="http://code.jquery.com/ui/1.10.3/jquery-ui.js"></script>

					<div class="row-fluid">
					<?php
					echo form_open('editor/attributes', array('id'=>'attributesForm')).form_close();
					echo form_open('editor/search', array('id'=>'searchForm'));
					?>
						<input type="text" name="s" value="<?=(!empty($lastSaved)) ? $lastSaved['search'] : 'UN40ES6500'?>" id="search" class="span11" placeholder="Search (SKU, Model #, Manufacturer, or URL) from CSV, DB or files"/>
						<button type="submit" class="btn pull-right">Search</button>
					<?php echo form_close();?>
					</div>
					<div class="row-fluid">
		                <div class="span8 search_area uneditable-input cursor_default" style="width: 597px; overflow : auto;" id="items">
		                Original product descriptions
		                </div>
		            	<div class="span4 search_area uneditable-input cursor_default" style="overflow : auto;" id="attributes">
		            		<?php if (!empty($lastSaved)){ 
		            			$attributes = unserialize($lastSaved['attributes']);
		            		?>
		            			<ul>
		            				<?php foreach ($attributes as $key => $value) { ?>
		            					<li><?=$key.' '.$value?></li>
		            				<?php } ?>
		            			</ul>
		            		<?php }else{ ?>
		                		Product attributes
		                	<?php } ?>
		                </div>
					</div>
<?php //echo form_open('editor/save'); ?>
					<div class="row-fluid auto_title">
                		<input type="text" class="span12" id = 'title' value="<?=(!empty($lastSaved)) ? htmlspecialchars($lastSaved['title']) : ''?>"/>
						<div class="chars_content title_length">
							<input type="text" name="title_length" value="128" class="span3"/>
							<label>Chars: <span id="tc">0</span> of </label>
						</div>
					</div>
					<div class="row-fluid new_product">
						<div class="search_area uneditable-input" id="textarea" onClick="this.contentEditable='true';" style="cursor: text; width: 98.5%;"><?=(!empty($lastSaved)) ? $lastSaved['description'] : ''?></div>
                        <ul id="trash" class="desc_title trash" style="display:none"></ul>
					</div>
					<div class="row-fluid new_product">
						<textarea class="span12 search_area" name='description' style="display:none"></textarea>
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
						<button id="save" class="btn new_btn_fr btn-success ml_15"><i class="icon-white icon-ok"></i>&nbsp;Save</button>
                        <button id="validate" class="btn new_btn_fr ml_15"><i class="icon-ok-sign"></i>&nbsp;Validate</button>
                        <button id="use" class="btn new_btn_fr ml_15"><i class="icon-ok-sign"></i>&nbsp;Use</button>
                    </div>
<?php //echo form_close(); ?>