<?php

if (!defined('BASEPATH'))
    exit('No direct script access allowed');

class Crons extends MY_Controller {

    function __construct() {
        parent::__construct();
        $this->load->library('ion_auth');
        $this->ion_auth->add_auth_rules(array(
            'index' => true,
            'screenscron' => true,
            'do_stats' => true,
            'duplicate_content' => true,
            'do_stats_new' => true,
            'do_duplicate_content' => true,
        ));
    }

    public function index() {
        
    }

    private function urlExists($url) {
        if ($url === null || trim($url) === "")
            return false;
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_TIMEOUT, 5);
        curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        $data = curl_exec($ch);
        $httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        if ($httpcode >= 200 && $httpcode <= 302) {
            return true;
        } else {
            return false;
        }
    }

    private function webthumb_call($url) {
        $webthumb_user_id = $this->config->item('webthumb_user_id');
        $api_key = $this->config->item('webthumb_api_key');
        $url = "http://$url";
        $c_date = gmdate('Ymd', time());
        $hash = md5($c_date . $url . $api_key);
        $e_url = urlencode(trim($url));
        return $res = array(
            "s" => "http://webthumb.bluga.net/easythumb.php?user=$webthumb_user_id&url=$e_url&hash=$hash&size=medium2",
            'l' => "http://webthumb.bluga.net/easythumb.php?user=$webthumb_user_id&url=$e_url&hash=$hash&size=large"
        );
    }

    private function customers_list() {
        $this->load->model('customers_model');
        $output = array();
        $customers_init_list = $this->customers_model->getAll();
        if (count($customers_init_list) > 0) {
            foreach ($customers_init_list as $key => $value) {
                $c_url = preg_replace('#^https?://#', '', $value->url);
                $c_url = preg_replace('#^www.#', '', $c_url);
                $mid = array(
                    'id' => $value->id,
                    'desc' => $value->description,
                    'image_url' => $value->image_url,
                    'name' => $value->name,
                    'name_val' => strtolower($value->name),
                    'c_url' => $c_url
                );
                $output[] = $mid;
            }
        }
        return $output;
    }

    private function upload_record_webshoot($ext_url, $url_name) {
        $file = file_get_contents($ext_url);
        $type = 'png';
        $dir = realpath(BASEPATH . "../webroot/webshoots");
        if (!file_exists($dir)) {
            mkdir($dir);
            chmod($dir, 0777);
        }
        // --- NEW STUFF (TIMESTAMP BASED IMAGES NAMES) (START)
        $url_name = $url_name . "-" . date('Y-m-d-H-i-s', time());
        // --- NEW STUFF (TIMESTAMP BASED IMAGES NAMES) (END)
        $t = file_put_contents($dir . "/$url_name.$type", $file);
        $path = base_url() . "webshoots/$url_name.$type";
        $res = array(
            'path' => $path,
            'dir' => $dir . "/$url_name.$type"
        );
        return $res;
    }

    /**
     * Cron Job for CI home tab screenshots generating
     */
    public function screenscron() {
        // $customers = $this->customers_list();
        //       $this->load->model('webshoots_model');
        //       $week = date("W", time());
        //       $year = date("Y", time());
        //       $sites = array();
        //       $primary_source_res = $this->urlExists('http://snapito.com');
        //       if($primary_source_res) { // ===== PRIMARY SCREENCAPTURE API (http://snapito.com/)
        //           $screen_api = 'snapito.com';
        //       } else { // ===== PRIMARY SCREENCAPTURE API (http://webyshots.com/)
        //           $screen_api = 'webyshots.com';
        //       }
        //       foreach ($customers as $k => $v) {
        //           if($this->urlExists($v['c_url'])) $sites[] = $v['c_url'];
        //       }
        //       foreach ($sites as $url) {
        //           $c_url = urlencode(trim($url));
        //           if($screen_api == 'snapito.com') {
        //               $api_key = $this->config->item('snapito_api_secret');
        //               if(in_array($url, $this->config->item('webthumb_sites'))) {
        //                   $res = $this->webthumb_call($url);
        //               } else {
        //                   $res = array(
        //                       "s" => "http://api.snapito.com/web/$api_key/mc/$url",
        //                       'l' => "http://api.snapito.com/web/$api_key/full/$url"
        //                   );
        //               }
        //           } else {
        //               $api_key = $this->config->item('webyshots_api_key');
        //               $api_secret = $this->config->item('webyshots_api_secret');
        //               $token = md5("$api_secret+$url");
        //               $size_s = "w600";
        //               $size_l = "w1260";
        //               $format = "png";
        //               $res = array(
        //                   "s" => "http://api.webyshots.com/v1/shot/$api_key/$token/?url=$c_url&dimension=$size_s&format=$format",
        //                   'l' => "http://api.webyshots.com/v1/shot/$api_key/$token/?url=$c_url&dimension=$size_l&format=$format"
        //               );
        //           }
        //           $crawl_s = $this->upload_record_webshoot($res['s'], $url."_small");
        //           $crawl_l = $this->upload_record_webshoot($res['l'], $url."_big");
        //           $result = array(
        //               'state' => false,
        //               'url' => $url,
        //               'small_crawl' => $crawl_s['path'],
        //               'big_crawl' => $crawl_l['path'],
        //               'dir_thumb' => $crawl_s['dir'],
        //               'dir_img' => $crawl_l['dir'],
        //               'uid' => 0,
        //               'year' => $year,
        //               'week' => $week,
        //               'pos' => 0
        //           );
        //           $insert_id = $this->webshoots_model->recordUpdateWebshoot($result);
        //       }
        echo "Cron Job Finished";
    }

    /**
     * Cron Job for CI home tab screenshots reports mailer
     */
    public function emailreports() {
        // $this->load->model('webshoots_model');
        // $current_day = lcfirst(date('l', time()));
        // $recs = $this->webshoots_model->get_recipients_list();
        // if(count($recs) > 0) {
        //     // --- mailer config (start)
        //     $this->load->library('email');
        //     $config['protocol'] = 'sendmail';
        //     $config['mailpath'] = '/usr/sbin/sendmail';
        //     $config['charset'] = 'UTF-8';
        //     $config['wordwrap'] = TRUE;
        //     $this->email->initialize($config);
        //     // --- mailer config (end)
        //     foreach ($recs as $k => $v) {
        //         if($v->day == $current_day) {
        //             $day = $v->day;
        //             $email = $v->email;
        //             $id = $v->id;
        //             $this->email->from('ishulgin8@gmail.com', "Content Solutions - Home Pages Report");
        //             $this->email->to("$email");
        //             $this->email->subject('Content Solutions - Home Pages Report');
        //             $this->email->message("Report screenshots in attachment. Preference day: $day.");
        //             // --- test (debug) attachments (start)
        //             $debug_screens = $this->webshoots_model->getLimitedScreens(3);
        //             if(count($debug_screens) > 0) {
        //                 foreach ($debug_screens as $key => $value) {
        //                     $path = $value->dir_thumb;
        //                     $this->email->attach("$path");
        //                 }
        //             }
        //             // --- test (debug) attachments (end)
        //             $this->email->send();
        //             echo "Report sended to $v->email"."<br>";
        //         }
        //     }
        // }
        echo "Cron Job Finished";
    }
    function send_email_report($subject, $message){
        $this->load->library('email');
            $this->email->from('info@dev.contentsolutionsinc.com', '!!!!');
            $this->email->to('bayclimber@gmail.com');
            $this->email->cc('max.kavelin@gmail.com');
            $this->email->subject($subject);
            $this->email->message($message);
            $this->email->send();
    }
    public function do_duplicate_content() {
        $this->load->model('imported_data_parsed_model');
        $this->load->model('research_data_model');
        $this->load->model('statistics_model');
        $this->load->model('statistics_duplicate_content_model');
        $this->load->model('similar_product_groups_model');
        $this->load->model('similar_data_model');
        $this->load->library('helpers');
        $this->load->helper('algoritm');
        $this->load->model('sites_model');
        $ids = $this->imported_data_parsed_model->do_stats_ids();
      
        foreach ($ids as $val) {
            $query = $this->db->where('imported_data_id', $val->imported_data_id)
            ->get('duplicate_content_new');
            if ($query->num_rows()==0){
                $this->duplicate_content_new($val->imported_data_id);
            }
        }
        $q = $this->db->select('key,description')->from('settings')->where('key', 'duplicate_offset');
        $res = $q->get()->row_array();
        $start = $res['description'];
        $start++;
        $data = array(
            'description' => $start
        );

        $this->db->where('key', 'duplicate_offset');
        $this->db->update('settings', $data);
        $data_arr=$this->imported_data_parsed_model->do_stats_ids();
        if (count($data_arr) > 1) {
            shell_exec('wget -S -O- http://dev.contentsolutionsinc.com/producteditor/index.php/crons/do_duplicate_content > /dev/null 2>/dev/null &');
        } else {
            $data = array(
                'description' => 0
            );

            $this->db->where('key', 'duplicate_offset');
            $this->db->update('settings', $data);

            $this->load->library('email');
            $this->email->from('info@dev.contentsolutionsinc.com', '!!!!');
            $this->email->to('bayclimber@gmail.com');
            $this->email->cc('max.kavelin@gmail.com');
            $this->email->subject('Cron job report');
            $this->email->message('Cron job for do_duplicate_content is done');
            $this->email->send();
        }
    }
    public function do_stats_new_test(){
        $id=1103;
        $this->load->model('imported_data_parsed_model');
        $this->load->model('research_data_model');
        $this->load->model('statistics_model');
        $this->load->model('statistics_duplicate_content_model');
        $this->load->model('similar_imported_data_model');
        $this->load->model('similar_product_groups_model');
        $this->load->model('similar_data_model');
        $this->load->library('helpers');
        $this->load->helper('algoritm');
        $this->load->model('sites_model');//do_stats_new_test
        $data_import = $this->imported_data_parsed_model->do_stats_new_test($id);
        $obj=$data_import[0];
        $data_import=(array)$data_import[0];
        
       // print_r($data_import);
        $own_price = 0;
        $competitors_prices = array();
        $price_diff = '';
        $items_priced_higher_than_competitors = 0;
        $short_description_wc = 0;
        $long_description_wc = 0;
        $short_seo_phrases = '?';
        $long_seo_phrases = '?';
        $similar_products_competitors = array();
        
        
        $sites_list = array();
                $query_cus = $this->similar_imported_data_model->db->order_by('name', 'asc')->get('sites');
                $query_cus_res = $query_cus->result();
                if (count($query_cus_res) > 0) {
                    foreach ($query_cus_res as $key => $value) {
                        $n = parse_url($value->url);
                        $sites_list[] = $n['host'];
                    }
                }
        
       
         if (isset($data_import['parsed_attributes']) && isset($data_import['parsed_attributes']['model'])) {

                        try {
                            $own_prices = $this->imported_data_parsed_model->getLastPrices($obj->imported_data_id);
                        } catch (Exception $e) {
                            echo 'РћС€РёР±РєР°', $e->getMessage(), "\n";
                            $own_prices = $this->imported_data_parsed_model->getLastPrices($obj->imported_data_id);
                        }

                        if (!empty($own_prices)) {
                            $own_price = floatval($own_prices[0]->price);
                            $obj->own_price = $own_price;
                            $price_diff_exists = array(); //"<input type='hidden'/>";
                            $price_diff_exists['id'] = $own_prices[0]->id;
                            $price_diff_exists['own_site'] = $own_site;
                            $price_diff_exists['own_price'] = floatval($own_price);
                        }
                            
                        echo '!!!!'.$data_import['parsed_attributes']['model'];
                        $similar_items = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['model']);
                           
 
        
                            if (!empty($similar_items)) {
                              
                                foreach ($similar_items as $ks => $vs) {
                                    $similar_item_imported_data_id = $similar_items[$ks]['imported_data_id'];
                                    if ($obj->imported_data_id == $similar_item_imported_data_id) {
                                        continue;
                                    }
//                                          $n = parse_url($vs['url']);
//                                          $customer=  strtolower($n['host']);
//                                          $customer = str_replace("www1.", "",$customer);
//                                          $customer =str_replace("www.", "", $customer);
                                    $customer = "";
                                    foreach ($sites_list as $ki => $vi) {
                                        if (strpos($vs['url'], "$vi") !== false) {
                                            $customer = $vi;
                                        }
                                    }


                                    $customer = strtolower($this->sites_model->get_name_by_url($customer));
                                    $similar_products_competitors[] = array(
                                        'imported_data_id' => $similar_item_imported_data_id,
                                        'customer' => $customer
                                    );

                                    try {
                                        $three_last_prices = $this->imported_data_parsed_model->getLastPrices($similar_item_imported_data_id);
                                    } catch (Exception $e) {
                                        echo 'РћС€РёР±РєР°', $e->getMessage(), "\n";
//                                        $this->statistics_model->db->close();
//                                        $this->statistics_model->db->initialize();
                                        $three_last_prices = $this->imported_data_parsed_model->getLastPrices($similar_item_imported_data_id);
                                    }

                                    if (!empty($three_last_prices)) {
                                        $price_scatter = $own_price * 0.03;
                                        $price_upper_range = $own_price + $price_scatter;
                                        $price_lower_range = $own_price - $price_scatter;
                                        $competitor_price = floatval($three_last_prices[0]->price);
                                        if ($competitor_price < $own_price) {
                                            $items_priced_higher_than_competitors = 1;
                                        }
                                        if ($competitor_price > $price_upper_range || $competitor_price < $price_lower_range) {
                                            $price_diff_exists['competitor_customer'][] = $similar_items[$ks]['customer'];
                                            $price_diff_exists['competitor_price'][] = $competitor_price;
                                            $price_diff = $price_diff_exists;
                                            $competitors_prices[] = $competitor_price;
                                        }
                                    }
                                }
                            }
                        

//                        $n = parse_url($data_import['url']);
//                                     $customer=  strtolower($n['host']);
//                                     $customer = str_replace("www1.", "",$customer);
//                                     $customer =str_replace("www.", "", $customer);

                        $customer = "";
                        foreach ($sites_list as $ki => $vi) {
                            if (strpos($data_import['url'], "$vi") !== false) {
                                $customer = $vi;
                            }
                        }

                        $customer = strtolower($this->sites_model->get_name_by_url($customer));

                        $similar_products_competitors[] = array(
                            'imported_data_id' => $data_import['imported_data_id'],
                            'customer' => $customer
                        );



                        $rows = $this->similar_data_model->get_group_id($data_import['imported_data_id']);
                        if (count($rows) > 0) {

                            foreach ($similar_products_competitors as $val) {
                                foreach ($rows as $key => $row) {
                                    if ($row['group_id'] == $val['imported_data_id']) {
                                        unset($rows[$key]);
                                    }
                                }
                            }
                        }
                        if (count($rows) > 0) {
                            $url = array();
                            foreach ($rows as $row) {
                                $data_similar = $this->imported_data_parsed_model->getByImId($row['group_id']);
                                $n = parse_url($data_similar['url']);
                                $customer = $n['host'];
                                $data_similar[$key]['customer'] = $customer;

                                if (!in_array($customer, $url)) {
                                    $url[] = $customer;
                                    $customer = "";
                                    foreach ($sites_list as $ki => $vi) {
                                        if (strpos($data_similar['url'], "$vi") !== false) {
                                            $customer = $vi;
                                        }
                                    }
                                    $customer = strtolower($this->sites_model->get_name_by_url($customer));
                                    $similar_products_competitors[] = array('imported_data_id' => $row['group_id'], 'customer' => $customer);
                                }
                            }
                        }
                    }
        
        
        print_r($similar_products_competitors);
        
       
    }
    public function do_stats_new() {
        echo "Script start working";
        $tmp_dir = sys_get_temp_dir() . '/';
        unlink($tmp_dir . ".locked");
        if (file_exists($tmp_dir . ".locked")) {
            exit;
        }

        touch($tmp_dir . ".locked");
        try {
            $this->load->model('imported_data_parsed_model');
            $this->load->model('research_data_model');
            $this->load->model('statistics_model');
            $this->load->model('statistics_duplicate_content_model');
            $this->load->model('similar_imported_data_model');
            $this->load->model('similar_product_groups_model');
            $this->load->model('similar_data_model');
            $this->load->library('helpers');
            $this->load->helper('algoritm');
            $this->load->model('sites_model');
            $trnc=$this->input->get('runcate');
            if(!$trnc){
                $trnc=1;
            }
            $data_arr = $this->imported_data_parsed_model->do_stats($trnc);
            if (count($data_arr) > 1) {

                $sites_list = array();
                $query_cus = $this->similar_imported_data_model->db->order_by('name', 'asc')->get('sites');
                $query_cus_res = $query_cus->result();
                if (count($query_cus_res) > 0) {
                    foreach ($query_cus_res as $key => $value) {
                        $n = parse_url($value->url);
                        $sites_list[] = $n['host'];
                    }
                }

                foreach ($data_arr as $obj) {
                    $own_price = 0;
                    $competitors_prices = array();
                    $price_diff = '';
                    $items_priced_higher_than_competitors = 0;
                    $short_description_wc = 0;
                    $long_description_wc = 0;
                    $short_seo_phrases = '?';
                    $long_seo_phrases = '?';
                    $similar_products_competitors = array();
                    // Price difference
                    $own_site = parse_url($obj->url, PHP_URL_HOST);
                    if (!$own_site)
                        $own_site = "own site";
                    $own_site = str_replace("www1.", "", str_replace("www.", "", $own_site));

                    // Price difference
                    $own_site = parse_url($obj->url, PHP_URL_HOST);
                    if (!$own_site)
                        $own_site = "own site";
                    $own_site = str_replace("www.", "", $own_site);

                    $data_import = (array) $obj;
                    if ($data_import['description'] !== null && trim($data_import['description']) !== "") {

                        $data_import['description'] = preg_replace('/[^a-zA-Z0-9_ %\[\]\.\(\)%&-]/s', '', $data_import['description']);
                        $data_import['description'] = preg_replace('/\s+/', ' ', $data_import['description']);
                        $data_import['description'] = preg_replace('/[a-zA-Z]-/', ' ', $data_import['description']);
                        $short_description_wc = count(explode(" ", $data_import['description']));
                    } else {
                        $short_description_wc = 0;
                    }
                    if ($data_import['long_description'] !== null && trim($data_import['long_description']) !== "") {

                        $data_import['long_description'] = preg_replace('/[^a-zA-Z0-9_ %\[\]\.\(\)%&-]/s', '', $data_import['long_description']);
                        $data_import['long_description'] = preg_replace('/\s+/', ' ', $data_import['long_description']);
                        $data_import['long_description'] = preg_replace('/[a-zA-Z]-/', ' ', $data_import['long_description']);
                        $long_description_wc = count(explode(" ", $data_import['long_description']));
                    } else {
                        $long_description_wc = 0;
                    }




                    // SEO Short phrases
                    $time_start = microtime(true);
                    if ($short_description_wc != 0) {

                        $short_seo_phrases = $this->helpers->measure_analyzer_start_v2_product_name($data_import['product_name'], preg_replace('/\s+/', ' ', $data_import['description']));
                        if (count($short_seo_phrases) > 0) {

                            foreach ($short_seo_phrases as $key => $val) {
                                $words = count(explode(' ', $val['ph']));
                                $desc_words_count = count(explode(' ', $data_import['description']));
                                $count = $val['count'];
                                $val['prc'] = number_format($count * $words / $desc_words_count * 100, 2);
                                $short_seo_phrases[$key] = $val;
                            }

                            $short_seo_phrases = serialize($short_seo_phrases);
                        } else {
                            $short_seo_phrases = "None";
                        }
                    } else {
                        $short_seo_phrases = 'None';
                    }

                    $time_end = microtime(true);
                    $time = $time_end - $time_start;
                    echo "SEO Short phrases - $time seconds\n";
                    // SEO Long phrases
                    $time_start = microtime(true);
                    if ($long_description_wc != 0) {

                        $long_seo_phrases = $this->helpers->measure_analyzer_start_v2_product_name($data_import['product_name'], preg_replace('/\s+/', ' ', $data_import['long_description']));
                        if (count($long_seo_phrases) > 0) {
                            foreach ($long_seo_phrases as $key => $val) {
                                $words = count(explode(' ', $val['ph']));
                                $desc_words_count = count(explode(' ', $data_import['long_description']));
                                $count = $val['count'];
                                $val['prc'] = number_format($count * $words / $desc_words_count * 100, 2);
                                $long_seo_phrases[$key] = $val;
                            }
                            $long_seo_phrases = serialize($long_seo_phrases);
                        } else {
                            $long_seo_phrases = "None";
                        }
                    } else {
                        $long_seo_phrases = 'None';
                    }
                    $time_end = microtime(true);
                    $time = $time_end - $time_start;
                    echo "SEO Long phrases - $time seconds\n";


                    $time_start = microtime(true);
                    if (isset($data_import['parsed_attributes']) && isset($data_import['parsed_attributes']['model'])) {

                        try {
                            $own_prices = $this->imported_data_parsed_model->getLastPrices($obj->imported_data_id);
                        } catch (Exception $e) {
                            echo 'РћС€РёР±РєР°', $e->getMessage(), "\n";
                            $own_prices = $this->imported_data_parsed_model->getLastPrices($obj->imported_data_id);
                        }

                        if (!empty($own_prices)) {
                            $own_price = floatval($own_prices[0]->price);
                            $obj->own_price = $own_price;
                            $price_diff_exists = array(); //"<input type='hidden'/>";
                            $price_diff_exists['id'] = $own_prices[0]->id;
                            $price_diff_exists['own_site'] = $own_site;
                            $price_diff_exists['own_price'] = floatval($own_price);
                        
                            try {
                                $similar_items = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['model']);
                            } catch (Exception $e) {
                                echo 'РћС€РёР±РєР°', $e->getMessage(), "\n";
                               
                                $similar_items = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['model']);
                            }

                            if (!empty($similar_items)) {
                                foreach ($similar_items as $ks => $vs) {
                                    $similar_item_imported_data_id = $similar_items[$ks]['imported_data_id'];
                                    if ($obj->imported_data_id == $similar_item_imported_data_id) {
                                        continue;
                                    }
//                                          $n = parse_url($vs['url']);
//                                          $customer=  strtolower($n['host']);
//                                          $customer = str_replace("www1.", "",$customer);
//                                          $customer =str_replace("www.", "", $customer);
                                    $customer = "";
                                    foreach ($sites_list as $ki => $vi) {
                                        if (strpos($vs['url'], "$vi") !== false) {
                                            $customer = $vi;
                                        }
                                    }


                                    $customer = strtolower($this->sites_model->get_name_by_url($customer));
                                    $similar_products_competitors[] = array(
                                        'imported_data_id' => $similar_item_imported_data_id,
                                        'customer' => $customer
                                    );

                                    try {
                                        $three_last_prices = $this->imported_data_parsed_model->getLastPrices($similar_item_imported_data_id);
                                    } catch (Exception $e) {
                                        echo 'РћС€РёР±РєР°', $e->getMessage(), "\n";
                                        $this->statistics_model->db->close();
                                        $this->statistics_model->db->initialize();
                                        $three_last_prices = $this->imported_data_parsed_model->getLastPrices($similar_item_imported_data_id);
                                    }

                                    if (!empty($three_last_prices)) {
                                        $price_scatter = $own_price * 0.03;
                                        $price_upper_range = $own_price + $price_scatter;
                                        $price_lower_range = $own_price - $price_scatter;
                                        $competitor_price = floatval($three_last_prices[0]->price);
                                        if ($competitor_price < $own_price) {
                                            $items_priced_higher_than_competitors = 1;
                                        }
                                        if ($competitor_price > $price_upper_range || $competitor_price < $price_lower_range) {
                                            $price_diff_exists['competitor_customer'][] = $similar_items[$ks]['customer'];
                                            $price_diff_exists['competitor_price'][] = $competitor_price;
                                            $price_diff = $price_diff_exists;
                                            $competitors_prices[] = $competitor_price;
                                        }
                                    }
                                }
                            }
                        }else{
                             try {
                                $similar_items = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['model']);
                            } catch (Exception $e) {
                                echo 'РћС€РёР±РєР°', $e->getMessage(), "\n";
                               
                                $similar_items = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['model']);
                            }

                            if (!empty($similar_items)) {
                                foreach ($similar_items as $ks => $vs) {
                                    $similar_item_imported_data_id = $similar_items[$ks]['imported_data_id'];
                                    if ($obj->imported_data_id == $similar_item_imported_data_id) {
                                        continue;
                                    }
//                                          $n = parse_url($vs['url']);
//                                          $customer=  strtolower($n['host']);
//                                          $customer = str_replace("www1.", "",$customer);
//                                          $customer =str_replace("www.", "", $customer);
                                    $customer = "";
                                    foreach ($sites_list as $ki => $vi) {
                                        if (strpos($vs['url'], "$vi") !== false) {
                                            $customer = $vi;
                                        }
                                    }


                                    $customer = strtolower($this->sites_model->get_name_by_url($customer));
                                    $similar_products_competitors[] = array(
                                        'imported_data_id' => $similar_item_imported_data_id,
                                        'customer' => $customer
                                    );
                                }
                            }
                        }

//                        $n = parse_url($data_import['url']);
//                                     $customer=  strtolower($n['host']);
//                                     $customer = str_replace("www1.", "",$customer);
//                                     $customer =str_replace("www.", "", $customer);

                        $customer = "";
                        foreach ($sites_list as $ki => $vi) {
                            if (strpos($data_import['url'], "$vi") !== false) {
                                $customer = $vi;
                            }
                        }

                        $customer = strtolower($this->sites_model->get_name_by_url($customer));

                        $similar_products_competitors[] = array(
                            'imported_data_id' => $data_import['imported_data_id'],
                            'customer' => $customer
                        );



                        $rows = $this->similar_data_model->get_group_id($data_import['imported_data_id']);
                        if (count($rows) > 0) {

                            foreach ($similar_products_competitors as $val) {
                                foreach ($rows as $key => $row) {
                                    if ($row['group_id'] == $val['imported_data_id']) {
                                        unset($rows[$key]);
                                    }
                                }
                            }
                        }
                        if (count($rows) > 0) {
                            $url = array();
                            foreach ($rows as $row) {
                                $data_similar = $this->imported_data_parsed_model->getByImId($row['group_id']);
                                $n = parse_url($data_similar['url']);
                                $customer = $n['host'];
                                $data_similar[$key]['customer'] = $customer;

                                if (!in_array($customer, $url)) {
                                    $url[] = $customer;
                                    $customer = "";
                                    foreach ($sites_list as $ki => $vi) {
                                        if (strpos($data_similar['url'], "$vi") !== false) {
                                            $customer = $vi;
                                        }
                                    }
                                    $customer = strtolower($this->sites_model->get_name_by_url($customer));
                                    $similar_products_competitors[] = array('imported_data_id' => $row['group_id'], 'customer' => $customer);
                                }
                            }
                        }
                    } else {
                        $im_data_id = $data_import['imported_data_id'];
                        if (!$this->similar_product_groups_model->checkIfgroupExists($data_import['imported_data_id'])) {

                            if (!isset($data_import['parsed_attributes'])) {

                                $same_pr = $this->imported_data_parsed_model->getByProductName($im_data_id, $data_import['product_name'], '', $strict);
                            }
                            if (isset($data_import['parsed_attributes'])) {

                                $same_pr = $this->imported_data_parsed_model->getByProductName($im_data_id, $data_import['product_name'], $data_import['parsed_attributes']['manufacturer'], $strict);
                            }
                        } else {

                            $rows = $this->similar_data_model->getByGroupId($im_data_id);
                            $data_similar = array();

                            foreach ($rows as $key => $row) {

                                $data_similar = $this->imported_data_parsed_model->getByImId($row->imported_data_id);
//                                    $n = parse_url($data_similar['url']);
//                                    $customer=  strtolower($n['host']);
//                                    $customer = str_replace("www1.", "",$customer);
//                                    $customer =str_replace("www.", "", $customer);
                                $customer = "";
                                foreach ($sites_list as $ki => $vi) {
                                    if (strpos($data_similar['url'], "$vi") !== false) {
                                        $customer = $vi;
                                    }
                                }

                                $customer = strtolower($this->sites_model->get_name_by_url($customer));
                                $similar_products_competitors[] = array('imported_data_id' => $row->imported_data_id, 'customer' => $customer);
                            }
                        }
                    }
                    $time_end = microtime(true);
                    $time = $time_end - $time_start;
//                          echo "price_diff - $time seconds\n";
                    // WC Short



                    $time_start = microtime(true);

                    try {
                        $insert_id = $this->statistics_model->insert_new($obj->imported_data_id, $obj->revision, $short_description_wc, $long_description_wc, $short_seo_phrases, $long_seo_phrases, $own_price, serialize($price_diff), serialize($competitors_prices), $items_priced_higher_than_competitors, serialize($similar_products_competitors)
                        );
                    } catch (Exception $e) {
                        echo 'РћС€РёР±РєР°', $e->getMessage(), "\n";
                        $this->statistics_model->db->close();
                        $this->statistics_model->db->initialize();

                        $insert_id = $this->statistics_model->insert_new($obj->imported_data_id, $obj->revision, $short_description_wc, $long_description_wc, $short_seo_phrases, $long_seo_phrases, $own_price, serialize($price_diff), serialize($competitors_prices), $items_priced_higher_than_competitors, serialize($similar_products_competitors));
                    }

                    $time_end = microtime(true);
                    $time = $time_end - $time_start;

                    echo '.';
                }

                $q = $this->db->select('key,description')->from('settings')->where('key', 'cron_job_offset');
                $res = $q->get()->row_array();
                $start = $res['description'];
                $start++;
                $data = array(
                    'description' => $start
                );

                $this->db->where('key', 'cron_job_offset');
                $this->db->update('settings', $data);
            }
        } catch (Exception $e) {
            echo 'Ошибка', $e->getMessage(), "\n";
            unlink($tmp_dir . ".locked");
        }
        unlink($tmp_dir . ".locked");
        $data_arr = $this->imported_data_parsed_model->do_stats();
        $q = $this->db->select('key,description')->from('settings')->where('key', 'cron_job_offset');
        $res = $q->get()->row_array();
        $start = $res['description'];
        if (count($data_arr) > 1) {
            shell_exec("wget -S -O- http://dev.contentsolutionsinc.com/producteditor/index.php/crons/do_stats_new/truncate/0 > /dev/null 2>/dev/null &");
        } else {
            $data = array(
                'description' => 0
            );

            $this->db->where('key', 'cron_job_offset');
            $this->db->update('settings', $data);

            $this->load->library('email');
            $this->email->from('info@dev.contentsolutionsinc.com', '!!!!');
            $this->email->to('bayclimber@gmail.com');
            $this->email->cc('max.kavelin@gmail.com');
            $this->email->subject('Cron job report');
            $this->email->message('Cron job for do_statistics_new is done');
            $this->email->send();
        }
    }

    public function do_stats_test() {
        echo "Script start working";
        $tmp_dir = sys_get_temp_dir() . '/';
        unlink($tmp_dir . ".locked");
        if (file_exists($tmp_dir . ".locked")) {
            exit;
        }

        touch($tmp_dir . ".locked");
        try {
            $this->load->model('batches_model');
            $this->load->model('research_data_model');
            $this->load->model('statistics_model');
            $this->load->model('statistics_duplicate_content_model');
            $this->load->model('imported_data_parsed_model');
            $this->statistics_model->truncate();
            $this->statistics_duplicate_content_model->truncate();
            $batches = $this->batches_model->getAll('id');
            $enable_exec = true;
            $conn = mysql_connect('localhost', 'c38trlmonk', '542piF88');
            foreach ($batches as $batch) {
                $batch_id = $batch->id;
                /* Make sure the connection is still alive, if not, try to reconnect */
                //if (!mysql_ping($conn)) {
                //echo 'Lost connection, exiting after query #2';
                //exit;
                //    $conn = mysql_connect('localhost', 'c38trlmonk', '542piF88');
                //}
                $data = $this->research_data_model->do_stats($batch->id);
                error_log("Problem after do_stats query", 3, 'log.txt');
                if (count($data) > 0) {
                    foreach ($data as $obj) {
                        $own_price = 0;
                        $competitors_prices = array();
                        $price_diff = '';
                        $items_priced_higher_than_competitors = 0;
                        $short_description_wc = 0;
                        $long_description_wc = 0;
                        $short_seo_phrases = '?';
                        $long_seo_phrases = '?';
                        $similar_products_competitors = array();
                        // Price difference
                        $own_site = parse_url($obj->url, PHP_URL_HOST);
                        if (!$own_site)
                            $own_site = "own site";
                        $own_site = str_replace("www1.", "", str_replace("www.", "", $own_site));

                        // Price difference
                        $own_site = parse_url($obj->url, PHP_URL_HOST);
                        if (!$own_site)
                            $own_site = "own site";
                        $own_site = str_replace("www.", "", $own_site);

                        $time_start = microtime(true);
                        $data_import = $this->imported_data_parsed_model->getByImId($obj->imported_data_id);
                        $time_end = microtime(true);
                        $time = $time_end - $time_start;
                        echo "data_import - $time seconds\n";

                        $time_start = microtime(true);
                        if (isset($data_import['parsed_attributes']) && isset($data_import['parsed_attributes']['model'])) {
                            $own_prices = $this->imported_data_parsed_model->getLastPrices($obj->imported_data_id);
                            if (!empty($own_prices)) {
                                $own_price = floatval($own_prices[0]->price);
                                $obj->own_price = $own_price;
                                $price_diff_exists = array(); //"<input type='hidden'/>";
                                $price_diff_exists['id'] = $own_prices[0]->id;
                                $price_diff_exists['own_site'] = $own_site;
                                $price_diff_exists['own_price'] = floatval($own_price);
                                $similar_items = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['model']);
                                if (!empty($similar_items)) {
                                    foreach ($similar_items as $ks => $vs) {
                                        $similar_item_imported_data_id = $similar_items[$ks]['imported_data_id'];
                                        if ($obj->imported_data_id == $similar_item_imported_data_id) {
                                            continue;
                                        }
                                        $similar_products_competitors[] = array(
                                            'imported_data_id' => $similar_item_imported_data_id,
                                            'customer' => $similar_items[$ks]['customer']
                                        );
                                        $three_last_prices = $this->imported_data_parsed_model->getLastPrices($similar_item_imported_data_id);
                                        if (!empty($three_last_prices)) {
                                            $price_scatter = $own_price * 0.03;
                                            $price_upper_range = $own_price + $price_scatter;
                                            $price_lower_range = $own_price - $price_scatter;
                                            $competitor_price = floatval($three_last_prices[0]->price);
                                            if ($competitor_price < $own_price) {
                                                $items_priced_higher_than_competitors = 1;
                                            }
                                            if ($competitor_price > $price_upper_range || $competitor_price < $price_lower_range) {
                                                $price_diff_exists['competitor_customer'][] = $similar_items[$ks]['customer'];
                                                $price_diff_exists['competitor_price'][] = $competitor_price;
                                                $price_diff = $price_diff_exists;
                                                $competitors_prices[] = $competitor_price;
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        $time_end = microtime(true);
                        $time = $time_end - $time_start;
                        echo "price_diff - $time seconds\n";

                        // WC Short
                        $time_start = microtime(true);
                        $short_description_wc = (count(preg_split('/\b/', $obj->short_description)) - 1) / 2;
                        if (is_null($obj->short_description_wc)) {
                            $this->imported_data_parsed_model->insert($obj->imported_data_id, "Description_WC", $short_description_wc);
                        } else {
                            if (intval($obj->short_description_wc) <> $short_description_wc) {
                                $this->imported_data_parsed_model->updateValueByKey($obj->imported_data_id, "Description_WC", $short_description_wc);
                            }
                        }
                        $time_end = microtime(true);
                        $time = $time_end - $time_start;
                        echo "WC Short - $time seconds\n";

                        // WC Long
                        $time_start = microtime(true);
                        $long_description_wc = (count(preg_split('/\b/', $obj->long_description)) - 1) / 2;
                        if (is_null($obj->long_description_wc)) {
                            $this->imported_data_parsed_model->insert($obj->imported_data_id, "Long_Description_WC", $long_description_wc);
                        } else {
                            if (intval($obj->long_description_wc) <> $long_description_wc) {
                                $this->imported_data_parsed_model->updateValueByKey($obj->imported_data_id, "Long_Description_WC", $long_description_wc);
                            }
                        }
                        $time_end = microtime(true);
                        $time = $time_end - $time_start;
                        echo "WC Long - $time seconds\n";

                        // SEO Short phrases
                        $time_start = microtime(true);
                        if ($short_description_wc == $obj->short_description_wc && !is_null($obj->short_seo_phrases)) {
                            $short_seo_phrases = $obj->short_seo_phrases;
                        } else {
                            if ($enable_exec) {
                                $cmd = $this->prepare_extract_phrases_cmd($obj->short_description);
                                $output = array();
                                exec($cmd, $output, $error);

                                if ($error > 0) {
                                    $enable_exec = false;
                                } else {
                                    $short_seo_phrases = $this->prepare_seo_phrases($output);
                                    if (is_null($obj->short_seo_phrases)) {
                                        $this->imported_data_parsed_model->insert($obj->imported_data_id, "short_seo_phrases", $short_seo_phrases);
                                    } else {
                                        $this->imported_data_parsed_model->updateValueByKey($obj->imported_data_id, "short_seo_phrases", $short_seo_phrases);
                                    }
                                }
                            }
                        }
                        $time_end = microtime(true);
                        $time = $time_end - $time_start;
                        echo "SEO Short phrases - $time seconds\n";
                        // SEO Long phrases
                        $time_start = microtime(true);
                        if ($long_description_wc == $obj->long_description_wc && !is_null($obj->long_seo_phrases)) {
                            $long_seo_phrases = $obj->long_seo_phrases;
                        } else {
                            if ($enable_exec) {
                                $cmd = $this->prepare_extract_phrases_cmd($obj->long_description);
                                $output = array();
                                exec($cmd, $output, $error);

                                if ($error > 0) {
                                    $enable_exec = false;
                                } else {
                                    $long_seo_phrases = $this->prepare_seo_phrases($output);
                                    if (is_null($obj->long_seo_phrases)) {
                                        $this->imported_data_parsed_model->insert($obj->imported_data_id, "long_seo_phrases", $long_seo_phrases);
                                    } else {
                                        $this->imported_data_parsed_model->updateValueByKey($obj->imported_data_id, "long_seo_phrases", $long_seo_phrases);
                                    }
                                }
                            }
                        }
                        $time_end = microtime(true);
                        $time = $time_end - $time_start;
                        echo "SEO Long phrases - $time seconds\n";

                        $time_start = microtime(true);
                        $insert_id = $this->statistics_model->insert($obj->rid, $obj->imported_data_id, $obj->research_data_id, $obj->batch_id, $obj->product_name, $obj->url, $obj->short_description, $obj->long_description, $short_description_wc, $long_description_wc, $short_seo_phrases, $long_seo_phrases, $own_price, serialize($price_diff), serialize($competitors_prices), $items_priced_higher_than_competitors, serialize($similar_products_competitors)
                        );
                        $time_end = microtime(true);
                        $time = $time_end - $time_start;
                        echo "insert_id - $time seconds\n";
                        var_dump($insert_id);
                        /* if($insert_id){
                          var_dump('--'.$obj->batch_id.'--');
                          } else {
                          print "<pre>";
                          print_r($obj->rid, $obj->imported_data_id,
                          $obj->research_data_id, $obj->batch_id,
                          $obj->product_name, $obj->url, $obj->short_description, $obj->long_description,
                          $short_description_wc, $long_description_wc,
                          $short_seo_phrases, $long_seo_phrases,
                          $own_price, serialize($price_diff), serialize($competitors_prices), $items_priced_higher_than_competitors);
                          print "</pre>";
                          die("error");
                          } */
                    }
                    /* $params = new stdClass();
                      $params->batch_id = $batch->id;
                      $params->txt_filter = '';
                      $stat_data= $this->statistics_model->getStatsData($params);
                      if(count($stat_data)>0){
                      foreach($stat_data as $stat){
                      $res_data = $this->check_duplicate_content($stat->imported_data_id);
                      foreach($res_data as $val){
                      $this->statistics_duplicate_content_model->insert($val['imported_data_id'],
                      $val['product_name'], $val['description'],
                      $val['long_description'], $val['url'],
                      $val['features'], $val['customer'],
                      $val['long_original'], $val['short_original']);
                      }
                      };
                      } */
                }
            }
            echo "Script finish working";
            echo "Cron Job Finished";
        } catch (Exception $e) {
            echo 'Ошибка', $e->getMessage(), "\n";
            unlink($tmp_dir . ".locked");
        }
        unlink($tmp_dir . ".locked");
    }

    public function do_stats() {
        echo "Script start working";
        $tmp_dir = sys_get_temp_dir() . '/';
        unlink($tmp_dir . ".locked");
        if (file_exists($tmp_dir . ".locked")) {
            exit;
        }

        touch($tmp_dir . ".locked");
        try {
            $subject='Cron Job Report - do_stats started';
            $message='Cron job for do_stats started';
            $this->send_email_report($subject,  $message);
            
            $this->load->model('batches_model');
            $this->load->model('research_data_model');
            $this->load->model('statistics_model');
            $this->load->model('statistics_duplicate_content_model');
            $this->load->model('imported_data_parsed_model');
            $this->statistics_model->truncate();
            $this->statistics_duplicate_content_model->truncate();
            $batches = $this->batches_model->getAll('id');
            $enable_exec = true;
//            $conn = mysql_connect('localhost', 'c38trlmonk', '542piF88');
            foreach ($batches as $batch) {
                $batch_id = $batch->id;
                /* Make sure the connection is still alive, if not, try to reconnect */
//                if (!mysql_ping($conn)) {
                //echo 'Lost connection, exiting after query #2';
                //exit;
//                    $conn = mysql_connect('localhost', 'c38trlmonk', '542piF88');
//                }

                try {
                    $data = $this->research_data_model->do_stats($batch->id);
                } catch (Exception $e) {
                    echo 'Ошибка', $e->getMessage(), "\n";
                    $this->statistics_model->db->close();
                    $this->statistics_model->db->initialize();
                    $data = $this->research_data_model->do_stats($batch->id);
                }
                if (count($data) > 0) {
                    foreach ($data as $obj) {
                        $own_price = 0;
                        $competitors_prices = array();
                        $price_diff = '';
                        $items_priced_higher_than_competitors = 0;
                        $short_description_wc = 0;
                        $long_description_wc = 0;
                        $short_seo_phrases = '?';
                        $long_seo_phrases = '?';
                        $similar_products_competitors = array();
                        // Price difference
                        $own_site = parse_url($obj->url, PHP_URL_HOST);
                        if (!$own_site)
                            $own_site = "own site";
                        $own_site = str_replace("www1.", "", str_replace("www.", "", $own_site));

                        // Price difference
                        $own_site = parse_url($obj->url, PHP_URL_HOST);
                        if (!$own_site)
                            $own_site = "own site";
                        $own_site = str_replace("www.", "", $own_site);

                        $time_start = microtime(true);

                        try {
                            $data_import = $this->imported_data_parsed_model->getByImId($obj->imported_data_id);
                        } catch (Exception $e) {
                            echo 'Ошибка', $e->getMessage(), "\n";
                            $this->statistics_model->db->close();
                            $this->statistics_model->db->initialize();
                            $data_import = $this->imported_data_parsed_model->getByImId($obj->imported_data_id);
                        }

                        $time_end = microtime(true);
                        $time = $time_end - $time_start;
//                          echo "data_import - $time seconds\n";

                        $time_start = microtime(true);
                        if (isset($data_import['parsed_attributes']) && isset($data_import['parsed_attributes']['model'])) {

                            try {
                                $own_prices = $this->imported_data_parsed_model->getLastPrices($obj->imported_data_id);
                            } catch (Exception $e) {
                                echo 'Ошибка', $e->getMessage(), "\n";
                                $this->statistics_model->db->close();
                                $this->statistics_model->db->initialize();
                                $own_prices = $this->imported_data_parsed_model->getLastPrices($obj->imported_data_id);
                            }

                            if (!empty($own_prices)) {
                                $own_price = floatval($own_prices[0]->price);
                                $obj->own_price = $own_price;
                                $price_diff_exists = array(); //"<input type='hidden'/>";
                                $price_diff_exists['id'] = $own_prices[0]->id;
                                $price_diff_exists['own_site'] = $own_site;
                                $price_diff_exists['own_price'] = floatval($own_price);

                                try {
                                    $similar_items = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['model']);
                                } catch (Exception $e) {
                                    echo 'Ошибка', $e->getMessage(), "\n";
                                    $this->statistics_model->db->close();
                                    $this->statistics_model->db->initialize();
                                    $similar_items = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['model']);
                                }

                                if (!empty($similar_items)) {
                                    foreach ($similar_items as $ks => $vs) {
                                        $similar_item_imported_data_id = $similar_items[$ks]['imported_data_id'];
                                        if ($obj->imported_data_id == $similar_item_imported_data_id) {
                                            continue;
                                        }
                                        $similar_products_competitors[] = array(
                                            'imported_data_id' => $similar_item_imported_data_id,
                                            'customer' => $similar_items[$ks]['customer']
                                        );

                                        try {
                                            $three_last_prices = $this->imported_data_parsed_model->getLastPrices($similar_item_imported_data_id);
                                        } catch (Exception $e) {
                                            echo 'Ошибка', $e->getMessage(), "\n";
                                            $this->statistics_model->db->close();
                                            $this->statistics_model->db->initialize();
                                            $three_last_prices = $this->imported_data_parsed_model->getLastPrices($similar_item_imported_data_id);
                                        }

                                        if (!empty($three_last_prices)) {
                                            $price_scatter = $own_price * 0.03;
                                            $price_upper_range = $own_price + $price_scatter;
                                            $price_lower_range = $own_price - $price_scatter;
                                            $competitor_price = floatval($three_last_prices[0]->price);
                                            if ($competitor_price < $own_price) {
                                                $items_priced_higher_than_competitors = 1;
                                            }
                                            if ($competitor_price > $price_upper_range || $competitor_price < $price_lower_range) {
                                                $price_diff_exists['competitor_customer'][] = $similar_items[$ks]['customer'];
                                                $price_diff_exists['competitor_price'][] = $competitor_price;
                                                $price_diff = $price_diff_exists;
                                                $competitors_prices[] = $competitor_price;
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        $time_end = microtime(true);
                        $time = $time_end - $time_start;
//                          echo "price_diff - $time seconds\n";
                        // WC Short
                        $time_start = microtime(true);
                        $short_description_wc = (count(preg_split('/\b/', $obj->short_description)) - 1) / 2;
                        if (is_null($obj->short_description_wc)) {
                            try {
                                $this->imported_data_parsed_model->insert($obj->imported_data_id, "Description_WC", $short_description_wc);
                            } catch (Exception $e) {
                                echo 'Ошибка', $e->getMessage(), "\n";
                                $this->statistics_model->db->close();
                                $this->statistics_model->db->initialize();
                                $this->imported_data_parsed_model->insert($obj->imported_data_id, "Description_WC", $short_description_wc);
                            }
                        } else {
                            if (intval($obj->short_description_wc) <> $short_description_wc) {
                                try {
                                    $this->imported_data_parsed_model->updateValueByKey($obj->imported_data_id, "Description_WC", $short_description_wc);
                                } catch (Exception $e) {
                                    echo 'Ошибка', $e->getMessage(), "\n";
                                    $this->statistics_model->db->close();
                                    $this->statistics_model->db->initialize();
                                    $this->imported_data_parsed_model->updateValueByKey($obj->imported_data_id, "Description_WC", $short_description_wc);
                                }
                            }
                        }
                        $time_end = microtime(true);
                        $time = $time_end - $time_start;
//                          echo "WC Short - $time seconds\n";
                        // WC Long
                        $time_start = microtime(true);
                        $long_description_wc = (count(preg_split('/\b/', $obj->long_description)) - 1) / 2;
                        if (is_null($obj->long_description_wc)) {
                            try {
                                $this->imported_data_parsed_model->insert($obj->imported_data_id, "Long_Description_WC", $long_description_wc);
                            } catch (Exception $e) {
                                echo 'Ошибка', $e->getMessage(), "\n";
                                $this->statistics_model->db->close();
                                $this->statistics_model->db->initialize();
                                $this->imported_data_parsed_model->insert($obj->imported_data_id, "Long_Description_WC", $long_description_wc);
                            }
                        } else {
                            if (intval($obj->long_description_wc) <> $long_description_wc) {
                                try {
                                    $this->imported_data_parsed_model->updateValueByKey($obj->imported_data_id, "Long_Description_WC", $long_description_wc);
                                } catch (Exception $e) {
                                    echo 'Ошибка', $e->getMessage(), "\n";
                                    $this->statistics_model->db->close();
                                    $this->statistics_model->db->initialize();
                                    $this->imported_data_parsed_model->updateValueByKey($obj->imported_data_id, "Long_Description_WC", $long_description_wc);
                                }
                            }
                        }
                        $time_end = microtime(true);
                        $time = $time_end - $time_start;
//                          echo "WC Long - $time seconds\n";
                        // SEO Short phrases
                        $time_start = microtime(true);
                        if ($short_description_wc == $obj->short_description_wc && !is_null($obj->short_seo_phrases)) {
                            $short_seo_phrases = $obj->short_seo_phrases;
                        } else {
                            if ($enable_exec) {
                                $cmd = $this->prepare_extract_phrases_cmd($obj->short_description);
                                $output = array();
                                exec($cmd, $output, $error);

                                if ($error > 0) {
                                    $enable_exec = false;
                                } else {
                                    $short_seo_phrases = $this->prepare_seo_phrases($output);
                                    if (is_null($obj->short_seo_phrases)) {
                                        try {
                                            $this->imported_data_parsed_model->insert($obj->imported_data_id, "short_seo_phrases", $short_seo_phrases);
                                        } catch (Exception $e) {
                                            echo 'Ошибка', $e->getMessage(), "\n";
                                            $this->statistics_model->db->close();
                                            $this->statistics_model->db->initialize();
                                            $this->imported_data_parsed_model->insert($obj->imported_data_id, "short_seo_phrases", $short_seo_phrases);
                                        }
                                    } else {
                                        try {
                                            $this->imported_data_parsed_model->updateValueByKey($obj->imported_data_id, "short_seo_phrases", $short_seo_phrases);
                                        } catch (Exception $e) {
                                            echo 'Ошибка', $e->getMessage(), "\n";
                                            $this->statistics_model->db->close();
                                            $this->statistics_model->db->initialize();
                                            $this->imported_data_parsed_model->updateValueByKey($obj->imported_data_id, "short_seo_phrases", $short_seo_phrases);
                                        }
                                    }
                                }
                            }
                        }
                        $time_end = microtime(true);
                        $time = $time_end - $time_start;
//                          echo "SEO Short phrases - $time seconds\n";
                        // SEO Long phrases
                        $time_start = microtime(true);
                        if ($long_description_wc == $obj->long_description_wc && !is_null($obj->long_seo_phrases)) {
                            $long_seo_phrases = $obj->long_seo_phrases;
                        } else {
                            if ($enable_exec) {
                                $cmd = $this->prepare_extract_phrases_cmd($obj->long_description);
                                $output = array();
                                exec($cmd, $output, $error);

                                if ($error > 0) {
                                    $enable_exec = false;
                                } else {
                                    $long_seo_phrases = $this->prepare_seo_phrases($output);
                                    if (is_null($obj->long_seo_phrases)) {
                                        try {
                                            $this->imported_data_parsed_model->insert($obj->imported_data_id, "long_seo_phrases", $long_seo_phrases);
                                        } catch (Exception $e) {
                                            echo 'Ошибка', $e->getMessage(), "\n";
                                            $this->statistics_model->db->close();
                                            $this->statistics_model->db->initialize();
                                            $this->imported_data_parsed_model->insert($obj->imported_data_id, "long_seo_phrases", $long_seo_phrases);
                                        }
                                    } else {
                                        try {
                                            $this->imported_data_parsed_model->updateValueByKey($obj->imported_data_id, "long_seo_phrases", $long_seo_phrases);
                                        } catch (Exception $e) {
                                            echo 'Ошибка', $e->getMessage(), "\n";
                                            $this->statistics_model->db->close();
                                            $this->statistics_model->db->initialize();
                                            $this->imported_data_parsed_model->updateValueByKey($obj->imported_data_id, "long_seo_phrases", $long_seo_phrases);
                                        }
                                    }
                                }
                            }
                        }
                        $time_end = microtime(true);
                        $time = $time_end - $time_start;
//                          echo "SEO Long phrases - $time seconds\n";

                        $time_start = microtime(true);

                        try {
                            $insert_id = $this->statistics_model->insert($obj->rid, $obj->imported_data_id, $obj->research_data_id, $batch->id, $obj->product_name, $obj->url, $obj->short_description, $obj->long_description, $short_description_wc, $long_description_wc, $short_seo_phrases, $long_seo_phrases, $own_price, serialize($price_diff), serialize($competitors_prices), $items_priced_higher_than_competitors, serialize($similar_products_competitors)
                            );
                        } catch (Exception $e) {
                            echo 'Ошибка', $e->getMessage(), "\n";
                            $this->statistics_model->db->close();
                            $this->statistics_model->db->initialize();

                            $insert_id = $this->statistics_model->insert($obj->rid, $obj->imported_data_id, $obj->research_data_id, $batch->id, $obj->product_name, $obj->url, $obj->short_description, $obj->long_description, $short_description_wc, $long_description_wc, $short_seo_phrases, $long_seo_phrases, $own_price, serialize($price_diff), serialize($competitors_prices), $items_priced_higher_than_competitors, serialize($similar_products_competitors)
                            );
                        }

                        $time_end = microtime(true);
                        $time = $time_end - $time_start;
                        echo "insert_id - $time seconds\n";
//                          var_dump($insert_id);
                        /* if($insert_id){
                          var_dump('--'.$obj->batch_id.'--');
                          } else {
                          print "<pre>";
                          print_r($obj->rid, $obj->imported_data_id,
                          $obj->research_data_id, $obj->batch_id,
                          $obj->product_name, $obj->url, $obj->short_description, $obj->long_description,
                          $short_description_wc, $long_description_wc,
                          $short_seo_phrases, $long_seo_phrases,
                          $own_price, serialize($price_diff), serialize($competitors_prices), $items_priced_higher_than_competitors);
                          print "</pre>";
                          die("error");
                          } */

                        echo '.';
                    }
                    /* $params = new stdClass();
                      $params->batch_id = $batch->id;
                      $params->txt_filter = '';
                      $stat_data= $this->statistics_model->getStatsData($params);
                      if(count($stat_data)>0){
                      foreach($stat_data as $stat){
                      $res_data = $this->check_duplicate_content($stat->imported_data_id);
                      foreach($res_data as $val){
                      $this->statistics_duplicate_content_model->insert($val['imported_data_id'],
                      $val['product_name'], $val['description'],
                      $val['long_description'], $val['url'],
                      $val['features'], $val['customer'],
                      $val['long_original'], $val['short_original']);
                      }
                      };
                      } */
                }
            }
            $subject='Cron Job Report - do_stats finished';
            $message='Cron job for do_stats finished';
            $this->send_email_report($subject,  $message);
            echo "Script finish working";
            echo "Cron Job Finished";
        } catch (Exception $e) {
            echo 'Ошибка', $e->getMessage(), "\n";
            unlink($tmp_dir . ".locked");
        }
        unlink($tmp_dir . ".locked");
    }

    function duplicate_content_new($imported_data_id) {

        try {

            $res_data = $this->check_duplicate_content($imported_data_id);

            $time_end = microtime(true);
            $time = $time_end - $time_start;
            echo "block with check_duplicate_content - $time seconds\n";
            $time_start = $time_end;
            foreach ($res_data as $val) {
                $this->statistics_duplicate_content_model->insert_new($val['imported_data_id'], $val['long_original'], $val['short_original'],'1');
            }
            $time_end = microtime(true);
            $time = $time_end - $time_start;
            echo "foreach insert - $time seconds\n";
        } catch (Exception $e) {
            echo 'Ошибка', $e->getMessage(), "\n";
        }
    }

    public function duplicate_content() {
        error_reporting(E_ALL);
        ini_set('display_errors', '1');
        set_time_limit(0);
        $tmp_dir = sys_get_temp_dir() . '/';
        unlink($tmp_dir . ".locked");
        if (file_exists($tmp_dir . ".locked")) {
            exit;
        }

        touch($tmp_dir . ".locked");
        try {
            $this->load->model('batches_model');
            $this->load->model('statistics_model');
            $this->load->model('statistics_duplicate_content_model');
            $this->statistics_duplicate_content_model->truncate();
            $batches = $this->batches_model->getAll('id');
            foreach ($batches as $batch) {
                $params = new stdClass();
                $params->batch_id = $batch->id;
                $params->txt_filter = '';
                $stat_data = $this->statistics_model->getStatsData($params);
//                $conn = mysql_connect('localhost', 'c38trlmonk', '542piF88');
                /* Make sure the connection is still alive, if not, try to reconnect */
//                if (!mysql_ping($conn)) {
//                    echo 'Lost connection, exiting after query #2';
//                    exit;
//                }
                if (count($stat_data) > 0) {
                    foreach ($stat_data as $stat) {
                        $time_start = microtime(true);
                        sleep(2);
                        $res_data = $this->check_duplicate_content($stat->imported_data_id);
                        sleep(2);
                        $time_end = microtime(true);
                        $time = $time_end - $time_start;
                        echo "block with check_duplicate_content - $time seconds\n";
                        $time_start = $time_end;
                        foreach ($res_data as $val) {
                            $this->statistics_duplicate_content_model->insert($val['imported_data_id'], $val['product_name'], $val['description'], $val['long_description'], $val['url'], $val['features'], $val['customer'], $val['long_original'], $val['short_original']);
                        }
                        $time_end = microtime(true);
                        $time = $time_end - $time_start;
                        echo "foreach insert - $time seconds\n";
                    };
                }
            }
            echo "Cron Job Finished";
        } catch (Exception $e) {
            echo 'Ошибка', $e->getMessage(), "\n";
            unlink($tmp_dir . ".locked");
        }
        unlink($tmp_dir . ".locked");
    }

    private function prepare_extract_phrases_cmd($text) {
        $text = str_replace("'", "\'", $text);
        $text = str_replace("`", "\`", $text);
        $text = str_replace('"', '\"', $text);
        $text = "\"" . $text . "\"";
        $cmd = str_replace($this->config->item('cmd_mask'), $text, $this->config->item('extract_phrases'));
        $cmd = $cmd . " 2>&1";
        return $cmd;
    }

    private function prepare_seo_phrases($seo_lines) {
        if (empty($seo_lines)) {
            return "None";
        }
        $seo_phrases = array();
        $result_phrases = array();
        foreach ($seo_lines as $line) {
            $line_array = explode(",", $line);
            $number_repetitions = intval(str_replace("\"", "", $line_array[1]));
            if ($number_repetitions < 2) {
                continue;
            }
            $phrase = str_replace("\"", "", $line_array[0]);
            $seo_phrases[] = array($number_repetitions, $phrase);
        }
        if (empty($seo_phrases)) {
            return "None";
        }
        $lines_count = 0;
        foreach ($seo_phrases as $seo_phrase) {
            if ($lines_count > 2) {
                break;
            }
            $result_phrases[] = $seo_phrase[1] . " (" . $seo_phrase[0] . ")";
            $lines_count++;
        }
        return implode(" ", $result_phrases);
    }

    private function check_duplicate_content($imported_data_id) {
        $this->load->model('imported_data_parsed_model');
        $this->load->model('similar_product_groups_model');
        $this->load->model('similar_data_model');
        $data_import = $this->imported_data_parsed_model->getByImId($imported_data_id);

        if ($data_import['description'] !== null && trim($data_import['description']) !== "") {
            $data_import['description'] = preg_replace('/\s+/', ' ', $data_import['description']);
            $data['s_product_short_desc_count'] = count(explode(" ", $data_import['description']));
        }
        if ($data_import['long_description'] !== null && trim($data_import['long_description']) !== "") {
            $data_import['long_description'] = preg_replace('/\s+/', ' ', $data_import['long_description']);
            $data['s_product_long_desc_count'] = count(explode(" ", $data_import['long_description']));
        }
        $data['s_product'] = $data_import;
        $same_pr = $this->imported_data_parsed_model->getSameProductsHuman($imported_data_id);

        if (empty($same_pr) && isset($data_import['parsed_attributes']) && isset($data_import['parsed_attributes']['model'])) {
            $strict = $this->input->post('strict');
            $same_pr = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['model'], $strict);
        }

        if (empty($same_pr) && isset($data_import['parsed_attributes']) && isset($data_import['parsed_attributes']['UPC/EAN/ISBN'])) {
            $same_pr = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['UPC/EAN/ISBN']);
        }
        if (empty($same_pr) && !isset($data_import['parsed_attributes']['model'])) {
            $data['mismatch_button'] = true;
            if (!$this->similar_product_groups_model->checkIfgroupExists($imported_data_id)) {

                if (!isset($data_import['parsed_attributes'])) {

                    $same_pr = $this->imported_data_parsed_model->getByProductName($imported_data_id, $data_import['product_name'], '', $strict);
                }
                if (isset($data_import['parsed_attributes'])) {
                    $same_pr = $this->imported_data_parsed_model->getByProductName($imported_data_id, $data_import['product_name'], $data_import['parsed_attributes']['manufacturer'], $strict);
                }
            } else {
                $this->load->model('similar_imported_data_model');
                $customers_list = array();
                $query_cus = $this->similar_imported_data_model->db->order_by('name', 'asc')->get('customers');
                $query_cus_res = $query_cus->result();
                if (count($query_cus_res) > 0) {
                    foreach ($query_cus_res as $key => $value) {
                        $n = parse_url($value->url);
                        $customers_list[] = $n['host'];
                    }
                }
                $customers_list = array_unique($customers_list);
                $rows = $this->similar_data_model->getByGroupId($imported_data_id);
                $data_similar = array();

                foreach ($rows as $key => $row) {
                    $data_similar[$key] = $this->imported_data_parsed_model->getByImId($row->imported_data_id);
                    $data_similar[$key]['imported_data_id'] = $row->imported_data_id;

                    $cus_val = "";
                    foreach ($customers_list as $ki => $vi) {
                        if (strpos($data_similar[$key]['url'], "$vi") !== false) {
                            $cus_val = $vi;
                        }
                    }
                    if ($cus_val !== "")
                        $data_similar[$key]['customer'] = $cus_val;
                }

                if (!empty($data_similar)) {
                    $same_pr = $data_similar;
                }
            }
        }
        if (count($same_pr) != 1) {
            foreach ($same_pr as $ks => $vs) {
                $maxshort = 0;
                $maxlong = 0;
                $k_sh = 0;
                $k_lng = 0;
                foreach ($same_pr as $ks1 => $vs1) {
                    if ($ks != $ks1) {
                        if ($vs['description'] != '') {
                            if ($vs1['description'] != '') {
                                $k_sh++;
                                $percent = $this->compare_text($vs['description'], $vs1['description']);
                                if ($percent > $maxshort) {
                                    $maxshort = $percent;
                                }
                            }

                            if ($vs1['long_description'] != '') {
                                $k_sh++;
                                $percent = $this->compare_text($vs['description'], $vs1['long_description']);
                                if ($percent > $maxshort) {
                                    $maxshort = $percent;
                                }
                            }
                        }

                        if ($vs['long_description'] != '') {

                            if ($vs1['description'] != '') {
                                $k_lng++;
                                $percent = $this->compare_text($vs['long_description'], $vs1['description']);
                                if ($percent > $maxlong) {
                                    $maxlong = $percent;
                                }
                            }

                            if ($vs1['long_description'] != '') {
                                $k_lng++;
                                $percent = $this->compare_text($vs['long_description'], $vs1['long_description']);
                                if ($percent > $maxlong) {
                                    $maxlong = $percent;
                                }
                            }
                        }
                    }
                }

                $vs['short_original'] = ceil($maxshort);
                $vs['long_original'] = ceil($maxlong);

                if ($k_lng == 0) {
                    $vs['long_original'] = 0;
                }
                if ($k_sh == 0) {
                    $vs['short_original'] =0;
                }

                $same_pr[$ks] = $vs;
            }
        } else {
            $same_pr[0]['long_original'] = 0;
            $same_pr[0]['short_original'] = 0;
            
        }
        return $same_pr;
    }

    private function compare_text($first_text, $second_text) {
        $first_text = preg_replace('/[^a-zA-Z0-9_ %\[\]\.\(\)%&-]/s', '', $first_text);
        $first_text = preg_replace('/[a-zA-Z]-/', ' ', $first_text);
        $second_text = preg_replace('/[^a-zA-Z0-9_ %\[\]\.\(\)%&-]/s', '', $second_text);
        $second_text = preg_replace('/[a-zA-Z]-/', ' ', $second_text);

        if ($first_text === $second_text) {
            return 100;
        } else {
            $a = explode(' ', strtolower($first_text));

            $b = explode(' ', strtolower($second_text));
            $arr = array_intersect($a, $b);
            $count = count($arr);
            $prc = $count / count($a) * 100;
            return $prc;
        }
    }

}