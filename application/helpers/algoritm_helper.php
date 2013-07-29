<?php

if (!defined('BASEPATH'))
    exit('No direct script access allowed');

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
if (!function_exists('leven_algoritm')) {

    function leven_algoritm($s, $t) {
        $m = strlen($s);
        $n = strlen($t);

        for ($i = 0; $i <= $m; $i++)
            $d[$i][0] = $i;
        for ($j = 0; $j <= $n; $j++)
            $d[0][$j] = $j;

        for ($i = 1; $i <= $m; $i++) {
            for ($j = 1; $j <= $n; $j++) {
                $c = ($s[$i - 1] == $t[$j - 1]) ? 0 : 1;
                $d[$i][$j] = min($d[$i - 1][$j] + 1, $d[$i][$j - 1] + 1, $d[$i - 1][$j - 1] + $c);
            }
        }
        $max = max(array($m, $n));
        $result = ((1 - $d[$m][$n] / $max) * 100);
        return $result;
    }

}


if (!function_exists('total_matches')) {

    function total_matches($currindex, $arr, $short_or_long) {
        $percents = array();
        foreach ($arr as $key => $value) {
              if ($key != $currindex) {
                if(isset($value['short'])){
                   
                $percents[] = leven_algoritm($arr[$currindex][$short_or_long], $value['short']);
                
                }
                if(isset($value['long'])){
                
                $percents[] = leven_algoritm($arr[$currindex][$short_or_long], $value['long']);
                }
            }
            
        }
        
        if (!empty($percents)) {
            return max($percents);
        }
        return false;
    }

}
// ------------------------------------------------------------------------
