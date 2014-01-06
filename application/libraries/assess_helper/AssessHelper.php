<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed'); 

class AssessHelper
{
	public static function getInitialFilterData()
	{			
		return require_once(APPPATH . 'libraries/assess_helper/_filter_variables.php');
	}
	
	public static function addCompetitorColumns($columns, $max_similar_item_count = 1)
	{
		if (!$max_similar_item_count) return array();
		
		// for now it should be 1 (no more)
		$max_similar_item_count /= $max_similar_item_count;		
		
		for ($i = 1; $i <= $max_similar_item_count; $i++)
		{
			foreach ($columns as $column)
			{				
				if (isset($column['nonCompared']))
					continue;
								
				$columns[] = array(
					'sTitle' => isset($column['newTitle']) ? str_replace('?', $i, $column['newTitle']) : $column['sTitle'],
					'sName' => $column['sName'] . $i,
					'sClass' => $column['sClass'] . $i,
					'bVisible' => isset($column['bVisible']) ? $column['bVisible'] : true
				);
			}			
		}
		
		return $columns;
	}
	
	public static function columns() 
	{        	
        return require_once(APPPATH . 'libraries/assess_helper/_columns.php');        
    }
	
	public static function getStringColumnNames($columns, $separator = ',', $max_similar_item_count = 1)
	{
		$r = '';
				
		foreach (self::addCompetitorColumns($columns, $max_similar_item_count) as $column)
			$r .= $column['sName'] . $separator;
			
		return rtrim($r, $separator);
	}
	
	public static function setTableData($columns, $data)
	{
		$r = array();
		foreach ($columns as $column)
		{
			$r[] = isset($data[$column['sName']])  ? $data[$column['sName']] : '';		
			// if (!isset($data[$column['sName']]))
				// var_dump($column['sName']);
		}
		
		return $r;
	}
	
	public static function getSelectableColumns($columns)
	{
		$r = array();
		
		foreach ($columns as $column)		
			if (isset($column['nonSelected']) && $column['nonSelected'] !== true  || !isset($column['nonSelected']))
				$r[] = $column;		
		
		return $r;
	}
}