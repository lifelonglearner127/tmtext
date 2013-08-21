<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Logins_model extends CI_Model {

    var $tables = array(
        'users' => 'users'
    );

    function __construct()
    {
        parent::__construct();
    }
	
	function get_last_logins(){
		$query = $this->db
			->select('first_name, email')
			->order_by("first_name", "asc")
			->get($this->tables['users']);
		return $query->result();
	}
	
}
