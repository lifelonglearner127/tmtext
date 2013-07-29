<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Research_data_model extends CI_Model {

    var $batch_id  = 0;
    var $user_id = 0;
    var $url = '';
    var $product_name = '';
    var $keyword1 = '';
    var $keyword2 = '';
    var $keyword3 = '';
    var $meta_name = '';
    var $meta_description = '';
    var $meta_keywords = '';
    var $short_description = '';
    var $long_description = '';
    var $priority = '';
    var $status = '';
    var $created = '';
    var $modified = '';


    var $tables = array(
        'research_data' => 'research_data',
        'batches' => 'batches',
        'users' => 'users',
        'items' => 'items',
        'imported_data_parsed'=>'imported_data_parsed',
        'imported_data'=>'imported_data'
        
    );

    function __construct()
    {
        parent::__construct();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['research_data']);

        return $query->result();
    }
    function get_by_id($id){//max
         $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['research_data']);

        return $query->row_array();
    }
    //Max
    function get_by_batch_id($batch_title){
        
        $query0=$this->db->where('title', $batch_title)
              ->get('batches');
         $res0= $query0->row_array();
        $batch_id=$res0['id'];
    //Max
        $query1 = $this->db->where('batch_id', $batch_id)
              ->get($this->tables['research_data']);
        
        $res= $query1->result_array();
        $urls=array();
        foreach($res as $val){
            $urls[]=$val['url'];
        }
        if(count($urls)>0){
        $this->db->select('p.imported_data_id, p.key, p.value')
            ->from($this->tables['imported_data_parsed'].' as p')
            ->join($this->tables['imported_data'].' as i', 'i.id = p.imported_data_id', 'left')
            ->where('p.key', 'URL')
           ->where_in('p.value', $urls);
        $query = $this->db->get();
        $results = $query->result();
        
        $data = array();
        foreach($results as $result){
            $query = $this->db->where('imported_data_id', $result->imported_data_id)->get($this->tables['imported_data_parsed']);
            $res = $query->result_array();
            $description = '';
            $long_description = '';
            $url = '';
            foreach($res as $val){
                if($val['key'] == 'URL'){ $url = $val['value']; }
                if($val['key'] == 'Description'){ $description = $val['value']; }
                if($val['key'] == 'Long_Description'){ $long_description = $val['value']; }

	            if($val['key'] == 'Product Name') { $product_name = $val['value']; }
            	if($val['key'] == 'Features') { $features = $val['value']; }

            }
            array_push($data, array('imported_data_id'=>$result->imported_data_id, 'product_name'=>$result->value,
               'description'=>$description, 'long_description'=>$long_description, 'url'=>$url, 'product_name' =>$product_name, 'features' => $features ));
        }
        return $data;
        }else{
            return NULL;
        }
        
        
        
   }
  //Max
    function insert($batch_id, $url, $product_name, $keyword1, $keyword2, $keyword3, $meta_name,
                    $meta_description, $meta_keywords, $short_description, $short_description_wc, $long_description, $long_description_wc, $revision = 1)
    {
        $CI =& get_instance();
        $this->batch_id = $batch_id;
        $this->user_id = $CI->ion_auth->get_user_id();
        $this->url = $url;
        $this->product_name = $product_name;
        $this->keyword1 = $keyword1;
        $this->keyword2 = $keyword2;
        $this->keyword3 = $keyword3;
        $this->meta_name = $meta_name;
        $this->meta_description = $meta_description ;
        $this->meta_keywords = $meta_keywords;
        $this->short_description = $short_description;
        $this->short_description_wc = $short_description_wc;
        $this->long_description = $long_description;
        $this->long_description_wc = $long_description_wc;
        $this->revision = $revision;
        $this->priority = 50;
        $this->status = 'created';
        $this->created = date('Y-m-d h:i:s');
        $this->modified = date('Y-m-d h:i:s');
        $this->db->insert($this->tables['research_data'], $this);
        return $this->db->insert_id();
    }

   function update($id, $batch_id, $url, $product_name, $short_description, $short_description_wc, $long_description, $long_description_wc, $keyword1='', $keyword2='', $keyword3='', $meta_name='',
                    $meta_description='', $meta_keywords='', $revision='')
    {
        $CI =& get_instance();
        $this->batch_id = $batch_id;
        $this->user_id = $CI->ion_auth->get_user_id();
        $this->url = $url;
        $this->product_name = $product_name;
        $this->keyword1 = $keyword1;
        $this->keyword2 = $keyword2;
        $this->keyword3 = $keyword3;
        $this->meta_name = $meta_name;
        $this->meta_description = $meta_description;
        $this->meta_keywords = $meta_keywords;
        $this->short_description = $short_description;
        $this->short_description_wc = $short_description_wc;
        $this->long_description = $long_description;
        $this->long_description_wc = $long_description_wc;
        $this->priority = 50;
        $this->status = 'edited';
        $this->revision = $revision;
        $this->modified = date('Y-m-d h:i:s');

        unset($this->created);

        $result = $this->db->update($this->tables['research_data'],
            $this,
            array('id' => $id));

        return $result;
    }

    function getAllByProductName( $product_name, $batch_id='')
    {
        if($batch_id == '') {
            $query = $this->db->where('product_name', $product_name)->limit(1)->get($this->tables['research_data']);
        } else {
            $query = $this->db->where('product_name', $product_name)->where('batch_id', $batch_id)
                ->limit(1)
                ->get($this->tables['research_data']);
        }

        return $query->result();
    }

    function getProductByURL($url, $batch_id) {
        $url = $url;
        $batch_id = intval($batch_id);
        $query = $this->db->where('url', $url)->where('batch_id', $batch_id)
            ->limit(1)
            ->get($this->tables['research_data']);
        return $query->result();
    }

   function getInfoFromResearchData($text, $batch_id)
   {
        $batch_first_str = "";
        $batch_second_str = "";
        if($batch_id != ''){
            $batch_first_str = " `rd`.`batch_id`= ". $batch_id ." and ";
            $batch_second_str = " `i`.`batch_id`= ". $batch_id ." and ";
        }

        $query = $this->db->query("(SELECT `rd`.`id`, `rd`.`batch_id`, `rd`.`url`,`rd`.`product_name`, `rd`.`keyword1`, `rd`.`keyword2`, `rd`.`keyword3`, `rd`.`meta_name`,`rd`.`meta_description`, `rd`.`meta_keywords`, `rd`.`short_description`, `rd`.`short_description_wc`, `rd`.`long_description`, `rd`.`long_description_wc`,
        `rd`.`status`,
        `u`.`email` as `user_id`,
        `b`.`title` as `batch_name`
     FROM ".$this->tables['research_data']." as `rd`
        left join ".$this->tables['batches']." as `b` on `rd`.`batch_id` = `b`.`id`
        left join ".$this->tables['users']." as `u` on `rd`.`user_id` = `u`.`id`
        where ". $batch_first_str." concat(`rd`.`url`, `rd`.`product_name`, `rd`.`keyword1`, `rd`.`keyword2`, `rd`.`keyword3`, `rd`.`meta_name`,
        `rd`.`meta_description`, `rd`.`meta_keywords`, `rd`.`short_description`, `rd`.`short_description_wc`,
        `rd`.`long_description`, `rd`.`long_description_wc`) like '%".$text."%')
union all
    (SELECT `i`.`id`, `i`.`batch_id`, `i`.`url`,`i`.`product_name`, `i`.`keyword1`, `i`.`keyword2`, `i`.`keyword3`, `i`.`meta_name`,`i`.`meta_description`, `i`.`meta_keywords`, `i`.`short_description`, `i`.`short_description_wc`, `i`.`long_description`, `i`.`long_description_wc`,
        `i`.`status`,
        `u`.`email` as `user_id`,
        `b`.`title` as `batch_name`
     FROM ".$this->tables['items']." as `i`
        left join ".$this->tables['batches']." as `b` on `i`.`batch_id` = `b`.`id`
        left join ".$this->tables['users']." as `u` on `i`.`user_id` = `u`.`id`
        where ".$batch_second_str." concat(`i`.`url`, `i`.`product_name`, `i`.`keyword1`, `i`.`keyword2`, `i`.`keyword3`, `i`.`meta_name`,
        `i`.`meta_description`, `i`.`meta_keywords`, `i`.`short_description`, `i`.`short_description_wc`,
        `i`.`long_description`, `i`.`long_description_wc`) like '%".$text."%')");

        return $query->result();
    }

    function getInfoForAssess($params)
    {
        $batch_name = $this->db->escape($params->batch_name);
//        $date_from = $params->date_from == '' ? '' : $this->db->escape($params->date_from);
//        $date_to = $params->date_to == '' ? '' : $this->db->escape($params->date_to);
        $txt_filter = $this->db->escape('%'.$params->txt_filter.'%');
//
//        $date_from = date_parse($date_from);
//        $date_to = date_parse($date_to);
//        if ($date_from['year'] > 0 & $date_from['month'] > 0 & $date_from['day'] > 0 & $date_to['year'] > 0 & $date_to['month'] > 0 & $date_to['day'] > 0) {
//            $d_from = $this->db->escape($date_from['year'].'-'.$date_from['month'].'-'.$date_from['day']);
//            $d_to = $this->db->escape($date_to['year'].'-'.$date_to['month'].'-'.$date_to['day']);
//            $date_filter = ' and rd.created>='.$d_from.' and rd.created<='.$d_to;
//        }

//        $count_sorting_cols = intval($this->input->get('iSortingCols', TRUE));
//        if($count_sorting_cols > 0) {
//            $columns_name_string = $this->input->get('sColumns', TRUE);
//            $sort_col_n = intval($this->input->get('iSortCol_0', TRUE));
//            $sort_direction_n = $this->input->get('sSortDir_0', TRUE);
//            $columns_names = explode(",", $columns_name_string);
//            if(!empty($columns_names[$sort_col_n]) && !empty($sort_direction_n)) {
//                $order_column_name = $columns_names[$sort_col_n];
//            }
//        }

        $sql_cmd = "
            SELECT
                r.id AS id,
	            r.imported_data_id AS imported_data_id,
                r.created AS created,
                group_concat(r.product_name, '') AS product_name,
                group_concat(r.url, '') AS url,
                group_concat(r.short_description, '') AS short_description,
                group_concat(r.long_description, '') AS long_description,
                group_concat(r.short_description_wc, '') AS short_description_wc,
                group_concat(r.long_description_wc, '') AS long_description_wc,
                group_concat(r.seo_s, '') AS seo_s,
                group_concat(r.seo_l, '') AS seo_l
            FROM (
                SELECT
                    kv.id,
		            kv.imported_data_id,
                    rd.created as created,
                    case when kv.`key` = 'Product Name' then kv.`value` end as product_name,
                    case when kv.`key` = 'URL' then kv.`value` end as url,
                    case when kv.`key` = 'Description' then kv.`value` end as short_description,
                    case when kv.`key` = 'Long_Description' then kv.`value` end as long_description,
                    case when kv.`key` = 'Description_WC' then kv.`value` end as short_description_wc,
                    case when kv.`key` = 'Long_Description_WC' then kv.`value` end as long_description_wc,
                    case when kv.`key` = 'seo_s' then kv.`value` end as seo_s,
                    case when kv.`key` = 'seo_l' then kv.`value` end as seo_l
                FROM
                    research_data AS rd
                INNER JOIN batches AS b ON
                    b.id = rd.batch_Id
                    AND b.title = $batch_name
                INNER JOIN imported_data_parsed AS idp ON
                    idp.value = rd.url
                    AND `key` = 'URL'
                INNER JOIN imported_data_parsed AS kv ON
                    kv.imported_data_id = idp.imported_data_id
                    AND kv.`value` like $txt_filter
            ) AS r
            GROUP BY
                r.imported_data_id
        ";

//        if(!empty($order_column_name)) {
//            $sql_cmd = $sql_cmd." order by $order_column_name $sort_direction_n";
//        }

        $query = $this->db->query($sql_cmd);
        $result =  $query->result();

        return $result;
    }

    function getLastRevision(){
        $query = $this->db->select('revision')->limit(1)->order_by("id", "desc")->get($this->tables['research_data']);
        return $query->result();
    }

    function getAllByBatchId($batch_id){
        $query = $this->db->where('batch_id', $batch_id)->limit(1)->order_by("modified", "desc")->get($this->tables['research_data']);
        return $query->result();
    }

    public function countAll($batch_id)
    {
        $this->db->select('id')->from($this->tables['research_data'])
            ->where('batch_id', $batch_id);

        return $this->db->count_all_results();
    }

    public function getLastAddedDateItem($batch_id)
    {
        $query = $this->db->where('batch_id', $batch_id)->limit(1)->get($this->tables['research_data']);
        return $query->result();
    }


    public function updateItem($id, $product_name, $url, $short_description, $long_description, $short_description_wc = 0, $long_description_wc = 0) {
        $data = array(
            'product_name' => $product_name,
            'url' => $url,
            'short_description' => $short_description,
            'long_description' => $long_description,
            'short_description_wc' => $short_description_wc,
            'long_description_wc' => $long_description_wc,
        );

        $this->db->update( 'research_data', $data, array( 'id' => $id ) );
    }

    function delete($id)
    {
        return $this->db->delete($this->tables['research_data'], array('id' => $id));
    }

    public function checkItemUrl($batch_id, $url){
        $query = $this->db->where('url', $url)->where('batch_id', $batch_id)
            ->limit(1)
            ->get($this->tables['research_data']);

        return $query->result();
    }

}