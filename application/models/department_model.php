<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Department_model extends CI_Model {

    var $name = '';
	var $short_name = '';
	var $level = 0;
	var $parent_id = null;

    var $tables = array(
        'departments' => 'departments'
    );

    function __construct()
    {
        parent::__construct();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['departments']);

        return $query->result();
    }

    function insert($name, $short_name, $level = 0, $parent_id = null)
    {
        $this->name = $name;
        $this->short_name = $short_name;
        $this->level = $level;
        $this->parent_id = $parent_id;

        $this->db->insert($this->tables['departments'], $this);
        return $this->db->insert_id();
    }

    function getAll()
    {
        $this->db->order_by("short_name", "asc");
        $query = $this->db->get($this->tables['departments']);

        return $query->result();
    }
}