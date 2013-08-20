<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Crons extends MY_Controller {

	function __construct() {
  		parent::__construct();
  		$this->load->library('ion_auth');
		$this->ion_auth->add_auth_rules(array(
  			'index' => true,
  			'screenscron' => true,
            'do_stats' => true,
            'hello'=>true
  		));
 	}

 	public function index() {

	}
	
	private function urlExists($url) {
        if($url === null || trim($url) === "") return false;  
        $ch = curl_init($url);  
        curl_setopt($ch, CURLOPT_TIMEOUT, 5);  
        curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);  
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);  
        $data = curl_exec($ch);  
        $httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);  
        curl_close($ch);  
        if($httpcode>=200 && $httpcode<=302){  
            return true;  
        } else {  
            return false;  
        }  
    }

    private function customers_list() {
        $this->load->model('customers_model');
        $output = array();
        $customers_init_list = $this->customers_model->getAll();
        if(count($customers_init_list) > 0) {
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
        $dir = realpath(BASEPATH."../webroot/webshoots");
        if(!file_exists($dir)) {
            mkdir($dir);
            chmod($dir, 0777);
        }
        // --- NEW STUFF (TIMESTAMP BASED IMAGES NAMES) (START)
        $url_name = $url_name."-".date('Y-m-d-H-i-s', time());
        // --- NEW STUFF (TIMESTAMP BASED IMAGES NAMES) (END)
        $t = file_put_contents($dir."/$url_name.$type", $file);
        $path = base_url()."webshoots/$url_name.$type";
        $res = array(
            'path' => $path,
            'dir' => $dir."/$url_name.$type"
        );
        return $res;
    }

	/**
     * Cron Job for CI home tab screenshots generating 
     */
	public function screenscron() {
		$customers = $this->customers_list();
        $this->load->model('webshoots_model');
        $week = date("W", time());
        $year = date("Y", time());
        $sites = array();
        $primary_source_res = $this->urlExists('http://snapito.com');
        if($primary_source_res) { // ===== PRIMARY SCREENCAPTURE API (http://snapito.com/)
            $screen_api = 'snapito.com';
        } else { // ===== PRIMARY SCREENCAPTURE API (http://webyshots.com/)
            $screen_api = 'webyshots.com';
        }
        foreach ($customers as $k => $v) {
            if($this->urlExists($v['c_url'])) $sites[] = $v['c_url'];
        }
        foreach ($sites as $url) {
            $c_url = urlencode(trim($url));
            if($screen_api == 'snapito.com') {
                $api_key = $this->config->item('snapito_api_secret');
                $format = "jpeg";
                $res = array(
                    "s" => "http://api.snapito.com/web/$api_key/mc/$c_url?type=$format",
                    'l' => "http://api.snapito.com/web/$api_key/full/$c_url?type=$format"
                );
            } else {
                $api_key = $this->config->item('webyshots_api_key');
                $api_secret = $this->config->item('webyshots_api_secret');
                $token = md5("$api_secret+$url");
                $size_s = "w600";
                $size_l = "w1260";
                $format = "png";
                $res = array(
                    "s" => "http://api.webyshots.com/v1/shot/$api_key/$token/?url=$c_url&dimension=$size_s&format=$format",
                    'l' => "http://api.webyshots.com/v1/shot/$api_key/$token/?url=$c_url&dimension=$size_l&format=$format"
                );
            }
            $crawl_s = $this->upload_record_webshoot($res['s'], $url."_small");
            $crawl_l = $this->upload_record_webshoot($res['l'], $url."_big");
            $result = array(
                'state' => false,
                'url' => $url,
                'small_crawl' => $crawl_s['path'],
                'big_crawl' => $crawl_l['path'],
                'dir_thumb' => $crawl_s['dir'],
                'dir_img' => $crawl_l['dir'],
                'uid' => 0,
                'year' => $year,
                'week' => $week,
                'pos' => 0
            );
            $insert_id = $this->webshoots_model->recordUpdateWebshoot($result);
        }
		echo "Cron Job Finished";
	}

    /**
     * Cron Job for CI home tab screenshots reports mailer   
     */
    public function emailreports() {
        $this->load->model('webshoots_model');
        $current_day = lcfirst(date('l', time()));
        $recs = $this->webshoots_model->get_recipients_list();
        if(count($recs) > 0) {
            // --- mailer config (start)
            $this->load->library('email');
            $config['protocol'] = 'sendmail';
            $config['mailpath'] = '/usr/sbin/sendmail';
            $config['charset'] = 'UTF-8';
            $config['wordwrap'] = TRUE;
            $this->email->initialize($config);
            // --- mailer config (end)
            foreach ($recs as $k => $v) {
                if($v->day == $current_day) {
                    $day = $v->day;
                    $email = $v->email;
                    $id = $v->id;
                    $this->email->from('ishulgin8@gmail.com', "Content Solutions");
                    $this->email->to("$email");
                    $this->email->subject('Content Solutions Screenshots Report');
                    $this->email->message("Report screenshots in attachment. Preference day: $day.");
                    // --- test (debug) attachments (start)
                    $debug_screens = $this->webshoots_model->getLimitedScreens(3);
                    if(count($debug_screens) > 0) {
                        foreach ($debug_screens as $key => $value) {
                            $path = $value->dir_thumb;
                            $this->email->attach("$path");
                        }
                    }
                    // --- test (debug) attachments (end)
                    $this->email->send();
                    echo "Report sended to $v->email"."<br>";
                }
            }
        }
        echo "Cron Job Finished";
    }

    public function do_stats(){
        $this->load->library('helpers');
        $this->load->helper('algoritm');
        $tmp_dir = sys_get_temp_dir().'/';
        unlink($tmp_dir.".locked");
        if ( file_exists($tmp_dir.".locked") )
        { exit;}

        touch($tmp_dir.".locked");
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
            foreach($batches as $batch){
                $batch_id = $batch->id;
                $data = $this->research_data_model->do_stats($batch->id);
                $conn = mysql_connect('localhost', 'c38trlmonk', '542piF88');
                /* Make sure the connection is still alive, if not, try to reconnect */
                if (!mysql_ping($conn)) {
                    echo 'Lost connection, exiting after query #2';
                    exit;
                }
                if(count($data) > 0){
                    foreach($data as $obj){
                          $own_price = 0;
                          $competitors_prices = array();
                          $price_diff = '';
                          $items_priced_higher_than_competitors = 0;
                          $short_description_wc = 0;
                          $long_description_wc = 0;
                          $short_seo_phrases = '?';
                          $long_seo_phrases = '?';
                          // Price difference
                          $own_site = parse_url($obj->url,  PHP_URL_HOST);
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
                                  $price_diff_exists = array();//"<input type='hidden'/>";
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
                          $insert_id = $this->statistics_model->insert($obj->rid, $obj->imported_data_id,
                              $obj->research_data_id, $obj->batch_id,
                              $obj->product_name, $obj->url, $obj->short_description, $obj->long_description,
                              $short_description_wc, $long_description_wc,
                              $short_seo_phrases, $long_seo_phrases,
                              $own_price, serialize($price_diff), serialize($competitors_prices), $items_priced_higher_than_competitors
                          );
                          $time_end = microtime(true);
                          $time = $time_end - $time_start;
                          echo "insert_id - $time seconds\n";
                          var_dump($insert_id);
                          /*if($insert_id){
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
                          }*/
                    }
                    /*$params = new stdClass();
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


                    }*/
                }
                //$params->url = $this->input->get('url');
            }
            echo "Cron Job Finished";
        } catch (Exception $e) {
            echo 'Ошибка',  $e->getMessage(), "\n";
            unlink($tmp_dir.".locked");
        }
        unlink($tmp_dir.".locked");
    }

    public function duplicate_content(){
        $this->load->model('batches_model');
        $this->load->model('statistics_model');
        $this->load->model('statistics_duplicate_content_model');
        $batches = $this->batches_model->getAll('id');
        foreach($batches as $batch){
            $time_start = microtime(true);
            $params = new stdClass();
            $params->batch_id = $batch->id;
            $params->txt_filter = '';
            $stat_data= $this->statistics_model->getStatsData($params);
            $time_end = microtime(true);
            $time = $time_end - $time_start;
            echo "getStatsData - $time seconds\n";
            if(count($stat_data)>0){
                foreach($stat_data as $stat){
                    $time_start = microtime(true);
                    $res_data = $this->check_duplicate_content($stat->imported_data_id);
                    $time_end = microtime(true);
                    $time = $time_end - $time_start;
                    echo "check_duplicate_content - $time seconds\n";
                    foreach($res_data as $val){
                        $time_start = microtime(true);
                        $this->statistics_duplicate_content_model->insert($val['imported_data_id'],
                            $val['product_name'], $val['description'],
                            $val['long_description'], $val['url'],
                            $val['features'], $val['customer'],
                            $val['long_original'], $val['short_original']);
                        $time_end = microtime(true);
                        $time = $time_end - $time_start;
                        echo "insert statistics_duplicate_content - $time seconds\n";
                    }
                };
            }
        }
    }


    private function prepare_extract_phrases_cmd($text) {
        $text = str_replace("'", "\'", $text);
        $text = str_replace("`", "\`", $text);
        $text = str_replace('"', '\"', $text);
        $text = "\"".$text."\"";
        $cmd = str_replace($this->config->item('cmd_mask'), $text ,$this->config->item('extract_phrases'));
        $cmd = $cmd." 2>&1";
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
            $result_phrases[] = $seo_phrase[1]." (".$seo_phrase[0].")";
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
        if(empty($same_pr) && !isset($data_import['parsed_attributes']['model'])){
            $data['mismatch_button']=true;
            if (!$this->similar_product_groups_model->checkIfgroupExists($imported_data_id)) {

                if (!isset($data_import['parsed_attributes'])) {

                    $same_pr = $this->imported_data_parsed_model->getByProductName($imported_data_id, $data_import['product_name'], '', $strict);
                }
                if (isset($data_import['parsed_attributes']) ) {
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

                $vs['short_original'] = 100 - round($maxshort, 2);
                $vs['long_original'] = 100 - round($maxlong, 2);


                if ($k_lng == 0) {
                    $vs['long_original'] = 100;
                }
                if ($k_sh == 0) {
                    $vs['short_original'] = 100;
                }

                $same_pr[$ks] = $vs;
            }
        } else {
            $same_pr[0]['long_original'] = 100;
            $same_pr[0]['short_original'] = 100;
        }
        return $same_pr;
    }

    private function compare_text($first_text, $second_text) {
        if($first_text===$second_text){
            return 100;
        }else{
            $a = explode(' ', $first_text);
            $b = explode(' ', $second_text);
            $count = 0;
            foreach ($a as $val) {
                if (in_array($val, $b)) {
                    $count++;
                }
            }

            $prc = $count / count($a) * 100;
            return $prc;
        }
    }
}