<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Rankapi_model extends CI_Model {

    var $tables = array(
    	'ranking_api_data' => 'ranking_api_data'
    );

    function __construct() {
        parent::__construct();
    }

    public function start_db_sync($sync_data) {
        $check_obj = array(
            'site' => $sync_data['site'],
            'keyword' => $sync_data['keyword']
        );
        $c_query = $this->db->where($check_obj)->order_by('stamp', 'desc')->limit(6)->get($this->tables['ranking_api_data']);
        $c_res = $c_query->result();
        if(count($c_res) > 0) { // === update
            $r = $c_res[0];
            $update_object = array(
                'location' => $sync_data['location'],
                'engine' => $sync_data['engine'],
                'rank_json_encode' => $sync_data['rank_json_encode'],
                'stamp' => date("Y-m-d H:i:s")
            );
            $c_object = array(
                'site' => $r->site,
                'keyword' => $r->keyword
            );
            $this->db->update($this->tables['ranking_api_data'], $update_object, $c_object);
        } else { // === insert
            $insert_object = array(
                'site' => $sync_data['site'],
                'keyword' => $sync_data['keyword'],
                'location' => $sync_data['location'],
                'engine' => $sync_data['engine'],
                'rank_json_encode' => $sync_data['rank_json_encode'],
                'stamp' => date("Y-m-d H:i:s")
            );
            $this->db->insert($this->tables['ranking_api_data'], $insert_object);
        }
        return true;   
    }

}
