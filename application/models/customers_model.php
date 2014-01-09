<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Customers_model extends CI_Model {

    var $tables = array(
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
                    ->get($this->tables['customers']);

        return $query->result();
    }

    function getAll()
    {
        // $query = $this->db->order_by('name', 'asc')->get($this->tables['customers']);
        $query = $this->db->order_by('url', 'asc')->get($this->tables['customers']);
        return $query->result();
    }

    function getIdByName($name)
    {
        $query = $this->db->where('name', $name)
            ->limit(1)
            ->get($this->tables['customers']);

        if($query->num_rows() > 0) {
            return $query->row()->id;
        }
        return '';
    }

    function getByName($name)
    {
        $query = $this->db->where('name', $name)
            ->limit(1)
            ->get($this->tables['customers']);

        if($query->num_rows() > 0) {
            return $query->row_array();
        }
        return '';
    }

    function  insert($customer_name, $customer_url, $logo)
    {
        $this->name = $customer_name;
        $this->url = $customer_url;
        $this->image_url = $logo;

        $this->db->insert($this->tables['customers'], $this);
        return $this->db->insert_id();
    }
    
    function update($name,$customer_url, $logo){
        $data = array(
               'url' => $customer_url,
               'image_url' => $logo,
               
            );

        $this->db->where('name', $name);
        $this->db->update($this->tables['customers'], $data); 
    }
    
    function delete($id){
		$this->db->delete($this->tables['customers'], array('id' => $id)); 
	}

    function getCustomersList()
    {
	    $customers_list = array();
            $query_cus = $this->db->select('url')->order_by('name', 'asc')->get($this->tables['customers']);
	    if ($query_cus->num_rows() > 0)
	    {
		$query_cus_res = $query_cus->result();
		foreach ($query_cus_res as $key => $value) 
		{
                    $n = parse_url($value->url);
                    $customers_list[] = $n['host'];
                }
		$customers_list = array_unique($customers_list);
	    }
	    $query_cus->free_result();
	    return $customers_list;
    }	
}
