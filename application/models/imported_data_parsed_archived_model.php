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

    function saveToArchive($imported_data_id, $without=null) {
    	$query = "insert into `".$this->tables['imported_data_parsed_archived']."` (`imported_data_id`, `key`, `value`, `model`, `revision`)
			select `imported_data_id`, `key`, `value`, `model`, `revision` from `".$this->tables['imported_data_parsed']."` where imported_data_id = ".$imported_data_id;

    	if (isset($without)) {
			$query .= " and revision<>".$without;
    	}

        return $this->db->query($query);
    }

}

