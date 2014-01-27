<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Keywords_model extends CI_Model {

    var $tables = array(
        'keywords' => 'keywords_new'
    );

    function __construct()
    {
        parent::__construct();
    }

    function get_by_imp_id($im_data_id)
    {
		if (!$im_data_id)
			return array();
			
        $query = $this->db->where('imported_data_id',$im_data_id)->where("revision = (SELECT  MAX(revision) as revision
                      FROM keywords_new WHERE `imported_data_id`= $im_data_id
                      GROUP BY imported_data_id)", NULL, FALSE)
           
        ->get($this->tables['keywords']);
       
        return $query->row_array();
    }
    function get_by_keyword($keyword){
        $keyword=trim(strtolower($keyword));
        $query = $this->db->where('LOWER(keyword)',$keyword)->where("create_date = (SELECT  MAX(create_date) as create_date
                      FROM keyword_data WHERE LOWER(keyword) = '".$keyword."'
                      )", NULL, FALSE)
           
        ->get('keyword_data');
         
        return $query->row_array();
    }
    function insert($im_data_id, $primary, $secondary, $tertiary){
    
        if(count($this->get_by_imp_id($im_data_id))>0){
            $data=$this->get_by_imp_id($im_data_id);
            $this->primary = $primary;
            $this->secondary = $secondary;
            $this->tertiary = $tertiary;
            $this->revision = $data['revision']+1;
            $this->imported_data_id = $im_data_id;
            $this->create_date = date('Y-m-d h:i:s');
            $this->db->insert($this->tables['keywords'], $this);
        }else{
            $this->imported_data_id = $im_data_id;
            $this->primary = $primary;
            $this->secondary = $secondary;
            $this->tertiary = $tertiary;
            $this->create_date = date('Y-m-d h:i:s');
            $this->revision= 1;
            $this->db->insert($this->tables['keywords'], $this);
        }

    }

    
}
