<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Imported_data_model extends CI_Model {

	var $key = '';
	var $imported_data_attribute_id = null;
	var $company_id;
	var $category_id;
	var $data = '';
	var $created = null;

    var $tables = array(
    	'imported_data' => 'imported_data',
    	'imported_data_parsed' => 'imported_data_parsed'
    );

    function __construct() {
        parent::__construct();
    }

    function getByCateggoryId($cat_id) {
    	$query = $this->db->where('category_id', $cat_id)
                  ->get($this->tables['imported_data']);
        return $query->result();
    }

    function get($id) {
    	$query = $this->db->where('id', $id)
                  ->limit(1)
                  ->get($this->tables['imported_data']);

        return $query->result();
    }

    function getRow($id) {
    	$query = $this->db->where('id', $id)
                  ->limit(1)
                  ->get($this->tables['imported_data']);

        return $query->row();
    }

    function insert($data, $category_id = null, $attribute_id = null) {
        $this->data = $data;
        $this->key = $this->_get_key($data);
        $this->imported_data_attribute_id = $attribute_id;
        $this->category_id = $category_id;
        $this->created = date('Y-m-d h:i:s');

        $this->db->insert($this->tables['imported_data'], $this);
        return $this->db->insert_id();
    }

    function update($id, $data, $category_id = null, $attribute_id = null) {
        $this->data = $data;
        $this->key = $this->_get_key($data);
        $this->imported_data_attribute_id = $attribute_id;

        $this->db->update($this->tables['imported_data'], $this, array('id' => $id));
    }

    function update_attribute_id($id, $attribute_id) {
        return $this->db->update($this->tables['imported_data'], array('imported_data_attribute_id'=>$attribute_id), array('id' => $id));
    }

	function addDataWithAttributes($data, $attributes, $category_id = null) {
    	$CI =& get_instance();
		$CI->load->model('Imported_data_attributes_model');

		if ($attribute_id = $CI->Imported_data_attributes_model->insert($attributes)) {
			return $this->insert($data, $category_id, $attribute_id);
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

	function findNullAttributes($limit = 10) {
		$this->db->select('i.id')
			->distinct()
			->join($this->tables['imported_data_parsed'].' as ip', 'i.id = ip.imported_data_id')
			->where('imported_data_attribute_id IS NULL')
			->limit($limit);
 		$query = $this->db->get($this->tables['imported_data'].' as i');

		return $query->result();
	}
}
