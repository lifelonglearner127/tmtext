<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Imported_data_parsed_model extends CI_Model {

	var $imported_data_id = null;
	var $key = '';
	var $value = '';

    var $tables = array(
    	'imported_data_parsed' => 'imported_data_parsed',
        'imported_data' => 'imported_data',
        'customers' => 'customers',
        'products_compare' => 'products_compare'
    );

    function __construct() {
        parent::__construct();
    }

    function get($id) {
    	$query = $this->db->where('id', $id)
                  ->limit(1)
                  ->get($this->tables['imported_data_parsed']);

        return $query->result();
    }

    function getSameProductsHuman($sid) {
        $this->db->where('rate', 2);
        $this->db->where('im_pr_f', $sid);
        $this->db->or_where('im_pr_s', $sid);
        $query = $this->db->get($this->tables['products_compare']);
        $results = $query->result(); 
        $ids = array();
        if(count($results) > 0) {
            foreach ($results as $key => $value) {
                $ids[] = $value->im_pr_f;
                $ids[] = $value->im_pr_s;
            }
            $ids = array_unique($ids);
            $d_key = null;
            foreach ($ids as $k => $v) {
                if($v == $sid) {
                    $d_key = $k;
                    break;
                } 
            }
            if($d_key !== null) unset($ids[$d_key]);
            if(count($ids) > 3) $ids = array_slice($ids, 0, 3); 
        }
        $template = array();
        if(count($ids) === 3) {
            // ---- get customers list (start)
            $customers_list = array();
            $query_cus = $this->db->order_by('name', 'asc')->get($this->tables['customers']);
            $query_cus_res = $query_cus->result();
            if(count($query_cus_res) > 0) {
                foreach ($query_cus_res as $key => $value) {
                    $n = strtolower($value->name);
                    $customers_list[] = $n;
                }
            }
            $customers_list = array_unique($customers_list);
            // ---- get customers list (end)
            if(count($ids) > 0) {
                foreach ($ids as $k => $v) {
                    $template[$v] = array('url' => '', 'product_name' => '', 'description' => '', 'long_description' => '', 'customer' => '', 'seo' => array('short' => array(), 'long' => array()));
                }
                $this->db->select('imported_data_id, key, value');
                $this->db->where_in('imported_data_id', $ids);
                $query = $this->db->get($this->tables['imported_data_parsed']);
                $results = $query->result();
                if(count($results) > 0) {
                    foreach ($results as $key => $value) {
                        $im_id_current = $value->imported_data_id;
                        if($value->key == 'URL') {
                            $template[$im_id_current]['url'] = $value->value;
                            $cus_val = "";
                            foreach ($customers_list as $ki => $vi) {
                                if(strpos($value->value, "$vi") !== false) {
                                    $cus_val  = $vi;
                                }
                            }
                            if($cus_val !== "") $template[$im_id_current]['customer'] = $cus_val;
                        }
                        if($value->key == 'Product Name') {
                            $template[$im_id_current]['product_name'] = $value->value;   
                        }
                        if($value->key == 'Description') {
                            $template[$im_id_current]['description'] = $value->value;
                        }
                        if($value->key == 'Long_Description') {
                            $template[$im_id_current]['long_description'] = $value->value;
                        }
                    }
                }
            }
        }
        return $template;
    }

    function deleteProductsVotedPair($id) {
        return $this->db->delete($this->tables['products_compare'], array('id' => $id)); 
    }

    function getProductsCompareVotedTotalCount() {
        return $this->db->count_all_results($this->tables['products_compare']);
    }

    function getProductsCompareVoted($page, $items_per_page) {
        $position = $items_per_page*($page-1);
        // ---- get customers list (start)
        $customers_list = array();
        $query_cus = $this->db->order_by('name', 'asc')->get($this->tables['customers']);
        $query_cus_res = $query_cus->result();
        if(count($query_cus_res) > 0) {
            foreach ($query_cus_res as $key => $value) {
                $n = strtolower($value->name);
                $customers_list[] = $n;
            }
        }
        $customers_list = array_unique($customers_list);
        // ---- get customers list (end)
        // $query_voted = $this->db->order_by('stamp', 'desc')->get($this->tables['products_compare']);
        $query_voted = $this->db->order_by('stamp', 'desc')->limit($items_per_page, $position)->get($this->tables['products_compare']);
        $query_voted_res = $query_voted->result();
        $res_stack = array();
        if(count($query_voted_res) > 0) {
            foreach ($query_voted_res as $k => $v) {
                $md = array(
                    'id' => $v->id,
                    'im_pr_f' => $v->im_pr_f,
                    'im_pr_s' => $v->im_pr_s,
                    'rate' => $v->rate,
                    'stamp' => $v->stamp,
                    'products_data' => array(
                        "$v->im_pr_f" => array(),
                        "$v->im_pr_s" => array()
                    )
                );
                // ----- get product details (start)
                // --- get first
                $this->db->select('imported_data_id, key, value');
                $this->db->where('imported_data_id', $v->im_pr_f);
                $query = $this->db->get($this->tables['imported_data_parsed']);
                $results = $query->result();
                $data_f = array('url' => '', 'product_name' => '', 'description' => '', 'long_description' => '', 'customer' => '');
                foreach($results as $result) {
                    if($result->key === 'URL') {
                        $data_f['url'] = $result->value;
                        $cus_val = "";
                        foreach ($customers_list as $ki => $vi) {
                            if(strpos($result->value, "$vi") !== false) {
                                $cus_val  = $vi;
                            }
                        }
                        if($cus_val !== "") $data_f['customer'] = $cus_val;
                    }
                    if($result->key === 'Product Name') {
                        $data_f['product_name'] = $result->value;
                    }
                    if($result->key === 'Description') {
                        $data_f['description'] = $result->value;
                    }
                    if($result->key === 'Long_Description') {
                        $data_f['long_description'] = $result->value;
                    }
                }
                if(count($data_f) > 0) {
                    $md['products_data']["$v->im_pr_f"] = $data_f;
                }
                // --- get second
                $this->db->select('imported_data_id, key, value');
                $this->db->where('imported_data_id', $v->im_pr_s);
                $query = $this->db->get($this->tables['imported_data_parsed']);
                $results = $query->result();
                $data_s = array('url' => '', 'product_name' => '', 'description' => '', 'long_description' => '', 'customer' => '');
                foreach($results as $result) {
                    if($result->key === 'URL') {
                        $data_s['url'] = $result->value;
                        $cus_val = "";
                        foreach ($customers_list as $ki => $vi) {
                            if(strpos($result->value, "$vi") !== false) {
                                $cus_val  = $vi;
                            }
                        }
                        if($cus_val !== "") $data_s['customer'] = $cus_val;
                    }
                    if($result->key === 'Product Name') {
                        $data_s['product_name'] = $result->value;
                    }
                    if($result->key === 'Description') {
                        $data_s['description'] = $result->value;
                    }
                    if($result->key === 'Long_Description') {
                        $data_s['long_description'] = $result->value;
                    }
                }
                if(count($data_s) > 0) {
                    $md['products_data']["$v->im_pr_s"] = $data_s;
                }
                // ----- get product details (end)
                $res_stack[] = $md;
            }
        }
        return $res_stack;
    }

    function voteCompareProducts($ids, $dec) {
        $st = 1; // 1 - insert, 2 - update
        $check_query = $this->db->get_where($this->tables['products_compare'], array('im_pr_f' => $ids[0], 'im_pr_s' => $ids[1]));
        $check_query_res = $check_query->result();
        if(count($check_query_res) > 0) {
            $st = 2;
        }
        $change_status = false;
        if($st === 1) { // insert
            $insert_object = array(
                'im_pr_f' => $ids[0],
                'im_pr_s' => $ids[1],
                'rate' => $dec,
                'stamp' => date("Y-m-d H:i:s")
            );
            $this->db->insert($this->tables['products_compare'], $insert_object);
            $insert_id = $this->db->insert_id();
            if($insert_id > 0) $change_status = true;
        } else if($st === 2) { // update
            $update_object = array(
                'rate' => $dec
            );
            $res = $this->db->update($this->tables['products_compare'], $update_object, array('im_pr_f' => $ids[0], 'im_pr_s' => $ids[1]));
            if($res) $change_status = true;
        }
        return $change_status;
    }

    function getProductsByIdStack($ids) {
        // ---- get customers list (start)
        $customers_list = array();
        $query_cus = $this->db->order_by('name', 'asc')->get($this->tables['customers']);
        $query_cus_res = $query_cus->result();
        if(count($query_cus_res) > 0) {
            foreach ($query_cus_res as $key => $value) {
                $n = strtolower($value->name);
                $customers_list[] = $n;
            }
        }
        $customers_list = array_unique($customers_list);
        // ---- get customers list (end)
        $template = array();
        if(count($ids) > 0) {
            foreach ($ids as $k => $v) {
                $template[$v] = array('url' => '', 'product_name' => '', 'description' => '', 'long_description' => '', 'customer' => '');
            }
            $this->db->select('imported_data_id, key, value');
            $this->db->where_in('imported_data_id', $ids);
            $query = $this->db->get($this->tables['imported_data_parsed']);
            $results = $query->result();
            if(count($results) > 0) {
                foreach ($results as $key => $value) {
                    $im_id_current = $value->imported_data_id;
                    if($value->key == 'URL') {
                        $template[$im_id_current]['url'] = $value->value;
                        $cus_val = "";
                        foreach ($customers_list as $ki => $vi) {
                            if(strpos($value->value, "$vi") !== false) {
                                $cus_val  = $vi;
                            }
                        }
                        if($cus_val !== "") $template[$im_id_current]['customer'] = $cus_val;
                    }
                    if($value->key == 'Product Name') {
                        $template[$im_id_current]['product_name'] = $value->value;   
                    }
                    if($value->key == 'Description') {
                        $template[$im_id_current]['description'] = $value->value;
                    }
                    if($value->key == 'Long_Description') {
                        $template[$im_id_current]['long_description'] = $value->value;
                    }
                }
            }
        }
        return $template;
    }

    function getAllProducts() {

        $this->db->select('imported_data_id, key, value');
        // $this->db->group_by('imported_data_id');
        $query = $this->db->get($this->tables['imported_data_parsed']);
        $results = $query->result();
        $ids = array();
        if(count($results) > 0) {
            foreach ($results as $key => $value) {  
                $ids[] = $value->imported_data_id;
            }
        }
        $ids = array_unique($ids);
        foreach ($ids as $k => $v) {
            $template[$v] = array('url' => '', 'product_name' => '', 'description' => '', 'long_description' => '');
        }


        $this->db->select('imported_data_id, key, value');
        $this->db->group_by(array('imported_data_id', 'key'));
        $query = $this->db->get($this->tables['imported_data_parsed']);
        $results = $query->result();
        if(count($results) > 0) {
            foreach ($results as $key => $value) {
                $im_id_current = $value->imported_data_id;
                if($value->key == 'URL') {
                    $template[$im_id_current]['url'] = $value->value;
                }
                if($value->key == 'Product Name') {
                    $template[$im_id_current]['product_name'] = $value->value;   
                }
                if($value->key == 'Description') {
                    $template[$im_id_current]['description'] = $value->value;
                }
                if($value->key == 'Long_Description') {
                    $template[$im_id_current]['long_description'] = $value->value;
                }
            }
        }
        return $template;
    }

    function getByImId($im_data_id) {
        $f_res = array();
        $this->db->select('imported_data_id, key, value');
        $this->db->where('imported_data_id', $im_data_id);
        $query = $this->db->get($this->tables['imported_data_parsed']);
        $results = $query->result();
        $data = array('url' => '', 'product_name' => '', 'description' => '', 'long_description' => '');
        foreach($results as $result) {
            if($result->key === 'URL') {
                $data['url'] = $result->value;
            }
            if($result->key === 'Product Name') {
                $data['product_name'] = $result->value;
            }
            if($result->key === 'Description') {
                $data['description'] = $result->value;
            }
            if($result->key === 'Long_Description') {
                $data['long_description'] = $result->value;
            }
        }
        if(count($data) > 0) {
            $f_res = $data;
        }
        return $f_res;
    }

    // function getByImId($im_data_id) {
    //     $this->db->select('imported_data_id, key, value');
    //     $this->db->where('key', 'Product Name');
    //     $this->db->where('imported_data_id', $im_data_id);
    //     $this->db->limit(1);
    //     $query = $this->db->get($this->tables['imported_data_parsed']);
    //     $results = $query->result();
    //     $data = array();
    //     foreach($results as $result){
    //         $res = $this->db->select('value')->where_in('key', array('URL', 'Description', 'Long_Description'))->where('imported_data_id', $result->imported_data_id)
    //             ->get($this->tables['imported_data_parsed']);
    //         $info = $res->result();
    //         array_push($data, array('imported_data_id'=>$result->imported_data_id, 'product_name'=>$result->value, 'url'=>$info[2]->value, 'description'=>$info[0]->value, 'long_description'=>$info[1]->value));
    //     }
    //     $f_res = null;
    //     if(count($data) > 0) {
    //         $f_res = $data[0];
    //     }
    //     return $f_res;
    // }

    function getByValueLikeGroupCat($s, $sl, $opt_ids) {
        $this->db->select('imported_data_id, key, value');
        $this->db->where('key', 'Product Name');
        $this->db->like('value', $s);
        if(count($opt_ids) > 0) $this->db->where_in('imported_data_id', $opt_ids);
        $query = $this->db->get($this->tables['imported_data_parsed']);
        $results = $query->result();
        $data = array();
        foreach($results as $result){
            $res = $this->db->select('value')->where_in('key', array('URL', 'Description', 'Long_Description'))->where('imported_data_id', $result->imported_data_id)
                ->get($this->tables['imported_data_parsed']);
            $info = $res->result();
            array_push($data, array('imported_data_id'=>$result->imported_data_id, 'product_name'=>$result->value, 'url'=>$info[2]->value, 'description'=>$info[0]->value, 'long_description'=>$info[1]->value));
        }

        if($sl !== "all") {
            foreach ($data as $key => $value) {
                if(strpos($value['url'], "$sl") === false) {
                    unset($data[$key]);
                }
            }
        }

        return $data;

    }

    function getByValueLikeGroup($s, $sl) {
        $this->db->select('imported_data_id, key, value');
        $this->db->like('value', $s);
        $this->db->group_by('imported_data_id');
        $res = $this->db->get($this->tables['imported_data_parsed']);
        if($res->num_rows() > 0) {
            $result = $res->result_array();
            
            // --- OLD ONE (START)
            // $im_data_id = $result[0]['imported_data_id'];
            // $query = $this->db->where('imported_data_id', $im_data_id)->get($this->tables['imported_data_parsed']);
            // return $query->result_array();
            // --- OLD ONE (END)

            // --- NEW ONE (START)
            $final_res = array();
            if($sl !== 'all') {
                $im_data_id_arr = array();
                foreach ($result as $key => $value) {
                    $im_data_id_arr[] = $value['imported_data_id'];
                }
                $query = $this->db->where_in('imported_data_id', $im_data_id_arr)->get($this->tables['imported_data_parsed']);
                $f_res = $query->result_array();
                $f_index = 0;
                foreach ($f_res as $key => $value) {
                    if($value['key'] === 'URL') {
                        if(strpos($value['value'], "$sl") !== false) {
                            $f_index = $value['imported_data_id'];
                            break;
                        }
                    }
                }
                if($f_index != 0) {
                    $im_data_id = $f_index;
                    $query = $this->db->where('imported_data_id', $im_data_id)->get($this->tables['imported_data_parsed']);
                    $f_res = $query->result_array();
                    $final_res = $f_res;
                    return $final_res;
                } else {
                    return $final_res;
                }
            } else {
                $im_data_id = $result[0]['imported_data_id'];
                $query = $this->db->where('imported_data_id', $im_data_id)->get($this->tables['imported_data_parsed']);
                $f_res = $query->result_array();
                $final_res = $f_res;
            }
            return $final_res;
            // --- NEW ONE (END)
            
        }
        return false;
    }

    function insert($imported_id, $key, $value) {
        $this->key = $key;
        $this->value = $value;
        $this->imported_data_id = $imported_id;

        $this->db->insert($this->tables['imported_data_parsed'], $this);
        return $this->db->insert_id();
    }

    function update($id, $imported_id, $key, $value) {
        $this->key = $key;
        $this->value = $value;
        $this->imported_data_id = $imported_id;

        return $this->db->update($this->tables['imported_data_parsed'], $this, array('id' => $id));
    }

    function getData($value, $website = '', $category_id='', $limit= ''){

        $this->db->select('p.imported_data_id, p.key, p.value')
            ->from($this->tables['imported_data_parsed'].' as p')
            ->join($this->tables['imported_data'].' as i', 'i.id = p.imported_data_id', 'left')
            ->where('p.key', 'Product Name')->like('p.value', $value);

        if ($category_id > 0) {
            $this->db->where('i.category_id', $category_id);
        }

        if($website != '' && $website != 'all'){
            $this->db->like('i.data', $website);
        }

        if ($limit) {
            $this->db->limit((int)$limit);
        }

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
            }

            array_push($data, array('imported_data_id'=>$result->imported_data_id, 'product_name'=>$result->value,
               'description'=>$description, 'long_description'=>$long_description, 'url'=>$url ));
        }

        return $data;
    }

}
