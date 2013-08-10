<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Statistics_model extends CI_Model {

    var $tables = array(
        'statistics' => 'statistics'
    );

    function __construct()
    {
        parent::__construct();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['statistics']);

        return $query->result();
    }

    function truncate()
    {
        $sql_cmd = "TRUNCATE TABLE `statistics`";
        return $this->db->query($sql_cmd);
    }

    function insert($rid, $imported_data_id, $batch_name,
                    $product_name, $url, $short_description, $long_description,
                    $short_description_wc, $long_description_wc,
                    $short_seo_phrases, $long_seo_phrases)
    {
        $this->rid = $rid;
        $this->imported_data_id = $imported_data_id;
        $this->batch_name = $batch_name;
        $this->product_name = $product_name;
        $this->url = $url;
        $this->short_description = (string)$short_description;
        $this->long_description = (string)$long_description;
        $this->short_description_wc = (string)$short_description_wc;
        $this->long_description_wc = (string)$long_description_wc;
        $this->short_seo_phrases = (string)$short_seo_phrases;
        $this->long_seo_phrases = (string)$long_seo_phrases;
        $this->created = date('Y-m-d h:i:s');

        $this->db->insert($this->tables['statistics'], $this);
        return $this->db->insert_id();
    }

}
