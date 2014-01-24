<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Statistics_new_model extends CI_Model {

    var $tables = array(
        'statistics' => 'statistics',
        'statistics_new' => 'statistics_new',
        'research_data' => 'research_data',
        'crawler_list' => 'crawler_list',
        'imported_data_parsed' => 'imported_data_parsed',
        'imported_data_parsed_archived' => 'imported_data_parsed_archived',
        'meta_kw_rank_source' => 'meta_kw_rank_source',
        'crawler_list_prices' => 'crawler_list_prices'
    );
    protected $res_array;

    function __construct()
    {
        parent::__construct();
    }
    
    function delete($im_id)
    {
        return $this->db->delete($this->tables['statistics_new'], array('imported_data_id' => $im_id));
    
    }
    function get_size_of_batch($batch_id){
        $this->db->select('count(*) as cnt');
        $this->db->from('statistics_new');
        $this->db->where('batch_id',$batch_id);
        $size = $this->db->get()->first_row();
        return $size->cnt;
    }
    function get_crawler_price_by_url_model($url) {
        $res_object = array(
            'status' => false,
            'msg' => '',
            'data' => null
        );
        $check_obj_cl = array(
            'url' => $url
        );
        $query_cl = $this->db->where($check_obj_cl)->limit(1)->get($this->tables['crawler_list']);
        $query_cl_res = $query_cl->result();
        if(count($query_cl_res) > 0) {
            $cl_object = $query_cl_res[0];
            $crawler_list_id = $cl_object->id;
            $check_obj_clp = array(
                'crawler_list_id' => $crawler_list_id
            );
            $query_clp = $this->db->where($check_obj_clp)->limit(1)->get($this->tables['crawler_list_prices']);
            $query_clp_res = $query_clp->result();
            if(count($query_clp_res) > 0) {
                $clp_object = $query_clp_res[0];
                $res_object['status'] = true;
                $res_object['msg'] = 'OK';
                $res_object['data'] = $clp_object;
            } else {
                $res_object['msg'] = 'Crawler List Prices Object Not Found';
            }
        } else {
            $res_object['msg'] = 'Crawler List Object Not Found';
        }
        return $res_object;
    }

    // === META KEYWORDS RANKING STUFFS (START)
    function get_keyword_source_by_id($id) {
        $res_object = array(
            'status' => false,
            'res' => array()
        );
        $check_obj = array(
            'id' => $id
        );
        $query = $this->db->where($check_obj)->limit(1)->get($this->tables['meta_kw_rank_source']);
        $query_res = $query->result();
        if(count($query_res) > 0) {
            $res_object['status'] = true;
            $res_object['res'] = $query_res[0];
        }
        return $res_object;
    }
    function delete_keyword_kw_source($id) {
        return $this->db->delete(
            $this->tables['meta_kw_rank_source'],
            array(
                'id' => $id
            )
        );
    }
    function check_keyword_kw_source($id, $batch_id, $kw) {
        $res_object = array(
            'status' => false,
            'last_id' => 0
        );
        $check_obj = array(
            'statistics_new_id' => $id,
            'batch_id' => $batch_id,
            'kw' => $kw
        );
        $query = $this->db->where($check_obj)->limit(1)->get($this->tables['meta_kw_rank_source']);
        $query_res = $query->result();
        if(count($query_res) > 0) {
            $res_object['status'] = true;
            $res_object['last_id'] = $query_res[0]->id;
        }
        return $res_object;
    }
    function add_keyword_kw_source($statistics_new_id, $batch_id, $kw, $kw_prc, $kw_count, $url, $imported_data_id) {
        $res = array(
            'status' => false,
            'msg' => '',
            'last_id' => 0
        );
        $check_obj = array(
            'statistics_new_id' => $statistics_new_id,
            'batch_id' => $batch_id,
            'kw' => $kw
        );
        $query = $this->db->where($check_obj)->limit(1)->get($this->tables['meta_kw_rank_source']);
        $query_res = $query->result();
        if(count($query_res) > 0) {
            $res['msg'] = 'Already exists';
        } else {
            $insert_object = array(
                'url' => $url,
                'batch_id' => $batch_id,
                'statistics_new_id' => $statistics_new_id,
                'kw' => $kw,
                'kw_prc' => $kw_prc,
                'kw_count' => $kw_count,
                'stamp' => date("Y-m-d H:i:s"),
                'imported_data_id' => $imported_data_id
            );
            $this->db->insert($this->tables['meta_kw_rank_source'], $insert_object);
            $res['msg'] = 'OK';
            $res['status'] = true;
            $res['last_id'] = $this->db->insert_id();
        }
        return $res;
    }
    // === META KEYWORDS RANKING STUFFS (END)

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
        $st_time = microtime(TRUE);
        $this->load->model('research_data_model');
        $params = new stdClass();
        $this->db->select('count(*) as cnt ');
        $this->db->from('statistics_new');
        $this->db->where('batch_id',$batch_id);
        $query = $this->db->get();
        $res = $query->first_row('array');
        $num_rows = $res['cnt'];
        /*
        $params->batch_id = $batch_id;
        $params->txt_filter = '';
        $res = $this->getStatsData($params);
        $num_rows = count($res);//*/
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
                         $title_keywords,
                         $own_price, $price_diff, $competitors_prices, $items_priced_higher_than_competitors, $similar_products_competitors,
                         $research_and_batch_ids,$manufacturerInfo){

        $idata['revision'] = $revision;
        $idata['short_description_wc'] = (string)$short_description_wc;
        $idata['long_description_wc'] = (string)$long_description_wc;
        $idata['title_keywords'] = (string)$title_keywords;
        $idata['created'] = date('Y-m-d h:i:s');
        $idata['own_price'] = (string)$own_price;
        $idata['price_diff'] = (string)$price_diff;
        $idata['competitors_prices'] = (string)$competitors_prices;
        $idata['items_priced_higher_than_competitors'] = $items_priced_higher_than_competitors;
        $idata['similar_products_competitors'] = $similar_products_competitors;
        $idata['manufacturer_info'] = $manufacturerInfo;
       
        foreach($research_and_batch_ids as $research_and_batch_id){
		$idata['batch_id'] = $research_and_batch_id['batch_id'];
		$idata['research_data_id'] = $research_and_batch_id['research_data_id']; 
		$idata['category_id'] = $research_and_batch_id['category_id']; 
		$this->db->where('imported_data_id', $imported_data_id)->where('batch_id', $research_and_batch_id['batch_id']);
		$query= $this->db->get("statistics_new");    
		if($query->num_rows()>0){
		   $this->db->where('imported_data_id', $imported_data_id);
		   $this->db->update('statistics_new', $idata);
		}else{
		   $idata['imported_data_id'] = $imported_data_id;
		   $this->db->insert('statistics_new', $idata);
		} 
        }
        
        
        
//        if($research_and_batch_ids){
//            $idata['research_data_id'] = $research_data_id;
//        }
//
//        $idata['batch_id'] = $batch_id;
//        
//        $this->db->where('imported_data_id', $imported_data_id);
//        $query= $this->db->get("statistics_new");
//        
//        if($query->num_rows()>0){
//         $row = $query->first_row();
//           $this->db->where('id', $row->id);
//           $this->db->update('statistics_new', $idata);
//        }else{
//        
//        $idata['imported_data_id'] = $imported_data_id;
//        $this->db->insert('statistics_new', $idata);
//        return $this->db->insert_id();
//        }

    }

    function getResearchDataAndBatchIds($imported_data_id) {
	    $result = array();
		//  SELECT research_data_id, batch_id FROM `crawler_list` as cl
		//	JOIN `research_data_to_crawler_list` as rdc ON (cl.id = rdc.crawler_list_id)
		//	JOIN `research_data` as rd ON (rdc.research_data_id = rd.id)
		//	JOIN `batches` as b ON (b.id = rd.batch_id)
		//	WHERE cl.imported_data_id = 20
               
        $query = $this->db
            ->select('research_data_id, batch_id, rd.category_id')
            ->from('crawler_list as cl')
            ->join('research_data_to_crawler_list as rdc', 'cl.id = rdc.crawler_list_id')
            ->join('research_data as rd', 'rdc.research_data_id = rd.id')
            ->join('batches as b', 'b.id = rd.batch_id')
            ->where('cl.imported_data_id', $imported_data_id)
           // ->limit(1)
            ->get();
	if ($query->num_rows() > 0)
	{    
		 $result = $query->result_array();
	}
	$query->free_result();
        return $result;

    }
            
    
    function get_compare_item($imported_data_id){
	$result = array();    
        $query = $this->db
            ->select('s.imported_data_id,s.long_description_wc,s.short_description_wc, cl.snap, cl.snap_date, cl.snap_state, s.title_keywords,
            (select `value` from imported_data_parsed where `key`="Product Name" and `imported_data_id` = `s`.`imported_data_id` limit 1) as `product_name`,
            (select `value` from imported_data_parsed where `key`="parsed_attributes" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `parsed_attributes`,
            (select `value` from imported_data_parsed where `key`="parsed_meta" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `parsed_meta`,
            (select `value` from imported_data_parsed where `key`="Date" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `Date`,
            (select `value` from imported_data_parsed where `key`="Description" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `Short_Description`,
            (select `value` from imported_data_parsed where `key`="Long_Description" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `Long_Description`,
            (select `value` from imported_data_parsed where `key`="HTags" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `HTags`,
            (select `value` from imported_data_parsed where `key`="Anchors" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `Anchors`,
            (select `value` from imported_data_parsed where `key`="Url" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `url`
            ')
            ->from($this->tables['statistics_new'].' as s')
            ->join($this->tables['crawler_list'].' as cl', 'cl.imported_data_id = s.imported_data_id', 'left')
            ->where('s.imported_data_id', $imported_data_id)->get();
	if($query->num_rows > 0)
	{	
		$result = $query->row();
	}	
	$query->free_result();
        return $result;
    }

    function getStatsDataPure($bid) {
        $sql = 'select `s`.*, `cl`.`snap`, `cl`.`snap_date`, `cl`.`snap_state`,
            (select `value` from imported_data_parsed where `key`="Product Name" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `product_name`,
            (select `value` from imported_data_parsed where `key`="Description" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `short_description`,
            (select `value` from imported_data_parsed where `key`="Long_Description" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `long_description`,
            (select `value` from imported_data_parsed where `key`="URL" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `url`,
            (select `value` from imported_data_parsed where `key`="HTags" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `htags`,
            (select `value` from imported_data_parsed where `key`="parsed_attributes" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `parsed_attributes`,
            (select `value` from imported_data_parsed where `key`="parsed_meta" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `parsed_meta`
            from '.$this->tables['statistics_new'].' as `s` left join '.$this->tables['crawler_list'].' as `cl` on `cl`.`imported_data_id` = `s`.`imported_data_id` where `s`.`batch_id`='.$bid;
        $query = $this->db->query($sql);
        $result = $query->result();
        return $result;
    }
    
    // function getStatsDataPure($bid, $limit, $skip) {
    //     $cf = " LIMIT $skip, $limit";
    //     $cf = "";
    //     $sql = 'select `s`.*, `cl`.`snap`, `cl`.`snap_date`, `cl`.`snap_state`,
    //         (select `value` from imported_data_parsed where `key`="Product Name" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `product_name`,
    //         (select `value` from imported_data_parsed where `key`="Description" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `short_description`,
    //         (select `value` from imported_data_parsed where `key`="Long_Description" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `long_description`,
    //         (select `value` from imported_data_parsed where `key`="URL" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `url`,
    //         (select `value` from imported_data_parsed where `key`="HTags" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `htags`,
    //         (select `value` from imported_data_parsed where `key`="parsed_attributes" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `parsed_attributes`
    //         from '.$this->tables['statistics_new'].' as `s` left join '.$this->tables['crawler_list'].' as `cl` on `cl`.`imported_data_id` = `s`.`imported_data_id` where `s`.`batch_id`='.$bid.$cf;
    //     $query = $this->db->query($sql);
    //     $result = $query->result();
    //     return $result;
    // }
    
	/**
	 * Check imported_data_parsed and imported_data_parsed_archived tables, get how many records were inserted in many dates, calculates the average of records inserted and returns the first 6 dates above the average
	 *
	 * @access	public
	 * @return	array
	 */
	function get_trendline_dates($batch_id)
	{
		if( ! is_numeric($batch_id))
		{
			return FALSE;
		}

		$imported_data_dates = $this->db->query("SELECT `imported_data_parsed`.`key`, SUBSTRING(`imported_data_parsed`.`value`, 1, 10) AS trendline_date, COUNT(*) AS crawled_items FROM statistics_new, `imported_data_parsed` , imported_data WHERE imported_data.id = imported_data_parsed.imported_data_id AND imported_data.id = statistics_new.imported_data_id AND `imported_data_parsed`.`key` = 'Date' AND batch_id = $batch_id GROUP BY trendline_date ORDER BY trendline_date DESC")->result_array();

		$imported_data_archived_dates = $this->db->query("SELECT `imported_data_parsed_archived`.`key`, SUBSTRING(`imported_data_parsed_archived`.`value`, 1, 10) AS trendline_date, COUNT(*) AS crawled_items FROM statistics_new, `imported_data_parsed_archived` , imported_data WHERE imported_data.id = imported_data_parsed_archived.imported_data_id AND imported_data.id = statistics_new.imported_data_id AND `imported_data_parsed_archived`.`key` = 'Date' AND batch_id = 123 GROUP BY trendline_date ORDER BY trendline_date DESC LIMIT 0, 20")->result_array();

		$all_dates = array();

		foreach($imported_data_dates as $imported_data_date)
		{
			$all_dates[$imported_data_date["trendline_date"]] = $imported_data_date;
		}

		foreach($imported_data_archived_dates as $imported_data_archived_date)
		{
			$all_dates[$imported_data_date["trendline_date"]] = $imported_data_archived_date;
		}

		$highest_value = 0;
		$sum = 0;

		foreach($all_dates as $date)
		{
			if($date["crawled_items"] > $highest_value)
			{
				$highest_value = $date["crawled_items"];
			}

			$sum += $date["crawled_items"];
		}

		$average_value = $sum / count($all_dates);

		$return_dates = array();

		foreach($all_dates as $date)
		{
			if(($date["crawled_items"] > $average_value && count($return_dates) < 6) || count($all_dates) < 6)
			{
				$return_dates[] = $date["trendline_date"];
			}
		}

		return $return_dates;
	}

	/**
	 * get the value of the items crawled in every date
	 *
	 * @access	private
	 * @param	int
	 * @param	string
	 * @param	array
	 * @return	array
	 */
	function getStatsData_trendlines($imported_data_id, $graphBuild) {   
		switch ($graphBuild) {
			case 'short_description_wc':
			$key = 'description';
			break;
	
			case 'long_description_wc':
			$key = 'long_description';
			break;
			
			case 'total_description_wc':
			$key = 'long_description';
			$key1 = 'description';
			break;
			
			case 'revision':
			$key = 'parsed_attributes';
			break;
		
			case 'Features':
			$key = 'parsed_attributes';
			break;
		
			case 'h1_word_counts':
			$key = 'HTags';
			break;
		
			case 'h2_word_counts':
			$key = 'HTags';
			break;
			
		}
		
		// Castro: search crawled_items in imported_data_parsed as imported_data_parsed_archived

		$tables_to_search = array('imported_data_parsed', 'imported_data_parsed_archived');

		$result = $result_key = array();
		
		foreach ($tables_to_search as $table_to_search) {
			$sql='SELECT ';
			$sql.=" idpa1.`value` as '".$key."',idpa.`value` as `date`";
			$sql.=' FROM `' . $table_to_search . '` as idpa';
			$sql.=" left join `" . $table_to_search . "` as idpa1 on idpa.`imported_data_id`  = idpa1.`imported_data_id` and idpa.`revision`=idpa1.`revision`";
			$sql.=" WHERE idpa1.`key` = '".$key."' and idpa.`key` = 'date' and idpa.`imported_data_id`=".$imported_data_id;
			$sql.=' GROUP BY SUBSTRING(`idpa`.`value`, 1, 10) ORDER BY SUBSTRING(`idpa`.`value`, 1, 10) DESC LIMIT 15';
//echo "\r\n".$sql."\r\n";
//echo "\r\n".microtime()."\r\n";
			$query = $this->db->query($sql);
//echo "\r\n".microtime()."\r\n";
			$temp_result = $query->result();

			foreach($temp_result as $this_result) {
				$result[] = $this_result;
			}
			
			if ($key1 !='') {
				$sql_key='SELECT ';
				$sql_key.=" idpa1.`value` as '".$key1."',idpa.`value` as `date`";
				$sql_key.=' FROM `' . $table_to_search . '` as idpa';
				$sql_key.=" left join `" . $table_to_search . "` as idpa1 on idpa.`imported_data_id`  = idpa1.`imported_data_id` and idpa.`revision`=idpa1.`revision`";
				$sql_key.=" WHERE idpa1.`key` = '".$key1."' and idpa.`key` = 'date' and idpa.`imported_data_id`=".$imported_data_id;
				$sql_key.=' GROUP BY SUBSTRING(`idpa`.`value`, 1, 10) ORDER BY SUBSTRING(`idpa`.`value`, 1, 15) DESC LIMIT 10';
				
				$query_key = $this->db->query($sql_key);
				$temp_result_key = $query_key->result();

				foreach($temp_result_key as $this_result_key) {
					$result_key[] = $this_result_key;
				}
			}
		}

		if((count($result) !=0) && (count($result_key) !=0)) {
			$res = array();
			foreach($result_key as $res_k) {
				foreach($result as $k) {
					if($k->date == $res_k->date) {
						$res[] = array('date'=>$res_k->date,'long_description'=>$k->long_description,'description'=>$res_k->description);break;
					}
				}
			}
			
			return (object) $res;
		} else if ((count($result_key) !=0) && (count($result) == 0)) {
			return $result_key;
		} else {
			return $result;
		}
	}
    
    function getStatsData_min_max($imported_data_id,$graphBuild)
    {   
        switch ($graphBuild) {
            case 'short_description_wc':
            $key = 'description';
            break;
    
            case 'long_description_wc':
            $key = 'long_description';
            break;
            
            case 'total_description_wc':
            $key = 'long_description';
            $key1 = 'description';
            break;
            
            case 'revision':
            $key = 'parsed_attributes';
            break;
        
            case 'Features':
            $key = 'parsed_attributes';
            break;
        
            case 'h1_word_counts':
            $key = 'HTags';
            break;
        
            case 'h2_word_counts':
            $key = 'HTags';
            break;
            
        }
        

        $sql='SELECT ';
        $sql.=" idpa1.`value` as '".$key."',idpa.`value` as `date`";
        $sql.=' FROM `imported_data_parsed_archived` as idpa';
        $sql.=" left join `imported_data_parsed_archived` as idpa1 on idpa.`imported_data_id`  = idpa1.`imported_data_id` and idpa.`revision`=idpa1.`revision` and idpa1.`key` = '".$key."'";
        $sql.=" WHERE idpa1.`key` = '".$key."' and idpa.`key` = 'date' and idpa.`imported_data_id`=".$imported_data_id;
        $sql.=' ORDER BY idpa.`revision` DESC LIMIT 5';

        $query = $this->db->query($sql);
        $result = $query->result();
        
        if($key1 !=''){
            $sql_key='SELECT ';
            $sql_key.=" idpa1.`value` as '".$key1."',idpa.`value` as `date`";
            $sql_key.=' FROM `imported_data_parsed_archived` as idpa';
            $sql_key.=" left join `imported_data_parsed_archived` as idpa1 on idpa.`imported_data_id`  = idpa1.`imported_data_id` and idpa.`revision`=idpa1.`revision` and idpa1.`key` = '".$key1."'";
            $sql_key.=" WHERE idpa1.`key` = '".$key1."' and idpa.`key` = 'date' and idpa.`imported_data_id`=".$imported_data_id;
            $sql_key.=' ORDER BY idpa.`revision` DESC LIMIT 5';
            
            $query_key = $this->db->query($sql_key);
            $result_key = $query_key->result();
        
            
       
        }
            
        if((count($result) !=0) && (count($result_key) !=0)){
            $res = array();
            foreach($result_key as $res_k){
                foreach($result as $k){
                    if($k->date == $res_k->date){
                        $res[] = array('date'=>$res_k->date,'long_description'=>$k->long_description,'description'=>$res_k->description);break;
                    }
                }
            }
            
           return (object) $res;
        }elseif((count($result_key) !=0) && (count($result) == 0)){
           return $result_key;
        }else{
        return $result;
    }
           
 
    }
    function getStatsData($params)
    {
//        $st_time = microtime(TRUE);
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
            $txt_filter_part2 = ')  as `data` where `data`.`imported_data_id` like \'%'.trim($this->db->escape($params->txt_filter),"'").'%\'';

        }
	if(isset($params->category_id) && intval($params->category_id) > 0)
	{
		$category = ' AND s.category_id = '.$params->category_id;
	}	
		
        $limit = isset($params->iDisplayLength) && $params->iDisplayLength != 0 ? "LIMIT $params->iDisplayStart, $params->iDisplayLength" : '';
		
        if(isset($params->id)){
            $txt_filter_part2 = ' AND  '.(int)$params->id.' < `s`.`id` AND `s`.`id` < '.((int)$params->id+4).' AND `cl`.`snap` != "" ';
        } else if(isset($params->snap_count)) {
            $txt_filter_part2 = ' AND `cl`.`snap` != "" AND LIMIT 0,'.$params->snap_count.' ';
        }
		else if(isset($params->halfResults)) // Castro: check if I have to show only half of results created for get_graph_data
		{
			$halfResults_int = 300;

			if($params->halfResults == 0) 
			{
				$txt_filter_part2 = ' LIMIT 0, '.$halfResults_int; // returns first 300 results, 300 fits in chart
			}
			else
			{
				$txt_filter_part2 = ' LIMIT '.$halfResults_int .', 18446744073709551615' ; // returns the rest
// 				$txt_filter_part2 = ' LIMIT '.$halfResults_int .', '.$halfResults_int ;
			}
		} 		
	
            $sql = $txt_filter_part1 . 'select `s`.*, `cl`.`snap`, `cl`.`snap_date`, `cl`.`snap_state`,
            (select `value` from imported_data_parsed where `key`="Product Name" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `product_name`,
            (select `value` from imported_data_parsed where `key`="Description" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `short_description`,
            (select `value` from imported_data_parsed where `key`="Long_Description" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `long_description`,
            (select `value` from imported_data_parsed where `key`="Date" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `Date`,
            (select `value` from imported_data_parsed where `key`="URL" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `url`,
            (select `value` from imported_data_parsed where `key`="HTags" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `htags`,
            (select `value` from imported_data_parsed where `key`="parsed_attributes" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `parsed_attributes`,
            (select `value` from imported_data_parsed where `key`="Anchors" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `Anchors`
            
            from '.$this->tables['statistics_new'].' as `s` left join '.$this->tables['crawler_list'].' as `cl` on `cl`.`imported_data_id` = `s`.`imported_data_id` where `s`.`batch_id`='.$batch_id.$txt_filter_part2.$category;
	    
            $query = $this->db->query($sql);
        
            $result = $query->result();
            $query->free_result();
        return $result;   
    }
//    function get_price_from_crawler_list($crawler_list_id){
//        $result = $this->db->query('select price from crawler_list_prices as clp
//            inner join 
//            (select crawler_list_id as cli, max(revision) as mr 
//            from crawler_list_prices group by crawler_list_id) as clp_mr
//            on clp.crawler_list_id = clp_mr.cli and clp.revision = clp_mr.mr 
//            where clp.crawler_list_id = '.$crawler_list_id);
//        
//    }
    function delete_by_research_data_id($batch_id, $research_data_id){
        return $this->db->delete(
            $this->tables['statistics_new'],
            array(
                'batch_id' => $batch_id,
                'research_data_id' => $research_data_id
            )
        );
    }

    
function if_url_in_batch($imported_data_id, $batch_id){
       
        $this->db->where('imported_data_id', $imported_data_id)->where('batch_id', $batch_id);
        $query= $this->db->get("statistics_new");    
        if($query->num_rows()>0){
         return true;
        }
        return false;
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
    
    public function update_similar_products_competitors($imp_id, $cmp_imp_id){
        $this->db->where('imported_data_id', $imp_id);
        $query= $this->db->get("statistics_new");
        $res = $query->row_array();
        $cmps = unserialize($res['similar_products_competitors']);
        foreach($cmps as $k => $v){
            if($v['imported_data_id'] == $cmp_imp_id){
                unset($cmps[$k]);
            }
        }
         $cmps = serialize( $cmps);   
        $data = array(
                        'similar_products_competitors' => $cmps,
                     );
        $this->db->where('imported_data_id', $imp_id);
        $this->db->update('statistics_new', $data); 
    }
        }
