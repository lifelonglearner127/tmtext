<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Crawler_List_Prices_model extends CI_Model {

    var $tables = array(
    	'crawler_list_prices'               => 'crawler_list_prices',
        'crawler_list'                      => 'crawler_list',
        'imported_data_parsed'              => 'imported_data_parsed',
    );

    var $price = 0;
    var $crawler_list_id = 0;
    var $created = '';

    function __construct()
    {
        parent::__construct();
    }

    function get($id)
    {
    	$query = $this->db->where('id', $id)
                    ->limit(1)
                    ->get($this->tables['crawler_list_prices']);

        return $query->result();
    }

    function getByCrawlerListId($id)
    {
    	$query = $this->db->where('crawler_list_id', $id)
                    ->get($this->tables['crawler_list_prices']);

        return $query->result();
    }

    function getAll()
    {
        $query = $this->db->order_by('created', 'asc')->get($this->tables['crawler_list_prices']);

        return $query->result();
    }

    function insert($crawler_list_id, $price) {

    	$this->crawler_list_id = $crawler_list_id;
    	$this->price = $price;
        $this->created = date('Y-m-d h:i:s');

        $this->db->insert($this->tables['crawler_list_prices'], $this);
        return $this->db->insert_id();
    }

    function get_products_with_price() {
        // get params
        $search = $this->input->get('sSearch', TRUE);
        $count_sorting_cols = intval($this->input->get('iSortingCols', TRUE));

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

        // set query limit
        $display_start = intval($this->input->get('iDisplayStart', TRUE));
        // Let's make sure we don't have bad data coming in. Let's protect the SQL
        if (empty($display_start)) {
            $display_start = 0;
        }

        $display_length = intval($this->input->get('iDisplayLength', TRUE));

        // get total rows for this query
        $total_rows = $this->get_product_price_total_rows();

        // Once again, protecting the SQL, as well as making sure we don't go over the limit
        if (empty($display_length)) {
            $display_length  = $total_rows - $display_start;
        }

        $this->db->select('clp.id, clp.created, idp3.value as url, idp2.value as parsed_attributes, idp.value as product_name, clp.price ')
            ->join($this->tables['crawler_list'].' as cl', 'clp.crawler_list_id = cl.id')
            ->join($this->tables['imported_data_parsed']. ' as idp', 'idp.imported_data_id = cl.imported_data_id')
            ->join($this->tables['imported_data_parsed']. ' as idp2', 'idp2.imported_data_id = cl.imported_data_id AND idp2.key = "parsed_attributes"', 'left')
            ->join($this->tables['imported_data_parsed']. ' as idp3', 'idp3.imported_data_id = cl.imported_data_id AND idp3.key = "URL"', 'left')
            ->where('idp.key = "Product Name"');
        if(!empty($search)) {
            $this->db->where('idp.value like ' . $this->db->escape('%' . $search . '%'));
        }
        if(!empty($order_column_name)) {
            $this->db->order_by($order_column_name, $sort_direction_n);
        }
        if(isset($display_start) && isset($display_length)) {
            $this->db->limit($display_length, $display_start);
        }
        $query = $this->db->get($this->tables['crawler_list_prices'].' as clp');

        $result_array = array(
            'result'                => $query->result(),
            'total_rows'            => $total_rows,
            'display_length'        => $display_length,
        );
        return $result_array;
    }

    function get_product_price_total_rows() {
        // get params
        $search = $this->input->get('sSearch', TRUE);

        $this->db->select('clp.id')
            ->join($this->tables['crawler_list'].' as cl', 'clp.crawler_list_id = cl.id')
            ->join($this->tables['imported_data_parsed']. ' as idp', 'idp.imported_data_id = cl.imported_data_id')
            ->where('idp.key = "Product Name"');
        if(!empty($search)) {
            $this->db->where('idp.value like ' . $this->db->escape('%' . $search . '%'));
        }
        $query = $this->db->get($this->tables['crawler_list_prices'].' as clp');
        $total_rows = $query->num_rows();
        return $total_rows;
    }

}
