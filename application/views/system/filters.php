<?php $this->load->model('batches_combinations') ?>
<div class="tabbable">
	<?php $this->load->view('system/_tabs', array(
		'active_tab' => 'system/filters'
	)) ?>
	<div class="tab-content">
			<div class="tab-pane active">
				<form action="" method="post" id="batches_combinations">
					
					<label for="all_possible_combinations">
						<input type="radio" name="type" id="all_possible_combinations" class="combination_type" value="<?php echo Batches_combinations::TYPE_ALL_POSSIBLE_COMBINATIONS ?>" checked="checked" /> All possible combinations
					</label>
					
					<label for="manual_combinations">
						<input type="radio" name="type" id="manual_combinations" class="combination_type" value="<?php echo Batches_combinations::TYPE_MANUAL_COMBINATIONS ?>" /> Manually combinations
					</label>
					
					<div style="display: none">
						
					</div>
					
					<button class="btn" id="generate_combinations" >Generate</button>
				</form>
			</div>
	</div>
</div>