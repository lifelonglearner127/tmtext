<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Statistics_duplicate_content_model extends CI_Model {

    var $tables = array(
        'statistics_duplicate_content' => 'statistics_duplicate_content'
    );

    function __construct()
    {
        parent::__construct();
    }

    function get($id)
    {
        $query = $this->db->where('imported_data_id', $id)
            ->get($this->tables['statistics_duplicate_content']);

        return $query->result();
    }

    function truncate()
    {
        $sql_cmd = "TRUNCATE TABLE `statistics_duplicate_content`";
        return $this->db->query($sql_cmd);
    }

    function insert( $imported_data_id, $product_name, $description, $long_description, $url,
                     $features, $parsed_attributes, $customer, $long_original, $short_original)
    {
        $this->imported_data_id = $imported_data_id;
        $this->product_name = $product_name;
        $this->description = (string)$description;
        $this->long_description = (string)$long_description;
        $this->url = $url;
        $this->features = (string)$features;
        $this->parsed_attributes = (string)$parsed_attributes;
        $this->customer = (string)$customer;
        $this->long_original = $long_original;
        $this->short_original = $short_original;
        $this->created = date('Y-m-d h:i:s');

        $this->db->insert($this->tables['statistics_duplicate_content'], $this);
        return $this->db->insert_id();
    }

}
