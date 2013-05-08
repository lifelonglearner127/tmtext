<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Saved_Description_model extends CI_Model {

    var $key   = '';
    var $title = '';
    var $description = '';
    var $revision = 1;
    var $user_id = 0;
    var $search_id = null;
    var $created = '';

    var $tables = array(
    	'saved_descriptions' => 'saved_descriptions'
    );

    function __construct()
    {
        parent::__construct();
    }

    function get($id)
    {
    	$query = $this->db->where('id', $id)
                  ->limit(1)
                  ->get($this->tables['saved_descriptions']);

        return $query->result();
    }

    function insert($title, $description, $search_id = null)
    {
    	$CI =& get_instance();

        $this->title = $title;
        $this->description = $description;
        $this->search_id = (isset($search_id)? $search_id: null);

        $this->user_id = $CI->ion_auth->get_user_id();

        $this->created = date('Y-m-d h:i:s');

        $this->db->insert($this->tables['saved_descriptions'], $this);
        return $this->db->insert_id();
    }

}
