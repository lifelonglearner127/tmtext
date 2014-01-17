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
	 *  @param $columns                existing primary columns
	 *  @param $max_similar_item_count count of similar item
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
	 *  @param $columns                existing columns
	 *  @param $max_similar_item_count count of similar items
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
	 *  @param $columns existing columns
	 *  @param $data    input data
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
	 *  @param $columns Existing columns
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
	 *  @param $data      Source data
	 *  @param $attribute h tag. Example: h1
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
	
	public static function getInitialScalarRowData($row)
	{
		$result_row = new stdClass();
        
		$result_row->gap = '';
		$result_row->id = $row->id;
		$result_row->imported_data_id = $row->imported_data_id;
		$result_row->research_data_id = $row->research_data_id;
		$result_row->created = $row->created;
		$result_row->url = $row->url ?: '-';
		$result_row->product_name = $row->product_name ?: '-';
		$result_row->short_description_wc = intval($row->short_description_wc);
		$result_row->long_description_wc = intval($row->long_description_wc);
		$result_row->short_seo_phrases = 'None';
		$result_row->title_seo_phrases = 'None';
		$result_row->images_cmp = 'None';
		$result_row->video_count = 'None';
		$result_row->title_pa = 'None';
		$result_row->links_count = 'None';
		$result_row->long_seo_phrases = 'None';
		$result_row->price_diff = '-';
		$result_row->imp_data_id = '';
		$result_row->column_external_content = '';
		$result_row->Custom_Keywords_Short_Description = '';
		$result_row->Custom_Keywords_Long_Description = '';
		$result_row->Meta_Description = '';
		$result_row->Meta_Description_Count = '';
		$result_row->item_id = '';
		$result_row->Meta_Keywords = '';
		$result_row->Page_Load_Time = '';
		$result_row->model = '';
		$result_row->H1_Tags = '';
		$result_row->H1_Tags_Count = '';
		$result_row->H2_Tags = '';
		$result_row->H2_Tags_Count = '';
		$result_row->column_reviews = 0;
		$result_row->average_review = '';
		$result_row->column_features = 0;
		$result_row->duplicate_content = '-';
		$result_row->own_price = floatval($row->own_price);
		$price_diff = unserialize($row->price_diff);
		$result_row->lower_price_exist = false;
		$result_row->snap = '';           
		$tb_product_name = '';
		$result_row->murl = '';
		$result_row->mimg = 0;
		$result_row->mvid = 0;
		$result_row->total_description_wc = $result_row->short_description_wc + $result_row->long_description_wc;
		$result_row->short_description = $row->short_description ?: '';
		$result_row->long_description = $row->long_description ?: '';
		
		return $result_row;
	}
	
	public static function appendResultRowData($result_row, $row)
	{
	
	}		
	
	/**
	 *  @brief Gets Custom Short Description Keywords
	 *  
	 *  @param $data array of input data
	 *  
	 *  @return concatenated custom description keywords
	 */
	public static function getCustomDescriptionKeywords($data)
	{
		$r = '<table class="' . $data['table_class'] . '">';
		
		foreach ($data['seo_elements'] as $seo_element)
		{					
			if (isset($data['custom_seo'][$seo_element]) && $custom_seo[$seo_element]) {
				if ($data['row']->{$data['key']}) {
					$_count = $data['controller']->keywords_appearence($data['row']->{$data['key']}, $data['custom_seo'][$seo_element]);
					$cnt = count(explode(' ', $data['custom_seo'][$seo_element]));
					$_count = round(($_count * $cnt / $data['row']->{$data['key'] . '_wc'}) * 100, 2) . '%';
					$r .= '<tr><td>' . $data['custom_seo'][$seo_element] . "</td><td>$_count</td></tr>";
				} else {
					$_count = ' ';
				}
			}		
		}
	
		return $r . '</table>';	
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