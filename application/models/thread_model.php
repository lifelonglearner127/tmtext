<?php

class Thread_model extends CI_Model{

    function add_process($data){
        $this->db->set($data);
        $this->db->set('status', 'start');
        return $this->db->insert('thread_process_info');
    }

    function updateStatus($id_process, $status='end', $another_data=false){
        $this->db->where('name_process', $id_process);
        if($another_data){
            $this->db->set($another_data);
        }
        $this->db->set('status', $status);
        return $this->db->update('thread_process_info');
    }

    function get_process_fields($process_name){
        $this->db->where('name_process', $process_name);
        return $this->db->get('thread_process_info')->row_array();
    }

    function clear($uid){
        $this->db->where('uid', $uid);
        return $this->db->delete('thread_process_info');
    }


}