<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Searches_model extends CI_Model {

    var $search   = '';
    var $attributes = '';
    var $created    = '';

    var $tables = array(
    	'searches' => 'searches'
    );

    function __construct()
    {
        parent::__construct();
    }

    function get($id)
    {
    	$query = $this->db->where('id', $id)
                  ->limit(1)
                  ->get($this->tables['searches']);

        return $query->result();
    }

    function insert($search, $attributes)
    {
        $this->search = $search;
        $this->attributes = $attributes;
        $this->created = date('Y-m-d h:i:s');

        $this->db->insert($this->tables['searches'], $this);
        return $this->db->insert_id();
    }

    function update($id, $search, $attributes)
    {
        $this->search = $search;
        $this->attributes = $attributes;

        $this->db->update($this->tables['searches'], $this, array('id' => $id));
    }

}
