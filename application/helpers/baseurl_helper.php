<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');
if ( ! function_exists('get_base_url'))
{
 function get_base_url($url)
    {
    $chars = preg_split('//', $url, -1, PREG_SPLIT_NO_EMPTY);

    $slash = 3; // 3rd slash

    $i = 0;

    foreach($chars as $key => $char)
    {
        if($char == '/')
        {
           $j = $i++;
        }

        if($i == 3)
        {
           $pos = $key; break;
        }
    }
    }
}
