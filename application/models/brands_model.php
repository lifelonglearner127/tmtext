<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Brands_model extends CI_Model {

    var $name = '';

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

}