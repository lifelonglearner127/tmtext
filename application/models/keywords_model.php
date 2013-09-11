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
        $query = $this->db->where('imported_data_id',$im_data_id)->where("revision = (SELECT  MAX(revision) as revision
                      FROM keywords_new WHERE `imported_data_id`= $im_data_id
                      GROUP BY imported_data_id)", NULL, FALSE)
           
        ->get($this->tables['keywords']);

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
