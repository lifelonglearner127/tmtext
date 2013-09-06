<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Statistics_new_model extends CI_Model {

    var $tables = array(
        'statistics' => 'statistics',
        'statistics_new' => 'statistics_new',
        'research_data' => 'research_data',
        'crawler_list' => 'crawler_list',
    );

    function __construct()
    {
        parent::__construct();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['statistics_new']);

        return $query->result();
    }


    function truncate()
    {
        $sql_cmd = "TRUNCATE TABLE `statistics_new`";
        return $this->db->query($sql_cmd);
    }

    function insert( $imported_data_id, $revision,

                         $short_description_wc, $long_description_wc,
                         $short_seo_phrases, $long_seo_phrases,
                         $own_price, $price_diff, $competitors_prices, $items_priced_higher_than_competitors, $similar_products_competitors){

        $this->imported_data_id = $imported_data_id;
        $this->revision = $revision;

        $this->short_description_wc = (string)$short_description_wc;
        $this->long_description_wc = (string)$long_description_wc;
        $this->short_seo_phrases = (string)$short_seo_phrases;
        $this->long_seo_phrases = (string)$long_seo_phrases;
        $this->created = date('Y-m-d h:i:s');
        $this->own_price = (string)$own_price;
        $this->price_diff = (string)$price_diff;
        $this->competitors_prices = (string)$competitors_prices;
        $this->items_priced_higher_than_competitors = $items_priced_higher_than_competitors;
        $this->similar_products_competitors = $similar_products_competitors;

        $this->db->insert('statistics_new', $this);
        return $this->db->insert_id();

    }


    function getStatsData($params)
    {
        if(empty($params->batch_id)){
            $batch_id = '';
        } else {
            $batch_id = $params->batch_id;
        }

//        $query = $this->db->where('batch_id', $batch_id)
//            ->like('product_name', $txt_filter)
//            ->get($this->tables['statistics']);

        $query = $this->db
            ->select('s.*, cl.snap, cl.snap_date, cl.snap_state')
            ->from($this->tables['statistics_new'].' as s')
            ->join($this->tables['crawler_list'].' as cl', 'cl.imported_data_id = s.imported_data_id', 'left')
            ->where('s.batch_id', $batch_id)->get();
        $result =  $query->result();
        return $result;
    }


}
