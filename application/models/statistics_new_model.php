<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Statistics_new_model extends CI_Model {

    var $tables = array(
        'statistics' => 'statistics',
        'statistics_new' => 'statistics_new',
        'research_data' => 'research_data',
        'crawler_list' => 'crawler_list',
        'imported_data_parsed' => 'imported_data_parsed',
        
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

//     function delete_rows_db () {
//        $query = "SELECT * FROM (SELECT id,url,MAX(imported_data_id) as max_imported_data_id, count(id) as c FROM crawler_list GROUP by url) as t WHERE c>1";
// 		$res = $this->db->query($query);
//                $value = $res->result_array();
//               
//                foreach($value as $val){
//                    $v = (int)$val['max_imported_data_id'];
//                    $query_del_c = "delete from crawler_list where `url` LIKE '".$val['url']."' or `imported_data_id` = null and `imported_data_id` < ".$v."";                   
//                    
//                    $res_imp_c = $this->db->query($query_del_c);
//                    }
//     
//                }
//  function delete_rows_db_imp () {
//        $query = "SELECT  `value` , MAX( imported_data_id )as max_imported_data_id , COUNT(  `id` ) AS c FROM  `imported_data_parsed` WHERE  `key` =  'URL' GROUP BY  `value` HAVING c >1";
// 		$res = $this->db->query($query);
//                $value = $res->result_array();
//            foreach($value as $val){
//                  $v = (int)$val['max_imported_data_id'];
//                    $query_del_i = "delete from imported_data_parsed where `value` LIKE '".$val['value']."' and `imported_data_id` < ".$v." or `imported_data_id` = null ";
//                    $res_imp_i = $this->db->query($query_del_i);
//     
//            } 
//        }   
            
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
        
        $this->imported_data_id = $imported_data_id;
        
        $this->db->insert('statistics_new', $this);
        return $this->db->insert_id();
        

    }


    function insert_updated( $imported_data_id, $revision,
                         $short_description_wc, $long_description_wc,
                         $short_seo_phrases, $long_seo_phrases,
                         $own_price, $price_diff, $competitors_prices, $items_priced_higher_than_competitors, $similar_products_competitors,
                         $research_data_id, $batch_id){
/* old script        
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
        
        $this->db->where('imported_data_id', $imported_data_id);
        $query= $this->db->get("statistics_new");
 //*/
        //new script
        $idata['revision'] = $revision;
        $idata['short_description_wc'] = (string)$short_description_wc;
        $idata['long_description_wc'] = (string)$long_description_wc;
        $idata['short_seo_phrases'] = (string)$short_seo_phrases;
        $idata['long_seo_phrases'] = (string)$long_seo_phrases;
        $idata['created'] = date('Y-m-d h:i:s');
        $idata['own_price'] = (string)$own_price;
        $idata['price_diff'] = (string)$price_diff;
        $idata['competitors_prices'] = (string)$competitors_prices;
        $idata['items_priced_higher_than_competitors'] = $items_priced_higher_than_competitors;
        $idata['similar_products_competitors'] = $similar_products_competitors;
        if($research_data_id){
            $idata['research_data_id'] = $research_data_id;
        }
//        if($research_data_id){
//            $idata['research_data_id'] = "'".$research_data_id."',";
//            $q_research_data_id = '`research_data_id`,';
//        }
//        else{
//            $idata['research_data_id'] = '';
//            $q_research_data_id = '';
//        }
        $idata['batch_id'] = $batch_id;
        
        $this->db->where('imported_data_id', $imported_data_id);
        $query= $this->db->get("statistics_new");
        
        if($query->num_rows()>0){
         $row = $query->first_row();
           $this->db->where('id', $row->id);
           $this->db->update('statistics_new', $idata);
        }else{
        
        $idata['imported_data_id'] = $imported_data_id;
        

        $this->db->insert('statistics_new', $idata);
        
//        $sql = "INSERT INTO `statistics_new` 
//(`revision`, `short_description_wc`, `long_description_wc`, `short_seo_phrases`, 
//`long_seo_phrases`, `created`, `own_price`, `price_diff`, `competitors_prices`, 
//`items_priced_higher_than_competitors`, `similar_products_competitors`,". 
//$q_research_data_id." `batch_id`, `imported_data_id`) 
//VALUES 
//('".$idata['revision']."','".$idata['short_description_wc']."','".$idata['long_description_wc']."'
//    ,'".$idata['short_seo_phrases']."','".$idata['long_seo_phrases']."','".$idata['created']."'
//        ,'".$idata['own_price']."','".$idata['price_diff']."','".$idata['competitors_prices']."'
//            ,'".$idata['items_priced_higher_than_competitors']."','".$idata['similar_products_competitors']."'
//                ,".$idata['research_data_id']."'".$idata['batch_id']."','".$idata['imported_data_id']."')";
//        $this->db->query($sql);
        return $this->db->insert_id();
        }

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
            
    
    function get_compare_item($imported_data_id){
        $query = $this->db
            ->select('s.imported_data_id,s.long_description_wc,s.short_description_wc, cl.snap, cl.snap_date, cl.snap_state,
            (select `value` from imported_data_parsed where `key`="Product Name" and `imported_data_id` = `s`.`imported_data_id` limit 1) as `product_name`,
            (select `value` from imported_data_parsed where `key`="parsed_attributes" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `parsed_attributes`,
            (select `value` from imported_data_parsed where `key`="parsed_meta" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `parsed_meta`,
            (select `value` from imported_data_parsed where `key`="Description" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `Short_Description`,
            (select `value` from imported_data_parsed where `key`="Long_Description" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `Long_Description`,
            
            (select `value` from imported_data_parsed where `key`="Url" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `url`
            ')
            ->from($this->tables['statistics_new'].' as s')
            ->join($this->tables['crawler_list'].' as cl', 'cl.imported_data_id = s.imported_data_id', 'left')
            ->where('s.imported_data_id', $imported_data_id)->get();
        $result =  $query->row();
        return $result;
    }
    
    
    
    function getStatsData($params)
    {
        if(empty($params->batch_id)){
            $batch_id = '';
        } else {
            $batch_id = $params->batch_id;
        }
        if(empty($params->txt_filter)){
            $txt_filter_part1 = '';
            $txt_filter_part2 = '';
        } else {
            $txt_filter_part1 = 'select * from (';
            $txt_filter_part2 = ')  as `data` where `data`.`product_name` like "%'.$params->txt_filter.'%"';

        }
        $limit=isset($params->iDisplayLength)&&$params->iDisplayLength!=0?"LIMIT $params->iDisplayStart, $params->iDisplayLength":"";
        if(isset($params->id)){
            $txt_filter_part2 = ' AND  '.(int)$params->id.' < `s`.`id` AND `s`.`id` < '.((int)$params->id+4).' AND `cl`.`snap` != "" ';
        } else if(isset($params->snap_count)) {
            $txt_filter_part2 = ' AND `cl`.`snap` != "" LIMIT 0,'.$params->snap_count.' ';
        }
////////////////////////////////////////////////
//        $bapslc = $build_assess_params->short_less_check?
//                " and short_description_wc<=$build_assess_params->short_less_check":"";
//                if ($build_assess_params->short_less_check && $result_row->short_description_wc > $build_assess_params->short_less) {
//                    continue;
//                }
//        $bapsmc = $build_assess_params->short_more_check?
//                " and short_description_wc=>$build_assess_params->short_more_check":"";
//                if ($build_assess_params->short_more_check && $result_row->short_description_wc < $build_assess_params->short_more) {
//                    continue;
//                }
//        $bapllc = $build_assess_params->long_less_check?
//                " and long_description_wc <= $build_assess_params->long_less":"";
//                if ($build_assess_params->long_less_check && $result_row->long_description_wc > $build_assess_params->long_less) {
//                    continue;
//                }
//        $baplmc = $build_assess_params->long_more_check?
//                " and long_description_wc => $build_assess_params->long_more":"";
//                if ($build_assess_params->long_more_check && $result_row->long_description_wc < $build_assess_params->long_more) {
//                    continue;
//                }
        /*

            $recomend = false;
            $flagged = '';
            if($build_assess_params->flagged){
                $sdwldw = "";
                if($build_assess_params->long_less_check || $build_assess_params->long_more_check){
                    $sdwldw = "or short_description_wc <= $build_assess_params->short_less or ".
                            "long_description_wc <= $build_assess_params->long_less";
                }
                $sphars = "short_seo_phrases == 'None' and long_seo_phrases == 'None'";
                $flagged = "($sphars $sdwldw)";
            }
//            if (($result_row->short_description_wc <= $build_assess_params->short_less ||
//                    $result_row->long_description_wc <= $build_assess_params->long_less) 
//                    && ($build_assess_params->long_less_check || $build_assess_params->long_more_check)
//            ) {
//                $recomend = true;
//            }
//            if ($result_row->short_seo_phrases == 'None' && $result_row->long_seo_phrases == 'None') {
//                $recomend = true;
//            }
            if ($result_row->lower_price_exist == true && !empty($result_row->competitors_prices)) {
                if (min($result_row->competitors_prices) < $result_row->own_price) {
                    $recomend = true;
                }
            }

            if ($build_assess_params->flagged == true && $recomend == false) {
                continue;
            }
            //*/
        $query = $this->db->query($txt_filter_part1 . 'select `s`.*, `cl`.`snap`, `cl`.`snap_date`, `cl`.`snap_state`,
            (select `value` from imported_data_parsed where `key`="Product Name" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `product_name`,
            (select `value` from imported_data_parsed where `key`="Description" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `short_description`,
            (select `value` from imported_data_parsed where `key`="Long_Description" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `long_description`,
            (select `value` from imported_data_parsed where `key`="URL" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `url`,
            (select `value` from imported_data_parsed where `key`="HTags" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `htags`,
            (select `value` from imported_data_parsed where `key`="parsed_attributes" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `parsed_attributes`
            
            from '.$this->tables['statistics_new'].' as `s` left join '.$this->tables['crawler_list'].' as `cl` on `cl`.`imported_data_id` = `s`.`imported_data_id` where `s`.`batch_id`='.$batch_id.$txt_filter_part2);
        $result =  $query->result();
        return $result;
    }

    function delete_by_research_data_id($batch_id, $research_data_id){
        return $this->db->delete(
            $this->tables['statistics_new'],
            array(
                'batch_id' => $batch_id,
                'research_data_id' => $research_data_id
            )
        );
    }

    public function updateStatsData($arr){
        $str = "";
        foreach($arr as $key => $val){
            if($key != "batch_id" && $key != "url"){
                $str .= " ".$key." = '".$val."', ";
            }
        }
        $str = substr($str, 0, -2);
        $result = $this->db->query("
            UPDATE
                `statistics_new`
            SET ".$str."
            WHERE
                `batch_id`='{$arr["batch_id"]}' and
                `url`='{$arr["url"]}'
            ");
        return $result;
    }
}
