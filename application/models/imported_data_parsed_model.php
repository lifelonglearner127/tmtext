<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Imported_data_parsed_model extends CI_Model {

	var $imported_data_id = null;
	var $key = '';
	var $value = '';
	var $revision = 1;

    // -------  WHITE LISTS FOR FILTERING (START)
    var $manu = array(
        'sony',
        'samsung',
        'lg',
        'nikon',
        'canon',
        'pentax',
        'fuji',
        'vizio',
        'toshiba',
        'kodak'
    );
    // -------  WHITE LISTS FOR FILTERING (END)

    var $tables = array(
    	'imported_data_parsed'              => 'imported_data_parsed',
        'imported_data'                     => 'imported_data',
        'customers'                         => 'customers',
        'products_compare'                  => 'products_compare',
        'product_match_collections'         => 'product_match_collections',
        'crawler_list_prices'               => 'crawler_list_prices',
        'crawler_list'                      => 'crawler_list',
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

    private function get_random_left_compare_pr_regression($customers_list, $ids) {
        $random_id = $ids[array_rand($ids, 1)];
        $this->db->select('imported_data_id, key, value');
        $this->db->where('imported_data_id', $random_id);
        $query = $this->db->get($this->tables['imported_data_parsed']);
        $results = $query->result();
        $data = array('id' => $random_id, 'url' => '', 'product_name' => '', 'description' => '', 'long_description' => '', 'customer' => '');
        foreach($results as $result) {
            if($result->key === 'URL') {
                $data['url'] = $result->value;
                $cus_val = "";
                foreach ($customers_list as $ki => $vi) {
                    if(strpos($result->value, "$vi") !== false) {
                        $cus_val  = $vi;
                    }
                }
                if($cus_val !== "") $data['customer'] = $cus_val;
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
        return $data;
    }

    private function get_random_right_compare_pr_regression($customer_exc, $customers_list, $ids) {
        $random_id = $ids[array_rand($ids, 1)];
        $this->db->select('imported_data_id, key, value');
        $this->db->where('imported_data_id', $random_id);
        $query = $this->db->get($this->tables['imported_data_parsed']);
        $results = $query->result();
        $data = array('id' => '', 'url' => '', 'product_name' => '', 'description' => '', 'long_description' => '', 'customer' => '');
        foreach($results as $result) {
            $data['id'] = $result->imported_data_id;
            if($result->key === 'URL') {
                $data['url'] = $result->value;
                $cus_val = "";
                foreach ($customers_list as $ki => $vi) {
                    if(strpos($result->value, "$vi") !== false) {
                        $cus_val  = $vi;
                    }
                }
                if($cus_val !== "" && $cus_val !== $customer_exc) $data['customer'] = $cus_val;
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
        return $data;
    }

    function checkIfUrlIExists($url) {
        $this->db->select('p.imported_data_id, p.key, p.value')
            ->from($this->tables['imported_data_parsed'].' as p')
            ->join($this->tables['imported_data'].' as i', 'i.id = p.imported_data_id', 'left')
            ->where('p.key', 'URL')->where('p.value', $url);
        $query = $this->db->get();
        $results = $query->result();
        if(count($results) > 0) {
            return $results[0]->imported_data_id;
        } else {
            return false;
        }
    }

    function recordProductMatchCollection($crawl) {
        return $this->db->insert_batch($this->tables['product_match_collections'], $crawl);
    }


    function getRandomRightCompareProductDrop($customer_r_selected, $customer_l, $id_l, $id_r) {
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

        $not_in = array($id_l, $id_r);
        $this->db->select('p.imported_data_id, p.key, p.value')
            ->from($this->tables['imported_data_parsed'].' as p')
            ->join($this->tables['imported_data'].' as i', 'i.id = p.imported_data_id', 'left')
            ->where('p.key', 'Product Name')->where_not_in('p.imported_data_id', $not_in)->like('i.data', $customer_r_selected)->not_like('i.data', $customer_l)->limit(1);

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
                if($val['key'] == 'URL') {
                    $url = $val['value'];
                    $cus_val = "";
                    foreach ($customers_list as $ki => $vi) {
                        if(strpos($url, "$vi") !== false) {
                            $cus_val  = $vi;
                        }
                    }
                    if($cus_val !== "") $customer = $cus_val;
                }
                if($val['key'] == 'Description'){ $description = $val['value']; }
                if($val['key'] == 'Long_Description'){ $long_description = $val['value']; }
            }
            $data = array('id' => $result->imported_data_id, 'url' => $url, 'product_name' => $result->value, 'description' => $description, 'long_description' => $long_description, 'customer' => $customer);
        }
        return $data;
    }

    function getRandomRightCompareProduct($customer_exc, $id_exc, $l_product_name) {
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

        // ---- get randomly indexed import id (start) (new stuff)
        $this->db->select('imported_data_id, key, value');
        $query = $this->db->where('imported_data_id != ', $id_exc)->get($this->tables['imported_data_parsed']);
        $results = $query->result();
        $ids = array();
        if(count($results) > 0) {
            foreach ($results as $key => $value) {
                $ids[] = $value->imported_data_id;
            }
        }
        $ids = array_unique($ids);
        $random_id = $ids[array_rand($ids, 1)];
        // ---- get randomly indexed import id (end) (new stuff)

        $this->db->select('imported_data_id, key, value');
        $this->db->where('imported_data_id', $random_id);
        $query = $this->db->get($this->tables['imported_data_parsed']);
        $results = $query->result();
        $data = array('id' => '', 'url' => '', 'product_name' => '', 'description' => '', 'long_description' => '', 'customer' => '');
        foreach($results as $result) {
            $data['id'] = $result->imported_data_id;
            if($result->key === 'URL') {
                $data['url'] = $result->value;
                $cus_val = "";
                foreach ($customers_list as $ki => $vi) {
                    if(strpos($result->value, "$vi") !== false) {
                        $cus_val  = $vi;
                    }
                }
                if($cus_val !== "" && $cus_val !== $customer_exc) $data['customer'] = $cus_val;
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

        // ------------ MANUFACTURER CHECK AND DETECTION  (START) ------------ //
        $manu_ckeck_st = true;
        // if(trim($data['product_name']) !== "") {
        //     // --- DETECT LEFT SIDE PRODUCT MANUFACTURER
        //     $man_left = "";
        //     foreach ($this->manu as $km => $vm) {
        //         if( (strpos($l_product_name, $vm) !== false) || (strpos($l_product_name, strtoupper($vm)) !== false) || strpos($l_product_name, ucfirst($vm)) !== false ) {
        //             $man_left = $vm;
        //             break;
        //         }
        //     }
        //     // --- DETECT RIGHT SIDE PRODUCT MANUFACTURER
        //     $man_right = "";
        //     foreach ($this->manu as $km => $vm) {
        //         if( (strpos($data['product_name'], $vm) !== false) || (strpos($data['product_name'], strtoupper($vm)) !== false) || strpos($data['product_name'], ucfirst($vm)) !== false ) {
        //             $man_right = $vm;
        //             break;
        //         }
        //     }
        //     if($man_left == $man_right) $manu_ckeck_st = true;
        // }
        // echo var_dump($l_product_name);
        // echo var_dump($data['product_name']);
        // echo var_dump($man_left);
        // echo var_dump($man_right);
        // ------------ MANUFACTURER CHECK AND DETECTION  (START) ------------ //

        // ------------ REGRESSION CHECKER (START) ------------ //
        // $i = 0;
        while( $manu_ckeck_st !== true || trim($data['url']) === '' || trim($data['product_name']) === '' || trim($data['description']) === '' || trim($data['long_description']) === '' || trim($data['customer']) === '' ) {
            // echo var_dump("ITERATION: ". $i);
            // if($i == 4) die;
            $data = $this->get_random_right_compare_pr_regression($customer_exc, $customers_list, $ids);
            // $i++;
        }
        // ------------ REGRESSION CHECKER (END) ------------ //
        return $data;
    }

    // function getRandomRightCompareProduct($customer_exc, $id_exc) {
    //     // ---- get customers list (start)
    //     $customers_list = array();
    //     $query_cus = $this->db->order_by('name', 'asc')->get($this->tables['customers']);
    //     $query_cus_res = $query_cus->result();
    //     if(count($query_cus_res) > 0) {
    //         foreach ($query_cus_res as $key => $value) {
    //             $n = strtolower($value->name);
    //             $customers_list[] = $n;
    //         }
    //     }
    //     $customers_list = array_unique($customers_list);
    //     // ---- get customers list (end)

    //     // ---- get randomly indexed import id (start) (new stuff)
    //     $this->db->select('imported_data_id, key, value');
    //     $query = $this->db->where('imported_data_id != ', $id_exc)->get($this->tables['imported_data_parsed']);
    //     $results = $query->result();
    //     $ids = array();
    //     if(count($results) > 0) {
    //         foreach ($results as $key => $value) {
    //             $ids[] = $value->imported_data_id;
    //         }
    //     }
    //     $ids = array_unique($ids);
    //     $random_id = $ids[array_rand($ids, 1)];
    //     // ---- get randomly indexed import id (end) (new stuff)

    //     $this->db->select('imported_data_id, key, value');
    //     $this->db->where('imported_data_id', $random_id);
    //     $query = $this->db->get($this->tables['imported_data_parsed']);
    //     $results = $query->result();
    //     $data = array('id' => '', 'url' => '', 'product_name' => '', 'description' => '', 'long_description' => '', 'customer' => '');
    //     foreach($results as $result) {
    //         $data['id'] = $result->imported_data_id;
    //         if($result->key === 'URL') {
    //             $data['url'] = $result->value;
    //             $cus_val = "";
    //             foreach ($customers_list as $ki => $vi) {
    //                 if(strpos($result->value, "$vi") !== false) {
    //                     $cus_val  = $vi;
    //                 }
    //             }
    //             if($cus_val !== "" && $cus_val !== $customer_exc) $data['customer'] = $cus_val;
    //         }
    //         if($result->key === 'Product Name') {
    //             $data['product_name'] = $result->value;
    //         }
    //         if($result->key === 'Description') {
    //             $data['description'] = $result->value;
    //         }
    //         if($result->key === 'Long_Description') {
    //             $data['long_description'] = $result->value;
    //         }
    //     }
    //     // ---- regression check (start)
    //     while( trim($data['url'] === '') || trim($data['product_name'] === '') || trim($data['description'] === '') || trim($data['long_description'] === '') || trim($data['customer'] === '') ) {
    //         $data = $this->get_random_right_compare_pr_regression($customer_exc, $customers_list, $ids);
    //     }
    //     // ---- regression check (end)
    //     return $data;
    // }

    function getRandomLeftCompareProduct() {
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

        // ---- get imported_data_id list (start) ( !!! OLD STUFF !!! )
        $this->db->select('imported_data_id, key, value');
        $query = $this->db->get($this->tables['imported_data_parsed']);
        $results = $query->result();
        $ids = array();
        if(count($results) > 0) {
            foreach ($results as $key => $value) {
                $ids[] = $value->imported_data_id;
            }
        }
        $ids = array_unique($ids);
        $random_id = $ids[array_rand($ids, 1)];
        // ---- get imported_data_id list (end) ( !!! OLD STUFF !!! )

        // ---- get random product by random id (start) ( !!! NEW STUFF !!! )
        // $this->db->select('p.imported_data_id, p.key, p.value')
        //     ->from($this->tables['imported_data_parsed'].' as p')
        //     ->join($this->tables['imported_data'].' as i', 'i.id = p.imported_data_id', 'left')
        //     ->where('p.key', 'Product Name');

        // foreach ($this->manu as $km => $vm) {
        //     if($km == 0) {
        //         $this->db->like('i.data', $vm, 'after')->or_like('i.data', strtoupper($vm), 'after')->or_like('i.data', ucfirst('i.data', $vm), 'after');
        //     } else {
        //         $this->db->or_like('i.data', $vm, 'after')->or_like('i.data', strtoupper($vm), 'after')->or_like('i.data', ucfirst('i.data', $vm), 'after');
        //     }
        // }

        // $query = $this->db->get();
        // $results = $query->result();
        // $data = array();
        // $data_ids = array();
        // foreach($results as $result) {
        //     $manu = "";
        //     foreach ($this->manu as $km => $vm) {
        //         if( (strpos($result->value, $vm) !== false) || (strpos($result->value, strtoupper($vm)) !== false) || strpos($result->value, ucfirst($vm)) !== false ) {
        //             $manu = $vm;
        //             break;
        //         }
        //     }
        //     $query = $this->db->where('imported_data_id', $result->imported_data_id)->get($this->tables['imported_data_parsed']);
        //     $res = $query->result_array();
        //     $description = '';
        //     $long_description = '';
        //     $url = '';
        //     foreach($res as $val) {
        //         if($val['key'] == 'URL') {
        //             $url = $val['value'];
        //             $customer = '';
        //             $cus_val = "";
        //             foreach ($customers_list as $ki => $vi) {
        //                 if(strpos($url, "$vi") !== false) {
        //                     $cus_val  = $vi;
        //                 }
        //             }
        //             if($cus_val !== "") $customer = $cus_val;
        //         }
        //         if($val['key'] == 'Description') { $description = $val['value']; }
        //         if($val['key'] == 'Long_Description') { $long_description = $val['value']; }
        //     }
        //     $mid = array('id' => $result->imported_data_id, 'url' => $url, 'product_name' => $result->value, 'description' => $description, 'long_description' => $long_description, 'customer' => $customer, 'manu' => $manu);
        //     array_push($data, $mid);
        //     array_push($data_ids, $result->imported_data_id);
        // }
        // $random_id = $data_ids[array_rand($data_ids, 1)];
        // $data_in = array('id' => '', 'url' => '', 'product_name' => '', 'description' => '', 'long_description' => '', 'customer' => '', 'manu' => '');
        // $key_s = null;
        // foreach ($data as $ks => $vs) {
        //     if($vs['id'] == $random_id) {
        //         $key_s = $ks;
        //         break;
        //     }
        // }
        // if($key_s !== null) $data_in = $data[$key_s];
        // die(var_dump($data_in));
        // return $data_in;
        // ---- get random product by random id (end) ( !!! NEW STUFF !!! )

        // ---- get random product by random id (start) ( !!! OLD STUFF !!! )
        $this->db->select('imported_data_id, key, value');
        $this->db->where('imported_data_id', $random_id);
        $query = $this->db->get($this->tables['imported_data_parsed']);
        $results = $query->result();
        $data = array('id' => $random_id, 'url' => '', 'product_name' => '', 'description' => '', 'long_description' => '', 'customer' => '', 'manu' => '');
        foreach($results as $result) {
            if($result->key === 'URL') {
                $data['url'] = $result->value;
                $cus_val = "";
                foreach ($customers_list as $ki => $vi) {
                    if(strpos($result->value, "$vi") !== false) {
                        $cus_val  = $vi;
                    }
                }
                if($cus_val !== "") $data['customer'] = $cus_val;
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
        // ---- get random product by random id (end) ( !!! OLD STUFF !!! )

        // ------------ REGRESSION CHECKER (START) ------------ // ( !!! OLD STUFF !!! )
        while( trim($data['url']) === '' || trim($data['product_name']) === '' || trim($data['description']) === '' || trim($data['long_description']) === '' || trim($data['customer']) === '' ) {
            $data = $this->get_random_left_compare_pr_regression($customers_list, $ids);
        }
        return $data;
        // ------------ REGRESSION CHECKER (END) ------------ // ( !!! OLD STUFF !!! )
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
        	if($result->key === 'Features') {
                $data['features'] = $result->value;
            }
        	if($result->key === 'parsed_attributes') {
                $data['parsed_attributes'] = unserialize($result->value);
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

    function insert($imported_id, $key, $value, $revision = 1) {
        $this->key = $key;
        $this->value = $value;
        $this->imported_data_id = $imported_id;
        $this->revision = $revision;

        $this->db->insert($this->tables['imported_data_parsed'], $this);
        return $this->db->insert_id();
    }

    function update($id, $imported_id, $key, $value) {
        $this->key = $key;
        $this->value = $value;
        $this->imported_data_id = $imported_id;

        return $this->db->update($this->tables['imported_data_parsed'], $this, array('id' => $id));
    }

    function getData($value, $website = '', $category_id='', $limit= '', $key = 'Product Name', $strict = false){

        $this->db->select('p.imported_data_id, p.key, p.value')
            ->from($this->tables['imported_data_parsed'].' as p')
            ->join($this->tables['imported_data'].' as i', 'i.id = p.imported_data_id', 'left')
            ->where('p.key', $key);

        if ($strict) {
        	$this->db->like('p.value', '"'.$value.'"');
        }  else {
        	$this->db->like('p.value', $value);
        }

        if ($category_id > 0 && $category_id!=2) {
            $this->db->where('i.category_id', $category_id);
        }

        if($website != '' && $website != 'All sites'){
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

	            if($val['key'] == 'Product Name') { $product_name = $val['value']; }
            	if($val['key'] == 'Features') { $features = $val['value']; }

            }
            array_push($data, array('imported_data_id'=>$result->imported_data_id, 'product_name'=>$result->value,
               'description'=>$description, 'long_description'=>$long_description, 'url'=>$url, 'product_name' =>$product_name, 'features' => $features ));

        }

        return $data;
    }

    function getDataWithPaging($value, $website = '', $category_id='', $key = 'Product Name'){

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
        $total_rows = $this->getDataWithPagingTotalRows($value, $website, $category_id);

        // Once again, protecting the SQL, as well as making sure we don't go over the limit
        if (empty($display_length)) {
            $display_length  = $total_rows - $display_start;
        }

        $this->db->select('id.id, idp.value AS product_name, idp2.value AS url')
            ->from($this->tables['imported_data'].' as id')
            ->join($this->tables['imported_data_parsed'].' as idp', 'id.id = idp.imported_data_id', 'left')
            ->join($this->tables['imported_data_parsed'].' as idp2', 'id.id = idp2.imported_data_id', 'left')
            ->where('idp.key', 'Product Name')->where('idp2.key', 'URL');
        if(!empty($value)) {
            $value = $this->db->escape($value);
            $this->db->like('idp.value', $value)->like('idp2.value', $value);
        }

        if ($category_id > 0 && $category_id!=2) {
            $this->db->where('i.category_id', $category_id);
        }

        if(!empty($website) && $website != 'All sites'){
            $this->db->like('i.data', $website);
        }

        if(!empty($order_column_name)) {
            $this->db->order_by($order_column_name, $sort_direction_n);
        }

        if(isset($display_start) && isset($display_length)) {
            $this->db->limit($display_length, $display_start);
        }

        $query = $this->db->get();

        $result = $query->result();

        $resultArray = array(
            'total_rows'            => $total_rows,
            'display_length'        => $display_length,
            'result'                => $result,
            'display_start'         => $display_start,
        );

        return $resultArray;
    }

    function getResearchDataWithPaging() {
        $status = "";
        if ($this->input->get('status') == 'batches_edited')
            $status = "and rd.status = 'edited'";
        else
            if ($this->input->get('status') == 'batches_unedited')
                $status = "and rd.status <> 'edited'";

        $like = "'%'";
        if ($this->input->get('sSearch')) {
            $like = $this->db->escape("%".$this->input->get('sSearch')."%");
        }

        $batch = "";
        if ($this->input->get('batch')) {
            $batch = " and b.title = ".$this->db->escape($this->input->get('batch'));
        }

        $sql_cmd = "
            select
                rd.id,
                rd.batch_id,
                rd.product_name,
                rd.url
            from
                research_data as rd
            inner join batches as b ON b.id = rd.batch_id
            where
                concat(rd.product_name, rd.url) like $like
                $status
                $batch
                and trim(rd.product_name) <> ''
	            and trim(rd.url) <> ''
        ";

        $query = $this->db->query($sql_cmd);

        $total_rows = $query->num_rows();
        $display_length = intval($this->input->get('iDisplayLength', TRUE));

        $display_start = intval($this->input->get('iDisplayStart', TRUE));
        if (empty($display_start)) {
            $display_start = 0;
        }

        if (empty($display_length)) {
            $display_length  = $total_rows - $display_start;
        }

        $count_sorting_cols = intval($this->input->get('iSortingCols', TRUE));

        if($count_sorting_cols > 0) {
            $columns_name_string = $this->input->get('sColumns', TRUE);
            $sort_col_n = intval($this->input->get('iSortCol_0', TRUE));
            $sort_direction_n = $this->input->get('sSortDir_0', TRUE);
            $columns_names = explode(",", $columns_name_string);
            if(!empty($columns_names[$sort_col_n]) && !empty($sort_direction_n)) {
                $order_column_name = $columns_names[$sort_col_n];
            }
        }

        if(!empty($order_column_name)) {
            $sql_cmd = $sql_cmd." order by $order_column_name $sort_direction_n";
        }

        if(isset($display_start) && isset($display_length)) {
            $sql_cmd = $sql_cmd." limit $display_start, $display_length";
        }

        $query = $this->db->query($sql_cmd);
        $result =  $query->result();

        $resultArray = array(
            'total_rows'            => $total_rows,
            'display_length'        => $display_length,
            'result'                => $result,
            'display_start'         => $display_start,
        );

        return $resultArray;
    }

    function getResearchDataByURLandBatchId($params) {
        $batch_id = $params->batch_id;
        $url = $this->db->escape($params->url);
        $sql_cmd = "
            select
                *
            from
                research_data as rd
            where
                rd.batch_id = $batch_id
                and rd.url = $url
            limit 0,1
        ";

        $query = $this->db->query($sql_cmd);
        $result =  $query->result();
        return $result[0];
    }

    protected function getDataWithPagingTotalRows($value, $website = '', $category_id='') {
        $this->db->select('id.id, idp.value AS product_name, idp2.value AS url')
            ->from($this->tables['imported_data'].' as id')
            ->join($this->tables['imported_data_parsed'].' as idp', 'id.id = idp.imported_data_id', 'left')
            ->join($this->tables['imported_data_parsed'].' as idp2', 'id.id = idp2.imported_data_id', 'left')
            ->where('idp.key', 'Product Name')->where('idp2.key', 'URL');
        if(!empty($value)) {
            $value = $this->db->escape($value);
            $this->db->like('idp.value', $value)->like('idp2.value', $value);
        }

        if ($category_id > 0 && $category_id!=2) {
            $this->db->where('i.category_id', $category_id);
        }

        if($website != '' && $website != 'All sites'){
            $this->db->like('i.data', $website);
        }

        $query = $this->db->get();
        $total_rows = $query->num_rows();
        return $total_rows;
    }

    function getMaxRevision($imported_data_id) {
    	$query = $this->db->select('max(revision) as revision')
    			  ->where('imported_data_id', $imported_data_id)
                  ->limit(1)
                  ->get($this->tables['imported_data_parsed']);

        return $query->row()->revision;
    }

    function getByParsedAttributes($search, $strict = false) {
		if ($rows = $this->getData($search, null, null, null, 'parsed_attributes', $strict)) {
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


	    	foreach ($rows as $key => $row) {
				$cus_val = "";
				foreach ($customers_list as $ki => $vi) {
					if(strpos($rows[$key]['url'], "$vi") !== false) {
						$cus_val  = $vi;
					}
				}
				if($cus_val !== "") $rows[$key]['customer'] = $cus_val;
			}
			return $rows;
		}
    }

    function getLastPrices($imported_data_id, $prices_count = 3) {
        $this->db->select('clp.id, clp.price, clp.created')
            ->join($this->tables['crawler_list'].' as cl', 'clp.crawler_list_id = cl.id')
            ->join($this->tables['imported_data_parsed']. ' as idp', 'idp.imported_data_id = cl.imported_data_id')
            ->where('idp.key = "Product Name"')
            ->where('idp.imported_data_id = ' . $imported_data_id)
            ->order_by('created', 'desc');
        if($prices_count > 0) {
            $this->db->limit($prices_count);
        }
        $query = $this->db->get($this->tables['crawler_list_prices'].' as clp');
        return $query->result();
    }

}
