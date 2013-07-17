<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Measure extends MY_Controller {

    function __construct()
    {
        parent::__construct();

        $this->load->library('form_validation');
        $this->load->library('helpers');
        $this->data['title'] = 'Measure';

        if (!$this->ion_auth->logged_in())
        {
            //redirect them to the login page
            redirect('auth/login', 'refresh');
        }
    }

    public function index() {
        $this->data['customers_list'] = $this->customers_list_new();
        $this->data['user_id'] = $this->ion_auth->get_user_id();
        $this->render();
    }

    private function upload_record_webshoot($ext_url, $url_name) {
        $file = file_get_contents($ext_url);
        $type = 'png';
        //$dir =  $_SERVER['DOCUMENT_ROOT']."/webroot/webshoots"; // for local server
        // $dir =  BASEPATH."../webroot/webshoots";
        $dir = "/ebs/sites/client38/web49/web/producteditor/webroot/webshoots"; // for dev server
        if(!file_exists($dir)) {
            mkdir($dir);
            chmod($dir, 0777);
        }
        // --- NEW STUFF (TIMESTAMP BASED IMAGES NAMES) (START)
        $url_name = $url_name."-".date('Y', time())."-".date('m', time())."-".date('d', time())."-".date('H', time())."-".date('i', time())."-".date('s', time());
        // --- NEW STUFF (TIMESTAMP BASED IMAGES NAMES) (END)
        $t = file_put_contents($dir."/$url_name.$type", $file);
        $path = base_url()."webshoots/$url_name.$type";
        $res = array(
            'path' => $path,
            'dir' => $dir."/$url_name.$type"
        );
        return $res;
    }

    private function check_screen_crawl_status($url) {
        $this->load->model('webshoots_model');
        return $this->webshoots_model->checkScreenCrawlStatus($url);
    }

    public function getwebshootbyurl() {
        $url = $this->input->post('url');
        $this->load->model('webshoots_model');
        $res = $this->webshoots_model->getWebShootByUrl($url);
        if($res !== false) {
            $result = $res;
        } else { // --- crawl it
            $url = urlencode(trim($url));
            // -- configs (start)
            $api_key = "dc598f9ae119a97234ea";
            $api_secret = "47c7248bc03fbd368362";
            $token = md5("$api_secret+$url");
            // $size_s = "200x150";
            // $size_l = "600x450";
            $size_s = "340x255";
            $size_l = "800x600";
            $format = "png";
            // -- configs (end)
            $res = array(
                "s" => "http://api.webyshots.com/v1/shot/$api_key/$token/?url=$url&dimension=$size_s&format=$format",
                'l' => "http://api.webyshots.com/v1/shot/$api_key/$token/?url=$url&dimension=$size_l&format=$format"
            );
            $crawl_s = $this->upload_record_webshoot($res['s'], $url."_small");
            $crawl_l = $this->upload_record_webshoot($res['l'], $url."_big");
            $result = array(
                'state' => false,
                'url' => $url,
                'small_crawl' => $crawl_s['path'],
                'big_crawl' => $crawl_l['path'],
                'dir_thumb' => $crawl_s['dir'],
                'dir_img' => $crawl_l['dir']  
            );
            $insert_id = $this->webshoots_model->recordUpdateWebshoot($result);
            $result = $this->webshoots_model->getWebshootDataById($insert_id);
        }
        $this->output->set_content_type('application/json')->set_output(json_encode($result));
    }

    public function getwebshootdata() {
        $url = $this->input->post('url');
        $this->load->model('webshoots_model');
        $res = $this->webshoots_model->getWebshootData($url);
        $this->output->set_content_type('application/json')->set_output(json_encode($res));
    }

    public function getcustomerslist_crawl() {
        $cs = $this->customers_list_new();
        $res = array();
        foreach ($cs as $k => $v) {
            $mid = array(
                'id' => $v['id'],
                'name' => $v['name'],
                'crawl_st' => $this->check_screen_crawl_status($v['name'])
            );
            $res[] = $mid;
        }
        $this->output->set_content_type('application/json')->set_output(json_encode($res));
    }

    public function webshootcrawl() {
        $url = $this->input->post('url');
        $url = urlencode(trim($url));
        // -- configs (start)
        $api_key = "dc598f9ae119a97234ea";
        $api_secret = "47c7248bc03fbd368362";
        $token = md5("$api_secret+$url");
        // $size_s = "200x150";
        // $size_l = "600x450";
        $size_s = "340x255";
        $size_l = "800x600";
        $format = "png";
        // -- configs (end)
        $res = array(
            "s" => "http://api.webyshots.com/v1/shot/$api_key/$token/?url=$url&dimension=$size_s&format=$format",
            'l' => "http://api.webyshots.com/v1/shot/$api_key/$token/?url=$url&dimension=$size_l&format=$format"
        );
        $crawl_s = $this->upload_record_webshoot($res['s'], $url."_small");
        $crawl_l = $this->upload_record_webshoot($res['l'], $url."_big");
        $result = array(
            'state' => false,
            'url' => $url,
            'small_crawl' => $crawl_s['path'],
            'big_crawl' => $crawl_l['path'],
            'dir_thumb' => $crawl_s['dir'],
            'dir_img' => $crawl_l['dir']  
        );
        $this->load->model('webshoots_model');
        $r = $this->webshoots_model->recordUpdateWebshoot($result);
        if($r > 0) $result['state'] = true;
        $this->output->set_content_type('application/json')->set_output(json_encode($result));
    }

    public function gethomepageyeardata() {
        $year = $this->input->post('year');
        $week = $this->input->post('week');
        $data = array(
            'year' => $year,
            'week' => $week,
            'customers_list' => $this->customers_list_new()
        );
        $this->load->view('measure/gethomepageyeardata', $data);
    }

    public function gethomepageweekdata() {
        $year = $this->input->post('year');
        $week = $this->input->post('week');
        $data = array(
            'year' => $year,
            'week' => $week,
            'customers_list' => $this->customers_list_new()
        );
        $this->load->view('measure/gethomepageweekdata', $data);
    }

    public function measure_products()
    {
        $this->data['category_list'] = $this->category_full_list();
        $this->data['customers_list'] = $this->category_customers_list();
        $this->load->model('batches_model');
        $batches = $this->batches_model->getAll();
        $batches_list = array(0 => 'No Batch');
        foreach($batches as $batch){
            array_push($batches_list, $batch->title);
        }
        $this->data['batches_list'] = $batches_list;
        $this->render();
    }

    public function measure_departments()
    {
        $this->data['customers_list'] = $this->customers_list_new();
        $this->render();
    }

    public function measure_categories()
    {
       $this->render();
    }

    public function measure_pricing()
    {
        $this->render();
    }

    public function get_product_price() {
        $this->load->model('crawler_list_prices_model');

        $price_list = $this->crawler_list_prices_model->get_products_with_price();

        if(!empty($price_list['total_rows'])) {
            $total_rows = $price_list['total_rows'];
        } else {
            $total_rows = 0;
        }

        $output = array(
            "sEcho"                     => intval($_GET['sEcho']),
            "iTotalRecords"             => $total_rows,
            "iTotalDisplayRecords"      => $total_rows,
            "iDisplayLength"            => $price_list['display_length'],
            "aaData"                    => array()
        );

        if(!empty($price_list['result'])) {
            foreach($price_list['result'] as $price) {
            	$parsed_attributes = unserialize($price->parsed_attributes);
            	$model = (!empty($parsed_attributes['model'])?$parsed_attributes['model']: $parsed_attributes['UPC/EAN/ISBN']);
                $output['aaData'][] = array(
                    $price->created,
                    '<a href ="'.$price->url.'">'.substr($price->url,0, 60).'</a>',
                    $model,
                    $price->product_name,
                    sprintf("%01.2f", $price->price),
                );
            }
        }

        $this->output->set_content_type('application/json')
            ->set_output(json_encode($output));
    }

    private function category_full_list() {
        $this->load->model('category_model');
        $categories = $this->category_model->getAll();
        return $categories;
    }

    private function customers_list_new() {
        $this->load->model('customers_model');
        $output = array();
        $customers_init_list = $this->customers_model->getAll();
        if(count($customers_init_list) > 0) {
            foreach ($customers_init_list as $key => $value) {
                $mid = array(
                    'id' => $value->id,
                    'desc' => $value->description,
                    'image_url' => $value->image_url,
                    'name' => $value->name,
                    'name_val' => strtolower($value->name)
                );
                $output[] = $mid;
            }
        }
        return $output;
    }

    public function getcustomerslist_general() {
        $output = $this->customers_list_new();
        $this->output->set_content_type('application/json')->set_output(json_encode($output));
    }

    private function category_customers_list() {
        $this->load->model('customers_model');
        $output = array();
        $customers_init_list = $this->customers_model->getAll();
        if(count($customers_init_list) > 0) {
            foreach ($customers_init_list as $key => $value) {
                $n = strtolower($value->name);
                $output[] = $n;
            }
        }
        $output = array_unique($output);
        return $output;
    }

    public function cisearchteram() {
        // $q = $this->input->get('term'); // OLD
        $q = $this->input->get('q'); // NEW
        $sl = $this->input->get('sl');
        $cat = $this->input->get('cat');
        $this->load->model('imported_data_parsed_model');
        $data = $this->imported_data_parsed_model->getData($q, $sl, $cat_id, 4);
        foreach ($data as $key => $value) {
            $response[] = array('id' => $value['imported_data_id'], 'value' => $value['product_name']);
        };
        $this->output->set_content_type('application/json')->set_output(json_encode($response));
    }

    public function gridview() {
        $im_data_id = $this->input->post('im_data_id');
        $data = array(
            'im_data_id' => $im_data_id,
            's_product' => array(),
            's_product_short_desc_count' => 0,
            's_product_long_desc_count' => 0,
            'seo' => array('short' => array(), 'long' => array()),
            'same_pr' => array()
        );
        if($im_data_id !== null && is_numeric($im_data_id)) {

            // --- GET SELECTED RPODUCT DATA (START)
            $this->load->model('imported_data_parsed_model');
            $data_import = $this->imported_data_parsed_model->getByImId($im_data_id);

            if($data_import['description'] !== null && trim($data_import['description']) !== "") {
                $data_import['description'] = preg_replace('/\s+/', ' ', $data_import['description']);
                // $data_import['description'] = preg_replace('/[^A-Za-z0-9\. -!]/', ' ', $data_import['description']);
                $data['s_product_short_desc_count'] = count(explode(" ", $data_import['description']));
            }
            if($data_import['long_description'] !== null && trim($data_import['long_description']) !== "") {
                $data_import['long_description'] = preg_replace('/\s+/', ' ', $data_import['long_description']);
                // $data_import['long_description'] = preg_replace('/[^A-Za-z0-9\. -!]/', ' ', $data_import['long_description']);
                $data['s_product_long_desc_count'] = count(explode(" ", $data_import['long_description']));
            }
            $data['s_product'] = $data_import;
            // --- GET SELECTED RPODUCT DATA (END)

            // --- ATTEMPT TO GET 'SAME' FROM 'HUMAN INTERFACE' (products_compare table) (START)
            $same_pr = $this->imported_data_parsed_model->getSameProductsHuman($im_data_id);

            // get similar by parsed_attributes
            if (empty($same_pr) && isset($data_import['parsed_attributes']) && isset($data_import['parsed_attributes']['model'])) {
            	$strict = $this->input->post('strict');
            	$same_pr = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['model'], $strict);
            }

        	if (empty($same_pr) && isset($data_import['parsed_attributes']) && isset($data_import['parsed_attributes']['UPC/EAN/ISBN'])) {
            	$same_pr = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['UPC/EAN/ISBN']);
            }

            // get similar for first row
			$this->load->model('similar_imported_data_model');

            $customers_list = array();
	        $query_cus = $this->similar_imported_data_model->db->order_by('name', 'asc')->get('customers');
	        $query_cus_res = $query_cus->result();
	        if(count($query_cus_res) > 0) {
	            foreach ($query_cus_res as $key => $value) {
	                $n = strtolower($value->name);
	                $customers_list[] = $n;
	            }
	        }
	        $customers_list = array_unique($customers_list);

			if (empty($same_pr) && ($group_id = $this->similar_imported_data_model->findByImportedDataId($im_data_id))) {
				if ($rows = $this->similar_imported_data_model->getImportedDataByGroupId($group_id)) {
					$data_similar = array();

					foreach ($rows as $key => $row) {
						$data_similar[$key] = $this->imported_data_parsed_model->getByImId($row->imported_data_id);
						$data_similar[$key]['imported_data_id'] = $row->imported_data_id;

						$cus_val = "";
						foreach ($customers_list as $ki => $vi) {
							if(strpos($data_similar[$key]['url'], "$vi") !== false) {
								$cus_val  = $vi;
							}
						}
						if($cus_val !== "") $data_similar[$key]['customer'] = $cus_val;
					}

					if (!empty($data_similar)) {
						$same_pr = $data_similar;
					}

				}

			}

//			if(count($same_pr) === 3) {
                foreach ($same_pr as $ks => $vs) {
                    $same_pr[$ks]['seo']['short'] = $this->helpers->measure_analyzer_start_v2(preg_replace('/\s+/', ' ', $vs['description']));
                    $same_pr[$ks]['seo']['long'] = $this->helpers->measure_analyzer_start_v2(preg_replace('/\s+/', ' ', $vs['long_description']));

                    // three last prices
                    $imported_data_id = $same_pr[$ks]['imported_data_id'];
                    $three_last_prices = $this->imported_data_parsed_model->getLastPrices($imported_data_id);
                    $same_pr[$ks]['three_last_prices'] = $three_last_prices;
                }
                $data['same_pr'] = $same_pr;
//            }
            // --- ATTEMPT TO GET 'SAME' FROM 'HUMAN INTERFACE' (products_compare table) (END)

            // --- GET SELECTED RPODUCT SEO DATA (TMP) (START)
            if($data_import['description'] !== null && trim($data_import['description']) !== "") {
                $data['seo']['short'] = $this->helpers->measure_analyzer_start_v2($data_import['description']);
            }
            if($data_import['long_description'] !== null && trim($data_import['long_description']) !== "") {
                $data['seo']['long'] = $this->helpers->measure_analyzer_start_v2($data_import['long_description']);
            }
            // --- GET SELECTED RPODUCT SEO DATA (TMP) (END)
        }

        // -------- COMPARING V1 (START)
        $s_term = $this->input->post('s_term');

        // -------- COMPARING V1 (END)

        $this->load->view('measure/gridview', $data);
    }

    public function getcustomerslist_new() {
        $this->load->model('customers_model');
        $this->load->model('users_to_customers_model');
        $admin = $this->ion_auth->is_admin($this->ion_auth->get_user_id());
        $customers_init_list = $this->users_to_customers_model->getByUserId($this->ion_auth->get_user_id());
        if (count($customers_init_list) == 0 && $admin) {
            $customers_init_list = $this->customers_model->getAll();
        }
        
        if(count($customers_init_list) > 0) {
            if(count($customers_init_list) != 1){
                $output[] = array('text'=>'All Customers',
                   'value'=>'All Customers',
                   'image'=> ''
                );
            }
            foreach ($customers_init_list as $key => $value) {
                $output[] = array('text'=>'',
                    'value'=>strtolower($value->name),
                    'image'=> base_url().'img/'.$value->image_url
                );
            }
        } else {
            $output[] = array('text'=>'No Customers',
                   'value'=>'No Customers',
                   'image'=> ''
                );
        }
        $this->output->set_content_type('application/json')->set_output(json_encode($output));
    }

    public function getsiteslist_new() {
        $this->load->model('sites_model');
        $customers_init_list = $this->sites_model->getAll();
        if(count($customers_init_list) > 0) {
            $output[] = array('text'=>'All sites',
                'value'=>'All sites',
                'image'=> ''
            );
            foreach ($customers_init_list as $key => $value) {
                $output[] = array('text'=>'',
                    'value'=>strtolower($value->name),
                    'image'=> base_url().'img/'.$value->image_url
                );
            }
        }
        $this->output->set_content_type('application/json')->set_output(json_encode($output));
    }


    public function getcustomerslist() {
        $this->load->model('customers_model');
        $output = array();
        $customers_init_list = $this->customers_model->getAll();
        if(count($customers_init_list) > 0) {
            foreach ($customers_init_list as $key => $value) {
                $n = strtolower($value->name);
                $output[] = $n;
            }
        }
        $output = array_unique($output);
        $this->output->set_content_type('application/json')->set_output(json_encode($output));
    }

    public function analyzestring() {
        $clean_t = $this->input->post('clean_t');
        $output = $this->helpers->measure_analyzer_start_v2($clean_t);
        $this->output->set_content_type('application/json')->set_output(json_encode($output));
    }

    public function analyzekeywords() {
        $primary_ph = $this->input->post('primary_ph');
        $secondary_ph = $this->input->post('secondary_ph');
        $tertiary_ph = $this->input->post('tertiary_ph');
        $short_desc = $this->input->post('short_desc');
        $long_desc = $this->input->post('long_desc');
        $output = $this->helpers->measure_analyzer_keywords($primary_ph, $secondary_ph, $tertiary_ph, $short_desc, $long_desc);
        $this->output->set_content_type('application/json')->set_output(json_encode($output));
    }

    public function searchmeasuredball() {
        $s = $this->input->post('s');
        $sl = $this->input->post('sl');
        $cat_id = $this->input->post('cat');
        $limit = $this->input->post('limit');
        $this->load->model('imported_data_parsed_model');
        $data = array(
            'search_results' => array()
        );

        if($limit !== 0) {
            $data_import = $this->imported_data_parsed_model->getData($s, $sl, $cat_id, $limit);
        } else {
            $data_import = $this->imported_data_parsed_model->getData($s, $sl, $cat_id);
        }

        if (empty($data_import)) {
            $this->load->library('PageProcessor');
			if ($this->pageprocessor->isURL($this->input->post('s'))) {
				$parsed_data = $this->pageprocessor->get_data($this->input->post('s'));
				$data_import[0] = $parsed_data;
				$data_import[0]['url'] = $this->input->post('s');
				$data_import[0]['imported_data_id'] = 0;
			}
		}

        $data['search_results'] = $data_import;
        $this->load->view('measure/searchmeasuredball', $data);
    }

    public function attributesmeasure() {

        $s = $this->input->post('s');

        $data = array('search_results'=>'', 'file_id'=>'', 'product_descriptions' => '', 'product_title' => '');
        $attributes = array();

        $attr_path = $this->config->item('attr_path');

        if ($path = realpath($attr_path)) {
            $objects = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path), RecursiveIteratorIterator::SELF_FIRST);
            foreach ($objects as $name => $object){
                if (!$object->isDir()) {
                    if ($object->getFilename() == 'attributes.dat') {
                        if ($content= file_get_contents($name)) {
                            if (preg_match("/$s/i",$content,$matches)) {

                                $part = str_ireplace($attr_path, '', $object->getPath());
                                if (preg_match('/\D*(\d*)/i',$part,$matches)) {
                                    $data['file_id'] = $matches[1];
                                }

                                foreach ($this->config->item('attr_replace') as $replacement) {
                                    $content = str_replace(array_keys($replacement), array_values($replacement), $content);
                                }

                                $data['search_results'] = nl2br($content);

                                if (preg_match_all('/\s?(\S*)\s*(.*)/i', $content, $matches)) {
                                    foreach($matches[1] as $i=>$v) {
                                        if (!empty($v))
                                        $attributes[strtoupper($v)] = $matches[2][$i];
                                    }
                                }

                                if (!empty($attributes)) {
                                    $title = array();
                                    foreach ($this->settings['product_title'] as $v) {
                                        if (isset($attributes[strtoupper($v)]))
                                            $title[] = $attributes[strtoupper($v)   ];
                                    }
                                    $data['product_title'] = implode(' ', $title);
                                    $data['attributes'] = $attributes;
                                }
                                break;
                            }
                        }
                    }
                }
            }
        }

        if ($this->system_settings['java_generator']) {
            $descCmd = str_replace($this->config->item('cmd_mask'), $data['file_id'] ,$this->system_settings['java_cmd']);
            if ($result = shell_exec($descCmd)) {
                if (preg_match_all('/\(.*\)\: "(.*)"/i',$result,$matches) && isset($matches[1]) && count($matches[1])>0) {
                    if( is_array($data['product_descriptions']) )
                        $data['product_descriptions'] = array_merge($data['product_descriptions'], $matches[1]);
                    else
                        $data['product_descriptions'] = $matches[1];
                }
            }
        }
        if ($this->system_settings['python_generator']) {
            $descCmd = str_replace($this->config->item('cmd_mask'), $s ,$this->system_settings['python_cmd']);
            if ($result = shell_exec($descCmd)) {
                if (preg_match_all('/.*ELECTR_DESCRIPTION:\s*(.*)\s*-{5,}/',$result,$matches)) {
                    if( is_array($data['product_descriptions']) )
                        $data['product_descriptions'] = array_merge($data['product_descriptions'], $matches[1]);
                    else
                        $data['product_descriptions'] = $matches[1];
                }
            }
        }

        if(!empty($this->exceptions) && !empty($data['attributes'])){
            foreach ($data['attributes'] as $key => $value) {
                foreach ($this->exceptions as $exception) {
                    if($exception['attribute_name'] == $key AND $exception['attribute_value'] == $value){
                        foreach ($data['product_descriptions'] as $pd_key => $product_description) {
                            foreach ($exception['exception_values'] as $exception_value) {
                                if (stristr($product_description, $exception_value)) {
                                    unset($data['product_descriptions'][$pd_key]);
                                }
                            }
                        }
                        sort($data['product_descriptions']);
                    }
                }
            }
        }

        $this->output->set_content_type('application/json')
            ->set_output(json_encode($data));

    }

}