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

    function getByValueLikeGroup($s) {
        $this->db->select('imported_data_id, key, value');
        $this->db->like('value', $s);
        $this->db->group_by('imported_data_id');
        $res = $this->db->get($this->tables['imported_data_parsed']);
        if($res->num_rows() > 0) {
            $result = $res->result_array();
            $im_data_id = $result[0]['imported_data_id'];

            $query = $this->db->where('imported_data_id', $im_data_id)->get($this->tables['imported_data_parsed']);
            return $query->result_array();
        }
        return false;
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

    function getData($value){

        $query = $this->db->select('imported_data_id, key, value')->where('key', 'Product Name')
            ->like('value', $value)->get($this->tables['imported_data_parsed']);
        $results = $query->result();
        $data = array();
        foreach($results as $result){
            $res = $this->db->select('value')->where('key', 'URL')->where('imported_data_id', $result->imported_data_id)
                ->get($this->tables['imported_data_parsed']);
            $url = $res->result();
            array_push($data, array('product_name'=>$result->value, 'url'=>$url[0]->value));
        }

        return $data;
    }

}
