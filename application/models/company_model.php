<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Company_model extends CI_Model {

    var $name = '';
	var $description = '';
	var $image = '';

    var $tables = array(
        'companies' => 'companies'
    );

    function __construct()
    {
        parent::__construct();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['companies']);

        return $query->result();
    }

    function insert($name, $image='', $description='')
    {
        $this->name = $name;
        $this->image = $image;
        $this->description = $description;

        $this->db->insert($this->tables['companies'], $this);
        return $this->db->insert_id();
    }

    function update($id, $name, $image, $description)
    {
        $this->name = $name;
        $this->image = $image;
        $this->description = $description;

    	return $this->db->update($this->tables['companies'],
                $this,
                array('id' => $id));
    }

    function delete($id)
    {
        return $this->db->delete($this->tables['companies'], array('id' => $id));
    }


}