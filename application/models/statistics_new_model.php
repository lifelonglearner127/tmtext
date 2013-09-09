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

    function insert( $imported_data_id, $revision,
                         $short_description_wc, $long_description_wc,
                         $short_seo_phrases, $long_seo_phrases,
                         $own_price, $price_diff, $competitors_prices, $items_priced_higher_than_competitors, $similar_products_competitors,
                         $research_data_id, $batch_id){

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
        $this->research_data_id = $research_data_id;
        $this->batch_id = $batch_id;

        $this->db->insert('statistics_new', $this);
        return $this->db->insert_id();

    }

    function getResearchDataAndBatchIds($imported_data_id) {
		//  SELECT research_data_id, batch_id FROM `crawler_list` as cl
		//	JOIN `research_data_to_crawler_list` as rdc ON (cl.id = rdc.crawler_list_id)
		//	JOIN `research_data` as rd ON (rdc.research_data_id = rd.id)
		//	JOIN `batches` as b ON (b.id = rd.batch_id)
		//	WHERE cl.imported_data_id = 20

		$query = $this->db
            ->select('research_data_id, batch_id')
            ->from('crawler_list as cl')
            ->join('research_data_to_crawler_list as rdc', 'cl.id = rdc.crawler_list_id')
            ->join('research_data as rd', 'rdc.research_data_id = rd.id')
            ->join('batches as b', 'b.id = rd.batch_id')
            ->where('cl.imported_data_id', $imported_data_id)
            ->limit(1)
            ->get();

        $result =  $query->result();
        return $result;

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
            ->select('s.*, cl.snap, cl.snap_date, cl.snap_state,
            (select `value` from imported_data_parsed where `key`="Product Name" and `imported_data_id` = `s`.`imported_data_id` and `revision`=`s`.`revision` limit 1) as `product_name`,
            (select `value` from imported_data_parsed where `key`="Url" and `imported_data_id` = `s`.`imported_data_id` and `revision`=`s`.`revision` limit 1) as `url`
            ')
            ->from($this->tables['statistics_new'].' as s')
            ->join($this->tables['crawler_list'].' as cl', 'cl.imported_data_id = s.imported_data_id', 'left')
            ->where('s.batch_id', $batch_id)->get();
        $result =  $query->result();
        return $result;
    }


}
