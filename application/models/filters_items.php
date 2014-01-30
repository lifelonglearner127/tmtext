<?php

require_once(APPPATH . 'models/base_model.php');
require_once(APPPATH . 'models/ifilters.php');

class Filters_items extends Base_model implements IFilters 
{	
	public $id;
	public $item_key;				
	public $filter_id;		
	public $combination_id;		
	
	public static function model($className = __CLASS__)
	{
		return parent::model($className);
	}
	
	public function getRules()
	{
		return array(
			'combination_id' => array('type' => 'required'),			
			'filter_id' => array('type' => 'required'),			
			'item_key' => array('type' => 'required')
		);
	}
	
	public function getTableName()
	{
		return 'filters_items';
	}		
		
	public function save_filtered_items($data, $stored_filter_items, $filter_id)
	{				
		$filter_items = array();
		$sql = 'INSERT INTO ' . $this->getTableName() . ' (item_key, filter_id, combination_id) VALUES ';
		$sql_rows = array();
		
		
		if (count($stored_filter_items) > 500) {
			$chunked_array = array_chunk($stored_filter_items, 500);
			foreach ($chunked_array as $chunk)
				
				$sql_rows[] = '("' . json_encode($chunk) . '", ' . $filter_id . ', ' .  $data['combination_id'] . ')';							
			
		} else {								
			$sql_rows[] = '("' . json_encode($stored_filter_items) . '", ' . $filter_id . ', ' .  $data['combination_id'] . ')';							
		}
		
		
		if ($sql_rows)
			$this->db->query($sql . implode(', ' , $sql_rows) . ';');
		
		return $filter_items;				
	}
}