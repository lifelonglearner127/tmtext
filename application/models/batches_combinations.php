<?php

require_once(APPPATH . 'models/base_model.php');

class Batches_combinations extends Base_model 
{	
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
			
}