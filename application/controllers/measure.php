<?php

if (!defined('BASEPATH'))
    exit('No direct script access allowed');

class Measure extends MY_Controller {

    function __construct() {
        parent::__construct();

        $this->load->library('form_validation');
        $this->load->library('helpers');
        $this->load->helper('algoritm');
        $this->load->helper('comparebysimilarwordscount');
        $this->load->helper('baseurl');
        $this->load->model('keywords_model');
        $this->data['title'] = 'Measure';
        $this->load->model('statistics_model');

        if (!$this->ion_auth->logged_in()) {
            //redirect them to the login page
            redirect('auth/login', 'refresh');
        }
    }

    public function index() {
        $this->load->model('webshoots_model');
        $this->data['customers_list'] = $this->customers_list_new();
        $this->data['user_id'] = $this->ion_auth->get_user_id();
        $c_week = date("W", time());
        $c_year = date("Y", time());
        $this->data['ct_final'] = date("m.d.Y", time());
        $this->data['c_week'] = $c_week;
        $this->data['c_year'] = $c_year;
        $this->data['img_av'] = $this->webshoots_model->getWeekAvailableScreens($c_week, $c_year);
        $this->data['webshoots_model'] = $this->webshoots_model;
        // $this->data['rec'] = $this->webshoots_model->get_recipients_list();
        $this->render();
    }

    public function debug_cmd_screenshots() {
        $opt = $this->input->post('opt');
        $id = $this->input->post('id');
        // $path_to_cron = base_url()."index.php/crons/site_crawler_screens?ids=$id";
        $path_to_cron = "http://dev.contentsolutionsinc.com/producteditor/index.php/crons/site_crawler_screens?ids=$id";
        $cmd = "";
        if ($opt == 1) {
            $cmd = "wget -q $path_to_cron > /dev/null 2>&1";
        } else if ($opt == 2) {
            $cmd = "wget -q $path_to_cron 2>&1";
        } else if ($opt == 3) {
            $cmd = "wget -O - -q -t 1 $path_to_cron";
        } else if ($opt == 4) {
            $cmd = "wget -S -O- $path_to_cron > /dev/null 2>/dev/null &";
        }
        shell_exec($cmd);
        $this->output->set_content_type('application/json')->set_output(json_encode($cmd));
    }

    public function ranking_api_db_sync() {
        $this->load->model('rankapi_model');
        $api_username = $this->config->item('ranking_api_username');
        $api_key = $this->config->item('ranking_api_key');
        $data = array("data" => json_encode(array("action" => "getAccountRankings", "id" => "$api_username", "apikey" => "$api_key")));
        $ch = curl_init('https://www.serpranktracker.com/tracker/webservice');
        curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
        curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        $track_data = curl_exec($ch);
        $data = json_decode($track_data);
        $res = array(
            'status' => false,
            'msg' => ''
        );
        if (isset($data) && $data->status == 'success') {
            foreach ($data->data as $k => $v) {
                $site = $v->site;
                $keywords = $v->keywords;
                if ((isset($site) && trim($site) !== "") && (isset($keywords) && count($keywords) > 0)) {
                    foreach ($keywords as $ks => $kv) {
                        // === extract not null and latest (according to date) rank object (start)
                        $r_object = null;
                        $rank_int = null;
                        $ranking_stack = array();
                        foreach ($kv->rankings as $ks => $vs) {
                            if (isset($vs->ranking) && $vs->ranking !== null && $vs->ranking !== "") {
                                $mid = array(
                                    'ranking' => $vs->ranking,
                                    'rankedurl' => $vs->rankedurl,
                                    'datetime' => $vs->datetime
                                );
                                array_push($ranking_stack, $mid);
                            }
                        }
                        $sort = array();
                        foreach ($ranking_stack as $k => $v) {
                            $sort['datetime'][$k] = $v['datetime'];
                        }
                        array_multisort($sort['datetime'], SORT_DESC, $ranking_stack);
                        if (count($ranking_stack) > 0) {
                            $r_object = $ranking_stack[0];
                        }
                        if ($r_object !== null)
                            $rank_int = $r_object['ranking'];
                        // === extract not null and latest (according to date) rank object (end)
                        $sync_data = array(
                            'site' => $site,
                            'keyword' => $kv->keyword,
                            'location' => $kv->location,
                            'engine' => $kv->searchengine,
                            'rank_json_encode' => json_encode($kv->rankings),
                            'rank' => $rank_int
                        );
                        $this->rankapi_model->start_db_sync($sync_data);
                    }
                }
            }
            $res['status'] = true;
            $res['msg'] = 'sync finished';
        } else {
            $res['msg'] = 'API call failed';
        }
        $this->output->set_content_type('application/json')->set_output(json_encode($res));
    }

    public function debug_ranking_data_delete() {
        // === incoming data§
        $url = $this->input->post('url');
        $key_word = $this->input->post('key_word');
        // === config
        $api_username = $this->config->item('ranking_api_username');
        $api_key = $this->config->item('ranking_api_key');
        // === delete keyword data to http://www.serpranktracker.com (start)
        $key_url = array(
            'site' => "$url",
            'keyword' => "$key_word",
            'location' => 'US',
            'searchengine' => 'G'
        );
        $data = array("data" => json_encode(array("action" => "deleteAccountKeywords", "id" => "$api_username", "apikey" => "$api_key", "keywords" => array($key_url))));
        $ch = curl_init('https://www.serpranktracker.com/tracker/webservice');
        curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
        curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        $result = curl_exec($ch);
        // === delete keyword data to http://www.serpranktracker.com (end)

        $this->output->set_content_type('application/json')->set_output(json_encode($result));
    }

    public function debug_ranking_data() {
        // === incoming data
        $url = $this->input->post('url');
        $key_word = $this->input->post('key_word');
        // === config
        $api_username = $this->config->item('ranking_api_username');
        $api_key = $this->config->item('ranking_api_key');
        // === add new keyword + url to http://www.serpranktracker.com (start)
        $key_url = array(
            "site" => "$url",
            "keyword" => "$key_word",
            "location" => "US",
            "searchengine" => "G"
        );
        $data = array("data" => json_encode(array("action" => "addAccountKeywords", "id" => "$api_username", "apikey" => "$api_key", "keywords" => array($key_url))));
        $ch = curl_init('https://www.serpranktracker.com/tracker/webservice');
        curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
        curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        $result = curl_exec($ch);
        // === add new keyword + url to http://www.serpranktracker.com (end)
        $this->output->set_content_type('application/json')->set_output(json_encode($result));
    }

    private function webthumb_call($url) {
        $webthumb_user_id = $this->config->item('webthumb_user_id');
        $api_key = $this->config->item('webthumb_api_key');
        $url = "http://$url";
        $c_date = gmdate('Ymd', time());
        $hash = md5($c_date . $url . $api_key);
        $e_url = urlencode(trim($url));
        return $res = array(
            "s" => "http://webthumb.bluga.net/easythumb.php?user=$webthumb_user_id&url=$e_url&hash=$hash&size=medium2&cache=1",
            'l' => "http://webthumb.bluga.net/easythumb.php?user=$webthumb_user_id&url=$e_url&hash=$hash&size=large&cache=1"
        );
    }

    private function webthumb_call_link($url) {
        $webthumb_user_id = $this->config->item('webthumb_user_id');
        $api_key = $this->config->item('webthumb_api_key');
        $url = "http://$url";
        $c_date = gmdate('Ymd', time());
        $hash = md5($c_date . $url . $api_key);
        $e_url = urlencode(trim($url));
        $call = "http://webthumb.bluga.net/easythumb.php?user=$webthumb_user_id&url=$e_url&hash=$hash&size=large&cache=1";
        return $call;
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
            'dir' => $dir . "/$url_name.$type",
            'shot_name' => $url_name . "." . $type,
            'call' => $ext_url
        );
        return $res;
    }

    private function urlExistsCode($url) {
        if ($url === null || trim($url) === "")
            return false;
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_TIMEOUT, 5);
        curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        $data = curl_exec($ch);
        $httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        return $httpcode;
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

    private function check_screen_crawl_status($url) {
        $this->load->model('webshoots_model');
        return $this->webshoots_model->checkScreenCrawlStatus($url);
    }

    public function batch_snap_process() {
        $this->load->model('webshoots_model');
        $this->load->model('crawler_list_model');
        $batch_id = $this->input->post('batch_id');
        $res = array(
            'status' => false,
            'data' => array()
        );
        if (isset($batch_id) && is_numeric($batch_id)) {
            // $urls = $this->crawler_list_model->getByBatchOverall($batch_id);
            $urls = $this->crawler_list_model->getByBatchLimit(5, 0, $batch_id);
            // ===== start snaps crawl process (start)
            if (count($urls) > 0) {
                foreach ($urls as $k => $v) {
                    // $http_status = $this->urlExistsCode($v->url);
                    // $url = preg_replace('#^https?://#', '', $v->url);
                    // $r_url = urlencode(trim($url));
                    // $call_url = $this->webthumb_call_link($url);
                    // $snap_res = $this->crawl_webshoot($call_url, $v->id);
                    // $file = $snap_res['dir'];
                    // $file_size = filesize($file);
                    // if($file_size === false || $file_size < 2048) {
                    //     @unlink($file);
                    //     $api_key = $this->config->item('snapito_api_secret');
                    //     $call_url = "http://api.snapito.com/web/$api_key/mc/$url";
                    //     $snap_res = $this->crawl_webshoot($call_url, $v->id);
                    // }
                    // $this->webshoots_model->updateCrawlListWithSnap($v->id, $snap_res['img'], $http_status);
                }
            }
            // ===== start snaps crawl process (end)
            $res['status'] = true;
            $res['data'] = $urls;
        }
        $this->output->set_content_type('application/json')->set_output(json_encode($res));
    }

    public function reset_screen_drop() {
        $this->load->model('webshoots_model');
        $uid = $this->input->post('uid');
        $pos = $this->input->post('pos');
        $year = $this->input->post('year');
        $week = $this->input->post('week');
        $reset = $this->webshoots_model->resetScreenDrop($uid, $pos, $year, $week);
        $this->output->set_content_type('application/json')->set_output(json_encode($reset));
    }

    public function get_emails_reports_recipient() {
        $this->load->model('webshoots_model');
        $c_week = $this->input->post('c_week');
        $c_year = $this->input->post('c_year');
        $data['c_week'] = $c_week;
        $data['c_year'] = $c_year;
        $data['user_id'] = $this->ion_auth->get_user_id();
        $data['rec'] = $this->webshoots_model->get_recipients_list();
        $this->load->view('measure/get_emails_reports_recipient', $data);
    }

    public function send_recipient_report_selected() {
        $this->load->model('webshoots_model');
        $this->load->model('settings_model');

        $email_report_config_sender = $this->webshoots_model->getEmailReportConfig('sender');

        $email_report_sender_name = $this->settings_model->get_general_setting('site_name');
        if ($email_report_sender_name === false)
            $email_report_sender_name = "Content Solutions - Home Pages Report";

        $attach_value = $this->webshoots_model->getEmailReportConfig('attach');
        if ($attach_value == 'yes') {
            $attach_st = true;
        } else {
            $attach_st = false;
        }

        $selected_data = $this->input->post('selected_data');
        $uid = $this->input->post('uid');

        // $c_week = $this->input->post('c_week');
        // $c_year = $this->input->post('c_year');
        $c_week = date("W", time());
        $c_year = date("Y", time());

        $email_logo = $this->webshoots_model->getEmailReportConfig('logo');
        $screens = $this->webshoots_model->getDistinctEmailScreens($c_week, $c_year, $uid);
        // ==== sort assoc by pos (start)
        if (count($screens) > 0) {
            $sort = array();
            foreach ($screens as $k => $v) {
                $sort['pos'][$k] = $v['pos'];
            }
            array_multisort($sort['pos'], SORT_ASC, $screens);
        }
        // ==== sort assoc by pos (end)
        // -- email config (dev configurations) (start) --
        $this->load->library('email');
        $config['protocol'] = 'sendmail';
        $config['mailpath'] = '/usr/sbin/sendmail';
        $config['charset'] = 'UTF-8';
        $config['wordwrap'] = TRUE;
        $config['mailtype'] = 'html';
        $this->email->initialize($config);
        // -- email config (dev configurations) (end) --
        foreach ($selected_data as $k => $v) {
            $day = $v['day'];
            $email = $v['email'];
            $id = $v['id'];
            $this->email->from("$email_report_config_sender", "$email_report_sender_name");
            $this->email->to("$email");
            $this->email->subject("$email_report_sender_name - Home Pages Report");
            $data_et['day'] = $day;
            $data_et['screens'] = $screens;
            $data_et['email_logo'] = $email_logo;
            $msg = $this->load->view('measure/rec_report_email_template', $data_et, true);
            $this->email->message($msg);
            // --- attachments (start)
            if ($attach_st) {
                if (count($screens) > 0) {
                    foreach ($screens as $key => $value) {
                        $path = $value['dir'];
                        $this->email->attach("$path");
                    }
                }
            }
            // --- attachments (end)
            $this->email->send();
        }
        $this->output->set_content_type('application/json')->set_output(json_encode($this->email->print_debugger()));
    }

    public function send_recipient_report() {
        $this->load->model('webshoots_model');
        $this->load->model('settings_model');

        $email_report_config_sender = $this->webshoots_model->getEmailReportConfig('sender');

        $email_report_sender_name = $this->settings_model->get_general_setting('site_name');
        if ($email_report_sender_name === false)
            $email_report_sender_name = "Content Solutions - Home Pages Report";

        $attach_value = $this->webshoots_model->getEmailReportConfig('attach');
        if ($attach_value == 'yes') {
            $attach_st = true;
        } else {
            $attach_st = false;
        }

        $id = $this->input->post('id');
        $email = $this->input->post('email');
        $day = $this->input->post('day');
        $uid = $this->input->post('uid');
        // $c_week = $this->input->post('c_week');
        // $c_year = $this->input->post('c_year');
        $c_week = date("W", time());
        $c_year = date("Y", time());

        $screens = $this->webshoots_model->getDistinctEmailScreens($c_week, $c_year, $uid);
        // ==== sort assoc by pos (start)
        if (count($screens) > 0) {
            $sort = array();
            foreach ($screens as $k => $v) {
                $sort['pos'][$k] = $v['pos'];
            }
            array_multisort($sort['pos'], SORT_ASC, $screens);
        }
        // ==== sort assoc by pos (end)
        // --------------- email sender (start) ---------------
        // -- email config (dev configurations) (start) --
        $this->load->library('email');

        $config['protocol'] = 'sendmail';
        $config['mailpath'] = '/usr/sbin/sendmail';
        $config['charset'] = 'UTF-8';
        $config['wordwrap'] = TRUE;
        $config['mailtype'] = 'html';

        $this->email->initialize($config);
        // -- email config (dev configurations) (end) --
        $this->email->from("$email_report_config_sender", "$email_report_sender_name");
        $this->email->to("$email");
        $this->email->subject("$email_report_sender_name - Home Pages Report");
        $data_et['day'] = $day;
        $data_et['screens'] = $screens;
        $data_et['email_logo'] = $this->webshoots_model->getEmailReportConfig('logo');
        $msg = $this->load->view('measure/rec_report_email_template', $data_et, true);
        $this->email->message($msg);
        // --- attachments (start)
        if ($attach_st) {
            if (count($screens) > 0) {
                foreach ($screens as $key => $value) {
                    $path = $value['dir'];
                    $this->email->attach("$path");
                }
            }
        }
        // --- attachments (end)
        $this->email->send();
        $this->output->set_content_type('application/json')->set_output(json_encode($this->email->print_debugger()));
        // --------------- email sender (end) -----------------
    }

    public function delete_recipient() {
        $this->load->model('webshoots_model');
        $id = $this->input->post('id');
        $res = $this->webshoots_model->delete_reports_recipient($id);
        $this->output->set_content_type('application/json')->set_output(json_encode($res));
    }

    private function crawl_webshoot($call_url, $id) {
        $file = file_get_contents($call_url);
        $type = 'png';
        $dir = realpath(BASEPATH . "../webroot/webshoots");
        if (!file_exists($dir)) {
            mkdir($dir);
            chmod($dir, 0777);
        }
        // --- NEW STUFF (TIMESTAMP BASED IMAGES NAMES) (START)
        $url_name = "crawl_snap-" . $id . "-" . date('Y-m-d-H-i-s', time());
        // --- NEW STUFF (TIMESTAMP BASED IMAGES NAMES) (END)
        $t = file_put_contents($dir . "/$url_name.$type", $file);
        $path = base_url() . "webshoots/$url_name.$type";
        $res = array(
            'path' => $path,
            'dir' => $dir . "/$url_name.$type",
            'img' => $url_name . "." . $type,
            'call' => $call_url
        );
        return $res;
    }

    // public function crawlsnapshoot() {
    //     $this->load->model('webshoots_model');
    //     $urls = $this->input->post('urls');
    //     if(count($urls) > 0) {
    //         $primary_source_res = $this->urlExists('http://snapito.com');
    //         $format = "png";
    //         if($primary_source_res) { // ===== PRIMARY SCREENCAPTURE API (http://snapito.com/)
    //             $screen_api = 'snapito.com';
    //             $api_key = $this->config->item('snapito_api_secret');
    //         } else { 
    //             $screen_api = 'webyshots.com';
    //             $api_key = $this->config->item('webyshots_api_key');
    //             $api_secret = $this->config->item('webyshots_api_secret');
    //             $size = "w800";
    //         }
    //         foreach ($urls as $k => $v) {
    //             // ---- snap it and update crawler_list table (start)
    //             $orig_url = $v['url'];
    //             $url = preg_replace('#^https?://#', '', $v['url']);
    //             $r_url = urlencode(trim($url));
    //             if($screen_api == 'snapito.com') {
    //                 $call_url = "http://api.snapito.com/web/$api_key/mc/$url";
    //             } else {
    //                 $token = md5("$api_secret+$url");
    //                 $call_url = "http://api.webyshots.com/v1/shot/$api_key/$token/?url=$r_url&dimension=$size&format=$format";
    //             }
    //             $snap_res = $this->crawl_webshoot($call_url, $v['id']);
    //             $this->webshoots_model->updateCrawlListWithSnap($v['id'], $snap_res['img']);
    //             // ---- snap it and update crawler_list table (end)
    //         }
    //     }
    //     $this->output->set_content_type('application/json')->set_output(true);
    // }

    public function crawlsnapshoot() {
        $this->load->model('webshoots_model');
        $urls = $this->input->post('urls');
        if (count($urls) > 0) {
            foreach ($urls as $k => $v) {
                $http_status = $this->urlExistsCode($v['url']);
                $orig_url = $v['url'];
                $url = preg_replace('#^https?://#', '', $v['url']);
                $r_url = urlencode(trim($url));
                $call_url = $this->webthumb_call_link($url);
                $snap_res = $this->crawl_webshoot($call_url, $v['id']);
                $this->webshoots_model->updateCrawlListWithSnap($v['id'], $snap_res['img'], $http_status);
            }
        }
        $this->output->set_content_type('application/json')->set_output(true);
    }

    public function crawlsnapshootcmd() { // shell_exec version
        $this->load->model('webshoots_model');
        $urls = $this->input->post('urls');
        $ids_string = "";
        $cmd = "";
        if (count($urls) > 0) {
            foreach ($urls as $k => $v) {
                $ids_string .= $v['id'] . ",";
            }
            $ids_string = substr($ids_string, 0, -1);
            $path_to_cron = base_url() . "index.php/crons/site_crawler_screens?ids=$ids_string";
            $cmd = "wget -q $path_to_cron > /dev/null 2>&1";
            shell_exec($cmd);
        }
        $this->output->set_content_type('application/json')->set_output(json_encode($cmd));
    }

    // public function crawlsnapshoot() {
    //     $this->load->model('webshoots_model');
    //     $urls = $this->input->post('urls');
    //     if(count($urls) > 0) {
    //         foreach ($urls as $k => $v) {
    //             $http_status = $this->urlExistsCode($v['url']);
    //             $orig_url = $v['url'];
    //             $url = preg_replace('#^https?://#', '', $v['url']);
    //             $r_url = urlencode(trim($url));
    //             $call_url = $this->webthumb_call_link($url);
    //             $snap_res = $this->crawl_webshoot($call_url, $v['id']);
    //             // ==== check for empty image (start)
    //             $image_up = $snap_res['img'];
    //             $file_size = realpath(BASEPATH . "../webroot/webshoots/$image_up");
    //             $fs = filesize($file_size);
    //             if($fs !== false && $fs > 2048) {
    //                 $this->webshoots_model->updateCrawlListWithSnap($v['id'], $snap_res['img'], $http_status);
    //             } else {
    //                 @unlink(realpath(BASEPATH . "../webroot/webshoots/$image_up"));
    //                 $call_url = $this->webthumb_call_link($url);
    //                 $snap_res = $this->crawl_webshoot($call_url, $v['id']);
    //                 $this->webshoots_model->updateCrawlListWithSnap($v['id'], $snap_res['img'], $http_status);
    //             }
    //             sleep(10);
    //             // ==== check for empty image (end)
    //         }
    //     }
    //     $this->output->set_content_type('application/json')->set_output(true);
    // }
    // public function webshootcrawlall() {
    //     $customers = $this->customers_list_new();
    //     $this->load->model('webshoots_model');
    //     $uid = $this->ion_auth->get_user_id();
    //     $week = date("W", time());
    //     $year = date("Y", time());
    //     $sites = array();
    //     $primary_source_res = $this->urlExists('http://snapito.com');
    //     if($primary_source_res) { // ===== PRIMARY SCREENCAPTURE API (http://snapito.com/)
    //         $screen_api = 'snapito.com';
    //     } else { 
    //         $screen_api = 'webyshots.com';
    //     }
    //     foreach ($customers as $k => $v) {
    //         if ($this->urlExists($v['c_url'])) $sites[] = $v['c_url'];
    //     }
    //     foreach ($sites as $url) {
    //         $c_url = urlencode(trim($url));
    //         if($screen_api == 'snapito.com') {
    //             $api_key = $this->config->item('snapito_api_secret');
    //             if(in_array($url, $this->config->item('webthumb_sites'))) {
    //                 $res = $this->webthumb_call($url);
    //             } else {
    //                 $res = array(
    //                     "s" => "http://api.snapito.com/web/$api_key/mc/$url",
    //                     'l' => "http://api.snapito.com/web/$api_key/full/$url"
    //                 );
    //             }
    //         } else {
    //             $api_key = $this->config->item('webyshots_api_key');
    //             $api_secret = $this->config->item('webyshots_api_secret');
    //             $token = md5("$api_secret+$url");
    //             $size_s = "w600";
    //             $size_l = "w1260";
    //             $format = "png";
    //             $res = array(
    //                 "s" => "http://api.webyshots.com/v1/shot/$api_key/$token/?url=$c_url&dimension=$size_s&format=$format",
    //                 'l' => "http://api.webyshots.com/v1/shot/$api_key/$token/?url=$c_url&dimension=$size_l&format=$format"
    //             );
    //         }
    //         $crawl_s = $this->upload_record_webshoot($res['s'], $url . "_small");
    //         $crawl_l = $this->upload_record_webshoot($res['l'], $url . "_big");
    //         $result = array(
    //             'state' => false,
    //             'url' => $url,
    //             'small_crawl' => $crawl_s['path'],
    //             'big_crawl' => $crawl_l['path'],
    //             'dir_thumb' => $crawl_s['dir'],
    //             'dir_img' => $crawl_l['dir'],
    //             'uid' => $uid,
    //             'year' => $year,
    //             'week' => $week,
    //             'pos' => 0
    //         );
    //         $insert_id = $this->webshoots_model->recordUpdateWebshoot($result);
    //     }
    //     $this->output->set_content_type('application/json')->set_output(true);
    // }

    public function webshootcrawlall() {
        $customers = $this->customers_list_new();
        $this->load->model('webshoots_model');
        $uid = $this->ion_auth->get_user_id();
        $week = date("W", time());
        $year = date("Y", time());
        $sites = array();
        foreach ($customers as $k => $v) {
            if ($this->urlExists($v['c_url']))
                $sites[] = $v['c_url'];
        }
        foreach ($sites as $url) {
            $c_url = preg_replace('#^https?://#', '', $url);

            if ($c_url === 'bjs.com') {
                $api_key = $this->config->item('snapito_api_secret');
                $call_url = "http://api.snapito.com/web/$api_key/mc/$c_url";
            } else {
                $call_url = $this->webthumb_call_link($c_url);
            }

            $crawl_l = $this->upload_record_webshoot($call_url, $c_url . "_big");
            $file = $crawl_l['dir'];
            $file_size = filesize($file);
            if ($file_size === false || $file_size < 2048) {
                @unlink($file);
                $crawl_l = $this->upload_record_webshoot($call_url, $c_url . "_big");
            }
            $result = array(
                'state' => false,
                'url' => $c_url,
                'small_crawl' => $crawl_l['path'],
                'big_crawl' => $crawl_l['path'],
                'dir_thumb' => $crawl_l['dir'],
                'dir_img' => $crawl_l['dir'],
                'uid' => $uid,
                'year' => $year,
                'week' => $week,
                'pos' => 0,
                'shot_name' => $crawl_l['shot_name']
            );
            $r = $this->webshoots_model->recordUpdateWebshoot($result);
            // === webshots selection refresh attempt (start)
            $this->webshoots_model->selectionRefreshDecision($r);
            // === webshots selection refresh attempt (end)
            sleep(5);
        }
        $this->output->set_content_type('application/json')->set_output(true);
    }

    public function dropselectionscan() {
        $year = $this->input->post('year');
        $week = $this->input->post('week');
        $uid = $this->ion_auth->get_user_id();
        $this->load->model('webshoots_model');
        $res = array();
        for ($i = 1; $i <= 6; $i++) {
            $mid = array(
                'pos' => $i,
                'cell' => $this->webshoots_model->getScreenCellSelection($i, $uid, $year, $week)
            );
            $res[] = $mid;
        }
        $this->output->set_content_type('application/json')->set_output(json_encode($res));
    }

    public function getwebshootbyurl() {
        ini_set("max_execution_time", 0);
        $year = $this->input->post('year');
        $week = $this->input->post('week');
        $c_url = $this->input->post('url');
        $pos = $this->input->post('pos');
        $label = $this->input->post('label');
        $uid = $this->ion_auth->get_user_id();
        $this->load->model('webshoots_model');
        $res = $this->webshoots_model->getWebShootByUrl($c_url);
        if ($res !== false) {
            $file_s = filesize($res->dir_img);
            if ($file_s === false || $file_s < 2048) { // === destroy bad image, crawl new one, update record in DB
                @unlink($res->dir_img);
                $call_url = $this->webthumb_call_link($c_url);
                $crawl_l = $this->upload_record_webshoot($call_url, $c_url . "_big");
                $file = $crawl_l['dir'];
                $file_size = filesize($file);
                if ($file_size !== false && $file_size > 2048) { // === update
                    $up_object = array(
                        'img' => $crawl_l['path'],
                        'thumb' => $crawl_l['path'],
                        'dir_thumb' => $crawl_l['dir'],
                        'dir_img' => $crawl_l['dir'],
                        'shot_name' => $crawl_l['shot_name']
                    );
                    $this->webshoots_model->updateWebshootById($up_object, $res->id);
                } else {
                    @unlink($file);
                    $call_url = $this->webthumb_call_link($c_url);
                    $crawl_l = $this->upload_record_webshoot($call_url, $c_url . "_big");
                    $up_object = array(
                        'img' => $crawl_l['path'],
                        'thumb' => $crawl_l['path'],
                        'dir_thumb' => $crawl_l['dir'],
                        'dir_img' => $crawl_l['dir'],
                        'shot_name' => $crawl_l['shot_name']
                    );
                    $this->webshoots_model->updateWebshootById($up_object, $res->id);
                }
            }
            $screen_id = $res->id;
            $this->webshoots_model->recordWebShootSelectionAttempt($screen_id, $uid, $pos, $year, $week, $res->img, $res->thumb, $res->stamp, $res->url, $label, $res->shot_name); // --- webshoot selection record attempt
            $result = $res;
        } else { // --- crawl brand new screenshot
            $http_status = $this->urlExistsCode($c_url);
            $c_url = preg_replace('#^https?://#', '', $c_url);
            $call_url = $this->webthumb_call_link($c_url);
            $crawl_l = $this->upload_record_webshoot($call_url, $c_url . "_big");
            $file = $crawl_l['dir'];
            $file_size = filesize($file);
            if ($file_size !== false && $file_size > 2048) {
                $result = array(
                    'state' => false,
                    'url' => $c_url,
                    'small_crawl' => $crawl_l['path'],
                    'big_crawl' => $crawl_l['path'],
                    'dir_thumb' => $crawl_l['dir'],
                    'dir_img' => $crawl_l['dir'],
                    'uid' => $uid,
                    'year' => $year,
                    'week' => $week,
                    'pos' => $pos,
                    'shot_name' => $crawl_l['shot_name']
                );
                $insert_id = $this->webshoots_model->recordUpdateWebshoot($result);
                $result = $this->webshoots_model->getWebshootDataById($insert_id);
                $this->webshoots_model->recordWebShootSelectionAttempt($insert_id, $uid, $pos, $year, $week, $result->img, $result->thumb, $result->stamp, $result->url, $label, $res->shot_name);
            } else {
                @unlink($file);
                $call_url = $this->webthumb_call_link($c_url);
                $crawl_l = $this->upload_record_webshoot($call_url, $c_url . "_big");
                $result = array(
                    'state' => false,
                    'url' => $c_url,
                    'small_crawl' => $crawl_l['path'],
                    'big_crawl' => $crawl_l['path'],
                    'dir_thumb' => $crawl_l['dir'],
                    'dir_img' => $crawl_l['dir'],
                    'uid' => $uid,
                    'year' => $year,
                    'week' => $week,
                    'pos' => $pos,
                    'shot_name' => $crawl_l['shot_name']
                );
                $insert_id = $this->webshoots_model->recordUpdateWebshoot($result);
                $result = $this->webshoots_model->getWebshootDataById($insert_id);
                $this->webshoots_model->recordWebShootSelectionAttempt($insert_id, $uid, $pos, $year, $week, $result->img, $result->thumb, $result->stamp, $result->url, $label, $res->shot_name);
            }
        }
        $this->output->set_content_type('application/json')->set_output(json_encode($result));
    }

    // public function getwebshootbyurl() {
    //     ini_set("max_execution_time", 0);
    //     $year = $this->input->post('year');
    //     $week = $this->input->post('week');
    //     $c_url = $this->input->post('url');
    //     $pos = $this->input->post('pos');
    //     $label = $this->input->post('label');
    //     $uid = $this->ion_auth->get_user_id();
    //     $this->load->model('webshoots_model');
    //     $res = $this->webshoots_model->getWebShootByUrl($c_url);
    //     if ($res !== false) {
    //         $screen_id = $res->id;
    //         $this->webshoots_model->recordWebShootSelectionAttempt($screen_id, $uid, $pos, $year, $week, $res->img, $res->thumb, $res->stamp, $res->url, $label); // --- webshoot selection record attempt
    //         $result = $res;
    //     } else { // --- crawl brand new screenshot
    //         $primary_source_res = $this->urlExists('http://snapito.com');
    //         if($primary_source_res) { // ===== PRIMARY SCREENCAPTURE API (http://snapito.com/)
    //             $api_key = $this->config->item('snapito_api_secret');
    //             if(in_array($c_url, $this->config->item('webthumb_sites'))) {
    //                 $res = $this->webthumb_call($c_url);
    //             } else {
    //                 $res = array(
    //                     "s" => "http://api.snapito.com/web/$api_key/mc/$c_url",
    //                     'l' => "http://api.snapito.com/web/$api_key/full/$c_url"
    //                 );
    //             }
    //         } else { // ===== SECONDARY SCREENCAPTURE API (http://webyshots.com)
    //             $url = urlencode(trim($c_url));
    //             $api_key = $this->config->item('webyshots_api_key');
    //             $api_secret = $this->config->item('webyshots_api_secret');
    //             $token = md5("$api_secret+$c_url");
    //             $size_s = "w600";
    //             $size_l = "w1260";
    //             $format = "png";
    //             $res = array(
    //                 "s" => "http://api.webyshots.com/v1/shot/$api_key/$token/?url=$url&dimension=$size_s&format=$format",
    //                 'l' => "http://api.webyshots.com/v1/shot/$api_key/$token/?url=$url&dimension=$size_l&format=$format"
    //             );
    //         }
    //         $crawl_s = $this->upload_record_webshoot($res['s'], $c_url . "_small");
    //         $crawl_l = $this->upload_record_webshoot($res['l'], $c_url . "_big");
    //         $result = array(
    //             'state' => false,
    //             'url' => $c_url,
    //             'small_crawl' => $crawl_s['path'],
    //             'big_crawl' => $crawl_l['path'],
    //             'dir_thumb' => $crawl_s['dir'],
    //             'dir_img' => $crawl_l['dir'],
    //             'uid' => $uid,
    //             'year' => $year,
    //             'week' => $week,
    //             'pos' => $pos
    //         );
    //         $insert_id = $this->webshoots_model->recordUpdateWebshoot($result);
    //         $result = $this->webshoots_model->getWebshootDataById($insert_id);
    //         $this->webshoots_model->recordWebShootSelectionAttempt($insert_id, $uid, $pos, $year, $week, $result->img, $result->thumb, $result->stamp, $result->url, $label); // --- webshoot selection record attempt
    //     }
    //     $this->output->set_content_type('application/json')->set_output(json_encode($result));
    // }

    public function getwebshootdata() {
        $url = $this->input->post('url');
        $this->load->model('webshoots_model');
        $res = $this->webshoots_model->getWebshootDataStampDesc($url);
        // $res = $this->webshoots_model->getWebshootData($url);
        $this->output->set_content_type('application/json')->set_output(json_encode($res));
    }

    public function getcustomerslist_crawl() {
        $cs = $this->customers_list_new();
        $res = array();
        foreach ($cs as $k => $v) {
            $mid = array(
                'id' => $v['id'],
                'name' => $v['name'],
                'url' => $v['c_url'],
                // 'crawl_st' => $this->check_screen_crawl_status($v['name'])
                'crawl_st' => $this->check_screen_crawl_status($v['c_url'])
            );
            $res[] = $mid;
        }
        $this->output->set_content_type('application/json')->set_output(json_encode($res));
    }

    // public function webshootcrawl() {
    //     ini_set("max_execution_time", 0);
    //     // === common params (start)
    //     $this->load->model('webshoots_model');
    //     $week = date("W", time());
    //     $year = date("Y", time());
    //     $c_url = $this->input->post('url');
    //     $uid = $this->ion_auth->get_user_id();
    //     // === common params (end)
    //     $primary_source_res = $this->urlExists('http://snapito.com');
    //     if($primary_source_res) { // ===== PRIMARY SCREENCAPTURE API (http://snapito.com/)
    //         $api_key = $this->config->item('snapito_api_secret');
    //         if(in_array($c_url, $this->config->item('webthumb_sites'))) {
    //             $res = $this->webthumb_call($c_url);
    //         } else {
    //             $res = array(
    //                 "s" => "http://api.snapito.com/web/$api_key/mc/$c_url",
    //                 'l' => "http://api.snapito.com/web/$api_key/full/$c_url"
    //             );
    //         }
    //         $crawl_s = $this->upload_record_webshoot($res['s'], $c_url . "_small");
    //         $crawl_l = $this->upload_record_webshoot($res['l'], $c_url . "_big");
    //         $result = array(
    //             'state' => false,
    //             'url' => $c_url,
    //             'small_crawl' => $crawl_s['path'],
    //             'big_crawl' => $crawl_l['path'],
    //             'dir_thumb' => $crawl_s['dir'],
    //             'dir_img' => $crawl_l['dir'],
    //             'uid' => $uid,
    //             'year' => $year,
    //             'week' => $week,
    //             'pos' => 0
    //         );
    //         $r = $this->webshoots_model->recordUpdateWebshoot($result);
    //         if ($r > 0) $result['state'] = true;
    //         $this->output->set_content_type('application/json')->set_output(json_encode($result));
    //     } else { // ===== SECONDARY SCREENCAPTURE API (http://webyshots.com)
    //         $url = urlencode(trim($c_url));
    //         // -- configs (start)
    //         $api_key = $this->config->item('webyshots_api_key');
    //         $api_secret = $this->config->item('webyshots_api_secret');
    //         $token = md5("$api_secret+$c_url");
    //         $size_s = "w600";
    //         $size_l = "w1260";
    //         $format = "png";
    //         // -- configs (end)
    //         $res = array(
    //             "s" => "http://api.webyshots.com/v1/shot/$api_key/$token/?url=$url&dimension=$size_s&format=$format",
    //             'l' => "http://api.webyshots.com/v1/shot/$api_key/$token/?url=$url&dimension=$size_l&format=$format"
    //         );
    //         $crawl_s = $this->upload_record_webshoot($res['s'], $url . "_small");
    //         $crawl_l = $this->upload_record_webshoot($res['l'], $url . "_big");
    //         $result = array(
    //             'state' => false,
    //             'url' => $url,
    //             'small_crawl' => $crawl_s['path'],
    //             'big_crawl' => $crawl_l['path'],
    //             'dir_thumb' => $crawl_s['dir'],
    //             'dir_img' => $crawl_l['dir'],
    //             'uid' => $uid,
    //             'year' => $year,
    //             'week' => $week,
    //             'pos' => 0
    //         );
    //         $r = $this->webshoots_model->recordUpdateWebshoot($result);
    //         if ($r > 0) $result['state'] = true;
    //         $this->output->set_content_type('application/json')->set_output(json_encode($result));
    //     }
    // }

    public function webshootcrawl() {
        ini_set("max_execution_time", 0);
        // === common params (start)
        $this->load->model('webshoots_model');
        $week = date("W", time());
        $year = date("Y", time());
        $c_url = $this->input->post('url');
        $uid = $this->ion_auth->get_user_id();
        // === common params (end)
        $c_url = preg_replace('#^https?://#', '', $c_url);

        if ($c_url === 'bjs.com') {
            $api_key = $this->config->item('snapito_api_secret');
            $call_url = "http://api.snapito.com/web/$api_key/mc/$c_url";
        } else {
            $call_url = $this->webthumb_call_link($c_url);
        }
        $crawl_l = $this->upload_record_webshoot($call_url, $c_url . "_big");

        $file = $crawl_l['dir'];
        $file_size = filesize($file);
        if ($file_size === false || $file_size < 10000) {
            @unlink($file);
            $crawl_l = $this->upload_record_webshoot($call_url, $c_url . "_big_s");
        }
        $result = array(
            'state' => false,
            'url' => $c_url,
            'small_crawl' => $crawl_l['path'],
            'big_crawl' => $crawl_l['path'],
            'dir_thumb' => $crawl_l['dir'],
            'dir_img' => $crawl_l['dir'],
            'uid' => $uid,
            'year' => $year,
            'week' => $week,
            'pos' => 0,
            'shot_name' => $crawl_l['shot_name']
        );
        $r = $this->webshoots_model->recordUpdateWebshoot($result);
        // === webshots selection refresh attempt (start)
        $this->webshoots_model->selectionRefreshDecision($r);
        // === webshots selection refresh attempt (end)
        if ($r > 0)
            $result['state'] = true;
        $this->output->set_content_type('application/json')->set_output(json_encode($result));
    }

    public function rec_emails_reports_recipient() {
        $recs_arr = $this->input->post('recs_arr');
        $rec_day = $this->input->post('rec_day');
        $this->load->model('webshoots_model');
        $result = $this->webshoots_model->rec_emails_reports_recipient($rec_day, $recs_arr);
        $this->output->set_content_type('application/json')->set_output(json_encode($result));
    }

    public function get_screenshots_slider_data() {
        $this->load->model('webshoots_model');
        $week = $this->input->post('week');
        $year = $this->input->post('year');
        $data['img_av'] = $this->webshoots_model->getWeekAvailableScreens($week, $year);
        $this->load->view('measure/get_screenshots_slider_data', $data);
    }

    public function timelineblock() {
        $this->load->model('webshoots_model');
        $first_cwp = $this->input->post('first_cwp');
        $last_cwp = $this->input->post('last_cwp');
        $state = $this->input->post('state');
        $year = $this->input->post('year');
        $week = date("W", time());
        $data = array(
            'first_cwp' => $first_cwp,
            'last_cwp' => $last_cwp,
            'state' => $state,
            'week' => $week,
            'year' => $year,
            'webshoots_model' => $this->webshoots_model
        );
        $this->load->view('measure/timelineblock', $data);
    }

    public function gethomepageyeardata() {
        $this->load->model('webshoots_model');
        $year = $this->input->post('year');
        $week = $this->input->post('week');
        if ($year == date('Y', time())) {
            $c_week = date("W", time());
            $c_year = date("Y", time());
            $data = array(
                'year' => $c_year,
                'week' => $c_week,
                'ct_final' => date("m.d.Y", time()),
                'customers_list' => $this->customers_list_new(),
                'status' => 'current',
                'img_av' => $this->webshoots_model->getWeekAvailableScreens($c_week, $year),
                'webshoots_model' => $this->webshoots_model,
                'user_id' => $this->ion_auth->get_user_id()
            );
        } else {
            $week = 1;
            $year_s = "01/01/" . $this->input->post('year');
            $i = ($week - 1) * 7;
            $total = strtotime($year_s) + 60 * 60 * 24 * $i;
            $ct_final = date('m.d.Y', $total);
            $data = array(
                'year' => $year,
                'week' => $week,
                'ct_final' => $ct_final,
                'customers_list' => $this->customers_list_new(),
                'status' => 'selected',
                'img_av' => $this->webshoots_model->getWeekAvailableScreens($week, $year),
                'webshoots_model' => $this->webshoots_model,
                'user_id' => $this->ion_auth->get_user_id()
            );
        }
        $this->load->view('measure/gethomepageyeardata', $data);
    }

    public function gethomepageweekdata() {
        $this->load->model('webshoots_model');
        $year = $this->input->post('year');
        $week = $this->input->post('week');
        $year_s = "01/01/" . $this->input->post('year');
        // ---- figure out total date (start)
        $i = ($week - 1) * 7;
        $total = strtotime($year_s) + 60 * 60 * 24 * $i;
        $ct_final = date('m.d.Y', $total);
        // ---- figure out total date (end)
        $data = array(
            'year' => $year,
            'week' => $week,
            'ct_final' => $ct_final,
            'customers_list' => $this->customers_list_new(),
            'img_av' => $this->webshoots_model->getWeekAvailableScreens($week, $year),
            'webshoots_model' => $this->webshoots_model,
            'user_id' => $this->ion_auth->get_user_id()
        );
        $this->load->view('measure/gethomepageweekdata', $data);
    }

    public function measure_products() {
        $this->load->model('sites_model');
        $sites = $this->sites_model->getAll();
        $this->data['sites'] = $sites;
        $this->data['customers_list'] = $this->category_customers_list();
        $this->load->model('department_members_model');
        $this->data['departmens_list'][] = 'All';
        foreach ($this->department_members_model->getAll() as $row) {
            $this->data['departmens_list'][$row->id] = $row->text;
        }
        $this->load->model('batches_model');
        $batches = $this->batches_model->getAll();
        $batches_list = array(0 => 'Choose Batch');
        //Max
        foreach ($batches as $batch) {
            $batches_list[$batch->title] = $batch->title;
        }
        //Max
        $this->data['batches_list'] = $batches_list;
        $this->render();
    }

    // Denis measure/measure_products_test page-----------------------------------------
    public function measure_products_test() {
        $this->load->model('sites_model');
        $sites = $this->sites_model->getAll();
        $this->data['sites'] = $sites;
        $this->data['customers_list'] = $this->category_customers_list();
        $this->load->model('department_members_model');
        $this->data['departmens_list'][] = 'All';
        foreach ($this->department_members_model->getAll() as $row) {
            $this->data['departmens_list'][$row->id] = $row->text;
        }
        $this->load->model('batches_model');
        $batches = $this->batches_model->getAll();
        $batches_list = array(0 => 'Choose Batch');
        //Max
        foreach ($batches as $batch) {
            $batches_list[$batch->title] = $batch->title;
        }
        //Max
        $this->data['batches_list'] = $batches_list;
        $this->render();
    }

    //-----------------------------------------------

    public function measure_departments() {
        $this->load->model('department_members_model');
        $this->load->model('site_categories_model');

        $this->data['departments_list'][] = 'All';
        foreach ($this->department_members_model->getAll() as $row) {
            $this->data['departments_list'][$row->id] = $row->text;
        }
        $this->data['category_list'][] = 'All';
        foreach ($this->site_categories_model->getAll() as $row) {
            $this->data['category_list'][$row->id] = $row->text;
        }
        $this->data['sites_list'] = $this->sites_list_new();
        $this->render();
    }

    private function sites_list_new() {
        $this->load->model('sites_model');
        $output = array();
        $sites_init_list = $this->sites_model->getAll();
        if (count($sites_init_list) > 0) {
            foreach ($sites_init_list as $key => $value) {
                $c_url = preg_replace('#^https?://#', '', $value->url);
                $c_url = preg_replace('#^www.#', '', $c_url);
                $mid = array(
                    'id' => $value->id,
                    'image_url' => $value->image_url,
                    'name' => $value->name,
                    'name_val' => $value->name,
                    'c_url' => $c_url
                );
                $output[] = $mid;
            }
        }
        return $output;
    }

    public function getDashboardDepData() {
        $this->load->model('sites_model');
        $this->load->model('department_members_model');
        $site_id = $this->sites_model->getIdByName($this->input->post('site_name'));
        $data = $this->department_members_model->getDescriptionData($site_id);
        $data_more = $this->department_members_model->getDepartmentsByWc($site_id);
        $keyword_optimize = 0;
        $keyword_optimize_data = array();
        $dep_optimize = array();
        foreach ($data_more as $key => $obj) {
            $keywords_density = json_decode($data_more[$key]->title_keyword_description_density);
            $num = 0;
            foreach ($keywords_density as $k => $v) {
                if (floatval($v) > 2) {
                    $num = 0;
                } else {
                    $num = 1;
                }
            }
            if ($num == 0) {
                array_push($dep_optimize, $obj);
            } else {
                array_push($keyword_optimize_data, $obj);
            }
            $keyword_optimize += $num;
        }
        $data = array_merge($data, array('keyword_optimize' => $keyword_optimize, 'keyword_optimize_data' => $keyword_optimize_data, 'dep_optimize' => $dep_optimize));
        $this->output->set_content_type('application/json')->set_output(json_encode($data));
    }

    public function getDashboardCatData() {
        $this->load->model('sites_model');
        $this->load->model('site_categories_model');
        $site_id = $this->sites_model->getIdByName($this->input->post('site_name'));
        $data = $this->site_categories_model->getDescriptionData($site_id);
        $data_more = $this->site_categories_model->getCategoriesByWc($site_id);
        $keyword_optimize = 0;
        $keyword_optimize_data = array();
        $dep_optimize = array();
        foreach ($data_more as $key => $obj) {
            $keywords_density = json_decode($data_more[$key]->title_keyword_description_density);
            $num = 0;
            foreach ($keywords_density as $k => $v) {
                if (floatval($v) > 2) {
                    $num = 0;
                } else {
                    $num = 1;
                }
            }
            if ($num == 0) {
                array_push($dep_optimize, $obj);
            } else {
                array_push($keyword_optimize_data, $obj);
            }
            $keyword_optimize += $num;
        }
        $data = array_merge($data, array('keyword_optimize' => $keyword_optimize, 'keyword_optimize_data' => $keyword_optimize_data, 'dep_optimize' => $dep_optimize));
        $this->output->set_content_type('application/json')->set_output(json_encode($data));
    }

    public function getDashboardCatDetails() {
        $this->load->model('sites_model');
        $this->load->model('site_categories_model');
        $condition = $this->input->post('condition');
        $site_id = $this->sites_model->getIdByName($this->input->post('site_name'));
        $data = $this->site_categories_model->getCatData($site_id, $condition);
        $this->output->set_content_type('application/json')->set_output(json_encode($data));
    }

    public function getDepartmentsByCustomer() {
        $this->load->model('sites_model');
        $this->load->model('department_members_model');
        $customerID = $this->sites_model->getIdByName($this->input->post('customer_name'));
        $result = $this->department_members_model->getAllByCustomerID($customerID);
        $this->output->set_content_type('application/json')->set_output(json_encode($result));
    }

    public function getCategoriesByCustomer() {
        $this->load->model('sites_model');
        $this->load->model('site_categories_model');
        $site_id = $this->sites_model->getIdByName($this->input->post('customer_name'));
        $result = $this->site_categories_model->getAllBySiteId($site_id);
        $this->output->set_content_type('application/json')->set_output(json_encode($result));
    }

    public function getKeywordByDescriptionText() {
        $this->load->model('site_categories_model');
        $category_id = $_POST['categoryID'];
        $result = $this->site_categories_model->getDataByCategory($category_id);
        if (empty($_POST['keyword'])) {
            $this->site_categories_model->UpdateKeywordsData($category_id);
            $density = ' N/A';
        } else {
            //var_dump($result);
            $description_text = trim($result->description_text, '"');
            $vowels = array(".", ",", "?", ":", "/", ">", "<", "&", "#", "^", ";", "`", "~", "*");
            $description_text = str_replace($vowels, "", $description_text);
            //echo $description_text;
            $description_words = $result->description_words;
            $array = explode(' ', $description_text);
            $keyword = trim($_POST['keyword']);
            //print_r($array);
            $count_key = 0;
            foreach ($array as $value) {
                if (strtolower(trim($value)) == strtolower($keyword))
                    $count_key++;
            }
            //echo $count_key;
            if ($description_words == 0 || $count_key == 0)
                $density = '0.0%';

            else {
                $densityDouble = $count_key / $description_words * 100;
                $density = sprintf("%01.2f", $densityDouble) . '%';
            }
            $this->site_categories_model->UpdateKeywordsData($category_id, $keyword, $count_key, sprintf("%01.2f", $densityDouble));
        }

        echo $density;
    }

    public function getKeywordDepartmentByDescriptionText() {
        $this->load->model('department_members_model');
        $department_id = $_POST['departmentID'];
        $result = $this->department_members_model->getDataByDepartment($department_id);
        if (empty($_POST['keyword'])) {
            $this->department_members_model->UpdateKeywordsDepartmentData($department_id);
            $density = ' N/A';
        } else {
            //var_dump($result);
            $description_text = trim($result->description_text, '"');
            $vowels = array(".", ",", "?", ":", "/", ">", "<", "&", "#", "^", ";", "`", "~", "*");
            $description_text = str_replace($vowels, "", $description_text);
            //echo $description_text;
            $description_words = $result->description_words;
            $array = explode(' ', $description_text);
            $keyword = trim($_POST['keyword']);
            //print_r($array);
            $count_key = 0;
            foreach ($array as $value) {
                if (strtolower(trim($value)) == strtolower($keyword))
                    $count_key++;
            }
            //echo $count_key;
            if ($description_words == 0 || $count_key == 0)
                $density = '0.0%';

            else {
                $densityDouble = $count_key / $description_words * 100;
                $density = sprintf("%01.2f", $densityDouble) . '%';
            }
            $this->department_members_model->UpdateKeywordsDepartmentData($department_id, $keyword, $count_key, sprintf("%01.2f", $densityDouble));
        }

        echo $density;
    }

    public function getCategoriesByDepartment() {
        $this->load->model('site_categories_model');
        $this->load->model('sites_model');
        $department_id = $this->input->post('department_id');
        $site_id = $this->sites_model->getIdByName($this->input->post('site_name'));
        $result = $this->site_categories_model->getAllBySiteId($site_id, $department_id);
        $this->output->set_content_type('application/json')->set_output(json_encode($result));
    }

    public function getDataByDepartment() {
        $this->load->model('department_members_model');
        $this->load->model('sites_model');
        $department_id = $this->input->post('department_id');
        $site_id = $this->sites_model->getIdByName($this->input->post('site_name'));
        $result = $this->department_members_model->getDataByDepartmentId($site_id, $department_id);
        $this->output->set_content_type('application/json')->set_output(json_encode($result));
    }

    public function getUrlByDepartment() {
        $this->load->model('department_members_model');
        $result = $this->department_members_model->getUrlByDepartment($this->input->post('department_id'));
        $this->output->set_content_type('application/json')->set_output(json_encode($result));
    }

    public function getUrlByCategory() {
        $this->load->model('site_categories_model');
        $result = $this->site_categories_model->getUrlByCategory($this->input->post('category_id'));
        $this->output->set_content_type('application/json')->set_output(json_encode($result));
    }

    public function measure_categories() {
        $this->render();
    }

    public function measure_social() {
        $this->render();
    }

    public function measure_pricing() {
        $this->render();
    }

    public function get_product_price() {
        $this->load->model('crawler_list_prices_model');

        $price_list = $this->crawler_list_prices_model->get_products_with_price();

        if (!empty($price_list['total_rows'])) {
            $total_rows = $price_list['total_rows'];
        } else {
            $total_rows = 0;
        }

        $output = array(
            "sEcho" => intval($_GET['sEcho']),
            "iTotalRecords" => $total_rows,
            "iTotalDisplayRecords" => $total_rows,
            "iDisplayLength" => $price_list['display_length'],
            "aaData" => array()
        );

        if (!empty($price_list['result'])) {
            foreach ($price_list['result'] as $price) {
                $parsed_attributes = unserialize($price->parsed_attributes);
                $model = (!empty($parsed_attributes['model']) ? $parsed_attributes['model'] : $parsed_attributes['UPC/EAN/ISBN']);
                $output['aaData'][] = array(
                    $price->created,
                    '<a href ="' . $price->url . '">' . substr($price->url, 0, 60) . '</a>',
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
        if (count($customers_init_list) > 0) {
            foreach ($customers_init_list as $key => $value) {
                $c_url = preg_replace('#^https?://#', '', $value->url);
                $c_url = preg_replace('#^www.#', '', $c_url);
                $mid = array(
                    'id' => $value->id,
                    'desc' => $value->description,
                    'image_url' => $value->image_url,
                    'name' => $value->name,
                    'name_val' => $value->name,
                    'c_url' => $c_url
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
        if (count($customers_init_list) > 0) {
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

//Max

    public function compare_text($first_text, $second_text) {

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
            $arr = array_unique($arr);
            $count = count($arr);
//        foreach ($a as $val) {
//            if (in_array($val, $b)) {
//                $arr[]=$val;
//                $count++;
//            }
//        }

            $prc = $count / count($a) * 100;
            $dubl_arr = array($prc, $arr);
            return $dubl_arr;
        }
    }

    public function similar_groups() {

        $this->load->model('imported_data_parsed_model');
        
        $this->imported_data_parsed_model->similiarity_cron();
        
    }

    public function report_mismatch() {

        $group_id = $this->input->post('group_id');
        $im_data_id = $this->input->post('im_data_id');
        $this->load->model('similar_data_model');
        $this->similar_data_model->update($group_id, $im_data_id, 1);
        $this->output->set_content_type('application/json')->set_output(json_encode("aaaaaaaa"));
    }

    function get_base_url($url) {
        $chars = preg_split('//', $url, -1, PREG_SPLIT_NO_EMPTY);

        $slash = 3; // 3rd slash

        $i = 0;

        foreach ($chars as $key => $char) {
            if ($char == '/') {
                $j = $i++;
            }

            if ($i == 3) {
                $pos = $key;
                break;
            }
        }
        if (preg_match('/www/', $url)) {
            $main_base = substr($url, 11, $pos - 11);
        } else {
            $main_base = substr($url, 7, $pos - 7);
        }

        return $main_base;
    }

    function matches_count($im_data_id) {
        if (!$this->statistics_model->getbyimpid($im_data_id)) {
            $data = array(
                'im_data_id' => $im_data_id,
                's_product' => array(),
                's_product_short_desc_count' => 0,
                's_product_long_desc_count' => 0,
                'seo' => array('short' => array(), 'long' => array()),
                'same_pr' => array()
            );
            if ($im_data_id !== null && is_numeric($im_data_id)) {

                // --- GET SELECTED RPODUCT DATA (START)
                $this->load->model('imported_data_parsed_model');
                $this->load->model('similar_product_groups_model');
                $this->load->model('similar_data_model');
                $data_import = $this->imported_data_parsed_model->getByImId($im_data_id);

                $same_pr = $this->imported_data_parsed_model->getSameProductsHuman($im_data_id);

                // get similar by parsed_attributes
                if (empty($same_pr) && isset($data_import['parsed_attributes']) && isset($data_import['parsed_attributes']['model'])) {

                    $strict = $this->input->post('strict');
                    $same_pr = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['model'], $strict);
                }

                if (empty($same_pr) && isset($data_import['parsed_attributes']) && isset($data_import['parsed_attributes']['UPC/EAN/ISBN'])) {

                    $same_pr = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['UPC/EAN/ISBN']);
                }
                if (empty($same_pr) && !isset($data_import['parsed_attributes']['model'])) {
                    $data['mismatch_button'] = true;
                    if (!$this->similar_product_groups_model->checkIfgroupExists($im_data_id)) {

                        if (!isset($data_import['parsed_attributes'])) {

                            $same_pr = $this->imported_data_parsed_model->getByProductName($im_data_id, $data_import['product_name'], '', $strict);
                        }
                        if (isset($data_import['parsed_attributes'])) {

                            $same_pr = $this->imported_data_parsed_model->getByProductName($im_data_id, $data_import['product_name'], $data_import['parsed_attributes']['manufacturer'], $strict);
                        }
                    } else {
                        $this->load->model('similar_imported_data_model');
                        $customers_list = array();
                        $query_cus = $this->similar_imported_data_model->db->order_by('name', 'asc')->get('sites');
                        $query_cus_res = $query_cus->result();
                        if (count($query_cus_res) > 0) {
                            foreach ($query_cus_res as $key => $value) {
                                $n = parse_url($value->url);
                                $customers_list[] = $n['host'];
                            }
                        }
                        $customers_list = array_unique($customers_list);
                        $rows = $this->similar_data_model->getByGroupId($im_data_id);
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
                // get similar for first row
                $this->load->model('similar_imported_data_model');

                $customers_list = array();
                $query_cus = $this->similar_imported_data_model->db->order_by('name', 'asc')->get('sites');
                $query_cus_res = $query_cus->result();
                if (count($query_cus_res) > 0) {
                    foreach ($query_cus_res as $key => $value) {
                        $n = parse_url($value->url);
                        $customers_list[] = $n['host'];
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

                foreach ($same_pr as $ks => $vs) {

                    if ($this->get_base_url($vs['url']) == $this->get_base_url($selectedUrl)) {
                        if ($ks != 0) {
                            $same_pr[] = $same_pr[0];
                            $same_pr[0] = $vs;
                            unset($same_pr[$ks]);
                        }
                    }
                }
                foreach ($same_pr as $ks => $vs) {

                    $this->load->model('sites_model');
                    $same_pr[$ks]['customer'] = strtolower($this->sites_model->get_name_by_url($same_pr[$ks]['customer']));
                }

                $matched_sites = array();
                foreach ($same_pr as $ks => $vs) {
                    $matched_sites[] = strtolower($vs['customer']);
                }

                // -------- COMPARING V1 (START)
                return $matched_sites;
            }
        } else {
            $matched_sites = array();
            $res = $this->statistics_model->getbyimpid($im_data_id);
            $matches = unserialize($res['similar_products_competitors']);
            foreach ($matches as $val) {
                $matched_sites[] = $val['customer'];
            }
            return $matched_sites;
        }
    }

    public function filterSiteNameByCustomerName() {
        $this->load->model('customers_model');
        $this->load->model('sites_model');
        $this->load->model('batches_model');
        $batch = $this->input->post('batch');
        $customer_name = $this->batches_model->getCustomerByBatch($batch);
        $customer = $this->customers_model->getByName($customer_name);
        $customer_url = $n = parse_url($customer['url']);
        $site = strtolower($this->sites_model->get_name_by_url($customer_url['host']));
        echo $site;
    }

    public function gridview() {
        $data['mismatch_button'] = false;
        $im_data_id = $this->input->post('im_data_id');
        $im_data_id = $this->input->post('im_data_id');
        $show_from = $this->input->post('show_from');
        if ($show_from != 'null') {
            $show_from = explode(',', $show_from);
            $show_from = array_map('strtolower', $show_from);
        }

        // ===== product snap scanner (start)
        // $this->load->model('webshoots_model');
        // $snap_data = $this->webshoots_model->scanForProductSnap($im_data_id);
        // ===== product snap scanner (end)

        $data = array(
            'im_data_id' => $im_data_id,
            's_product' => array(),
            's_product_short_desc_count' => 0,
            's_product_long_desc_count' => 0,
            'seo' => array('short' => array(), 'long' => array()),
            'same_pr' => array(),
            'webshoots_model' => $this->load->model('webshoots_model'),
            'rankapi_model' => $this->load->model('rankapi_model')
        );
        if ($im_data_id !== null && is_numeric($im_data_id)) {

            // --- GET SELECTED RPODUCT DATA (START)
            $this->load->model('imported_data_parsed_model');
            $this->load->model('similar_product_groups_model');
            $this->load->model('similar_data_model');
            $data_import = $this->imported_data_parsed_model->getByImId($im_data_id);

            if ($data_import['description'] !== null && trim($data_import['description']) !== "") {
                $data_import['description'] = preg_replace('/\s+/', ' ', $data_import['description']);
                // $data_import['description'] = preg_replace('/[^A-Za-z0-9\. -!]/', ' ', $data_import['description']);
                $data['s_product_short_desc_count'] = count(explode(" ", $data_import['description']));
            }
            if ($data_import['long_description'] !== null && trim($data_import['long_description']) !== "") {
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
                $rows = $this->similar_data_model->get_group_id($im_data_id);

                //echo "<pre>";
                // print_r($rows);
                if (count($rows) > 0) {

                    foreach ($same_pr as $val) {
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
                        $data_similar['imported_data_id'] = $row['group_id'];
                        $n = parse_url($data_similar['url']);
                        $customer = $n['host'];
                        $customer = str_replace("www1.", "", $customer);
                        $customer = str_replace("www.", "", $customer);
                        $data_similar['customer'] = $customer;

                        if (!in_array($customer, $url)) {
                            $url[] = $customer;
                            $same_pr[] = $data_similar;
                        }
                    }
                }
            }

//            if (empty($same_pr) && isset($data_import['parsed_attributes']) && isset($data_import['parsed_attributes']['UPC/EAN/ISBN'])) {
//
//                $same_pr = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['UPC/EAN/ISBN']);
//            }
            if (empty($same_pr) && !isset($data_import['parsed_attributes']['model'])) {
                $data['mismatch_button'] = true;
                if (!$this->similar_product_groups_model->checkIfgroupExists($im_data_id)) {

                    if (!isset($data_import['parsed_attributes'])) {

                        $same_pr = $this->imported_data_parsed_model->getByProductName($im_data_id, $data_import['product_name'], '', $strict);
                    }
                    if (isset($data_import['parsed_attributes'])) {

                        $same_pr = $this->imported_data_parsed_model->getByProductName($im_data_id, $data_import['product_name'], $data_import['parsed_attributes']['manufacturer'], $strict);
                    }
                } else {
                    $this->load->model('similar_imported_data_model');
                    $customers_list = array();
                    $query_cus = $this->similar_imported_data_model->db->order_by('name', 'asc')->get('sites');
                    $query_cus_res = $query_cus->result();
                    if (count($query_cus_res) > 0) {
                        foreach ($query_cus_res as $key => $value) {
                            $n = parse_url($value->url);
                            $customers_list[] = $n['host'];
                        }
                    }
                    $customers_list = array_unique($customers_list);
                    $rows = $this->similar_data_model->getByGroupId($im_data_id);
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
            // get similar for first row
            $this->load->model('similar_imported_data_model');

            $customers_list = array();
            $query_cus = $this->similar_imported_data_model->db->order_by('name', 'asc')->get('sites');
            $query_cus_res = $query_cus->result();
            if (count($query_cus_res) > 0) {
                foreach ($query_cus_res as $key => $value) {
                    $n = parse_url($value->url);
                    $customers_list[] = $n['host'];
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

            foreach ($same_pr as $ks => $vs) {

                $this->load->model('sites_model');
                //echo $this->get_base_url($vs['url']);
                //echo 'bbb'.strtolower($this->sites_model->get_name_by_url($this->get_base_url($vs['url']))).'aaaaaaaaa';

                $same_pr[$ks]['customer'] = strtolower($this->sites_model->get_name_by_url($same_pr[$ks]['customer']));
                $same_pr[$ks]['seo']['short'] = $this->helpers->measure_analyzer_start_v2_product_name($vs['product_name'], preg_replace('/\s+/', ' ', $vs['description']));
                $same_pr[$ks]['seo']['long'] = $this->helpers->measure_analyzer_start_v2_product_name($vs['product_name'], preg_replace('/\s+/', ' ', $vs['long_description']));

                // three last prices
                $imported_data_id = $same_pr[$ks]['imported_data_id'];
                $three_last_prices = $this->imported_data_parsed_model->getLastPrices($imported_data_id);
                $same_pr[$ks]['three_last_prices'] = $three_last_prices;
                if (!empty($three_last_prices)) {
                    $same_pr[$ks]['three_last_prices'] = $three_last_prices;
                } elseif ($this->imported_data_parsed_model->PriceOld($imported_data_id)) {
                    $same_pr[$ks]['three_last_prices'] = array((object) array('price' => $this->imported_data_parsed_model->PriceOld($imported_data_id), 'created' => ''));
                } else {
                    $same_pr[$ks]['three_last_prices'] = array();
                }


                $keywords = $this->imported_data_parsed_model->getKeywordsBy_imported_data_id($imported_data_id);
                $same_pr[$ks]['seo']['keyword'] = $keywords;

                $parsed_meta = $this->imported_data_parsed_model->getByImId($imported_data_id);
                $same_pr[$ks]['parsed_meta'] = $parsed_meta['parsed_meta'];
            }

            $selectedUrl = $this->input->post('selectedUrl');
            foreach ($same_pr as $ks => $vs) {
                if ($this->get_base_url($vs['url']) == $this->get_base_url($selectedUrl)) {
                    if ($ks != 0) {
                        $same_pr[] = $same_pr[0];
                        $same_pr[0] = $vs;
                        unset($same_pr[$ks]);
                    }
                }
            }


            if ($show_from != 'null') {

                foreach ($same_pr as $ks => $vs) {
                    if (!in_array($vs['customer'], $show_from)) {
                        unset($same_pr[$ks]);
                    }
                }
            }


            //     Max
            if (count($same_pr) != 1) {
                foreach ($same_pr as $ks => $vs) {
                    $maxshort = 0;
                    $maxlong = 0;
                    $maxshorttext = 0;
                    $maxlongtext = 0;
                    $k_sh = 0;
                    $k_lng = 0;
                    foreach ($same_pr as $ks1 => $vs1) {

                        if ($ks != $ks1) {
                            if ($vs['description'] != '') {
                                if ($vs1['description'] != '') {
                                    //echo 1;
                                    $k_sh++;
                                    //$percent = array();
                                    $percent = $this->compare_text($vs['description'], $vs1['description']);
                                    if ($percent[0] > $maxshort) {
                                        $maxshort = $percent[0];
                                        $maxshorttext = $percent[1];
                                    }
                                }

                                if ($vs1['long_description'] != '') {
                                    // echo 2;
                                    $k_sh++;
                                    $percent = $this->compare_text($vs['description'], $vs1['long_description']);
                                    if ($percent[0] > $maxshort) {
                                        $maxshort = $percent[0];
                                        $maxshorttext = $percent[1];
                                    }
                                }
                            }

                            if ($vs['long_description'] != '') {

                                if ($vs1['description'] != '') {
                                    //echo 3
                                    $k_lng++;
                                    $percent = $this->compare_text($vs['long_description'], $vs1['description']);
                                    if ($percent[0] > $maxlong) {
                                        $maxlong = $percent[0];
                                        $maxlongtext = $percent[1];
                                    }
                                }

                                if ($vs1['long_description'] != '') {
                                    //echo 4;
                                    $k_lng++;
                                    $percent = $this->compare_text($vs['long_description'], $vs1['long_description']);
                                    if ($percent[0] > $maxlong) {
                                        $maxlong = $percent[0];
                                        $maxlongtext = $percent[1];
                                    }
                                }
                            }
                        }
                    }
                    if ($maxshort != 0) {
                        $vs['short_original'] = ceil($maxshort) . '%';
                        $vs['short_original_text'] = $maxshorttext;
                    } else {
                        $vs['short_original'] = "Insufficient data";
                        unset($vs['short_original_text']);
                    }

                    if ($maxlong != 0) {
                        $vs['long_original'] = ceil($maxlong) . '%';
                        $vs['long_original_text'] = $maxlongtext;
                    } else {
                        $vs['long_original'] = "Insufficient data";
                        unset($vs['long_original_text']);
                    }

                    if ($k_lng == 0) {
                        $vs['long_original'] = "Insufficient data";
                        unset($vs['long_original_text']);
                    }
                    if ($k_sh == 0) {
                        $vs['short_original'] = "Insufficient data";
                        unset($vs['short_original_text']);
                    }

                    $same_pr[$ks] = $vs;
                }
            } else {
                $same_pr[0]['long_original'] = 'Insufficient data';
                $same_pr[0]['short_original'] = 'Insufficient data';
                unset($vs['short_original_text']);
                unset($vs['long_original_text']);
            }
            //   Max
//Max

            foreach ($same_pr as $ks => $vs) {
                $model = $this->imported_data_parsed_model->getByImId($vs['imported_data_id']);
                if ($model) {
                    $same_pr[$ks]['parsed_attributes'] = $model['parsed_attributes'];
                }

                if (!empty($vs['seo']['short'])) {
                    foreach ($vs['seo']['short'] as $key => $val) {
                        $volume = '';
                        $from_keyword_data = $this->keywords_model->get_by_keyword($val['ph']);
                        if (count($from_keyword_data) > 0) {
                            $volume = $from_keyword_data['volume'];
                        }
                        $words = count(explode(' ', $val['ph']));
                        $desc_words_count = count(explode(' ', $vs['description']));
                        $count = $val['count'];
                        $val['prc'] = round($count * $words / $desc_words_count * 100, 2);
                        $val['volume'] = $volume;
                        $same_pr[$ks]['seo']['short'][$key] = $val;
                    }
                }
                if (!empty($vs['seo']['long'])) {
                    foreach ($vs['seo']['long'] as $key => $val) {
                        $volume = '';
                        $from_keyword_data = $this->keywords_model->get_by_keyword($val['ph']);
                        if (count($from_keyword_data) > 0) {
                            $volume = $from_keyword_data['volume'];
                        }
                        $words = count(explode(' ', $val['ph']));
                        $desc_words_count = count(explode(' ', $vs['long_description']));
                        $count = $val['count'];
                        $same_pr[$ks]['seo']['long'][$key]['prc'] = round($count * $words / $desc_words_count * 100, 2);
                        $same_pr[$ks]['seo']['long'][$key]['volume'] = $volume;
                    }
                }
            }


            foreach ($same_pr as $ks => $vs) {
                $custom_seo = $this->keywords_model->get_by_imp_id($vs['imported_data_id']);
                $meta = array();
                if ((isset($vs['parsed_meta']['Keywords']) && $vs['parsed_meta']['Keywords'] != '')) {
                    $meta = explode(',', $vs['parsed_meta']['Keywords']);
                }
                if ((isset($vs['parsed_meta']['keywords']) && $vs['parsed_meta']['keywords'] != '')) {
                    $meta = explode(',', $vs['parsed_meta']['keywords']);
                }
                if (count($meta) > 0 && isset($vs['description']) && $vs['description'] != '') {
                    foreach ($meta as $key => $val) {
                        $volume = '';
                        $from_keyword_data = $this->keywords_model->get_by_keyword($val['ph']);
                        if (count($from_keyword_data) > 0) {
                            $volume = $from_keyword_data['volume'];
                        }
                        $words = count(explode(' ', trim($val)));
                        $count = $this->keywords_appearence_count(strtolower($vs['description']), strtolower($val));
                        $desc_words_count = count(explode(' ', $vs['description']));

                        $prc = round($count * $words / $desc_words_count * 100, 2);
                        $same_pr[$ks]['short_meta'][] = array('value' => $val, 'count' => $count, 'prc' => $prc, 'volume' => $volume);
                    }
                }
                if (count($meta) > 0 && isset($vs['long_description']) && $vs['long_description'] != '') {

                    foreach ($meta as $key => $val) {
                        $volume = '';
                        $from_keyword_data = $this->keywords_model->get_by_keyword($val);
                        if (count($from_keyword_data) > 0) {
                            $volume = $from_keyword_data['volume'];
                        }
                        $words = count(explode(' ', trim($val)));
                        $count = $this->keywords_appearence_count(strtolower($vs['long_description']), strtolower($val));
                        $desc_words_count = count(explode(' ', $vs['long_description']));

                        $prc = round($count * $words / $desc_words_count * 100, 2);
                        $same_pr[$ks]['long_meta'][] = array('value' => $val, 'count' => $count, 'prc' => $prc, 'volume' => $volume);
                    }
                }
                $same_pr[$ks]['custom_seo'] = $custom_seo;
                if ($res = $this->statistics_model->getbyimpid($vs['imported_data_id'])) {
                    $same_pr[$ks]['short_description_wc'] = $res['short_description_wc'];
                    $same_pr[$ks]['long_description_wc'] = $res['long_description_wc'];
                    //$same_pr[$ks]['seo']['long']= $res['short_seo_phrases']!='None'? unserialize($res['short_seo_phrases']):array();
                    //$same_pr[$ks]['seo']['long']= $res['long_seo_phrases']!='None'?unserialize($res['long_seo_phrases']):array();
                }
            }





            $data['same_pr'] = $same_pr;

//            }
            // --- ATTEMPT TO GET 'SAME' FROM 'HUMAN INTERFACE' (products_compare table) (END)
            // --- GET SELECTED RPODUCT SEO DATA (TMP) (START)
            if ($data_import['description'] !== null && trim($data_import['description']) !== "") {
                $data['seo']['short'] = $this->helpers->measure_analyzer_start_v2($data_import['description']);
            }
            if ($data_import['long_description'] !== null && trim($data_import['long_description']) !== "") {
                $data['seo']['long'] = $this->helpers->measure_analyzer_start_v2($data_import['long_description']);
            }
            // --- GET SELECTED RPODUCT SEO DATA (TMP) (END)
        }

        // -------- COMPARING V1 (START)
        $s_term = $this->input->post('s_term');

        // -------- COMPARING V1 (END)


        $var = explode('?', $this->input->post('current_url'));
        $page = preg_replace('/.*\/([^\/])/', '$1', $var[0]);
        unset($var);

        if ($page == 'measure_products_test')
            $this->load->view('measure/gridview_test', $data);
        else
            $this->load->view('measure/gridview', $data);
    }

    private function keywords_appearence_count($desc, $phrase) {
        return substr_count($desc, $phrase);
    }

    public function save_new_words() {
        $keyword = $this->input->post('keywords');
        $keyword_num = $this->input->post('keyword_num');
        $imported_data_id = $this->input->post('imported_data_id');

        $query = $this->db->where('imported_data_id = ' . $imported_data_id . ' AND word_num = ' . $keyword_num)
                ->get('keywords');
        $result = $query->result();

        if ($query->num_rows() > 0) {
            foreach ($result as $rs) {
                $id = $rs->id;
            }
            $data_update = array(
                'imported_data_id' => $imported_data_id,
                'word_num' => $keyword_num,
                'keyword' => $keyword
            );
            $this->db->where('id', $id);
            $this->db->update('keywords', $data_update);
        } else {
            $data = array(
                'imported_data_id' => $imported_data_id,
                'word_num' => $keyword_num,
                'keyword' => $keyword
            );
            $this->db->set($data);
            $this->db->insert('keywords');
        }
    }

    function tableview() {
        if ($same_pr = $this->input->post('result_data')) {
            $data['ind0'] = $this->input->post('ind0');
            $data['ind1'] = $this->input->post('ind1');
            $data['same_pr'] = $same_pr;
            $this->load->view('measure/tableview', $data);
        } else {
            $im_data_id = $this->input->post('im_data_id');

            $data = array(
                'im_data_id' => $im_data_id,
                's_product' => array(),
                's_product_short_desc_count' => 0,
                's_product_long_desc_count' => 0,
                'seo' => array('short' => array(), 'long' => array()),
                'same_pr' => array()
            );
            if ($im_data_id !== null && is_numeric($im_data_id)) {

                // --- GET SELECTED RPODUCT DATA (START)
                $this->load->model('imported_data_parsed_model');
                $this->load->model('similar_product_groups_model');
                $this->load->model('similar_data_model');
                $data_import = $this->imported_data_parsed_model->getByImId($im_data_id);

                if ($data_import['description'] !== null && trim($data_import['description']) !== "") {
                    $data_import['description'] = preg_replace('/\s+/', ' ', $data_import['description']);
                    // $data_import['description'] = preg_replace('/[^A-Za-z0-9\. -!]/', ' ', $data_import['description']);
                    $data['s_product_short_desc_count'] = count(explode(" ", $data_import['description']));
                }
                if ($data_import['long_description'] !== null && trim($data_import['long_description']) !== "") {
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
                if (empty($same_pr) && !isset($data_import['parsed_attributes']['model'])) {
                    $data['mismatch_button'] = true;
                    if (!$this->similar_product_groups_model->checkIfgroupExists($im_data_id)) {

                        if (!isset($data_import['parsed_attributes'])) {

                            $same_pr = $this->imported_data_parsed_model->getByProductName($im_data_id, $data_import['product_name'], '', $strict);
                        }
                        if (isset($data_import['parsed_attributes'])) {

                            $same_pr = $this->imported_data_parsed_model->getByProductName($im_data_id, $data_import['product_name'], $data_import['parsed_attributes']['manufacturer'], $strict);
                        }
                    } else {
                        $this->load->model('similar_imported_data_model');
                        $customers_list = array();
                        $query_cus = $this->similar_imported_data_model->db->order_by('name', 'asc')->get('sites');
                        $query_cus_res = $query_cus->result();
                        if (count($query_cus_res) > 0) {
                            foreach ($query_cus_res as $key => $value) {
                                $n = parse_url($value->url);
                                $customers_list[] = $n['host'];
                            }
                        }
                        $customers_list = array_unique($customers_list);
                        $rows = $this->similar_data_model->getByGroupId($im_data_id);
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
                // get similar for first row
                $this->load->model('similar_imported_data_model');

                $customers_list = array();
                $query_cus = $this->similar_imported_data_model->db->order_by('name', 'asc')->get('sites');
                $query_cus_res = $query_cus->result();
                if (count($query_cus_res) > 0) {
                    foreach ($query_cus_res as $key => $value) {
                        $n = parse_url($value->url);
                        $customers_list[] = $n['host'];
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

                foreach ($same_pr as $ks => $vs) {
                    $this->load->model('sites_model');
                    $same_pr[$ks]['customer'] = strtolower($this->sites_model->get_name_by_url($same_pr[$ks]['customer']));
                    $same_pr[$ks]['seo']['short'] = $this->helpers->measure_analyzer_start_v2_product_name($vs['product_name'], preg_replace('/\s+/', ' ', $vs['description']));
                    $same_pr[$ks]['seo']['long'] = $this->helpers->measure_analyzer_start_v2_product_name($vs['product_name'], preg_replace('/\s+/', ' ', $vs['long_description']));
                    $imported_data_id = $same_pr[$ks]['imported_data_id'];
                    //snap
                    $this->load->model('crawler_list_model');
                    $same_pr[$ks]['snap'] = $this->crawler_list_model->selectSnap($imported_data_id);

                    // three last prices

                    $three_last_prices = $this->imported_data_parsed_model->getLastPrices($imported_data_id);
                    $same_pr[$ks]['three_last_prices'] = $three_last_prices;
                    if (!empty($three_last_prices)) {
                        $same_pr[$ks]['three_last_prices'] = $three_last_prices;
                    } elseif ($this->imported_data_parsed_model->PriceOld($imported_data_id)) {
                        $same_pr[$ks]['three_last_prices'] = array((object) array('price' => $this->imported_data_parsed_model->PriceOld($imported_data_id), 'created' => ''));
                    } else {
                        $same_pr[$ks]['three_last_prices'] = array();
                    }
                }



                //     Max
                if (count($same_pr) != 1) {
                    foreach ($same_pr as $ks => $vs) {
                        $maxshort = 0;
                        $maxlong = 0;
                        $maxshorttext = 0;
                        $maxlongtext = 0;
                        $k_sh = 0;
                        $k_lng = 0;
                        foreach ($same_pr as $ks1 => $vs1) {

                            if ($ks != $ks1) {
                                if ($vs['description'] != '') {
                                    if ($vs1['description'] != '') {
                                        //echo 1;
                                        $k_sh++;
                                        //$percent = array();
                                        $percent = $this->compare_text($vs['description'], $vs1['description']);
                                        if ($percent[0] > $maxshort) {
                                            $maxshort = $percent[0];
                                        }
                                    }

                                    if ($vs1['long_description'] != '') {
                                        // echo 2;
                                        $k_sh++;
                                        $percent = $this->compare_text($vs['description'], $vs1['long_description']);
                                        if ($percent[0] > $maxshort) {
                                            $maxshort = $percent[0];
                                        }
                                    }
                                }

                                if ($vs['long_description'] != '') {

                                    if ($vs1['description'] != '') {
                                        //echo 3
                                        $k_lng++;
                                        $percent = $this->compare_text($vs['long_description'], $vs1['description']);
                                        if ($percent[0] > $maxlong) {
                                            $maxlong = $percent[0];
                                        }
                                    }

                                    if ($vs1['long_description'] != '') {
                                        //echo 4;
                                        $k_lng++;
                                        $percent = $this->compare_text($vs['long_description'], $vs1['long_description']);
                                        if ($percent[0] > $maxlong) {
                                            $maxlong = $percent[0];
                                        }
                                    }
                                }
                            }
                        }
                        if ($maxshort != 0) {
                            $vs['short_original'] = ceil($maxshort) . '%';
                        } else {
                            $vs['short_original'] = "Insufficient data";
                        }

                        if ($maxlong != 0) {
                            $vs['long_original'] = ceil($maxlong) . '%';
                        } else {
                            $vs['long_original'] = "Insufficient data";
                        }

                        if ($k_lng == 0) {
                            $vs['long_original'] = "Insufficient data";
                        }
                        if ($k_sh == 0) {
                            $vs['short_original'] = "Insufficient data";
                        }

                        $same_pr[$ks] = $vs;
                    }
                } else {
                    $same_pr[0]['long_original'] = 'Insufficient data';
                    $same_pr[0]['short_original'] = 'Insufficient data';
                }
                //   Max
//Max
                $selectedUrl = $this->input->post('selectedUrl');
                foreach ($same_pr as $ks => $vs) {

                    if ($this->get_base_url($vs['url']) == $this->get_base_url($selectedUrl)) {
                        if ($ks != 0) {
                            $same_pr[] = $same_pr[0];
                            $same_pr[0] = $vs;
                            unset($same_pr[$ks]);
                        }
                    }
                }

                foreach ($same_pr as $ks => $vs) {

                    if ($res = $this->statistics_model->getbyimpid($vs['imported_data_id'])) {

                        $same_pr[$ks]['short_description_wc'] = $res['short_description_wc'];
                        $same_pr[$ks]['long_description_wc'] = $res['long_description_wc'];
                        $same_pr[$ks]['seo']['long'] = $res['short_seo_phrases'] != 'None' ? unserialize($res['short_seo_phrases']) : array();
                        $same_pr[$ks]['seo']['long'] = $res['long_seo_phrases'] != 'None' ? unserialize($res['long_seo_phrases']) : array();
                    }
                }

                $data['same_pr'] = $same_pr;


//            }
                // --- ATTEMPT TO GET 'SAME' FROM 'HUMAN INTERFACE' (products_compare table) (END)
                // --- GET SELECTED RPODUCT SEO DATA (TMP) (START)
                if ($data_import['description'] !== null && trim($data_import['description']) !== "") {
                    $data['seo']['short'] = $this->helpers->measure_analyzer_start_v2($data_import['description']);
                }
                if ($data_import['long_description'] !== null && trim($data_import['long_description']) !== "") {
                    $data['seo']['long'] = $this->helpers->measure_analyzer_start_v2($data_import['long_description']);
                }
                // --- GET SELECTED RPODUCT SEO DATA (TMP) (END)
            }

            // -------- COMPARING V1 (START)
            $s_term = $this->input->post('s_term');

            // -------- COMPARING V1 (END)

            $this->load->view('measure/tableview', $data);
        }
    }

    public function getcustomerslist_new() {
        $this->load->model('customers_model');
        $this->load->model('users_to_customers_model');
        $admin = $this->ion_auth->is_admin($this->ion_auth->get_user_id());
        $customers_init_list = $this->users_to_customers_model->getByUserId($this->ion_auth->get_user_id());
        if (count($customers_init_list) == 0 && $admin) {
            $customers_init_list = $this->customers_model->getAll();
        }

        if (count($customers_init_list) > 0) {
            if (count($customers_init_list) != 1) {
                $output[] = array('text' => 'All Customers',
                    'value' => 'All Customers',
                    'image' => ''
                );
            }
            foreach ($customers_init_list as $key => $value) {
                $output[] = array('text' => '',
                    'value' => strtolower($value->name),
                    'image' => base_url() . 'img/' . $value->image_url
                );
            }
        } else {
            $output[] = array('text' => 'No Customers',
                'value' => 'No Customers',
                'image' => ''
            );
        }
        $this->output->set_content_type('application/json')->set_output(json_encode($output));
    }

    public function getsiteslist_new() {
        $this->load->model('sites_model');
        $customers_init_list = $this->sites_model->getAll();
        if (count($customers_init_list) > 0) {
            $output[] = array('text' => 'All sites',
                'value' => 'All sites',
                'image' => ''
            );
            foreach ($customers_init_list as $key => $value) {
                $output[] = array('text' => '',
                    'value' => strtolower($value->name),
                    'image' => base_url() . 'img/' . $value->image_url
                );
            }
        }
        $this->output->set_content_type('application/json')->set_output(json_encode($output));
    }

    public function getcustomerslist() {
        $this->load->model('customers_model');
        $output = array();
        $customers_init_list = $this->customers_model->getAll();
        if (count($customers_init_list) > 0) {
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
        $output = $this->measure_analyzer_keywords($primary_ph, $secondary_ph, $tertiary_ph, $short_desc, $long_desc);
        $this->output->set_content_type('application/json')->set_output(json_encode($output));
    }

    public function searchmeasuredball() {
        $status_results = $this->input->post('status_results');
        $selected_cites = $this->input->post('selected_cites');

        if ($selected_cites != 'null') {
            $selected_cites = explode(',', $selected_cites);
            foreach ($selected_cites as $key => $val) {
                $selected_cites[$key] = strtolower($val);
            }
        }
        $batch_id = $this->input->post('batch_id');
        if (!$batch_id) {
            $s = $this->input->post('s');
            $sl = $this->input->post('sl');
            $cat_id = $this->input->post('cat');
            $limit = $this->input->post('limit');
            $this->load->model('imported_data_parsed_model');
            $data = array(
                'search_results' => array()
            );

            if ($limit !== 0) {
                if (preg_match('/www/', $s) || preg_match('/http:/', $s)) {

                    $data_import = $this->imported_data_parsed_model->getData($s, $sl, $cat_id, $limit, 'URL');
                } else {
                    $data_import = $this->imported_data_parsed_model->getData($s, $sl, $cat_id, $limit);
                }
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
            foreach ($data_import as $key => $row) {
                $volume[$key] = $row['product_name'];
            }
            array_multisort($volume, SORT_ASC, $data_import);

            $data['search_results'] = $data_import;
            $this->load->view('measure/searchmeasuredball', $data);
        } else {

            $this->load->model('research_data_model');

            $result = $this->research_data_model->get_by_batch_id($batch_id);
            if ($status_results == 'no_match') {
                foreach ($result as $kay => $val) {
                    $matches_sites = $this->matches_count($val['imported_data_id']);
                    if (count($matches_sites) > 1) {

                        unset($result[$kay]);
                    }
                }
            }
            if ($status_results == 'one_match') {

                foreach ($result as $kay => $val) {
                    $matches_sites = $this->matches_count($val['imported_data_id']);
                   
                    if (count($matches_sites) == 1) {

                        unset($result[$kay]);
                    }
                }
            }
            if ($status_results == 'matchon' && $selected_cites != 'null') {

                foreach ($result as $kay => $val) {
                    $matches_sites = array_unique($this->matches_count($val['imported_data_id']));
                    if (count($matches_sites) == 1 && count($selected_cites) > 1) {
                        if (count(array_intersect($matches_sites, $selected_cites)) < 2) {

                            unset($result[$kay]);
                        }
                    } else {
                        if (count(array_intersect($matches_sites, $selected_cites)) < 1) {

                            unset($result[$kay]);
                        }
                    }
                }
            }
            foreach ($result as $key => $row) {
                $volume[$key] = $row['product_name'];
            }
            array_multisort($volume, SORT_ASC, $result);

            $data['search_results'] = $result;

            $this->load->view('measure/searchmeasuredball', $data);
        }
    }

    public function attributesmeasure() {

        $s = $this->input->post('s');

        $data = array('search_results' => '', 'file_id' => '', 'product_descriptions' => '', 'product_title' => '');
        $attributes = array();

        $attr_path = $this->config->item('attr_path');

        if ($path = realpath($attr_path)) {
            $objects = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path), RecursiveIteratorIterator::SELF_FIRST);
            foreach ($objects as $name => $object) {
                if (!$object->isDir()) {
                    if ($object->getFilename() == 'attributes.dat') {
                        if ($content = file_get_contents($name)) {
                            if (preg_match("/$s/i", $content, $matches)) {

                                $part = str_ireplace($attr_path, '', $object->getPath());
                                if (preg_match('/\D*(\d*)/i', $part, $matches)) {
                                    $data['file_id'] = $matches[1];
                                }

                                foreach ($this->config->item('attr_replace') as $replacement) {
                                    $content = str_replace(array_keys($replacement), array_values($replacement), $content);
                                }

                                $data['search_results'] = nl2br($content);

                                if (preg_match_all('/\s?(\S*)\s*(.*)/i', $content, $matches)) {
                                    foreach ($matches[1] as $i => $v) {
                                        if (!empty($v))
                                            $attributes[strtoupper($v)] = $matches[2][$i];
                                    }
                                }

                                if (!empty($attributes)) {
                                    $title = array();
                                    foreach ($this->settings['product_title'] as $v) {
                                        if (isset($attributes[strtoupper($v)]))
                                            $title[] = $attributes[strtoupper($v)];
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
            $descCmd = str_replace($this->config->item('cmd_mask'), $data['file_id'], $this->system_settings['java_cmd']);
            if ($result = shell_exec($descCmd)) {
                if (preg_match_all('/\(.*\)\: "(.*)"/i', $result, $matches) && isset($matches[1]) && count($matches[1]) > 0) {
                    if (is_array($data['product_descriptions']))
                        $data['product_descriptions'] = array_merge($data['product_descriptions'], $matches[1]);
                    else
                        $data['product_descriptions'] = $matches[1];
                }
            }
        }
        if ($this->system_settings['python_generator']) {
            $descCmd = str_replace($this->config->item('cmd_mask'), $s, $this->system_settings['python_cmd']);
            if ($result = shell_exec($descCmd)) {
                if (preg_match_all('/.*ELECTR_DESCRIPTION:\s*(.*)\s*-{5,}/', $result, $matches)) {
                    if (is_array($data['product_descriptions']))
                        $data['product_descriptions'] = array_merge($data['product_descriptions'], $matches[1]);
                    else
                        $data['product_descriptions'] = $matches[1];
                }
            }
        }

        if (!empty($this->exceptions) && !empty($data['attributes'])) {
            foreach ($data['attributes'] as $key => $value) {
                foreach ($this->exceptions as $exception) {
                    if ($exception['attribute_name'] == $key AND $exception['attribute_value'] == $value) {
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

    public function get_best_sellers() {
        $this->load->model('best_sellers_model');
        $this->load->model('sites_model');
        $department = '';
        if ($this->input->post('site') != '') {
            $site_id = $this->sites_model->getIdByName($this->input->post('site'));
            if ($this->input->post('department') != '' && $this->input->post('department') != 'All') {
                $department = $this->input->post('department');
            }
            $output = $this->best_sellers_model->getAllBySiteId($site_id, $department);
        } else {
            $output = $this->best_sellers_model->getAll();
        }
        $this->output->set_content_type('application/json')
                ->set_output(json_encode($output));
    }

    public function addseo() {
        $primary = $this->input->post('primary');
        $secondary = $this->input->post('secondary');
        $tertiary = $this->input->post('tertiary');
        $imported_data_id = $this->input->post('imported_data_id');

        $this->keywords_model->insert($imported_data_id, $primary, $secondary, $tertiary);
    }

    public function measure_analyzer_keywords($primary_ph, $secondary_ph, $tertiary_ph, $short_desc, $long_desc) {
        $this->load->model('keywords_model');
        // --- default res array and values (start)
        $primary_ph = strtolower($primary_ph);
        $secondary_ph = strtolower($secondary_ph);
        $tertiary_ph = strtolower($tertiary_ph);
        $short_desc = strtolower($short_desc);
        $long_desc = strtolower($long_desc);

        $res = array();
        $res['primary']=array(0=>array('prc'=>0), 1=> array('prc'=>0));
        $res['secondary']=array(0=>array('prc'=>0), 1=> array('prc'=>0));
        $res['secondary']=array(0=>array('prc'=>0), 1=> array('prc'=>0));
        $short_desc_words_count = count(explode(" ", $short_desc));
        $long_desc_words_count = count(explode(" ", $long_desc));
        // --- default res array and values (end)
        // --- primary calculation (start)
        if ($primary_ph !== "") {
            $primary_ph_words_count = count(explode(" ", $primary_ph));
            if ($short_desc !== "") {
                // if($this->keywords_appearence($short_desc, $primary_ph) !== 0) $res['primary'][0] = $short_desc_words_count / ($this->keywords_appearence($short_desc, $primary_ph) * $primary_ph_words_count);
                $res['primary'][0]['prc'] = ($this->keywords_appearence($short_desc, $primary_ph) * $primary_ph_words_count) / $short_desc_words_count;

                $volume = '';
                $from_keyword_data = $this->keywords_model->get_by_keyword($primary_ph);
                if (count($from_keyword_data) > 0) {
                    $volume = $from_keyword_data['volume'];
                }
                $res['primary'][0]['volume'] = $volume;
            }
            if ($long_desc !== "") {
                // if($this->keywords_appearence($long_desc, $primary_ph) !== 0) $res['primary'][1] = $long_desc_words_count / ($this->keywords_appearence($long_desc, $primary_ph) * $primary_ph_words_count);
                $res['primary'][1]['prc'] = ($this->keywords_appearence($long_desc, $primary_ph) * $primary_ph_words_count) / $long_desc_words_count;

                $volume = '';
                $from_keyword_data = $this->keywords_model->get_by_keyword($primary_ph);
                if (count($from_keyword_data) > 0) {
                    $volume = $from_keyword_data['volume'];
                }
                $res['primary'][1]['volume'] = $volume;
            }
        }
        // --- primary calculation (end)
        // --- secondary calculation (start)
        if ($secondary_ph !== "") {
            $secondary_ph_words_count = count(explode(" ", $secondary_ph));
            if ($short_desc !== "") {
                // if($this->keywords_appearence($short_desc, $secondary_ph) !== 0) $res['secondary'][0] = $short_desc_words_count / ($this->keywords_appearence($short_desc, $secondary_ph) * $secondary_ph_words_count);
                $res['secondary'][0]['prc'] = ($this->keywords_appearence($short_desc, $secondary_ph) * $secondary_ph_words_count) / $short_desc_words_count;

                $volume = '';
                $from_keyword_data = $this->keywords_model->get_by_keyword($secondary_ph);
                if (count($from_keyword_data) > 0) {
                    $volume = $from_keyword_data['volume'];
                }
                $res['secondary'][0]['volume'] = $volume;
            }
            if ($long_desc !== "") {
                // if($this->keywords_appearence($long_desc, $secondary_ph) !== 0) $res['secondary'][1] = $long_desc_words_count / ($this->keywords_appearence($long_desc, $secondary_ph) * $secondary_ph_words_count);
                $res['secondary'][1]['prc'] = ($this->keywords_appearence($long_desc, $secondary_ph) * $secondary_ph_words_count) / $long_desc_words_count;
                $volume = '';
                $from_keyword_data = $this->keywords_model->get_by_keyword($secondary_ph);
                if (count($from_keyword_data) > 0) {
                    $volume = $from_keyword_data['volume'];
                }
                $res['secondary'][1]['volume'] = $volume;
            }
        }
        // --- secondary calculation (end)
        // --- tertiary calculation (start)
        if ($tertiary_ph !== "") {
            $tertiary_ph_words_count = count(explode(" ", $tertiary_ph));
            if ($short_desc !== "") {
                // if($this->keywords_appearence($short_desc, $tertiary_ph) !== 0) $res['tertiary'][0] = $short_desc_words_count / ($this->keywords_appearence($short_desc, $tertiary_ph) * $tertiary_ph_words_count);
                $res['tertiary'][0]['prc'] = ($this->keywords_appearence($short_desc, $tertiary_ph) * $tertiary_ph_words_count) / $short_desc_words_count;

                $volume = '';
                $from_keyword_data = $this->keywords_model->get_by_keyword($tertiary_ph);
                if (count($from_keyword_data) > 0) {
                    $volume = $from_keyword_data['volume'];
                }
                $res['tertiary'][0]['volume'] = $volume;
            }
            if ($long_desc !== "") {
                // if($this->keywords_appearence($long_desc, $tertiary_ph) !== 0) $res['tertiary'][1] = $long_desc_words_count / ($this->keywords_appearence($long_desc, $tertiary_ph) * $tertiary_ph_words_count);
                $res['tertiary'][1]['prc'] = ($this->keywords_appearence($long_desc, $tertiary_ph) * $tertiary_ph_words_count) / $long_desc_words_count;
                $volume = '';
                $from_keyword_data = $this->keywords_model->get_by_keyword($tertiary_ph);
                if (count($from_keyword_data) > 0) {
                    $volume = $from_keyword_data['volume'];
                }
                $res['tertiary'][1]['volume'] = $volume;
            }
        }
        // --- tertiary calculation (end)

        return $res;
    }

    private function keywords_appearence($desc, $phrase) {
        return substr_count($desc, $phrase);
    }

}
