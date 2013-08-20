<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Statistics_model extends CI_Model {

    var $tables = array(
        'statistics' => 'statistics',
        'research_data' => 'research_data'
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

    function insert($rid, $imported_data_id, $research_data_id, $batch_id,
                    $product_name, $url, $short_description, $long_description,
                    $short_description_wc, $long_description_wc,
                    $short_seo_phrases, $long_seo_phrases,
                    $own_price, $price_diff, $competitors_prices, $items_priced_higher_than_competitors, $similar_products_competitors
    )
    {
        $this->rid = $rid;
        $this->imported_data_id = $imported_data_id;
        $this->research_data_id = $research_data_id;
        $this->batch_id = (int)$batch_id;
        $this->product_name = (string)$product_name;
        $this->url = (string)$url;
        $this->short_description = (string)$short_description;
        $this->long_description = (string)$long_description;
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

        $this->db->insert($this->tables['statistics'], $this);
        return $this->db->insert_id();
    }

    function getStatsData($params)
    {
        if(empty($params->batch_id)){
            $batch_id = '';
        } else {
            $batch_id = $params->batch_id;
        }
        $txt_filter = $params->txt_filter;

//        $query = $this->db->where('batch_id', $batch_id)
//            ->like('product_name', $txt_filter)
//            ->get($this->tables['statistics']);

        $query = $this->db
            ->select('s.*, rd.include_in_assess_report')
            ->from($this->tables['statistics'].' as s')
            ->join($this->tables['research_data'].' as rd', 'rd.id = s.research_data_id', 'left')
            ->where('s.batch_id', $batch_id)->like('s.product_name', $txt_filter)
            ->get();
        $result =  $query->result();
        return $result;
    }

    public function countAllItemsHigher($batch_id)
    {
            $this->db->select('id')->from($this->tables['statistics'])
                ->where('batch_id', $batch_id)->where('items_priced_higher_than_competitors', '1');

            return $this->db->count_all_results();
    }

    function products_comparisons_by_batch_id($batch_id){
        $batch_id = $this->db->escape($batch_id);
        $sql_cmd = "
        select
            s.*
        FROM
            statistics as s
        inner join research_data as rd on
            rd.id = s.research_data_id
            and rd.batch_id = $batch_id
            and rd.include_in_assess_report = 1
        ";
        $query = $this->db->query($sql_cmd);
        $result =  $query->result();

        return $result;
    }

    function product_comparisons_by_imported_data_id($imported_data_id){
        $imported_data_id = $this->db->escape($imported_data_id);
        $sql_cmd = "
        select
            s.*
        FROM
            statistics as s
        where
            s.imported_data_id = $imported_data_id
        limit 1
        ";
        $query = $this->db->query($sql_cmd);
        $result =  $query->result();

        return $result;
    }
}
