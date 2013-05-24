<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Category_model extends CI_Model {

    var $name = '';

    var $tables = array(
        'categories' => 'categories'
    );

    function __construct()
    {
        parent::__construct();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['categories']);

        return $query->result();
    }

    function getIdByName($name)
    {
        $query = $this->db->where('name', $name)
            ->limit(1)
            ->get($this->tables['categories']);

    	if($query->num_rows() > 0) {
			return $query->row()->id;
		}
        return false;
    }

    function insert($name)
    {
        $this->name = $name;

        $this->db->insert($this->tables['categories'], $this);
        return $this->db->insert_id();
    }

    function delete($id)
    {
        return $this->db->delete($this->tables['categories'], array('id' => $id));
    }


}