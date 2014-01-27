<?php

require_once(APPPATH . 'models/base_model.php');

class Operations_model extends Base_model {

    public function getRules() {
        return array(
            'func_url' => array('type' => 'required')
        );
    }

    public function getTableName() {
        return 'operations';
    }

    public function add($title,$url) {
        $this->db->select('id');
        $this->db->from('operations');
        $this->db->where('func_url', $url);
        $query = $this->db->get();
        if ($query->num_rows > 0) {
            return FALSE;
        }
        $data = array(
            'func_title' => $title,
            'func_url' => $url
        );
        $this->db->insert('operations', $data);
        return $this->db->insert_id();
    }

    public function update() {
        
    }

//    public function delete($id) {
//        
//    }

}

?>