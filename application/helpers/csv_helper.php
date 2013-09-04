<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

// ------------------------------------------------------------------------

/**
 * CSV Helpers
 * Inspiration from PHP Cookbook by David Sklar and Adam Trachtenberg
 * 
 * @author		Jérôme Jaglale
 * @link		http://maestric.com/en/doc/php/codeigniter_csv
 */

// ------------------------------------------------------------------------

/**
 * Array to CSV
 *
 * download == "" -> return CSV string
 * download == "toto.csv" -> download file toto.csv
 */
if ( ! function_exists('array_to_csv'))
{
	function array_to_csv($array, $download = "")
	{
		if ($download != "")
		{	
			header('Content-Type: application/csv');
			header('Content-Disposition: attachement; filename="' . $download . '"');
		}		

		ob_start();
		$f = fopen('php://output', 'w') or show_error("Can't open php://output");
		$n = 0;		
		foreach ($array as $line)
		{
			$n++;
			if ( ! fputcsv($f, $line))
			{
				show_error("Can't write line $n: $line");
			}
		}
		fclose($f) or show_error("Can't close php://output");
		$str = ob_get_contents();
		ob_end_clean();

		if ($download == "")
		{
			return $str;	
		}
		else
		{	
			echo $str;
		}		
	}
}

// ------------------------------------------------------------------------

/**
 * Query to CSV
 *
 * download == "" -> return CSV string
 * download == "toto.csv" -> download file toto.csv
 */
if ( ! function_exists('query_to_csv'))
{
	function query_to_csv($query, $headers = TRUE, $download = "")
	{
		if ( ! is_object($query) OR ! method_exists($query, 'list_fields'))
		{
			show_error('invalid query');
		}
		
		$array = array();
		
		if ($headers)
		{
			$line = array();
			foreach ($query->list_fields() as $name)
			{
				$line[] = $name;
			}
			$array[] = $line;
		}
		
		foreach ($query->result_array() as $row)
		{
			$line = array();
			foreach ($row as $item)
			{
				$line[] = $item;
			}
			$array[] = $line;
		}

		echo array_to_csv($array, $download);
	}
}

/**
 * Parse from CSV
 *
 * return array containing data from csv
 */
if ( ! function_exists('csv_to_array'))
{
	function csv_to_array($csv = null, $header = array(), $delimiter = ',')
	{
            
            if($csv != null && file_exists(dirname($_SERVER['SCRIPT_FILENAME']).'/webroot/img/'.$csv)) {
                if (($handle = fopen(dirname($_SERVER['SCRIPT_FILENAME']).'/webroot/img/'.$csv, "r")) !== FALSE) {
                        $first_line = true;
                        while (($parsed = fgetcsv($handle, 2000, "$delimiter", "\"")) !== false) {
                                $continue = false;
                                // first line is a header?
                                if ($first_line) {
                                        $first_line = false;

                                        foreach($parsed as &$col) {
                                                if ( in_array(strtolower($col), $header) ) {
                                                        $continue = true;
                                                }
                                                if (isset($header_replace[$col])) {
                                                        $col = $header_replace[$col];
                                                }
                                        }

                                }
                                if ($continue) {
                                        $header = $parsed;
                                        continue;
                                }

                                $parsed_tmp = $parsed;
                                foreach($parsed_tmp as &$col) {
                                        $col = '"'.str_replace('"','\"', $col).'"';
                                }
                                $row = implode(',',$parsed_tmp);

                                $key = sha1($row); $i++;
                                if (!array_key_exists($key, $_rows)) {
                                        $_rows[$key] = array(
                                                'row'=>$row,
                                        );
                                        // add parsed data
                                        if (!empty($header)) {
                                                foreach( $header as $i=>$h ){
                                                        if (!empty($h)) {
                                                                $_rows[$key]['parsed'][$h] = $parsed[$i];
                                                        }
                                                }
                                        }

                                }
                        }
                }
                fclose($handle);
                
                if(isset($_rows) && !empty($_rows)) {
                    return $_rows;
                }
                    
            }
            
            return array();
            
	}
}



/* End of file csv_helper.php */
/* Location: ./system/helpers/csv_helper.php */