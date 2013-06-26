<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Batches_model extends CI_Model {

    var $title = '';
    var $user_id = 0;
    var $customer_id = 0;
    var $created = '';
    var $modified = '';

    var $tables = array(
        'batches' => 'batches',
        'customers' => 'customers'
    );

    function __construct()
    {
        parent::__construct();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['batches']);

        return $query->result();
    }

    function getAll()
    {
        $query =  $this->db->select('*, b.id as id')
            ->from($this->tables['batches'].' as b')
            ->join($this->tables['customers'].' as c', 'c.id = b.customer_id', 'left')
            ->order_by("b.title", "asc")->get();

        return $query->result();
    }

    function getAllByCustomer($customer_id='')
    {
        $this->db->order_by("title", "asc");
        $query = $this->db->where('customer_id', $customer_id)->get($this->tables['batches']);

        return $query->result();
    }

    function insert($title, $customer_id)
    {
        $CI =& get_instance();
        $this->title = $title;
        $this->user_id = $CI->ion_auth->get_user_id();
        $this->customer_id = $customer_id;
        $this->created = date('Y-m-d h:i:s');
        $this->modified = date('Y-m-d h:i:s');

        $this->db->insert($this->tables['batches'], $this);
        return $this->db->insert_id();
    }

    function getIdByName($title)
    {
        $query = $this->db->where('title', $title)
            ->limit(1)
            ->get($this->tables['batches']);

        if($query->num_rows() > 0) {
            return $query->row()->id;
        }
        return false;
    }

    function update($id, $title)
    {
        $CI =& get_instance();
        $this->user_id = $CI->ion_auth->get_user_id();
        $this->title = $title;
        $this->modified = date('Y-m-d h:i:s');

        return $this->db->update($this->tables['batches'],
            $this,
            array('id' => $id));
    }

    function delete($id)
    {
        return $this->db->delete($this->tables['batches'], array('id' => $id));
    }

    function getCustomerByBatch($batch)
    {
        $query =  $this->db->select('c.name')
            ->from($this->tables['batches'].' as b')
            ->join($this->tables['customers'].' as c', 'c.id = b.customer_id', 'left')
            ->where('b.title', trim($batch))->limit(1)->get();
        if($query->num_rows() > 0) {
            return $query->row()->name;
        }
        return false;
    }

}