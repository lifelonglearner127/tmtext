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
		$r = array();
		
		for ($i = 1; $i <= $max_similar_item_count; $i++)
		{
			foreach ($columns as $column)
			{				
				if (isset($column['nonCompared']))
					continue;
								
				$columns[] = array(
					'sTitle' => isset($column['newTitle']) ? str_replace('?', $i, $column['newTitle']) : $column['sTitle'],
					'sName' => $column['sName'] . $i,
					'sClass' => $column['sClass'] . $i
				);
			}			
		}
		
		return $columns;
	}
	
	public static function columns() 
	{
        return require_once(APPPATH . 'libraries/assess_helper/_columns.php');        
    }
}