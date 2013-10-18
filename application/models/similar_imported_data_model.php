<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Similar_imported_data_model extends CI_Model {

	var $similar_group_id = 0;
	var $imported_data_id = 0;


    var $tables = array(
    	'similar_imported_data' => 'similar_imported_data',
    	'imported_data' => 'imported_data'
    );

    function __construct() {
        parent::__construct();
    }

    function get($id) {
    	$query = $this->db->where('id', $id)
                  ->limit(1)
                  ->get($this->tables['similar_imported_data']);

        return $query->result();
    }

    function insert($imported_data_id, $similar_group_id) {
        $this->imported_data_id = $imported_data_id;
        $this->similar_group_id = $similar_group_id;

        $this->db->insert($this->tables['similar_imported_data'], $this);
        return $this->db->insert_id();
    }

    function findByImportedDataId($imported_data_id) {
    	$query = $this->db->where('imported_data_id', $imported_data_id)
	    		->limit(1)
	    		->get($this->tables['similar_imported_data']);
       	if($query->num_rows() > 0) {
        	return $query->row()->similar_group_id;
       	}
       	return false;
    }

    function getImportedDataByGroupId($similar_group_id) {
    	return $this->db->where('similar_group_id', $similar_group_id)
    		->get($this->tables['similar_imported_data'])
    		->result();
    }


}
