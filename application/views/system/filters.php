<?php $this->load->model('batches_combinations') ?>
<?php $this->load->model('batches_model') ?>
			
<div class="tabbable">
	<?php $this->load->view('system/_tabs', array(
		'active_tab' => 'system/filters'
	)) ?>
	<?php $batches = $this->batches_model->getAll() ?>
	<div class="tab-content">
			<div class="tab-pane active">
				<div>
					<p>
						Current Combinations
					</p>
					<p>
						<div id="current_combinations">
							<?php if ($current_batches_combinations = $this->batches_combinations->findAll()): ?>
								<?php foreach ($current_batches_combinations as $key => $current_batches_combination): ?>
									<div>
										<?php echo $key + 1 ?>. <?php echo $current_batches_combination->title ?>
										<?php echo $current_batches_combination->category_id ? '(' . $current_batches_combination->category_id . ')' : '' ?>
										<a href="#" data-combination-id="<?php echo $current_batches_combination->id ?>" data-combination-code="<?php echo $current_batches_combination->batches_combination ?>" class="remove_batches_combinations">
											<i class="icon-remove"></i>
										</a>
									</div>
								<?php endforeach ?>
							<?php endif ?>
						</div>
					</p>
				</div>
				<form action="" method="post" id="batches_combinations">
					
					<label for="all_possible_combinations">
						<input type="radio" name="type" id="all_possible_combinations" class="combination_type" value="<?php echo Batches_combinations::TYPE_ALL_POSSIBLE_COMBINATIONS ?>" checked="checked" /> All possible combinations
					</label>									
					
					<label for="manual_combinations">
						<input type="radio" name="type" id="manual_combinations" class="combination_type" value="<?php echo Batches_combinations::TYPE_MANUAL_COMBINATIONS ?>" /> Manually combinations
					</label>
					
					<div style="display: none" class="manual_wrapper">
						<div class="manual_wrapper_content">
						</div>
						
						<button class="btn btn-primary add_one_more_combination" >Add more</button>
					</div>
					
					<button class="btn" id="generate_combinations" >Generate</button>
				</form>
				
				<div class="raw_fields" style="display: none">					
					<div class="batches_combinations_fields_row">						
						<div class="first_fields_row">							
							
							<select name="batches_combination[0][first_batch]" class="first_batch">
								<option value="0">Select batch</option>
								<?php foreach ($batches as $batch): ?>
									<option value="<?php echo $batch->id ?>">
										<?php echo $batch->title ?>
									</option>
								<?php endforeach ?>
							</select>
							
							<select name="batches_combination[0][category]" class="category">
								<option value="0">Select category</option>
							</select>															
						</div>
						
						<div class="second_fields_row">													
							<select name="batches_combination[0][second_batch]" class="second_batch">
								<option value="0">Select batch</option>
								<?php foreach ($batches as $batch): ?>
									<option value="<?php echo $batch->id ?>">
										<?php echo $batch->title ?>
									</option>
								<?php endforeach ?>
							</select>
						</div>
						<div >
							<input name="batches_combination[0][title]" type="text" placeholder="Title" />
						</div >
						<div class="clearfix"></div>
					</div>	
				</div>
			</div>
	</div>
</div>