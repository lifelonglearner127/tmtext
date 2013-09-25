<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Helpers_model extends CI_Model {

    var $tables = array();

    function __construct() {
        parent::__construct();
    } 

    public function random_string_gen($length) {
      $random = "";
      srand((double)microtime()*1000000);
      $char_list = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
      $char_list .= "abcdefghijklmnopqrstuvwxyz";
      $char_list .= "1234567890";
      for($i = 0; $i < $length; $i++) {
        $random .= substr($char_list,(rand()%(strlen($char_list))), 1);
      }
      return $random;
    }

}
