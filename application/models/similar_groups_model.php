<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Similar_groups_model extends CI_Model {

	var $similarity = 0;
	var $percent = 0;


    var $tables = array(
    	'similar_groups' => 'similar_groups',
    	'imported_data' => 'imported_data',
    	'imported_data_attributes' => 'imported_data_attributes',
    	'similar_imported_data' => 'similar_imported_data'
    );

    function __construct() {
        parent::__construct();
    }

    function get($id) {
    	$query = $this->db->where('id', $id)
                  ->limit(1)
                  ->get($this->tables['similar_groups']);

        return $query->result();
    }

    function insert($similarity = 1, $percent = 0) {
        $this->similarity = $similarity;
        $this->percent = $percent;

        $this->db->insert($this->tables['similar_groups'], $this);
        return $this->db->insert_id();
    }

	function getIdsForComparition($limit=null) {
    	 $this->db->select('i.id as id')
    			->join($this->tables['imported_data_attributes'].' as ia', 'ia.id = i.imported_data_attribute_id')
    			->join($this->tables['similar_imported_data'].' as s', 's.imported_data_id = i.id', 'left')
    			->where('s.imported_data_id IS NULL');

		if (!is_null($limit)) {
    		$this->db->limit($limit);
		}

        $query = $this->db->get($this->tables['imported_data'].' as i');

        if($query->num_rows() > 0) {
        	$result = array();
        	foreach($query->result() as $row) {
        		$result[] = $row->id;
        	}
			return $result;
		}
		return false;
    }
}
