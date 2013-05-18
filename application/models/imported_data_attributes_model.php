<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Imported_data_attributes_model extends CI_Model {

	var $attributes = '';
	var $created = null;


    var $tables = array(
    	'imported_data_attributes' => 'imported_data_attributes'
    );

    function __construct() {
        parent::__construct();
    }

    function get($id) {
    	$query = $this->db->where('id', $id)
                  ->limit(1)
                  ->get($this->tables['imported_data_attributes']);

        return $query->result();
    }

    function insert($attributes) {
        $this->attributes = $attributes;
        $this->created = date('Y-m-d h:i:s');

        $this->db->insert($this->tables['imported_data_attributes'], $this);
        return $this->db->insert_id();
    }

    function update($id, $attributes) {
        $this->attributes = $attributes;

        $this->db->update($this->tables['imported_data_attributes'], $this, array('id' => $id));
    }

}
