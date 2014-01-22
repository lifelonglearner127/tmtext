<?php

require_once(APPPATH . 'models/base_model.php');
require_once(APPPATH . 'models/ifilters.php');

class Filters_values extends Base_model implements IFilters 
{		
	public $id;
	public $value;
	public $filter_id;
	public $combination_id;	
	public $icon;		
	
	public function getRules()
	{
		return array(
			'filter_id' => array('type' => 'required'),
			'combination_id' => array('type' => 'required'),
			'value' => array('type' => 'required')
		);
	}
	
	public function getTableName()
	{
		return 'filters_values';
	}		
			
}