					<div class="row-fluid">
						<h3>Descriptions Generator:</h3>
					    <form class="form-horizontal" id="system_configure">
					    <?php foreach ($this->config->item('generator') as $key => $generator) {?>
				    		<div class="control-group">
								<label class="control-label" for="java_generator"><?php echo $generator[0];?></label>
								<div class="controls">
									<?php echo form_radio('generator', $key, $generator[2], 'id="'.$generator[1].'"');?>
								</div>
							</div>
						<?php } ?>
						    <div class="control-group">
							    <div class="controls">
								    <button type="submit" class="btn btn-danger"><i class="icon-white icon-ok"></i>&nbsp;Save</button>
							    </div>
							</div>
					    </form>
					</div>