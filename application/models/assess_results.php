<?php

require_once(APPPATH . 'models/base_model.php');

class Assess_results extends Base_model
{	
	public $id;
	public $row_data;

	//it's for multiple insertion (Oleg)
	public $rows = array();
	
	public static function model($className = __CLASS__)
	{
		return parent::model($className);
	}
	
	public function getRules()
	{
		return array(
			'id' => array('type' => 'required'),			
			'row_data' => array('type' => 'required'),			
		);
	}
	
	public function getTableName()
	{
		return 'assess_results';
	}	
	
	//please look at deleteAll(true) base_model method (Oleg)
	public function truncate()
	{
		$this->db->truncate($this->getTableName()); 
	}
	//you can use save method from base_model (Oleg)
	public function saveRow($row)
	{
		$this->db->insert($this->getTableName(),array('row_data'=>json_encode($row))); 
	}
}