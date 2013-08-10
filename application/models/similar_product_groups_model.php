
<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Similar_product_groups_model extends CI_Model {

    
    var $tables = array(
        'similar_data' => 'similar_data',
        'similar_product_groups' => 'similar_product_groups',
        
    );
    
    function __construct()
    {
        parent::__construct();
    }
     public function get_all(){
         $query = $this->db->get($this->tables['similar_product_groups']);
         $res=$query->result_array();
         $result=array();
         foreach($res as $val){
             $result[]=$val['ipd_id'];
         }
         return $result;
     }
    public function insert($group_id){
        
        $this->ipd_id= $group_id;
        $this->db->insert($this->tables['similar_product_groups'], $this);
        return $this->db->insert_id();
   }
   public function checkIfgroupExists($group_id){
       $query = $this->db->where('ipd_id', $group_id)
              ->get($this->tables['similar_product_groups']);
     if($query->num_rows() > 0){
       return true;
   }
   return false;
   }
    
}