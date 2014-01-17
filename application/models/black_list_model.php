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
}