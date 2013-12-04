<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Kwsync_queue_list_model extends CI_Model {
    
    var $tables = array(
        'kwsync_queue_list' => 'kwsync_queue_list'
    );

    function __construct()
    {
        parent::__construct();
    }

   function insert($id,$kw,$url){
       $data['meta_kw_rank_source_id'] = $id;
       $data['kw'] = $kw;
       $data['url'] = $url;
       $this->db->insert($this->tables['kwsync_queue_list'], $data);
   }

}