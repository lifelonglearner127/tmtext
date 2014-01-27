<?php

require_once(APPPATH . 'models/base_model.php');
require_once(APPPATH . 'models/ifilters.php');

class Filters_items extends Base_model implements IFilters 
{	
	public $id;
	public $item_key;				
	public $filters_values_id;		
	public $combination_id;		
	
	public static function model($className = __CLASS__)
	{
		return parent::model($className);
	}
	
	public function getRules()
	{
		return array(
			'combination_id' => array('type' => 'required'),			
			'filters_values_id' => array('type' => 'required'),			
			'item_key' => array('type' => 'required')
		);
	}
	
	public function getTableName()
	{
		return 'filters_items';
	}		
		
	public function save_filtered_items($data, $stored_filter_items, $filters_values_id)
	{				
		$filter_items = array();
		$sql = 'INSERT INTO ' . $this->getTableName() . ' (item_key, filters_values_id, combination_id) VALUES ';
		$sql_rows = array();
		
		foreach ($stored_filter_items as $stored_filters)		
		{
			if (count($stored_filters) > 500) {
				$chunked_array = array_chunk($stored_filters, 500);
				foreach ($chunked_array as $chunk)
					
					$sql_rows[] = '("' . json_encode($chunk) . '", ' . $filters_values_id . ', ' .  $data['combination_id'] . ')';							
				
			} else {								
				$sql_rows[] = '("' . json_encode($stored_filters) . '", ' . $filters_values_id . ', ' .  $data['combination_id'] . ')';							
			}
		}
		
		if ($sql_rows)
			$this->db->query($sql . implode(', ' , $sql_rows) . ';');
		
		return $filter_items;				
	}
}