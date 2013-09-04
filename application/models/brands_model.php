<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Brands_model extends CI_Model {

    var $name = '';
    var $created = '';
    var $company_id = 0;
    var $brand_type = 0;
    
    var $tables = array(
        'brands' => 'brands',
        'companies' => 'companies',
        'brand_data' => 'brand_data',
        'brand_data_summary' => 'brand_data_summary',
        'brand_types' => 'brand_types',
    );

    function __construct()
    {
        parent::__construct();
    }

    function getAll()
    {
        $this->db->order_by("name", "asc");
        $query = $this->db->get($this->tables['brands']);

        return $query->result();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['brands']);

        return $query->result();
    }
    
    function getByName($name)
    {
        $query = $this->db->query("SELECT * FROM ".$this->tables['brands']." WHERE name = ?", array($name));

        return $query->row();
    }
    
    function insert($name, $company_id=0, $brand_type=0, $created=0)
    {
        $this->name = $name;
        $this->company_id = $company_id;
        $this->brand_type = $brand_type;
        $this->created = date('Y-m-d h:i:s');

        $this->db->insert($this->tables['brands'], $this);
        return $this->db->insert_id();
    }

    function update($id, $name, $company_id=0, $brand_type=0, $created)
    {
        $this->name = $name;
        $this->company_id = $company_id;
        $this->brand_type = $brand_type;
        $this->created = $created;

    	return $this->db->update($this->tables['brands'],
                $this,
                array('id' => $id));
    }

    function delete($id)
    {
        return $this->db->delete($this->tables['brands'], array('id' => $id));
    }
    
    function rankings()
    {
        // get params
        $search = $this->input->get('sSearch', TRUE);
        $count_sorting_cols = intval($this->input->get('iSortingCols', TRUE));
        
        // get filters (brand type, month, year)
        $sSearch = $this->input->get('sSearch_1', null);
        if($sSearch == '') return array('display_length' => 0);
        
        $sSearch = explode(',', $sSearch);
        $brand_type = $sSearch[0];
        $month = $sSearch[1];
        $year = $sSearch[2];
        $date = $year.'-'.$month;

        // Now just get one column for sort order. If need more columns need TODO: processing iSortCol_(int) and iSortDir_(int)
        if($count_sorting_cols > 0) {
            $columns_name_string = $this->input->get('sColumns', TRUE);
            $sort_col_n = intval($this->input->get('iSortCol_0', TRUE));
            $sort_direction_n = $this->input->get('sSortDir_0', TRUE);
            $columns_names = explode(",", $columns_name_string);
            if(!empty($columns_names[$sort_col_n]) && !empty($sort_direction_n)) {
                $order_column_name = $columns_names[$sort_col_n];
            }
        }
                 
        $columns = 'SQL_CALC_FOUND_ROWS b.*, b.name, bt.IR500Rank, SUM(bd.tweet_count) AS tweets, SUM(bd.twitter_followers) AS followers, SUM(bd.following) AS following, ';
        $columns .= 'SUM(bd.youtube_video_count) AS videos, SUM(bd.youtube_view_count) AS views, ';
        $columns .= 'bds.total_tweets, bds.total_youtube_videos, bds.total_youtube_views ';
        $this->db->select($columns, FALSE)
            ->join($this->tables['brand_types'].' as bt', 'b.brand_type = bt.id', 'inner')
            ->join($this->tables['brand_data']. ' as bd', 'b.id = bd.brand_id', 'inner')
            ->join($this->tables['brand_data_summary']. ' as bds', 'b.id = bds.brand_id', 'inner')
            ->group_by("b.id");

        $this->db->distinct();
        
        $this->db->where('bd.date LIKE '.$this->db->escape($date . '%'));
        $this->db->where('b.brand_type = '.$brand_type);
        
        if(!empty($search)) {
            $this->db->where('b.name like ' . $this->db->escape('%' . $search . '%'));
        }
        if(!empty($order_column_name)) {
            //$this->db->order_by($order_column_name, $sort_direction_n);
        }
        
        // set query limit
        $display_start = intval($this->input->get('iDisplayStart', TRUE));
        $display_length = intval($this->input->get('iDisplayLength', TRUE));
        // Let's make sure we don't have bad data coming in. Let's protect the SQL
        if (empty($display_start)) {
            $display_start = 0;
        }
        
        if(isset($display_start) && isset($display_length)) {
            $this->db->limit($display_length, $display_start);
        }
        
        $query = $this->db->get($this->tables['brands'].' as b');
//        echo $this->db->last_query(); exit;
        $results = $query->result();
        
        // get total rows for this query
        $this->db->select('FOUND_ROWS() AS num_rows', FALSE);
        $res = $this->db->get();
        $total_rows = $res->row()->num_rows;

        // Once again, protecting the SQL, as well as making sure we don't go over the limit
        if (empty($display_length)) {
            $display_length  = $total_rows - $display_start;
        }

        $result_array = array(
            'result'                => $results,
            'total_rows'            => $total_rows,
            'display_length'        => $display_length,
        );
        return $result_array;
    }

}