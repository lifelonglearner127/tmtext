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
    
    	/**
	 *  @brief Returns the size of current table.
	 *  
	 *  @return Count of rows in table
	 */
    function getTableSize(){
        $sql='select count(*) as size from '
                .$this->getTableName();
        $query = $this->db->query($sql);
        $res = $query->first_row();
        return $res->size;
    }

	/**
	 *  @brief Add operation to operatin list.
	 *  
	 *  @param string $title title of operation, string $url link for running operation, order of running.
	 *  @return ID of added operation if success
	 */
    public function add($title,$url,$ord=0) {
        $this->db->select('id');
        $this->db->from('operations');
        $this->db->where('func_url', $url);
        $query = $this->db->get();
        if ($query->num_rows > 0) {
            return FALSE;
        }
        if($ord===0){
            $ord = $this->getTableSize()+1;
        }
        else{
            $sql = 'UPDATE operations SET operation_order=operation_order+1 WHERE operation_order >= '.$ord;
            $this->db->query($sql);
        }
        $data = array(
            'func_title' => $title,
            'func_url' => $url,
            'operation_order'=> $ord
        );
        $this->db->insert('operations', $data);
        return $this->db->insert_id();
    }
	/**
	 *  @brief Retruns all operations from table.
	 *  
	 *  @return Array of operation
	 */
        public function getAll(){
            $this->db->select('*');
            $this->db->from('operations');
            $this->db->order_by('operation_order');
            $query = $this->db->get();
            if($query->num_rows===0){
                return FALSE;
            }
            return $query->result_array();
        }

    public function update() {
        $this->db->update($this->getTableName(), $data, array('id' => $data['id']));       
    }


//    public function delete($id) {
//        
//    }

}

?>