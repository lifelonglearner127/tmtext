<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Style_Guide_Model extends CI_Model {
    public $style = '';
    public $customer_id = '';
    
    var $tables = array(
    	'style_gide' => 'style_guide'
    );


    function __construct() {
        parent::__construct();
    }
    
    public function insertStyle($txtcontent, $customerId)
    {
        $this->style = $txtcontent;
        $this->customer_id = $customerId;
        if($this->getStyleByCustomerId($customerId)){
            $this->db->update($this->tables['style_gide'],$this , array('customer_id' => $customerId));
        }else{
            $this->db->insert($this->tables['style_gide'], $this);
        }
        
        
        //return $this->db->insert_id();

    }
    
    public function getStyleByCustomerId($customerId)
    {
         $query = $this->db->where('customer_id', $customerId)
                  ->get($this->tables['style_gide']);
        return $query->result();
    }
}
