<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Crawler_List_model extends CI_Model {
    var $url = '';
    var $user_id = 0;
    var $status = 'new'; // new, reserved, finished
    var $created = '';
	var $category_id = 0;

    var $tables = array(
    	'crawler_list' => 'crawler_list'
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


    function getAllNew()
    {
    	$CI =& get_instance();

    	$this->db->select('id, url, category_id')
    		->where('user_id',  $CI->ion_auth->get_user_id())
    		->where('status', 'new');
        $query = $this->db->get($this->tables['crawler_list']);

        return $query->result();
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
