<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed'); 

/**
 *  @file AssessHelper.php
 *  @brief Helper for building summary report data.
 *  @author Oleg Meleshko <qu1ze34@gmail.com>
 */

class AssessHelper
{	
	/**
	 *  @brief Adds competitor columns to the existing columns
	 *  
	 *  @param [in] $columns                existing primary columns
	 *  @param [in] $max_similar_item_count count of similar item
	 *  
	 *  @return appended with competitor columns array of columns
	 */
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
					'bVisible' => isset($column['bVisible']) ? $column['bVisible'] : true,
					'batch_number' => $i,
					'sWidth' => $column['sWidth'],
				);
			}			
		}
		
		return $columns;
	}	
	
	/**
	 *  @brief Get string representation of existing columns (with competitor columns)
	 *  
	 *  @param [in] $columns                existing columns
	 *  @param [in] $max_similar_item_count count of similar items
	 *  
	 *  @return string of column names
	 */
	public static function getStringColumnNames($columns, $separator = ',', $max_similar_item_count = 1)
	{
		$r = '';
				
		foreach (self::addCompetitorColumns($columns, $max_similar_item_count) as $column)
			$r .= $column['sName'] . $separator;
			
		return rtrim($r, $separator);
	}
	
	/**
	 *  @brief Link columns with column data
	 *  
	 *  @param [in] $columns existing columns
	 *  @param [in] $data    input data
	 *  
	 *  @return array of data
	 */
	public static function setTableData($columns, $data)
	{
		$r = array();
		foreach ($columns as $column)		
			$r[] = isset($data[$column['sName']])  ? $data[$column['sName']] : '';							
		
		return $r;
	}
	
	/**
	 *  @brief Returns array of selectable columns for the frontend modal popup list
	 *  
	 *  @param [in] $columns Existing columns
	 *  @return array of selectable columns	   	
	 */
	public static function getSelectableColumns($columns)
	{
		$r = array();
		
		foreach ($columns as $column)		
			if (isset($column['nonSelected']) && $column['nonSelected'] !== true  || !isset($column['nonSelected']))
				$r[] = $column;		
		
		return $r;
	}
	
	/**
	 *  @brief Build H[attribute] output data
	 *  
	 *  @param [in] $data      Source data
	 *  @param [in] $attribute h tag. Example: h1
	 *  @return array of H[attribute] with value and count	 
	 */
	public static function buildHField($data, $attribute)
	{
		$value = $count = '';
		
		if (isset($data[$attribute]) && ($h_data = $data[$attribute])) 
		{		
			if (is_array($h_data)) 
			{
				$value = '<table class="table_keywords_long">';
				$count = '<table class="table_keywords_long">';
				foreach ($h_data as $h_elem) {
					$value .= '<tr><td>' . $h_elem . '</td></tr>';
					$count .= '<tr><td>' . strlen($h_elem) . '</td></tr>';
				}
				$value .= '</table>';
				$count .= '</table>';
												
			} else {
				$h_count = strlen($data[$attribute]);
				
				$value = '<table class="table_keywords_long"><tr><td>' . $h_data . '</td></tr></table>';
				$count = '<table class="table_keywords_long"><tr><td>' . $h_count . '</td></tr></table>';				
			}
			
		}
		
		return array(
			'value' => $value,
			'count' => $count,
		);
	}
	
	public static function getInitialFilterData()
	{			
		return require_once(APPPATH . 'libraries/assess_helper/_filter_variables.php');
	}
	
	public static function columns() 
	{        	
        return require_once(APPPATH . 'libraries/assess_helper/_columns.php');        
    }
}