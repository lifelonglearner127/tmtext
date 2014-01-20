<?php

require_once(APPPATH . 'models/base_model.php');

class Filters_values extends Base_model 
{	
	const ICON_BLUE = 'assess_report_seo.png';
	const ICON_YELLOW = 'assess_report_yellow.png';
	const ICON_RED = 'assess_report_seo_red.png';

	public $id;
	public $value;
	public $filter_id;
	public $combination_id;	
	public $icon;		
	
	public function getRules()
	{
		return array(
			'filter_id' => array('type' => 'required'),
			'combination_id' => array('type' => 'required')
			'value' => array('type' => 'required')
		);
	}
	
	public function getTableName()
	{
		return 'filters_values';
	}		
			
}