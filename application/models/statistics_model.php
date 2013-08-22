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

    function product_comparison($batch_id){
        $this->load->model('sites_model');
        $this->load->model('settings_model');

        $all_sites = $this->sites_model->getAll();
        $user_id = $this->ion_auth->get_user_id();
        $key = 'research_assess_report_options';
        $existing_settings = $this->settings_model->get_value($user_id, $key);
        $batch_settings = $existing_settings[$batch_id];

        $competitors_sites_for_comparisons = array();
        $comparison_product_array = array();

        foreach ($all_sites as $k => $v){
            if (in_array($v->id, $batch_settings->assess_report_competitors)) {
                $competitors_sites_for_comparisons[] = strtolower($v->name);
            }
        }

        $marked = $this->products_comparisons_by_batch_id($batch_id);
        foreach ($marked as $marked_product){
            $similar_products_competitors = unserialize($marked_product->similar_products_competitors);
            if (count($similar_products_competitors) > 0) {
                foreach ($similar_products_competitors as $product) {
                    foreach ($competitors_sites_for_comparisons as $competitor_site) {
                        if (strtolower(trim($competitor_site)) == strtolower(trim($product['customer']))) {
                            $comparison_product_obj = new stdClass();
                            $comparison_product = $this->product_comparisons_by_imported_data_id($product['imported_data_id']);

                            if (count($comparison_product) > 0) {
                                $site = $this->get_site_by_url($all_sites, $marked_product->url);
                                if (!$site) {
                                    $own_logo = '';
                                } else {
                                    $own_logo = $site->image_url;
                                }
                                $site = $this->get_site_by_url($all_sites, $comparison_product[0]->url);
                                if (!$site) {
                                    $competitor_logo = '';
                                } else {
                                    $competitor_logo = $site->image_url;
                                }

                                if (intval($marked_product->short_description_wc) > 0) {
                                    $own_short_description = $marked_product->short_description_wc.' words';
                                } else {
                                    $own_short_description = 'None';
                                    $comparison_product_obj->red[] = 'short_description';
                                }
                                if (intval($comparison_product[0]->short_description_wc) > 0) {
                                    $competitor_short_description = $comparison_product[0]->short_description_wc.' words';
                                } else {
                                    $competitor_short_description = 'None';
                                }

                                if (intval($marked_product->long_description_wc) > 0) {
                                    $own_long_description = $marked_product->long_description_wc.' words';
                                } else {
                                    $own_long_description = 'None';
                                    $comparison_product_obj->red[] = 'long_description';
                                }
                                if (intval($comparison_product[0]->long_description_wc) > 0) {
                                    $competitor_long_description = $comparison_product[0]->long_description_wc.' words';
                                } else {
                                    $competitor_long_description = 'None';
                                }

                                $own_price = floatval($marked_product->own_price);
                                $competitor_price = floatval($comparison_product[0]->own_price);
                                if ($own_price > $competitor_price) {
                                    $comparison_product_obj->red[] = 'price';
                                }

                                $comparison_product_obj->left_product = array(
                                    'logo' => $own_logo,
                                    'url' => $marked_product->url,
                                    'product' => $marked_product->product_name,
                                    'price' => $own_price,
                                    'short_description' => $own_short_description,
                                    'short_seo_keyword' => $marked_product->short_seo_phrases,
                                    //'short_duplicate_content' => $marked_product->
                                    'long_description' => $own_long_description,
                                    'long_seo_keyword' => $marked_product->long_seo_phrases,
                                    //'long_duplicate_content' => $marked_product->
                                );

                                $comparison_product_obj->right_product = array(
                                    'logo' => $competitor_logo,
                                    'url' => $comparison_product[0]->url,
                                    'product' => $comparison_product[0]->product_name,
                                    'price' => $competitor_price,
                                    'short_description' => $competitor_short_description,
                                    'short_seo_keyword' => $comparison_product[0]->short_seo_phrases,
                                    //'short_duplicate_content' =>
                                    'long_description' => $competitor_long_description,
                                    'long_seo_keyword' => $comparison_product[0]->long_seo_phrases,
                                    //'long_duplicate_content' =>
                                );

                                $comparison_product_array[] = $comparison_product_obj;
                            }
                        }
                    }
                }
            }
        }
        return $comparison_product_array;
    }

    private function get_site_by_url($all_sites, $site_url){
        $search_host = parse_url(trim(strtolower($site_url)));
        $search_host = str_replace('www.', '', $search_host['host']);
        foreach ($all_sites as $k => $v){
            $current_host = parse_url(trim(strtolower($v->url)));
            $current_host = str_replace('www.', '', $current_host['host']);
            if (strcasecmp($current_host, $search_host) == 0) {
                return $v;
            }
        }
        return false;
    }

    public function batches_compare($own_batch_id, $compare_batch_id){
        $query = $this->db->where('batch_id', $own_batch_id)
            ->get($this->tables['statistics']);
        $own_batch =  $query->result();

        $query = $this->db->where('batch_id', $compare_batch_id)
            ->get($this->tables['statistics']);
        $compare_batch =  $query->result();

        $absent_items = array();
        foreach ($compare_batch as $compare_product){
            foreach ($own_batch as $own_product){
                $similar_products_competitors = unserialize($own_product->similar_products_competitors);
                foreach ($similar_products_competitors as $similar_product){
                    if ($similar_product['imported_data_id'] == $compare_product->imported_data_id){
                        continue 3;
                    }
                }
            }
            $absent_items[] = array(
                'product_name' => $compare_product->product_name,
                'url' => $compare_product->url,
                'recommendations' => 'Add item to product selection',
            );
        }

        //asort($absent_items);

        return $absent_items;
    }

    public function total_items_in_batch($batch_id){
        $this->load->model('research_data_model');
        $params = new stdClass();
        $params->batch_id = $batch_id;
        $params->txt_filter = '';
        $res = $this->getStatsData($params);
        $num_rows = count($res);
        if($num_rows == 0){
            $num_rows = $this->research_data_model->countAll($batch_id);
        }
        return $num_rows;
    }
}
