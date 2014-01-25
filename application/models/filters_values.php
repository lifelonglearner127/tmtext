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
	
	public function __construct()
	{
		parent::__construct();
		$this->load->model('filter_items', 'fi');
		$this->load->model('statistics_new_model');
	}
	
	public static function model($className = __CLASS__)
	{
		return parent::model($className);
	}
	
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

	public function getComparisonData(array $data)
	{
		$params = new stdClass();
		$params->batch_id = $data['batch_id'];		
		$params->category_id = $data['category_id'];							
		
		$results = $this->statistics_new_model->getStatsData($params);
		
		return $results;
	}

	public function generateFiltersValues(array $data)
	{
		$comparison_data = $this->getComparisonData(array(
			'batch_id' => $data['first_batch_id'],			
			'category_id' => $data['category']
		));

		$this->buildFilters($comparison_data, $data);
		
		return true;
	}
	
	public function buildFilters($results, $data)
	{
		
		
		
	}
			
}