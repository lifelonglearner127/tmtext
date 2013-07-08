<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Items_model extends CI_Model {

    var $tables = array(
        'items' => 'items',
    );

    function __construct()
    {
        parent::__construct();
    }

    function getAll()
    {
        $this->db->order_by("id", "asc");
        $query = $this->db->get($this->tables['items']);

        return $query->result();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['items']);

        return $query->result();
    }


    function insert($batch_id, $customer_id, $url)
    {
        $CI =& get_instance();
        $this->user_id = $CI->ion_auth->get_user_id();
        $this->batch_id = $batch_id;
        $this->customer_id = $customer_id;
        $this->url = $url;
        $this->created = date('Y-m-d h:i:s');
        $this->modified = date('Y-m-d h:i:s');

        $this->db->insert($this->tables['items'], $this);
        return $this->db->insert_id();
    }

    function delete($id)
    {
        return $this->db->delete($this->tables['items'], array('id' => $id));
    }


}