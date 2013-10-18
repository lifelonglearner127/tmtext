<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class snapshot_queue_list_model extends CI_Model {
    
    var $tables = array(
        'snapshot_queue_list' => 'snapshot_queue_list'
    );
    
    function __construct()
    {
        parent::__construct();
    }
    
    public function insert($snapshot_id_arr,$type){
        foreach($snapshot_id_arr as $snapshot_id){
            $query = $this->db->get_where($this->tables['snapshot_queue_list'], array(
                    'snapshot_id' => $snapshot_id,
                    'user_id' => $this->ion_auth->get_user_id(),
                    'type' => $type
                ));
            $result = $query->result();
            if(!$result){
                $data = array(
                    'snapshot_id' => $snapshot_id,
                    'user_id' => $this->ion_auth->get_user_id(),
                    'type' => $type
                );
                $this->db->insert($this->tables['snapshot_queue_list'], $data);
            }
        }
    }
    
    public function select(){
        $query = $this->db->get($this->tables['snapshot_queue_list']);
        $result = $query->result_array();
        return $result;
    }

    public function delete(){
        $this->db->empty_table($this->tables['snapshot_queue_list']);
    }
    
    public function deleteByDepId($snapshot_id){
        $this->db->delete($this->tables['snapshot_queue_list'], array('snapshot_id' => $snapshot_id,'user_id' => $this->ion_auth->get_user_id())); 
    }

}
