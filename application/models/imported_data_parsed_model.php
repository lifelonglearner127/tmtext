<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Imported_data_parsed_model extends CI_Model {

	var $imported_data_id = null;
	var $key = '';
	var $value = '';

    var $tables = array(
    	'imported_data_parsed' => 'imported_data_parsed'
    );

    function __construct() {
        parent::__construct();
    }

    function get($id) {
    	$query = $this->db->where('id', $id)
                  ->limit(1)
                  ->get($this->tables['imported_data_parsed']);

        return $query->result();
    }

    function insert($imported_id, $key, $value) {
        $this->key = $key;
        $this->value = $value;
        $this->imported_data_id = $imported_id;

        $this->db->insert($this->tables['imported_data_parsed'], $this);
        return $this->db->insert_id();
    }

    function update($id, $imported_id, $key, $value) {
        $this->key = $key;
        $this->value = $value;
        $this->imported_data_id = $imported_id;

        return $this->db->update($this->tables['imported_data_parsed'], $this, array('id' => $id));
    }

}
