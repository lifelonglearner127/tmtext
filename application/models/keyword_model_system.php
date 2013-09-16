<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Keyword_model_system extends CI_Model {

    var $tables = array(
        'keyword_data' => 'keyword_data'
    );

    function __construct()
    {
        parent::__construct();
    }
       
	function get_keywords(){
		$time_now = time();
		$query = $this->db
			->select('keyword, volume, search_engine,region,create_date')
			->where('create_date <=', $time_now)
			->order_by("create_date", "desc")
			->limit(30)
			->get($this->tables['keyword_data']);
		return $query->result();
	}
    function insertKeywords($new_keyword,$new_volume,$new_search_engine,$new_region)
        {
            $this->keyword = $new_keyword;
            $this->volume= $new_volume;
            $this->search_engine= $new_search_engine;
            $this->region= $new_region;
            $this->create_date= time();
            $this->db->insert($this->tables['keyword_data'], $this);
            $query = $this->db
			->select('keyword, volume, search_engine,region,create_date')
			->where('create_date =',  $this->create_date)
			->get($this->tables['keyword_data']);
            return $query->result();
        }
	
}
