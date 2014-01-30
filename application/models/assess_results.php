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
			'combination' => array('type' => 'required'),			
		);
	}
	
	public function getTableName()
	{
		return 'assess_results';
	}	
}