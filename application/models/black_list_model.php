<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Black_list_model extends CI_Model {

    var $tables = array(
        'black_list' => 'black_list',
    );

    function __construct()
    {
        parent::__construct();
    }
    function insert($im_id_1, $im_id_2){
        $query = $this->db->where('im_id_1', $im_id_1)
                ->or_where('im_id_2', $im_id_1)
                ->or_where('im_id_1', $im_id_2)
                ->or_where('im_id_2', $im_id_2)
            ->limit(1)
            ->get($this->tables['black_list']);

        if($query->num_rows()== 0){
            $data = array(
                'im_id_1' => $im_id_1,
                'im_id_2' => $im_id_2
            );
            $this->db->insert($this->tables['black_list'],$data);
        }
    }
    function create_csv(){
        $sql = "SELECT idp1.`value` AS url1, idp2.`value` AS url2
                FROM black_list AS bl
                INNER JOIN imported_data_parsed AS idp1 ON bl.im_id_1 = idp1.imported_data_id
                AND idp1.`key` =  'url'
                INNER JOIN imported_data_parsed AS idp2 ON bl.im_id_2 = idp2.imported_data_id
                AND idp2.`key` =  'url'";
        $query = $this->db->query($sql);
        $results = $query->result_array();
        return $results;
    }
    
     function bad_matches_data($search, $iDisplayStart , $iDisplayLength,$sEcho) {
        $sql = "SELECT count(*) as cnt from black_list";
        $q = $this->db->query($sql);
        $res= $q->row_array();
        $items_count = $res['cnt'];
        $sql = "SELECT idp1.`value` AS url1, idp2.`value` AS url2, idp1.`imported_data_id` AS im_id_1, idp2.`imported_data_id` AS im_id_2
                FROM black_list AS bl
                INNER JOIN imported_data_parsed AS idp1 ON bl.im_id_1 = idp1.imported_data_id
                AND idp1.`key` =  'url'
                INNER JOIN imported_data_parsed AS idp2 ON bl.im_id_2 = idp2.imported_data_id
                AND idp2.`key` = 'url'";
        if($search){
           $sql .= " and (idp1.`value` like   '%".$search."%' or idp2.`value` like   '%".$search."%')";
                }
        $sql .= " LIMIT $iDisplayLength OFFSET  $iDisplayStart";
        $query = $this->db->query($sql);
        $results = $query->result_array();
        $data = array();
        foreach($results as $val){
            $delUrl = base_url('/index.php/system/delete_unmatching_couple/'.$val['im_id_1'].'/'.$val['im_id_2']);
            $action =  '<div id="'.$val['im_id_1'].'"><a class="deleteBtn  icon-remove ml_5" data-id1="'.$val['im_id_1'].'"  data-id2="'.$val['im_id_2'].'"style="float:left;" href="' .  $delUrl  . '"></a></div>';
            $data[]= array($val['url2'],  $val['url1'] ,  $action);
        }
        
        $result = array(
            "sEcho" => (int)$sEcho,
            "iTotalRecords" =>  (int)$items_count ,
            "iTotalDisplayRecords" =>  (int)$items_count,
            "aaData" => $data
        );
        return $result;
    }
    function delete($id1, $id2){
        $sql = "delete from black_list where (im_id_1 = $id1 and im_id_2 = $id2) or (im_id_1 = $id2 and im_id_2 = $id1)";
        $this->db->query($sql);
        echo  "ok";
    }
}