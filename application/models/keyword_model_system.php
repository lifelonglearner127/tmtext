<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Keyword_model_system extends CI_Model {

    var $tables = array(
        'keyword_data' => 'keyword_data',
        'search_engine' => 'search_engine',
        'regions'=>'regions'
    );

    function __construct()
    {
        parent::__construct();
    }
         
    
    function get_regions(){
		
		$query = $this->db
			->select('id,region')
                        ->from($this->tables['regions'])
			->order_by("region", "desc")
			->get();
		return $query->result();
	}
      function get_serach_engine(){
		
		$query = $this->db
			->select('id,search_engine')
                        ->from($this->tables['search_engine'])
			->order_by("search_engine", "desc")
			->get();
		return $query->result();
	}
    
    
	function get_keywords(){
		$time_now = time();
		$query = $this->db
			->select('k.keyword, k.volume, s.search_engine,r.region,k.create_date')
                        ->from($this->tables['keyword_data'].' as k')
                        ->join($this->tables['search_engine'].' as s', 'k.search_engine = s.id', 'left')
                        ->join($this->tables['regions'].' as r', 'k.region = r.id', 'left')
			->where('k.create_date <=', $time_now)
			->order_by("k.create_date", "desc")
			->limit(30)
			->get();
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
			->select('k.keyword, k.volume, s.search_engine,r.region,k.create_date')
                        ->from($this->tables['keyword_data'].' as k')
                        ->join($this->tables['search_engine'].' as s', 'k.search_engine = s.id', 'left')
                        ->join($this->tables['regions'].' as r', 'k.region = r.id', 'left')
			->where('create_date =',  $this->create_date)
			->order_by("k.create_date", "desc")
			->limit(30)
			->get();
		return $query->result();
        }
	
}
