<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Sites_model extends CI_Model {

    var $tables = array(
        'sites' => 'sites'
    );

    function __construct()
    {
        parent::__construct();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['sites']);

        return $query->result();
    }

    function getAll()
    {
        $query = $this->db->order_by('name', 'asc')->get($this->tables['sites']);

        return $query->result();
    }

    function getIdByName($name)
    {
        $query = $this->db->where('name', $name)
            ->limit(1)
            ->get($this->tables['sites']);

        if($query->num_rows() > 0) {
            return $query->row()->id;
        }
        return '';
    }
}
