<?php

if (!defined('BASEPATH'))
    exit('No direct script access allowed');

class Imported_data_parsed_archived_model extends CI_Model {

    var $imported_data_id = null;
    var $key = '';
    var $value = '';
    var $revision = 1;
    var $model = null;

    var $tables = array(
        'imported_data_parsed' => 'imported_data_parsed',
    	'imported_data_parsed_archived' => 'imported_data_parsed_archived',
        'imported_data' => 'imported_data'
    );

    function __construct() {
        parent::__construct();
    }
    
    function get($id) {
        $query = $this->db->where('id', $id)
                ->limit(1)
                ->get($this->tables['imported_data_parsed_archived']);

        return $query->result();
    }
    function duplicate_revisions_count(){
        $sql = "SELECT COUNT( * ) as count
                FROM (
                SELECT  `imported_data_id` ,  `key` ,  `revision` , COUNT(  `id` ) AS cnt, MIN( id ) AS min_id
                FROM  `imported_data_parsed_archived` 
                GROUP BY  `imported_data_id` ,  `key` ,  `revision` 
                HAVING cnt >1
                ) AS tt";
       $query = $this->db->query($sql);
       $res= $query->row_array();
        
       return $res['count'];
    }
    
    function mark_queued_from_archive_count(){
        $sql = "SELECT COUNT( * ) AS count
                FROM (
                SELECT idpa.imported_data_id AS itemid
                FROM imported_data_parsed_archived AS idpa
                LEFT JOIN imported_data_parsed AS idp ON idpa.imported_data_id = idp.imported_data_id
                INNER JOIN crawler_list AS cl ON idpa.imported_data_id = cl.imported_data_id
                INNER JOIN research_data_to_crawler_list AS rdcl ON rdcl.crawler_list_id = cl.id
                INNER JOIN research_data AS rd ON rd.id = rdcl.research_data_id
                INNER JOIN batches AS b ON b.id = rd.batch_id
                WHERE idp.imported_data_id IS NULL 
                AND rd.batch_id IS NOT NULL 
                GROUP BY idpa.imported_data_id
                ) AS tt";
        $query = $this->db->query($sql);
        $res= $query->row_array();
        
        return $res['count'];
    }
    function delete_duplicate_revisions(){
       $sql = "select `imported_data_id`,`key`, `revision`, count(`id`) as cnt, min(id) as min_id
                From imported_data_parsed_archived
                Group By `imported_data_id` ,`key`, `revision`
                having cnt > 1" ;
       $query = $this->db->query($sql);
       $results = $query->result_array();
       
       foreach($results as $k => $res){
            $this->db->where('id', $res['min_id']);
            $this->db->delete($this->tables['imported_data_parsed_archived']);
       }
       
    }
    function saveToArchive($imported_data_id, $without=null) {
    	$query = "insert into `".$this->tables['imported_data_parsed_archived']."` (`imported_data_id`, `key`, `value`, `model`, `revision`)
			select `imported_data_id`, `key`, `value`, `model`, `revision` from `".$this->tables['imported_data_parsed']."` where imported_data_id = ".$imported_data_id;

    	if (isset($without)) {
			$query .= " and revision<>".$without;
    	}

        return $this->db->query($query);
    }
    function mark_queued_from_archive(){
         $sql = "select idpa.imported_data_id as itemid from imported_data_parsed_archived as idpa
                left join imported_data_parsed as idp on idpa.imported_data_id = idp.imported_data_id
                inner join crawler_list as cl on idpa.imported_data_id = cl.imported_data_id
                inner join research_data_to_crawler_list as rdcl on rdcl.crawler_list_id=cl.id
                inner join research_data as rd on rd.id = rdcl.research_data_id
                inner join batches as b on b.id = rd.batch_id
                where idp.imported_data_id is null and rd.batch_id is not null
                group by idpa.imported_data_id";
        $query = $this->db->query($sql);
        $results = $query->result_array();
        foreach($results as $res ){
            $this->db->update('crawler_list', array('status' => 'queued'), array('imported_data_id' => $res['itemid']));
        }
    }

}

