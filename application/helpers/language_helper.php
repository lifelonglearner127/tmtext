<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');
if ( ! function_exists('lang'))
{
	function lang($line, $id = '', $extra = '')
	{
		$CI =& get_instance();
		$line = $CI->lang->line($line);

		if ($id != '')
		{
			$line = '<label for="'.$id.'"'.$extra.'>'.$line."</label>";
		}

		return $line;
	}
}
