					<div class="row-fluid">
						<h3>Descriptions Generator:</h3>
				    	<?php echo form_open("system/save", array("class"=>"form-horizontal", "id"=>"system_configure"));?>
					    <?php foreach ($this->config->item('generators') as $key => $generator) {?>
				    		<div class="control-group">
								<label class="control-label" for="java_generator"><?php echo $generator[0];?></label>
								<div class="controls">
									<?php echo form_checkbox($generator[1], 1, $generator[2], 'id="'.$generator[1].'"'.(($generator[1]=='python_generator')?' disabled':''));?>
								</div>
							</div>
						<?php } ?>
						    <div class="control-group">
							    <div class="controls">
								    <button type="submit" class="btn btn-danger"><i class="icon-white icon-ok"></i>&nbsp;Save</button>
							    </div>
							</div>
					    <?php echo form_close(); ?>
					</div>