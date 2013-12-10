<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Kwsync_queue_list_model extends CI_Model {
    
    var $tables = array(
        'kwsync_queue_list' => 'kwsync_queue_list'
    );

    function __construct()
    {
        parent::__construct();
    }
    
    function getAll(){
        
        $query = $this->db->get($this->tables['kwsync_queue_list']);

        return $query->result_array();
    }

   function insert($id,$kw,$url){
        $data['meta_kw_rank_source_id'] = $id;
        $data['kw'] = $kw;
        $data['url'] = $url;
        $data['status'] = 0;
        $data['stamp'] = date("Y-m-d H:i:s");
        
        $query = $this->db->get_where($this->tables['kwsync_queue_list'], array('meta_kw_rank_source_id' => $id));
        $result = $query->result_array();
        if(!$result)
            $this->db->insert($this->tables['kwsync_queue_list'], $data);
   }
   
   function deleteAll(){
       $this->db->empty_table($this->tables['kwsync_queue_list']);
   }

}