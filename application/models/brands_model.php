<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Brands_model extends CI_Model {

    var $name = '';
    var $company_id = 0;
    var $brand_type = 0;
    
    var $tables = array(
        'brands' => 'brands',
    );

    function __construct()
    {
        parent::__construct();
    }

    function getAll()
    {
        $this->db->order_by("name", "asc");
        $query = $this->db->get($this->tables['brands']);

        return $query->result();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['brands']);

        return $query->result();
    }
    
    function getByName($name)
    {
        $query = $this->db->query("SELECT * FROM ".$this->tables['brands']." WHERE name = ?", array($name));

        return $query->row();
    }
    
    function insert($name, $company_id=0, $brand_type=0)
    {
        $this->name = $name;
        $this->company_id = $company_id;
        $this->brand_type = $brand_type;

        $this->db->insert($this->tables['brands'], $this);
        return $this->db->insert_id();
    }

    function update($id, $name, $company_id=0, $brand_type=0)
    {
        $this->name = $name;
        $this->company_id = $company_id;
        $this->brand_type = $brand_type;

    	return $this->db->update($this->tables['brands'],
                $this,
                array('id' => $id));
    }

    function delete($id)
    {
        return $this->db->delete($this->tables['brands'], array('id' => $id));
    }

}