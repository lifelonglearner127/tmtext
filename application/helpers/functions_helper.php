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
if (!function_exists('get_days')) {

    function get_days() {
        $result = array();
        for($i = 1; $i <= 31; $i++){
            if($i < 10) {
                array_push($result, '0'.$i);
            } else {
                array_push($result, $i);
            }
        }
        
        return $result;
    }

}


if (!function_exists('get_months')) {

    function get_months() {
        $result = array(
                '01' => 'January',
                '02' => 'Fabruary',
                '03' => 'March',
                '04' => 'April',
                '05' => 'May',
                '06' => 'June',
                '07' => 'July',
                '08' => 'August',
                '09' => 'September',
                '10' => 'October',
                '11' => 'November',
                '12' => 'December',
            );
        
        return $result;
    }

}

if (!function_exists('get_years')) {

    function get_years() {
        $result = array();
        for($i = date('Y'); $i >= 1990; $i--){
            array_push($result, $i);
        }
        
        return $result;
    }

}

// ------------------------------------------------------------------------
