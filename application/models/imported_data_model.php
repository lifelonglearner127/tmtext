<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Imported_data_model extends CI_Model {

	var $key = '';
	var $imported_data_attribute_id = null;
	var $data = '';
	var $created = null;

    var $tables = array(
    	'imported_data' => 'imported_data'
    );

    function __construct() {
        parent::__construct();
    }

    function get($id) {
    	$query = $this->db->where('id', $id)
                  ->limit(1)
                  ->get($this->tables['imported_data']);

        return $query->result();
    }

    function insert($data, $attribute_id = null) {
        $this->data = $data;
        $this->key = $this->_get_key($data);
        $this->imported_data_attribute_id = $attribute_id;
        $this->created = date('Y-m-d h:i:s');

        $this->db->insert($this->tables['imported_data'], $this);
        return $this->db->insert_id();
    }

    function update($id, $data, $attribute_id = null) {
        $this->data = $data;
        $this->key = $this->_get_key($data);
        $this->imported_data_attribute_id = $attribute_id;

        $this->db->update($this->tables['imported_data'], $this, array('id' => $id));
    }

	function addDataWithAttributes($data, $attributes) {
    	$CI =& get_instance();
		$CI->load->model('Imported_data_attributes_model');

		if ($attribute_id = $CI->Imported_data_attributes_model->insert($attributes)) {
			return $this->insert($data, $attribute_id);
		}
		return false;
	}

	function findByKey($key) {
		$res = $this->db->where('key', $key)
			->limit(1)
			->get($this->tables['imported_data']);

		if($res->num_rows() > 0) {
			return $res->row();
		}
		return false;
	}

	function findByData($search) {
		$this->db->select('data');

		if (is_array($search)) {
			foreach($search as $word) {
				$this->db->like('data', $word);
			}
		} else {
			$this->db->like('data', $search);
		}

		$res = $this->db->get($this->tables['imported_data']);

		if($res->num_rows() > 0) {
			return $res->result_array();
		}
		return false;
	}

	/**
	 * Generate key for data
	 * @param unknown_type $data
	 * @return unknown_type
	 */
	function _get_key($data) {
		return sha1($data);
	}
}
