<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Users_To_Customers_model extends CI_Model {

    var $tables = array(
    	'users_to_customers' => 'users_to_customers',
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
                    ->get($this->tables['users_to_customers']);

        return $query->result();
    }
    
    function getByUserId($user_id){
        $query = $this->db->select('*')
                      ->from($this->tables['users_to_customers'].' as u')
                      ->join($this->tables['customers'].' as c', 'c.id = u.customer_id', 'left')
                      ->where('user_id', $user_id)
                      ->get();

        return $query->result();
    }

    function getAll()
    {
        $query = $this->db->get($this->tables['users_to_customers']);

        return $query->result();
    }

    function set($user_id, $customer_id){
         $data = array(
           'user_id' => $user_id ,
           'customer_id' => $customer_id 
        );

        $query = $this->db->insert('users_to_customers', $data);

        return $query;
    }

    function delete($user_id, $customer_id){
        $query = $this->db->where('user_id', $user_id)->where('customer_id', $customer_id)->delete($this->tables['users_to_customers']);
    
        return $query;
    }
}
