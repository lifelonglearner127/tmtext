<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Similar_data_model extends CI_Model {

    
    var $tables = array(
        'similar_data' => 'similar_data',
        'similar_product_groups' => 'similar_product_groups',
        
    );

    function __construct()
    {
        parent::__construct();
    }
    
    public function insert($imported_data_id, $group_id){
        
        $this->imported_data_id = $imported_data_id;
        $this->group_id= $group_id;
        $this->black_list=0;

        $this->db->insert($this->tables['similar_data'], $this);
        return $this->db->insert_id();
    }
    
    public function getByGroupId($group_id){
        return $this->db->where('group_id', $group_id)
                ->where('black_list', 0)
    		->get($this->tables['similar_data'])
    		->result();
    }
    
    public function update($group_id,$imported_data_id,$blacklist=1){
        
        $this->black_list=1;

        return $this->db->update($this->tables['similar_data'],
                $this,
                array('group_id' => $group_id,'imported_data_id'=>$imported_data_id));
                                   
    }
    
    public function get_group_id($imp_data_id){
        return $this->db->where('imported_data_id', $imp_data_id)
                ->where('black_list', 0)
    		->get($this->tables['similar_data'])
    		->result_array();;
    }
    
    function get_new_group(){
        
    }
}