<?php

require_once(APPPATH . 'models/base_model.php');
require_once(APPPATH . 'models/ifilters.php');

class Filters_items extends Base_model implements IFilters 
{	
	public $id;
	public $item_key;
	public $filter_id;
	public $combination_id;	
	
	public function getRules()
	{
		return array(
			'filter_id' => array('type' => 'required'),
			'combination_id' => array('type' => 'required')
			'item_key' => array('type' => 'required')
		);
	}
	
	public function getTableName()
	{
		return 'filters_items';
	}		
			
}