<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');
if ( ! function_exists('compare_text'))
{
	function compare_text($first_text, $second_text) {
        if($first_text===$second_text){
            return 100;
        }else{
        $a = explode(' ', $first_text);
        $b = explode(' ', $second_text);
        $count = 0;
        foreach ($a as $val) {
            if (in_array($val, $b)) {
                $count++;
            }
        }

        $prc = $count / count($a) * 100;
        return $prc;
        }
      }
}
