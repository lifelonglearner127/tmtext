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
		$time_now = time();
		$query = $this->db
			->select('first_name, email, last_login')
			->where('last_login <=', $time_now)
			->order_by("last_login", "desc")
			->limit(30)
			->get($this->tables['users']);
		return $query->result();
	}
	
}
