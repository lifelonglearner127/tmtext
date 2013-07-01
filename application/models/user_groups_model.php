<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class User_Groups_model extends CI_Model {

    var $tables = array(
    	'groups' => 'groups',
        'users_groups' => 'users_groups',
        'users' => 'users'
    );

    function __construct()
    {
        parent::__construct();
    }

    function checkRegEmail($email) {
        $query = $this->db->where('email', $email)
                    ->limit(1)
                    ->get($this->tables['users']);
        $res = $query->result();
        if($res) {
            return false;
        } else {
            return true;
        }
    }

    function get($id)
    {
    	$query = $this->db->where('id', $id)
                    ->limit(1)
                    ->get($this->tables['groups']);

        return $query->result();
    }

    function getRoleByUserId($user_id){
        $query = $this->db
                      ->select('group_id')
                      ->where('user_id', $user_id)
                      ->get($this->tables['users_groups']);

        return $query->result();
    }

    function getAll()
    {
        $query = $this->db->get($this->tables['groups']);

        return $query->result();
    }

    function getGroupById($id){
        $query = $this->db
                    ->where('id', $id)
                    ->limit(1)
                    ->get($this->tables['groups']);

        return $query->result_array();
    }

}
