<?php

require_once(APPPATH . 'models/base_model.php');

class Batches_combinations extends Base_model 
{	
	const TYPE_ALL_POSSIBLE_COMBINATIONS = 1;
	const TYPE_MANUAL_COMBINATIONS = 2;

	public $id;
	public $batches_combination;
	public $category_id;	
	
	public function getRules()
	{
		return array(
			'batches_combination' => array('type' => 'required'),			
		);
	}
	
	public function getTableName()
	{
		return 'batches_combinations';
	}

	public function generateAllPossibleCombinations()
	{
		$this->load->model('batches_model');
		$batches = $this->batches_model->getAll();
				
		return $this->generateCombinations($batches, true);
	}
	
	public function generateManualCombinations($batches)
	{
		return $this->generateCombinations($batches);
	}
	
	private function buildBatchesCombinationObject(array $data = array())
	{
		$combination = new Batches_combinations;
		$combination->batches_combination = $data['first_batch_id'] == $data['second_batch_id'] ? $data['first_batch_id'] . '_0' : $data['first_batch_id'] . '_' . $data['second_batch_id'];
		$combination->batches_combination .= $data['category'] ? '_' . $data['category'] : '_0';
		
		// needs to be fixed
		$combination->category_id = $data['category'];
		
		$combination->title = $data['first_batch_id'] == $data['second_batch_id'] || isset($data['hasCustomTitle']) ? $data['first_batch_title'] : $data['first_batch_title'] . ' - ' . $data['second_batch_title'];
					
		return $combination->save() && Filters_values::model()->generateFiltersValues($data) ? $combination : false;		
	}
	
	private function generateCombinations(array $batches = array(), $from_db = false)
	{		
		$this->load->model('product_category_model');
			
		$combinations = array();
		
		//truncating batches_combinations table
		$this->deleteAll(true);
		
		//creating all possible combinations from database	
		if ($from_db)
			foreach ($batches as $first_batch)
				foreach ($batches as $second_batch) {
					
					if (($categories = $this->product_category_model->getCatsByBatchId($first_batch->id)) !== array())
					{						
						foreach ($categories as $category) 
							if ($combination = $this->buildBatchesCombinationObject(array(
								'first_batch_id' => $first_batch->id,
								'second_batch_id' => $second_batch->id,
								'category' => $category->id,
								'first_batch_title' => $first_batch->title,
								'second_batch_title' => $second_batch->title,
							))) {
								$combinations[] = $combination;
							}
					} else {						
						if ($combination = $this->buildBatchesCombinationObject(array(
							'first_batch_id' => $first_batch->id,
							'second_batch_id' => $second_batch->id,
							'category' => 0,
							'first_batch_title' => $first_batch->title,
							'second_batch_title' => $second_batch->title,
						))) {
							$combinations[] = $combination;
						}
					}
				}
		else
			foreach ($batches as $batch_combination) {
				if ($combination = $this->buildBatchesCombinationObject(array(
					'first_batch_id' => $batch_combination['first_batch'],
					'second_batch_id' => $batch_combination['second_batch'],
					'category' => $batch_combination['category'],
					'first_batch_title' => $batch_combination['title'],
					'hasCustomTitle' => true
				))) {
					$combinations[] = $combination;
				}				
			}
		
		return $combinations;
	}
}