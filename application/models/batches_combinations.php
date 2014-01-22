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
		$combinations = array();
		
		//truncating batches_combinations table
		$this->deleteAll(true);
		
		//creating all possible combinations		
		foreach ($batches as $first_batch)
			foreach ($batches as $second_batch) {
				$combination = new Batches_combinations;
				$combination->batches_combination = $first_batch == $second_batch ? $first_batch->id : $first_batch->id . '_' . $second_batch->id;
				$combination->category_id = null;
				
				if ($combination->save())
					$combinations[] = $combination;
			}
		
		return $combinations;
	}
	
	public function generateManualCombinations($combinations)
	{
		return false;
	}
}