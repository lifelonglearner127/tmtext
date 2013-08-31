<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Brand_types_model extends CI_Model {

    var $name = '';

    var $tables = array(
        'brand_types' => 'brand_types',
    );

    function __construct()
    {
        parent::__construct();
    }

    function getAll()
    {
        $this->db->order_by("name", "asc");
        $query = $this->db->get($this->tables['brand_types']);

        return $query->result();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['brand_types']);

        return $query->result();
    }
    
    function insert($name)
    {
        $this->name = $name;

        $this->db->insert($this->tables['brand_types'], $this);
        return $this->db->insert_id();
    }

    function update($name)
    {
        $this->name = $name;

    	return $this->db->update($this->tables['brand_types'],
                $this,
                array('id' => $id));
    }

    function delete($id)
    {
        return $this->db->delete($this->tables['brand_types'], array('id' => $id));
    }

}