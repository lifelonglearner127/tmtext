<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Imported_data_attributes_model extends CI_Model {

	var $attributes = '';
	var $created = null;


    var $tables = array(
    	'imported_data_attributes' => 'imported_data_attributes',
    	'imported_data' => 'imported_data'
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

	function getByImportedDataId($imported_id) {
    	$query = $this->db->select('attributes')
    			->join($this->tables['imported_data'].' as i', 'ia.id = i.imported_data_attribute_id')
    			->where('i.id', $imported_id)
                ->limit(1)
                ->get($this->tables['imported_data_attributes'].' as ia');

        return $query->row();
    }


    function insert($attributes) {
        $this->attributes = $attributes;
        $this->created = date('Y-m-d h:i:s');

        $this->db->insert($this->tables['imported_data_attributes'], $this);
        return $this->db->insert_id();
    }

    function update($id, $attributes) {
        return $this->db->update($this->tables['imported_data_attributes'], array('attributes' => $attributes), array('id' => $id));
    }

}
