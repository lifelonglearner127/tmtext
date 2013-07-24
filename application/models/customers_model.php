<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Customers_model extends CI_Model {

    var $tables = array(
    	'customers' => 'customers'
    );

    function __construct()
    {
        parent::__construct();
    }

    function get($id)
    {
    	$query = $this->db->where('id', $id)
                    ->limit(1)
                    ->get($this->tables['customers']);

        return $query->result();
    }

    function getAll()
    {
        $query = $this->db->order_by('name', 'asc')->get($this->tables['customers']);

        return $query->result();
    }

    function getIdByName($name)
    {
        $query = $this->db->where('name', $name)
            ->limit(1)
            ->get($this->tables['customers']);

        if($query->num_rows() > 0) {
            return $query->row()->id;
        }
        return '';
    }

    function getByName($name)
    {
        $query = $this->db->where('name', $name)
            ->limit(1)
            ->get($this->tables['customers']);

        if($query->num_rows() > 0) {
            return $query->row_array();
        }
        return '';
    }

}
