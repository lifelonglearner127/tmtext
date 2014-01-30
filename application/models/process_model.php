<?php

require_once(APPPATH . 'models/base_model.php');

class Process_model extends Base_model {

    public function getRules() {
        return array(
            'process_name' => array('type' => 'required')
        );
    }

    public function getTableName() {
        return 'processes';
    }

    public function add($title, $day) {
        $day = intval($day);
        if ($day > 6 || $day < 0) {
            return FALSE;
        }
        $data = array(
            'process_name' => $title,
            'week_day' => $day
        );
        $this->db->insert('processes', $data);
        return $this->db->insert_id();
    }

    public function update() {
        
    }

    public function delete($id) {
        
    }

}

?>