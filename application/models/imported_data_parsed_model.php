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

    function getByValueLikeGroup($s, $sl) {
        $this->db->select('imported_data_id, key, value');
        $this->db->like('value', $s);
        $this->db->group_by('imported_data_id');
        $res = $this->db->get($this->tables['imported_data_parsed']);
        if($res->num_rows() > 0) {
            $result = $res->result_array();
            
            // --- OLD ONE (START)
            // $im_data_id = $result[0]['imported_data_id'];
            // $query = $this->db->where('imported_data_id', $im_data_id)->get($this->tables['imported_data_parsed']);
            // return $query->result_array();
            // --- OLD ONE (END)

            // --- NEW ONE (START)
            $final_res = array();
            if($sl !== 'all') {
                $im_data_id_arr = array();
                foreach ($result as $key => $value) {
                    $im_data_id_arr[] = $value['imported_data_id'];
                }
                $query = $this->db->where_in('imported_data_id', $im_data_id_arr)->get($this->tables['imported_data_parsed']);
                $f_res = $query->result_array();
                $f_index = 0;
                foreach ($f_res as $key => $value) {
                    if($value['key'] === 'URL') {
                        if(strpos($value['value'], "$sl") !== false) {
                            $f_index = $value['imported_data_id'];
                            break;
                        }
                    }
                }
                if($f_index != 0) {
                    $im_data_id = $f_index;
                    $query = $this->db->where('imported_data_id', $im_data_id)->get($this->tables['imported_data_parsed']);
                    $f_res = $query->result_array();
                    $final_res = $f_res;
                    return $final_res;
                } else {
                    return $final_res;
                }
            } else {
                $im_data_id = $result[0]['imported_data_id'];
                $query = $this->db->where('imported_data_id', $im_data_id)->get($this->tables['imported_data_parsed']);
                $f_res = $query->result_array();
                $final_res = $f_res;
            }
            return $final_res;
            // --- NEW ONE (END)
            
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
            $res = $this->db->select('value')->where_in('key', array('URL', 'Description'))->where('imported_data_id', $result->imported_data_id)
                ->get($this->tables['imported_data_parsed']);
            $info = $res->result();
            array_push($data, array('imported_data_id'=>$result->imported_data_id, 'product_name'=>$result->value, 'url'=>$info[1]->value, 'description'=>$info[0]->value));
        }

        return $data;
    }

}
