<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class User_Groups_model extends CI_Model {

    var $tables = array(
    	'groups' => 'groups'
    );

    function __construct()
    {
        parent::__construct();
    }

    function get($id)
    {
    	$query = $this->db->where('id', $id)
                    ->limit(1)
                    ->get($this->tables['groups']);

        return $query->result();
    }

    function getAll()
    {
        $query = $this->db->get($this->tables['groups']);

        return $query->result();
    }

}
