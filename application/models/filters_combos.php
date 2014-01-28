<?php

require_once(APPPATH . 'models/base_model.php');
require_once(APPPATH . 'models/ifilters.php');

class Filters_combos extends Base_model implements IFilters 
{	
	public $id;
	public $title;				
	public $filters_ids;			
	
	public static function model($className = __CLASS__)
	{
		return parent::model($className);
	}
	
	public function getRules()
	{
		return array(			
			'title' => array('type' => 'required'),			
			'filters_ids' => array('type' => 'required')
		);
	}
	
	public function getTableName()
	{
		return 'filters_combos';
	}		
		
	public function beforeValidate()
	{
		$r = parent::beforeValidate();
		
		if (!$this->title || !$this->filters_ids)
			return false;
		
		return $r;
	}
	
}