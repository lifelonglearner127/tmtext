<?php

require_once(APPPATH . 'models/base_model.php');

class Assess_results extends Base_model
{	
	public $id;
	public $row_data;				
	
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
	
	public function truncate()
	{
		$this->db->truncate($this->getTableName()); 
	}
	
	public function saveRow($row)
	{
		$this->db->insert($this->getTableName(),array('row_data'=>json_encode($row))); 
	}
}