<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class snapshot_queue_model extends CI_Model {
    
    var $tables = array(
        'snapshot_queue' => 'snapshot_queue'
    );
    
    function __construct()
    {
        parent::__construct();
    }
    
    function insertCount($processCount){
        $data = array(
            'user_id' => $this->ion_auth->get_user_id(),
            'process' => $processCount
        );

        $this->db->insert($this->tables['snapshot_queue'], $data); 
    }
    
    function updateCount(){
        $query = $this->db->query("SELECT process,done FROM {$this->tables['snapshot_queue']} WHERE user_id = {$this->ion_auth->get_user_id()}");
        $result = $query->result_array();
        
        $data = array(
            'process' => (int)$result[0]['process'] - 1,
            'done' => (int)$result[0]['done'] + 1
        );

        $this->db->where('user_id', $this->ion_auth->get_user_id());
        $this->db->update($this->tables['snapshot_queue'], $data); 
    }
    
    function deleteCount(){
        $this->db->delete($this->tables['snapshot_queue'], array('user_id' => $this->ion_auth->get_user_id())); 
    }
    
    function checkCount(){
        $query = $this->db->query("SELECT process,done FROM {$this->tables['snapshot_queue']} WHERE user_id = {$this->ion_auth->get_user_id()}");
        $result = $query->result_array();
        return $result[0];
    }

}
