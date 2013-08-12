<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Crawler_List_model extends CI_Model {
    var $url = '';
    var $user_id = 0;
    var $status = 'new'; // new, reserved, finished
    var $created = '';
	var $category_id = 0;

    var $tables = array(
    	'crawler_list' => 'crawler_list',
    	'categories' => 'categories'
    );

    function __construct() {
        parent::__construct();
    }

    function get($id) {
    	$query = $this->db->where('id', $id)
                  ->limit(1)
                  ->get($this->tables['crawler_list']);

        return $query->result();
    }

    function insert($url, $category_id) {
		$CI =& get_instance();

    	$this->url = $url;
        $this->user_id = $CI->ion_auth->get_user_id();
        $this->category_id = $category_id;
        $this->created = date('Y-m-d h:i:s');

        $this->db->insert($this->tables['crawler_list'], $this);
        return $this->db->insert_id();
    }

    function updateUrl($id, $url) {
    	$CI =& get_instance();
        return $this->db->update($this->tables['crawler_list'], array('url' => $url), array('id' => $id, 'user_id' => $CI->ion_auth->get_user_id()));
    }


    function updateStatus($id, $status) {
        return $this->db->update($this->tables['crawler_list'], array('status' => $status), array('id' => $id));
    }

    function updated($id) {
    	 return $this->db->update($this->tables['crawler_list'], array('updated' => date('Y-m-d h:i:s')), array('id' => $id));
    }

	function updateImportedDataId($id, $imported_id) {
    	 return $this->db->update($this->tables['crawler_list'], array('imported_data_id' => $imported_id), array('id' => $id));
    }


    function delete($id) {
    	$CI =& get_instance();

    	return $this->db->delete($this->tables['crawler_list'], array('id' => $id, 'user_id' => $CI->ion_auth->get_user_id()));
    }

    function getByUrl($url)
    {
       $query = $this->db->where('url', $url)->limit(1)->get($this->tables['crawler_list']);
       if($query->num_rows() > 0) {
           return $query->row()->id;
       }
       return false;
    }


    function getAllNew($limit, $only_my=true)
    {
    	$CI =& get_instance();

    	$this->db->select('id, url, category_id')
    		->where('status', 'new');

    	if ($only_my) {
    		$this->db->where('user_id',  $CI->ion_auth->get_user_id());
    	}

    	if (isset($limit) && $limit>0) {
    		$this->db->limit($limit);
    	}

        $query = $this->db->get($this->tables['crawler_list']);

        return $query->result();
    }

    function getAll($limit = null, $only_my=true)
    {
    	$CI =& get_instance();

    	$this->db->select('id, url, category_id, imported_data_id, status')
    		->where('user_id',  $CI->ion_auth->get_user_id());

    	if ($only_my) {
    		$this->db->where('user_id',  $CI->ion_auth->get_user_id());
    	}

    	if (isset($limit) && $limit>0) {
    		$this->db->limit($limit);
    	}

        $query = $this->db->get($this->tables['crawler_list']);

        return $query->result();
    }

    function getAllLimit($limit, $start, $only_my=true, $search_crawl_data='')
    {
    	$CI =& get_instance();

    	$this->db->select('cl.id, cl.imported_data_id, cl.url, c.name as name, cl.status, DATE(cl.updated) as updated')
    		->from($this->tables['crawler_list'].' as cl')
            ->join($this->tables['categories'].' as c', 'cl.category_id = c.id', 'left');

    	if ($only_my) {
    		$this->db->where('user_id',  $CI->ion_auth->get_user_id());
    	}
        if($search_crawl_data != ''){
            $this->db->like('cl.url', $search_crawl_data)->or_like('c.name', $search_crawl_data)->or_like('cl.status', $search_crawl_data)->or_like('DATE(cl.updated)', $search_crawl_data);
        }

        $query = $this->db->order_by("cl.created", "desc")->limit($limit, $start)->get();

        return $query->result();
    }

    function countAll($only_my=true, $search_crawl_data='')
    {
    	$CI =& get_instance();

    	$this->db->select('cl.id')
    		->from($this->tables['crawler_list'].' as cl')
            ->join($this->tables['categories'].' as c', 'cl.category_id = c.id', 'left')
    		->order_by("cl.created", "desc");

    	if ($only_my) {
    		$this->db->where('user_id',  $CI->ion_auth->get_user_id());
    	}
        if($search_crawl_data != ''){
            $this->db->like('cl.url', $search_crawl_data)->or_like('c.name', $search_crawl_data)->or_like('cl.status', $search_crawl_data)->or_like('DATE(cl.updated)', $search_crawl_data);
        }

        return $this->db->count_all_results();
    }


    function getNew()
    {
    	$this->db->select('id, url')
    		->limit(1)
    		->where('status', 'new')
    		 ->order_by('created', 'asc');
        $query = $this->db->get($this->tables['crawler_list']);

        return $query->row();
    }


}
