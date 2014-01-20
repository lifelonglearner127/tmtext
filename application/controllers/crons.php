<?php

if (!defined('BASEPATH'))
	exit('No direct script access allowed');

class Crons extends MY_Controller
{
    /**
     * Max count by maxthreads
     *
     * @var int
     * @access private
     */
    private $maxthreads;
    
    /**
     * Array hreads
     *
     * @var array
     * @access private
     */
    private $threads = array();
        
	function __construct()
	{
		parent::__construct();
		$this->load->library('ion_auth');
		$this->ion_auth->add_auth_rules(array(
		    'index' => true,
		    'screenscron' => true,
		    'do_stats' => true,
		    'duplicate_content' => true,
		    'do_stats_new' => true,
		    'similar_groups' => true,
		    'do_stats_forupdated' => true,
		    'do_duplicate_content' => true,
		    'ranking_api_exp' => true,
		    'archive_imported_data_parsed' => true,
		    'get_all_rows' => TRUE,
		    'get_update_status' => true,
		    'save_departments_categories' => TRUE,
		    'match_urls' => TRUE,
		    'match_urls_thread' => TRUE,
                    'match_urls_thread_update' => TRUE,
		    'match_urls_thread_worker' => TRUE,
		    'stop_do_stats' => true,
		    'get_stats_status' => true,
		    'stop_do_stats' => true,
		    'delete_batch_items_from_statistics_new' => true,
		    'fix_imported_data_parsed_models' => true,
		    'fixmodel_length' => true,
		    'fix_revisions' => true,
		    'checkUploadedFiles' =>true, 
		    'do_stats_bybatch' =>true, 
		    'renameExistingFiles' =>true 
		));
		$this->load->library('helpers');
		$this->load->helper('algoritm');
	}

	public function index()
	{
		
	}

	public function similar_groups()
	{

		$this->load->model('imported_data_parsed_model');

		$result = $this->imported_data_parsed_model->similiarity_cron_new();
		exit;
		if ($result)
		{
			echo 'call by wget';
			shell_exec("wget -S -O- ".site_url('/crons/similar_groups')." > /dev/null 2>/dev/null &");
			echo 'call by wget AFTER';
		} else
		{
			$data = array(
			    'description' => 0
			);

			$this->db->where('key', 'custom_model_offset');
			$this->db->update('settings', $data);
		}
	}

	public function site_crawler_screens()
	{
		$this->load->model('webshoots_model');
		$this->load->library('email');
		$ids_debug = $_GET['ids'];
		$ids = $_GET['ids'];
		$ids = explode(",", $ids);
		$crawls = $this->webshoots_model->get_crawler_list_by_ids($ids);
		if (count($crawls) > 0)
		{
			foreach ($crawls as $k => $v)
			{
				$http_status = $this->urlExistsCode($v->url);
				$url = preg_replace('#^https?://#', '', $v->url);
				$call_url = $this->webshoots_model->webthumb_call_link($url);
				$snap_res = $this->webshoots_model->crawl_webshoot($call_url, $v->id, 'crawl_snap-');
				$f = $snap_res['img'];
				$file_path = realpath(BASEPATH . "../webroot/webshoots/$f");
				$fs = filesize($file_path);
				if ($fs === false || $fs < 10000)
				{ // === so re-craw it
					@unlink(realpath(BASEPATH . "../webroot/webshoots/$f"));
					$api_key = $this->config->item('snapito_api_secret');
					$call_url = "http://api.snapito.com/web/$api_key/mc/$url";
					$snap_res = $this->webshoots_model->crawl_webshoot($call_url, $v->id, 'crawl_snap-');
				}
				$this->webshoots_model->updateCrawlListWithSnap($v->id, $snap_res['img'], $http_status);
				// === email debug (start)
				$this->email->from('info@dev.contentsolutionsinc.com', 'Cron notification');
				$this->email->to('ishulgin8@gmail.com');
				$this->email->subject('Cron job report for site_crawler_screens');
				$this->email->message("Cron job for site_crawler_screens is done. Crawler list ids: $ids_debug");
				$this->email->send();
				// === email debug (end)
			}
		}
	}

	private function urlExistsCode($url)
	{
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

	/**
	 * Cron Job for CI home tab screenshots generating
	 */
	public function screenscron()
	{
		$customers = $this->customers_list();
		$this->load->model('webshoots_model');
		$week = date("W", time());
		$year = date("Y", time());
		$sites = array();
		foreach ($customers as $k => $v)
		{
			if ($this->urlExists($v['c_url']))
				$sites[] = $v['c_url'];
		}
		// $sites = array_slice($sites, 0, 1);
		foreach ($sites as $url)
		{
			$c_url = preg_replace('#^https?://#', '', $url);
			if ($c_url === 'bjs.com')
			{
				$api_key = $this->config->item('snapito_api_secret');
				$call_url = "http://api.snapito.com/web/$api_key/mc/$c_url";
			} else
			{
				$call_url = $this->webshoots_model->webthumb_call_link($c_url);
			}
			$crawl_l = $this->upload_record_webshoot($call_url, $c_url . "_big");
			$file = $crawl_l['dir'];
			$file_size = filesize($file);
			if ($file_size === false || $file_size < 2048)
			{
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
			    'uid' => 4,
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
		echo "Cron Job Finished";
	}

	private function customers_list()
	{
		$this->load->model('customers_model');
		$output = array();
		$customers_init_list = $this->customers_model->getAll();
		if (count($customers_init_list) > 0)
		{
			foreach ($customers_init_list as $key => $value)
			{
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

	private function urlExists($url)
	{
		if ($url === null || trim($url) === "")
			return false;
		$ch = curl_init($url);
		curl_setopt($ch, CURLOPT_TIMEOUT, 5);
		curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
		$data = curl_exec($ch);
		$httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
		curl_close($ch);
		if ($httpcode >= 200 && $httpcode <= 302)
		{
			return true;
		} else
		{
			return false;
		}
	}

	private function upload_record_webshoot($ext_url, $url_name)
	{
		$file = file_get_contents($ext_url);
		$type = 'png';
		$dir = realpath(BASEPATH . "../webroot/webshoots");
		if (!file_exists($dir))
		{
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
		    'shot_name' => $url_name . "." . $type
		);
		return $res;
	}

	/**
	 * Cron Job for CI home tab screenshots reports mailer
	 */
	public function emailreports()
	{
		$this->load->model('webshoots_model');
		$this->load->model('settings_model');
		$current_day = lcfirst(date('l', time()));
		$c_week = date("W", time());
		$c_year = date("Y", time());
		$data_et['email_logo'] = $email_logo;
		$recs = $this->webshoots_model->get_recipients_list();
		$email_logo = $this->webshoots_model->getEmailReportConfig('logo');
		$email_report_sender_name = $this->settings_model->get_general_setting('site_name');
		if ($email_report_sender_name === false)
			$email_report_sender_name = "Content Solutions - Home Pages Report";

		$email_report_config_sender = $this->webshoots_model->getEmailReportConfig('sender');
		$attach_value = $this->webshoots_model->getEmailReportConfig('attach');
		if ($attach_value == 'yes')
		{
			$attach_st = true;
		} else
		{
			$attach_st = false;
		}
		if (count($recs) > 0)
		{
			$this->load->library('email');

			$config['protocol'] = 'sendmail';
			$config['mailpath'] = '/usr/sbin/sendmail';
			$config['charset'] = 'UTF-8';
			$config['wordwrap'] = TRUE;
			$config['mailtype'] = 'html';

			$this->email->initialize($config);
			foreach ($recs as $k => $v)
			{
				$screens = $this->webshoots_model->getDistinctEmailScreensAnonim($c_week, $c_year);
				// ==== sort assoc by pos (start)
				if (count($screens) > 0)
				{
					$sort = array();
					foreach ($screens as $k => $vs)
					{
						$sort['pos'][$k] = $vs['pos'];
					}
					array_multisort($sort['pos'], SORT_ASC, $screens);
				}
				// ==== sort assoc by pos (end)
				$day = $v->day;
				$email = $v->email;
				$this->email->from("$email_report_config_sender", "$email_report_sender_name");
				$this->email->to("$email");
				$this->email->subject("$email_report_sender_name - Home Pages Report");
				$data_et['day'] = $day;
				$data_et['screens'] = $screens;
				$data_et['email_logo'] = $email_logo;
				$msg = $this->load->view('measure/rec_report_email_template', $data_et, true);
				// die($msg);
				$this->email->message($msg);
				// --- attachments (start)
				if ($attach_st)
				{
					if (count($screens) > 0)
					{
						foreach ($screens as $key => $value)
						{
							$path = $value['dir'];
							$this->email->attach("$path");
						}
					}
				}
				// --- attachments (end)
				$this->email->send();
				echo "Report sended to $email" . "<br>";
			}
		}
		echo "Cron Job Finished";
	}

	public function do_duplicate_content()
	{
		$this->load->model('imported_data_parsed_model');
		$this->load->model('research_data_model');
		$this->load->model('statistics_model');
		$this->load->model('statistics_duplicate_content_model');
		$this->load->model('similar_product_groups_model');
		$this->load->model('similar_data_model');
		$this->load->library('helpers');
		$this->load->helper('algoritm');
		$this->load->model('sites_model');
		$trnc = $this->uri->segment(3);

		if ($trnc === false)
		{
			$trnc = 1;
		}
		$ids = $this->imported_data_parsed_model->do_stats_ids();

		foreach ($ids as $val)
		{
			$query = $this->db->where('imported_data_id', $val->imported_data_id)
				->get('duplicate_content_new');
			if ($query->num_rows() == 0)
			{
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
		$data_arr = $this->imported_data_parsed_model->do_stats_ids();
		if (count($data_arr) > 1)
		{
			shell_exec("wget -S -O- ".site_url('/crons/do_duplicate_content/'.$trnc)." > /dev/null 2>/dev/null &");
		} else
		{
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

	function duplicate_content_new($imported_data_id)
	{

		try
		{

			$res_data = $this->check_duplicate_content($imported_data_id);

			$time_end = microtime(true);
			$time = $time_end - $time_start;
			echo "block with check_duplicate_content - $time seconds\n";
			$time_start = $time_end;
			foreach ($res_data as $val)
			{
				$this->statistics_duplicate_content_model->insert_new($val['imported_data_id'], $val['long_original'], $val['short_original'], '1');
			}
			$time_end = microtime(true);
			$time = $time_end - $time_start;
			echo "foreach insert - $time seconds\n";
		} catch (Exception $e)
		{
			echo 'Error', $e->getMessage(), "\n";
		}
	}

	private function check_duplicate_content($imported_data_id)
	{
		$this->load->model('imported_data_parsed_model');
		$this->load->model('similar_product_groups_model');
		$this->load->model('similar_data_model');
		$data_import = $this->imported_data_parsed_model->getByImId($imported_data_id);

		if ($data_import['description'] !== null && trim($data_import['description']) !== "")
		{
			$data_import['description'] = preg_replace('/\s+/', ' ', $data_import['description']);
			$data['s_product_short_desc_count'] = count(explode(" ", $data_import['description']));
		}
		if ($data_import['long_description'] !== null && trim($data_import['long_description']) !== "")
		{
			$data_import['long_description'] = preg_replace('/\s+/', ' ', $data_import['long_description']);
			$data['s_product_long_desc_count'] = count(explode(" ", $data_import['long_description']));
		}
		$data['s_product'] = $data_import;
		$same_pr = $this->imported_data_parsed_model->getSameProductsHuman($imported_data_id);

		if (empty($same_pr) && isset($data_import['parsed_attributes']) && isset($data_import['parsed_attributes']['model']))
		{
			$strict = $this->input->post('strict');
			$same_pr = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['model'], $strict);
		}

//        if (empty($same_pr) && isset($data_import['parsed_attributes']) && isset($data_import['parsed_attributes']['UPC/EAN/ISBN'])) {
//            $same_pr = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['UPC/EAN/ISBN']);
//        }
		if (empty($same_pr) && !isset($data_import['parsed_attributes']['model']))
		{
			$data['mismatch_button'] = true;
			if (!$this->similar_product_groups_model->checkIfgroupExists($imported_data_id))
			{

				if (!isset($data_import['parsed_attributes']))
				{

					$same_pr = $this->imported_data_parsed_model->getByProductName($imported_data_id, $data_import['product_name'], '', $strict);
				}
				if (isset($data_import['parsed_attributes']))
				{
					$same_pr = $this->imported_data_parsed_model->getByProductName($imported_data_id, $data_import['product_name'], $data_import['parsed_attributes']['manufacturer'], $strict);
				}
			} else
			{
				$this->load->model('similar_imported_data_model');
				$customers_list = array();
				$query_cus = $this->similar_imported_data_model->db->order_by('name', 'asc')->get('customers');
				$query_cus_res = $query_cus->result();
				if (count($query_cus_res) > 0)
				{
					foreach ($query_cus_res as $key => $value)
					{
						$n = parse_url($value->url);
						$customers_list[] = $n['host'];
					}
				}
				$customers_list = array_unique($customers_list);
				$rows = $this->similar_data_model->getByGroupId($imported_data_id);
				$data_similar = array();

				foreach ($rows as $key => $row)
				{
					$data_similar[$key] = $this->imported_data_parsed_model->getByImId($row->imported_data_id);
					$data_similar[$key]['imported_data_id'] = $row->imported_data_id;

					$cus_val = "";
					foreach ($customers_list as $ki => $vi)
					{
						if (strpos($data_similar[$key]['url'], "$vi") !== false)
						{
							$cus_val = $vi;
						}
					}
					if ($cus_val !== "")
						$data_similar[$key]['customer'] = $cus_val;
				}

				if (!empty($data_similar))
				{
					$same_pr = $data_similar;
				}
			}
		}
		if (count($same_pr) != 1)
		{
			foreach ($same_pr as $ks => $vs)
			{
				$maxshort = 0;
				$maxlong = 0;
				$k_sh = 0;
				$k_lng = 0;
				foreach ($same_pr as $ks1 => $vs1)
				{
					if ($ks != $ks1)
					{
						if ($vs['description'] != '')
						{
							if ($vs1['description'] != '')
							{
								$k_sh++;
								$percent = $this->compare_text($vs['description'], $vs1['description']);
								if ($percent > $maxshort)
								{
									$maxshort = $percent;
								}
							}

							if ($vs1['long_description'] != '')
							{
								$k_sh++;
								$percent = $this->compare_text($vs['description'], $vs1['long_description']);
								if ($percent > $maxshort)
								{
									$maxshort = $percent;
								}
							}
						}

						if ($vs['long_description'] != '')
						{

							if ($vs1['description'] != '')
							{
								$k_lng++;
								$percent = $this->compare_text($vs['long_description'], $vs1['description']);
								if ($percent > $maxlong)
								{
									$maxlong = $percent;
								}
							}

							if ($vs1['long_description'] != '')
							{
								$k_lng++;
								$percent = $this->compare_text($vs['long_description'], $vs1['long_description']);
								if ($percent > $maxlong)
								{
									$maxlong = $percent;
								}
							}
						}
					}
				}

				$vs['short_original'] = ceil($maxshort);
				$vs['long_original'] = ceil($maxlong);

				if ($k_lng == 0)
				{
					$vs['long_original'] = 0;
				}
				if ($k_sh == 0)
				{
					$vs['short_original'] = 0;
				}

				$same_pr[$ks] = $vs;
			}
		} else
		{
			$same_pr[0]['long_original'] = 0;
			$same_pr[0]['short_original'] = 0;
		}
		return $same_pr;
	}

	private function compare_text($first_text, $second_text)
	{
		$first_text = preg_replace('/[^a-zA-Z0-9_ %\[\]\.\(\)%&-]/s', '', $first_text);
		$first_text = preg_replace('/[a-zA-Z]-/', ' ', $first_text);
		$second_text = preg_replace('/[^a-zA-Z0-9_ %\[\]\.\(\)%&-]/s', '', $second_text);
		$second_text = preg_replace('/[a-zA-Z]-/', ' ', $second_text);

		if ($first_text === $second_text)
		{
			return 100;
		} else
		{
			$a = explode(' ', strtolower($first_text));

			$b = explode(' ', strtolower($second_text));
			$arr = array_intersect($a, $b);
			$count = count($arr);
			$prc = $count / count($a) * 100;
			return $prc;
		}
	}

	public function get_all_rows()
	{
		$this->load->model('settings_model');
		echo $this->settings_model->countItemsForReset();
	}

	public function stop_do_stats()
	{
		$this->load->model('settings_model');
		$this->settings_model->stopDoStats();
	}

	public function get_stats_status()
	{
		$this->load->model('imported_data_parsed_model');
		$status = $this->imported_data_parsed_model->getDoStatsStatus();
		echo $status ? $status->description : '';
	}

	public function get_update_status()
	{

		$this->load->model('settings_model');
		$this->load->model('imported_data_parsed_model');

		$lud = $this->settings_model->getLastUpdate();
		$dss = $this->settings_model->getDoStatsStatus();
		$res_arr = array();

		if ($dss)
		{
			$res_arr['currentTime'] = date('Y-m-d H:i:s');
			$res_arr['status'] = $dss->description;
			$res_arr['started'] = $dss->created;
			$res_arr['remain'] = $this->settings_model->countItemsForReset();
		}


		if ($lud)
		{
			$res_arr['total'] = $lud['description'];
			$res_arr['updated'] = $lud['modified'];
		}

		$res = json_encode($res_arr);
		echo $res;
	}

	public function delete_batch_items_from_statistics_new()
	{
		$batch_id = intval($this->uri->segment(3));
		$sql_cmd = "select rdc.research_data_id, rd.batch_id
        , idp.imported_data_id
        from crawler_list as cl
        join research_data_to_crawler_list as rdc on cl.id = rdc.crawler_list_id
        join research_data as rd on rdc.research_data_id = rd.id
        join batches as b on b.id = rd.batch_id
        join imported_data_parsed as idp on cl.imported_data_id=idp.imported_data_id
        where rd.batch_id = $batch_id
        and idp.`key`='url'
        group by idp.imported_data_id";
		$q = $this->db->query($sql_cmd);
		$results = $q->result();
		foreach ($results as $res)
		{
			$this->db->delete('statistics_new', array('imported_data_id' => $res->imported_data_id));
		}
		echo "batch_id = $batch_id <br> end";
	}

	public function do_stats_forupdated($forceKeywords = FALSE)
	{
		echo "Script start working";
		$tmp_dir = sys_get_temp_dir() . '/';
		unlink($tmp_dir . ".locked");
		if (file_exists($tmp_dir . ".locked"))
		{
			exit;
		}
		$first_start = time();
		touch($tmp_dir . ".locked");
		$cjo = 0;
		try
		{
			$this->load->model('imported_data_parsed_model');
			$this->load->model('sites_model');
			$this->load->model('statistics_new_model');
			
			//$this->statistics_new_model->truncate();
			
			//Checking the third segment of URI for truncate flag 
			$trnc = $this->uri->segment(3);
			$trnc = $trnc === FALSE ? 0 : 1;
			$this->different_revissions();
			$dss = $this->imported_data_parsed_model->getDoStatsStatus(); //getting status of do_stats process
			if (!$dss) //if status info does not exists
			{
				//Set status for prevent duplicate
				$this->imported_data_parsed_model->setDoStatsStatus();
				$this->settings_model->setLastUpdate(1); //adding last update info
			} else
			{
				if ($dss->description === 'stopped') //if status info exists, and description is 'stopped'
				{
					$this->imported_data_parsed_model->updDoStatsStatus(1); //update status info
				}
				$this->settings_model->setLastUpdate(); //update status info
			}
			//Get items for scanning
			$time_start = microtime(true);
			$data_arr = $this->imported_data_parsed_model->do_stats_newupdated();
			echo "<br>get_data ---- " . (microtime(true) - $time_start);
			if (count($data_arr) > 0) //run analyze if array does not empty
			{
				$sites_list = array();
				//Get all existing sites, generate site list
				$query_cus_res = $this->sites_model->getAll();
				if (count($query_cus_res) > 0)
				{
					foreach ($query_cus_res as $key => $value)
					{
						$n = parse_url($value->url);
						$sites_list[] = $n['host'];
					}
				}
				$this->load->model('customers_model');
				$customersList = $this->customers_model->getCustomersList();
				//end of list creating script
				//Start analize each item
				foreach ($data_arr as $obj)
				{
					$foreach_start = microtime(true);
					$own_price = 0;
					$competitors_prices = array();
					$price_diff = '';
					$items_priced_higher_than_competitors = 0;
					$short_description_wc = 0;
					$long_description_wc = 0;
					$short_seo_phrases = '?';
					$long_seo_phrases = '?';
					$similar_products_competitors = array();
					$manufacturerInfo = '';
					// Price difference
					$own_site = parse_url($obj->url, PHP_URL_HOST);
					if (!$own_site)
					{	
						$own_site = "own site";
					}
					$own_site = str_replace("www1.", "", str_replace("www.", "", $own_site));

					$short_description = '';
					$long_description = '';
					echo "<br>" . "im+daat+id= " . $obj->imported_data_id . "</br>";
					//Prepare description field
					$short_description_wc = 0;
					if (($obj->description !== null || $obj->description !== 'null') && trim($obj->description) !== "")
					{
						$short_description = $obj->description;
						//replace all tags and big spaces to single space
						$obj->description = preg_replace('#<[^>]+>#',' ', $obj->description);
						$obj->description = preg_replace('/\s+/',' ', $obj->description);
						//getting count of words in short description
						$short_description_wc = count(explode(" ", $obj->description));
					}
					//Prepare long description field
					$long_description_wc = 0;
					if (($obj->long_description !== null || $obj->long_description !== 'null') && trim($obj->long_description) !== "")
					{
						$long_description = $obj->long_description;
						//replace all tags and big spaces to single space
						$obj->long_description = preg_replace('#<[^>]+>#', ' ', $obj->long_description);
						$obj->long_description = preg_replace('/\s+/', ' ', $obj->long_description);
						//getting count of words in short description
						$long_description_wc = count(explode(" ", $obj->long_description));
					}
					//Prepare manufacturer info
					if(!empty($obj->manufacturer_url))
					{
						$manufacturerInfo = serialize(array('url'=>$obj->manufacturer_url,
						'images'=>$obj->manufacturer_images,'videos'=>$obj->manufacturer_videos));
					}
					$title_keywords = FALSE;
					if(!$forceKeywords)
					{
						$hash_start = microtime(true);	
						$title_keywords = $this->imported_data_parsed_model->checkHash($obj->imported_data_id, $obj->product_name, $short_description, $long_description);
						echo 'Check hash '.(microtime(true) - $hash_start);
					}
					if(!$title_keywords)
					{	
						// Generate Title Keywords
						$keywords_start = microtime(true);
						$title_keywords = $this->title_keywords($obj->product_name, $short_description, $long_description);
						echo "Title Keywords -------------------- <b>".(microtime(true) - $keywords_start)." seconds</b>\n";
					}
					$modelStart = microtime(true);
					$m = '';
					//If parsed attributes are exist, finding similar items and price diff
					if (isset($obj->parsed_attributes) && isset($obj->parsed_attributes['model']) && strlen($obj->parsed_attributes['model']) > 3)
					{
						//getting model of item
$modelGet = microtime(true);
						if ($obj->model && (strlen($obj->model) > 3))
						{
							$m = $obj->model;
						} else
						{
							$m = $obj->parsed_attributes['model'];
						}
						//getting model of item
						try
						{
							//Get last existing price
							$own_prices = $this->imported_data_parsed_model->getLastPrices($obj->imported_data_id,1);
						} catch (Exception $e)
						{
							echo 'Error', $e->getMessage(), "\n";
							$own_prices = $this->imported_data_parsed_model->getLastPrices($obj->imported_data_id,1);
						}
echo '<br> - model get -- '.(microtime(true) - $modelGet);
						//if own_prices is not empty make price difference data
						if (!empty($own_prices))
						{
$getSimilar = microtime(true);
							$own_price = floatval($own_prices->price);
							$obj->own_price = $own_price;
							$price_diff_exists = array();
							$price_diff_exists['id'] = $own_prices->id;
							$price_diff_exists['own_site'] = $own_site;
							$price_diff_exists['own_price'] = $own_price;
							// getting list of similar items
							try
							{
								$similar_items = $this->imported_data_parsed_model->getByParsedAttributes($m, 0, $obj->imported_data_id,$customersList);
							} catch (Exception $e)
							{
								echo 'Error', $e->getMessage(), "\n";
								$similar_items = $this->imported_data_parsed_model->getByParsedAttributes($m, 0, $obj->imported_data_id,$customersList);
							}
echo '<br> - similar get -- '.(microtime(true) - $getSimilar);
							//If similar items was found, start comparing
							if (!empty($similar_items))
							{
$checkSimilar = microtime(true);								
								foreach ($similar_items as $ks => $vs)
								{
									$customer = "";
									//find customer of similar item
									foreach ($sites_list as $ki => $vi)
									{
										if (strpos($vs['url'], "$vi") !== false)
										{
											$customer = strtolower($this->sites_model->get_name_by_url($vi));
											break;
										}
									}
									
									$similar_products_competitors[] = array(
									    'imported_data_id' => $vs['imported_data_id'],
									    'customer' => $customer
									);
$getPrices = microtime(true);								
									//Getting a three last prices for each item
									try
									{
										$three_last_prices = $this->imported_data_parsed_model->getLastPrices($vs['imported_data_id'],1);
									} catch (Exception $e)
									{
										echo 'Error', $e->getMessage(), "\n";
										//$this->load->model('statistics_model');
										//$this->statistics_model->db->close();
										//$this->statistics_model->db->initialize();
										$three_last_prices = $this->imported_data_parsed_model->getLastPrices($vs['imported_data_id'],1);
									}
echo '<br> -- get last prices -- '.(microtime(true) - $getPrices);									
									//If last three prices are exist, define range of prices and start comparing
									if (!empty($three_last_prices))
									{
										$price_scatter = $own_price * 0.03;
										$price_upper_range = $own_price + $price_scatter;
										$price_lower_range = $own_price - $price_scatter;
										$competitor_price = floatval($three_last_prices->price);
										//If own price greater than competitor price, flag will be set,
										//or if competitor price not in the defined range, then price should be updated 
										if ($competitor_price < $own_price)
										{
											$items_priced_higher_than_competitors = 1;
										}
										if ($competitor_price > $price_upper_range || $competitor_price < $price_lower_range)
										{
											$price_diff_exists['competitor_customer'][] = $similar_items[$ks]['customer'];
											$price_diff_exists['competitor_price'][] = $competitor_price;
											$price_diff = $price_diff_exists;
											$competitors_prices[] = $competitor_price;
										}
									}
echo '<br> - similar check -- '.(microtime(true) - $checkSimilar);									
								}
							}
						} else
						{
$getSimilar2 = 	microtime(true);						
							//own priece does not exists, looking for similar items
							try
							{
								$similar_items = $this->imported_data_parsed_model->getByParsedAttributes($m, 0, $obj->imported_data_id,$customersList);
							} catch (Exception $e)
							{
								echo 'Error', $e->getMessage(), "\n";
								$similar_items = $this->imported_data_parsed_model->getByParsedAttributes($m, 0, $obj->imported_data_id,$customersList);
							}
echo '<br> - similar get 2 -- '.(microtime(true) - $getSimilar2);							
							//If similar items were found, add imported_data_id and customer to similar product competitors
							if (!empty($similar_items))
							{
$checkSimilar2 = microtime(true);								
								foreach ($similar_items as $ks => $vs)
								{
									$customer = "";
									foreach ($sites_list as $ki => $vi)
									{
										if (strpos($vs['url'], "$vi") !== false)
										{
											$customer = strtolower($this->sites_model->get_name_by_url($vi));
											break;
										}
									}
									$similar_products_competitors[] = array(
									    'imported_data_id' => $vs['imported_data_id'],
									    'customer' => $customer
									);
								}
echo '<br> - similar check 2 -- '.(microtime(true) - $checkSimilar2);								
							}
						}
						$time = microtime(true) - $modelStart;
						echo "<br>model exists_and some actions - " . $time . 'seconds';
					} else
					{
						//if parsed attributes were not found, create custom model
						$time_start = microtime(true);
						if(isset($obj->imported_data_id))
						{
							echo "<br>im+daat+id= " . $obj->imported_data_id;
							//checking for custom model
							if ($model = $this->imported_data_parsed_model->check_if_exists_custom_model($obj->imported_data_id))
							{
								echo "<br>exists custom model ------------- ";
								$same_pr = $this->imported_data_parsed_model->getByParsedAttributes($model, 0, $obj->imported_data_id,$customersList);
							} else //geterate custom model if it does not exists
							{
								echo "<br>geting custom model - ";
								$same_pr = array();
								echo "product name  = " . $obj->product_name;
								$same_pr = $this->imported_data_parsed_model->getByProductNameNew($obj->imported_data_id, $obj->product_name, '', 0, $sites_list);
								echo "<br>custom model is ready ------------ ";
							}
						}
						$time = microtime(true) - $time_start;
						echo $time . " seconds (important)";
						//looking for similar competitors
						foreach ($same_pr as $key => $val)
						{
							$customer = "";
							foreach ($sites_list as $ki => $vi)
							{
								if (strpos($val['url'], "$vi") !== false)
								{
									$customer = strtolower($this->sites_model->get_name_by_url($vi));
									break;
								}
							}
							$similar_products_competitors[] = array('imported_data_id' => $val['imported_data_id'], 'customer' => $customer);
						}
					}

					$time = microtime(true) - $time_start;
					//WC Short
					$time_start = microtime(true);
					//Get research_data_id, batch_id and category_id
					$research_and_batch_ids = $this->statistics_new_model->getResearchDataAndBatchIds($obj->imported_data_id);
					if (!$research_and_batch_ids)
					{
						//If research_data_id, batch_id and category_id were not found, define them by default
						$research_and_batch_ids = array(array(
							'research_data_id' => 0,
							'batch_id' => 0,
						        'category_id' => 0
						));
					}
					$time = microtime(true) - $time_start;
					echo "<br>research_data ---------------------- " . $time . " seconds";
					//$insertStart = microtime(true);
					//insert new statistics data to statistics_new table if it not exists in table and update if exists
					try
					{
						$insert_id = $this->statistics_new_model->insert_updated($obj->imported_data_id, $obj->revision, $short_description_wc, $long_description_wc, $title_keywords, $own_price, serialize($price_diff), serialize($competitors_prices), $items_priced_higher_than_competitors, serialize($similar_products_competitors), $research_and_batch_ids, $manufacturerInfo);
					} catch (Exception $e)
					{
						echo 'Error', $e->getMessage(), "\n";
						//$this->load->model('statistics_model');
						//$this->statistics_model->db->close();
						//$this->statistics_model->db->initialize();

						$insert_id = $this->statistics_new_model->insert_updated($obj->imported_data_id, $obj->revision, $short_description_wc, $long_description_wc, $title_keywords, $own_price, serialize($price_diff), serialize($competitors_prices), $items_priced_higher_than_competitors, serialize($similar_products_competitors), $research_and_batch_ids, $manufacturerInfo);
					}
					$endTime = microtime(true);
					//echo "<br>insert/update ----------------------- " . ($endTime - $insertStart) . " seconds<br>";
					echo "<br>global foreach --------------------- " . ($endTime - $foreach_start) . " seconds<br>";
				} //end foreach
				
				$cjo = $this->settings_model->getDescription();
				$cjo++;
				$this->settings_model->updateDescription($cjo);
			}
		} catch (Exception $e)
		{
			echo 'Error', $e->getMessage(), "\n";
			unlink($tmp_dir . ".locked");
		}
		$time = time() - $first_start;
		echo "<br>all -- " . $time . "<br>";
		unlink($tmp_dir . ".locked");
		$data_arr = $this->imported_data_parsed_model->do_stats_newupdated(); //get next 50 items to scan
		$start = $this->settings_model->getDescription();
		$stats_status = $this->settings_model->getDoStatsStatus(); //get status of do_stats
		$total_items = $this->settings_model->getLastUpdate(); //get count of all items in time of starting
		//If queque has items and status is started and count of all items bigger than count of scanned items , start script again
		if (count($data_arr) > 0 && $stats_status->description === 'started' && ($cjo - 1) * 50 < intval($total_items['description']))
		{ 
			$utd = $this->imported_data_parsed_model->getLUTimeDiff();
			echo $utd->td;  //exit;
			//make asynchronous web request to do_stats_forupdated page
                        $url_link ="wget -S -O - ".site_url('/crons/do_stats_forupdated/'.$trnc)." > /dev/null 2>/dev/null &"; 
			shell_exec($url_link);
		} else
		{
			//Or send report about success
			$this->settings_model->setLastUpdate(); //set last update time
			$mtd = $this->imported_data_parsed_model->getTimeDif(); // timing of process
			echo $mtd->td;
			//Remove status about started state
			if ($stats_status->description === 'started') //if status is started
			{
				$this->imported_data_parsed_model->delDoStatsStatus(); //remove status info
			}
			$this->settings_model->updateDescription(0);  //reset cron_job_offset 0

			
			$this->load->library('email');
			$this->email->from('info@dev.contentsolutionsinc.com', '!!!!');
			$this->email->to('bayclimber@gmail.com');
			$this->email->subject('Cron job report');
			$this->email->message('Cron job for do_statistics_new is done.<br> Timing = ' . $mtd->td); //.'<br> Total items updated: '.$qty['description']
			$this->email->send(); 
		}
		unlink($tmp_dir . ".locked");
	}

	function different_revissions()
	{
		$sql_cmd = "select imported_data_id, max(revision) as max_revision
                    from (
                    select imported_data_id, revision from imported_data_parsed
                    group by imported_data_id, revision) as res
                    group by imported_data_id
                    having count(revision)>1";
		$results = $this->db->query($sql_cmd)->result_array;
		foreach ($results as $res)
		{
			$this->db->update('imported_data_parsed', array('revision' => $res['max_revision']), array('imported_data_id' => $res['imported_data_id']));
		}
	}

	function title_keywords($product_name, $short_description, $long_description)
	{
		$short_sp = $this->get_keywords($product_name, $short_description);
		$long_sp = $this->get_keywords($product_name, $long_description);
		$title_seo_prases = array();
		if ($short_sp)
		{

			foreach ($short_sp as $pr)
			{
				//if($pr['prc']>2) {
					$title_seo_prases[] = $pr;
				//}
			}
		}
		if ($long_sp)
		{

			foreach ($long_sp as $pr)
			{
				//if($pr['prc']>2) {
					$title_seo_prases[] = $pr;
				//}
			}
		}
		$sub_title_prases_keys = array();
		if (!empty($title_seo_prases))
		{
			foreach ($title_seo_prases as $ar_key => $seo_pr)
			{
				foreach ($title_seo_prases as $ar_key1 => $seo_pr1)
				{

//                    if($ar_key!=$ar_key1 && substr_count($seo_pr1['ph'],$seo_pr['ph'])){
//                        //$sub_title_prases_keys[]=$ar_key;
//                    }
					if ($ar_key != $ar_key1 && $seo_pr['ph'] == $seo_pr1['ph'] && $seo_pr['frq'] >= $seo_pr1['frq'])
					{
						unset($title_seo_prases[$ar_key1]);
					}
				}
			}
//            foreach( $sub_title_prases_keys  as $k){
//                if(key_exists($k, $title_seo_prases)){
//                    unset($title_seo_prases[$k]);
//                }
//            }
			return serialize($title_seo_prases);
		}
		return 'None';
	}

	private function get_keywords($title, $string)
	{
		if (trim($title) == '' || $title == NULL || $string == '')
		{
			return array();
		}
		$black_list = array('and', 'the', 'in', 'on', 'at', 'for');
		$title = trim(preg_replace('/\(.*\)/', '', $title));
		$title = trim(str_replace(',', ' ', $title));
		$title = trim(preg_replace('/\s+/', ' ', $title));
		$string = trim(preg_replace('/\(.*\)/', '', $string));
		$string = trim(str_replace(',', ' ', $string));
		$string = trim(preg_replace('/\s+/', ' ', $string));
		$string = $this->str_cleaner($black_list, $string);
		$title_w = explode(' ', $title);
		$title_wc = count($title_w);
		$string_w = explode(' ', $string);
		$string_wc = count($string_w);
		$phrases = array();
		$i = 0;
		while ($title_wc - $i > 1)
		{
			for ($j = 0; $j < $i + 1; ++$j)
			{
				$needl = '';
				for ($k = $j; $k < $title_wc - $i + $j; ++$k)
				{
					$needl .= $title_w[$k] . ' ';
				}
				$needl = trim($needl);
				$frc = substr_count(strtolower($string), strtolower($this->str_cleaner($black_list, $needl)));
				$prc = ($frc * ($title_wc - $i)) / $string_wc * 100;
				if ($frc > 0 && $prc > 2)
				{ //
					$phrases[] = array(
					    'frq' => $frc,
					    'prc' => round($prc, 2),
					    'ph' => $needl
					);
				}
			}
//            if(!empty($phrases)){
//                break;
//            }
			++$i;
		}
		//*
		foreach ($black_list as $w)
		{
			foreach ($phrases as $key => $val)
			{
				$val['ph'] = substr($val['ph'], 0, strlen($w)) === $w ? substr($val['ph'], strlen($w)) : $val['ph'];
				$val['ph'] = substr($val['ph'], (-1) * strlen($w)) === $w ? substr($val['ph'], 0, strlen($val['ph']) - strlen($w)) : $val['ph'];
				$val['ph'] = trim($val['ph']);
				$pw = explode(' ', $val['ph']);
				if (count($pw) < 2)
				{
					unset($phrases[$key]);
				}
			}
		}
		foreach ($phrases as $ar_key => $seo_pr)
		{
			foreach ($phrases as $ar_key1 => $seo_pr1)
			{
				if ($ar_key != $ar_key1 && $this->compare_str($seo_pr['ph'], $seo_pr1['ph']) && $seo_pr['frq'] >= $seo_pr1['frq']
				)
				{
					unset($phrases[$ar_key1]);
				}
			}
		}
		foreach ($phrases as $ar_key => $seo_pr)
		{
			foreach ($phrases as $ar_key1 => $seo_pr1)
			{
				if ($ar_key != $ar_key1 && $this->compare_str($seo_pr['ph'], $seo_pr1['ph']))
				{
					if ($seo_pr['frq'] >= $seo_pr1['frq'])
					{
						unset($phrases[$ar_key1]);
					} else
					{
						$phrases[$ar_key1]['frq'] -= $seo_pr['frq'];
						$akw = explode(' ', $seo_pr1['ph']);
						$phrases[$ar_key1]['prc'] = round($phrases[$ar_key1]['frq'] * count($akw) / $string_wc * 100, 2);
					}
				}
			}
		}
//*/
		return $phrases;
	}

	private function str_cleaner($bl, $string)
	{
		$str_arr = explode(' ', $string);
		foreach ($str_arr as $key => $val)
		{
			if (in_array($val, $bl))
			{
				unset($str_arr[$key]);
			}
		}
		$string = trim(preg_replace('/\s+/', ' ', implode(' ', $str_arr)));
		return $string;
	}

	private function compare_str($str1, $str2)
	{
		$str1 = trim(strtolower($str1));
		$str2 = trim(strtolower($str2));
		$black_list = array('and', 'the', 'on', 'in', 'at', 'is', 'for');
		foreach ($black_list as $word)
		{
			$str1 = (substr($str1, 0, strlen($word)) === $word) ? substr($str1, strlen($word)) : $str1;
			$str1 = (substr($str1, (-1) * strlen($word)) === $word) ? substr($str1, 0, strlen($str1) - strlen($word)) : $str1;
			$str1 = trim($str1);
			$str2 = (substr($str2, 0, strlen($word)) === $word) ? substr($str2, strlen($word)) : $str2;
			$str2 = (substr($str2, (-1) * strlen($word)) === $word) ? substr($str2, 0, strlen($str2) - strlen($word)) : $str2;
			$str2 = trim($str2);
		}
		return strpos($str1, $str2) !== FALSE;
	}

	public function do_stats_new()
	{
		echo "Script start working";
		$tmp_dir = sys_get_temp_dir() . '/';
		unlink($tmp_dir . ".locked");
		if (file_exists($tmp_dir . ".locked"))
		{
			exit;
		}

		touch($tmp_dir . ".locked");
		try
		{
			$this->load->model('imported_data_parsed_model');
			$this->load->model('research_data_model');
			$this->load->model('statistics_model');
			$this->load->model('statistics_new_model');
			$this->load->model('statistics_duplicate_content_model');
			$this->load->model('similar_imported_data_model');
			$this->load->model('similar_product_groups_model');
			$this->load->model('similar_data_model');
			$this->load->library('helpers');
			$this->load->helper('algoritm');
			$this->load->model('sites_model');
			//$this->statistics_new_model->truncate();

			$trnc = $this->uri->segment(3);
			var_dump($trnc);
			if ($trnc === false)
			{
				$trnc = 1;
			}

			$data_arr = $this->imported_data_parsed_model->do_stats($trnc);

			if (count($data_arr) > 1)
			{

				$sites_list = array();
				$query_cus = $this->similar_imported_data_model->db->order_by('name', 'asc')->get('sites');
				$query_cus_res = $query_cus->result();
				if (count($query_cus_res) > 0)
				{
					foreach ($query_cus_res as $key => $value)
					{
						$n = parse_url($value->url);
						$sites_list[] = $n['host'];
					}
				}

				foreach ($data_arr as $obj)
				{
					echo $obj->imported_data_id . "<br>";
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
					if ($data_import['description'] !== null && trim($data_import['description']) !== "")
					{

						$data_import['description'] = preg_replace('/[^a-zA-Z0-9_ %\[\]\.\(\)%&-]/s', '', $data_import['description']);
						$data_import['description'] = preg_replace('/\s+/', ' ', $data_import['description']);
						//$data_import['description'] = preg_replace('/[a-zA-Z]-/', ' ', $data_import['description']);
						$short_description_wc = count(explode(" ", strip_tags($data_import['description'])));
					} else
					{
						$short_description_wc = 0;
					}
					if ($data_import['long_description'] !== null && trim($data_import['long_description']) !== "")
					{

						$data_import['long_description'] = preg_replace('/[^a-zA-Z0-9_ %\[\]\.\(\)%&-]/s', '', $data_import['long_description']);
						$data_import['long_description'] = preg_replace('/\s+/', ' ', $data_import['long_description']);
						//$data_import['long_description'] = preg_replace('/[a-zA-Z]-/', ' ', $data_import['long_description']);
						$long_description_wc = count(explode(" ", strip_tags($data_import['long_description'])));
					} else
					{
						$long_description_wc = 0;
					}


					// SEO Short phrases
					$time_start = microtime(true);
					if ($short_description_wc != 0)
					{

						$short_seo_phrases = $this->helpers->measure_analyzer_start_v2_product_name($data_import['product_name'], preg_replace('/\s+/', ' ', $data_import['description']));
						if (count($short_seo_phrases) > 0)
						{

							foreach ($short_seo_phrases as $key => $val)
							{
								$words = count(explode(' ', $val['ph']));
								$desc_words_count = count(explode(' ', $data_import['description']));
								$count = $val['count'];
								$val['prc'] = number_format($count * $words / $desc_words_count * 100, 2);
								$short_seo_phrases[$key] = $val;
							}

							$short_seo_phrases = serialize($short_seo_phrases);
						} else
						{
							$short_seo_phrases = "None";
						}
					} else
					{
						$short_seo_phrases = 'None';
					}

					$time_end = microtime(true);
					$time = $time_end - $time_start;
					echo "SEO Short phrases - $time seconds\n";
					// SEO Long phrases
					$time_start = microtime(true);
					if ($long_description_wc != 0)
					{

						$long_seo_phrases = $this->helpers->measure_analyzer_start_v2_product_name($data_import['product_name'], preg_replace('/\s+/', ' ', $data_import['long_description']));
						if (count($long_seo_phrases) > 0)
						{
							foreach ($long_seo_phrases as $key => $val)
							{
								$words = count(explode(' ', $val['ph']));
								$desc_words_count = count(explode(' ', $data_import['long_description']));
								$count = $val['count'];
								$val['prc'] = number_format($count * $words / $desc_words_count * 100, 2);
								$long_seo_phrases[$key] = $val;
							}
							$long_seo_phrases = serialize($long_seo_phrases);
						} else
						{
							$long_seo_phrases = "None";
						}
					} else
					{
						$long_seo_phrases = 'None';
					}
					$time_end = microtime(true);
					$time = $time_end - $time_start;
					echo "SEO Long phrases - $time seconds\n";


					$time_start = microtime(true);
					if (isset($data_import['parsed_attributes']) && isset($data_import['parsed_attributes']['model']))
					{
						//$this->imported_data_parsed_model->model_info($data_import['imported_data_id'],$data_import['parsed_attributes']['model'],$data_import['revision']);
						try
						{
							$own_prices = $this->imported_data_parsed_model->getLastPrices($obj->imported_data_id);
						} catch (Exception $e)
						{
							echo 'Error', $e->getMessage(), "\n";
							$own_prices = $this->imported_data_parsed_model->getLastPrices($obj->imported_data_id);
						}

						if (!empty($own_prices))
						{
							$own_price = floatval($own_prices[0]->price);
							$obj->own_price = $own_price;
							$price_diff_exists = array(); //"<input type='hidden'/>";
							$price_diff_exists['id'] = $own_prices[0]->id;
							$price_diff_exists['own_site'] = $own_site;
							$price_diff_exists['own_price'] = floatval($own_price);

							try
							{
								$similar_items = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['model'], 0, $data_import['imported_data_id']);
							} catch (Exception $e)
							{
								echo 'Error', $e->getMessage(), "\n";

								$similar_items = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['model'], 0, $data_import['imported_data_id']);
							}

							if (!empty($similar_items))
							{
								foreach ($similar_items as $ks => $vs)
								{
									$similar_item_imported_data_id = $similar_items[$ks]['imported_data_id'];
//                                    if ($obj->imported_data_id == $similar_item_imported_data_id) {
//                                        continue;
//                                    }
//                                          $n = parse_url($vs['url']);
//                                          $customer=  strtolower($n['host']);
//                                          $customer = str_replace("www1.", "",$customer);
//                                          $customer =str_replace("www.", "", $customer);
									$customer = "";
									foreach ($sites_list as $ki => $vi)
									{
										if (strpos($vs['url'], "$vi") !== false)
										{
											$customer = $vi;
										}
									}


									$customer = strtolower($this->sites_model->get_name_by_url($customer));
									$similar_products_competitors[] = array(
									    'imported_data_id' => $similar_item_imported_data_id,
									    'customer' => $customer
									);

									try
									{
										$three_last_prices = $this->imported_data_parsed_model->getLastPrices($similar_item_imported_data_id);
									} catch (Exception $e)
									{
										echo 'Error', $e->getMessage(), "\n";
										$this->statistics_model->db->close();
										$this->statistics_model->db->initialize();
										$three_last_prices = $this->imported_data_parsed_model->getLastPrices($similar_item_imported_data_id);
									}

									if (!empty($three_last_prices))
									{
										$price_scatter = $own_price * 0.03;
										$price_upper_range = $own_price + $price_scatter;
										$price_lower_range = $own_price - $price_scatter;
										$competitor_price = floatval($three_last_prices[0]->price);
										if ($competitor_price < $own_price)
										{
											$items_priced_higher_than_competitors = 1;
										}
										if ($competitor_price > $price_upper_range || $competitor_price < $price_lower_range)
										{
											$price_diff_exists['competitor_customer'][] = $similar_items[$ks]['customer'];
											$price_diff_exists['competitor_price'][] = $competitor_price;
											$price_diff = $price_diff_exists;
											$competitors_prices[] = $competitor_price;
										}
									}
								}
							}
						} else
						{
							try
							{
								$similar_items = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['model'], 0, $data_import['imported_data_id']);
							} catch (Exception $e)
							{
								echo 'Error', $e->getMessage(), "\n";

								$similar_items = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['model'], 0, $data_import['imported_data_id']);
							}

							if (!empty($similar_items))
							{
								foreach ($similar_items as $ks => $vs)
								{
									$similar_item_imported_data_id = $similar_items[$ks]['imported_data_id'];
//                                    if ($obj->imported_data_id == $similar_item_imported_data_id) {
//                                        continue;
//                                    }
//                                          $n = parse_url($vs['url']);
//                                          $customer=  strtolower($n['host']);
//                                          $customer = str_replace("www1.", "",$customer);
//                                          $customer =str_replace("www.", "", $customer);
									$customer = "";
									foreach ($sites_list as $ki => $vi)
									{
										if (strpos($vs['url'], "$vi") !== false)
										{
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
						foreach ($sites_list as $ki => $vi)
						{
							if (strpos($data_import['url'], "$vi") !== false)
							{
								$customer = $vi;
							}
						}

						$customer = strtolower($this->sites_model->get_name_by_url($customer));

						$similar_products_competitors[] = array(
						    'imported_data_id' => $data_import['imported_data_id'],
						    'customer' => $customer
						);
					} else
					{
						$im_data_id = $data_import['imported_data_id'];
//                        if (!$this->similar_product_groups_model->checkIfgroupExists($data_import['imported_data_id'])) {
//
//                            if (!isset($data_import['parsed_attributes'])) {
//
//                                $same_pr = $this->imported_data_parsed_model->getByProductName($im_data_id, $data_import['product_name'], '', 0);
//                            }
//                            if (isset($data_import['parsed_attributes'])) {
//
//                                $same_pr = $this->imported_data_parsed_model->getByProductName($im_data_id, $data_import['product_name'], $data_import['parsed_attributes']['manufacturer'],0);
//                            }
						if ($model = $this->imported_data_parsed_model->check_if_exists_custom_model($im_data_id))
						{

							$same_pr = $this->imported_data_parsed_model->get_by_custom_model($model, $im_data_id);
						} else
						{

							$same_pr = $this->imported_data_parsed_model->getByProductNameNew($im_data_id, $data_import['product_name'], '', $strict);
						}

						foreach ($same_pr as $key => $val)
						{
							$customer = "";
							foreach ($sites_list as $ki => $vi)
							{
								if (strpos($val['url'], "$vi") !== false)
								{
									$customer = $vi;
								}
							}

							$customer = strtolower($this->sites_model->get_name_by_url($customer));
							$similar_products_competitors[] = array('imported_data_id' => $val['imported_data_id'], 'customer' => $customer);
						}


//                        } else {
//
//                            $rows = $this->similar_data_model->getByGroupId($im_data_id);
//                            $data_similar = array();
//
//                            foreach ($rows as $key => $row) {
//
//                                $data_similar = $this->imported_data_parsed_model->getByImId($row->imported_data_id);
////                                    $n = parse_url($data_similar['url']);
////                                    $customer=  strtolower($n['host']);
////                                    $customer = str_replace("www1.", "",$customer);
////                                    $customer =str_replace("www.", "", $customer);
//                                $customer = "";
//                                foreach ($sites_list as $ki => $vi) {
//                                    if (strpos($data_similar['url'], "$vi") !== false) {
//                                        $customer = $vi;
//                                    }
//                                }
//
//                                $customer = strtolower($this->sites_model->get_name_by_url($customer));
//                                $similar_products_competitors[] = array('imported_data_id' => $row->imported_data_id, 'customer' => $customer);
//                            }
					}
					$time_end = microtime(true);
					$time = $time_end - $time_start;
//                          echo "price_diff - $time seconds\n";
					// WC Short


					$time_start = microtime(true);

					$query_research_data_id = 0;
					$query_batch_id = 0;
					if ($query = $this->statistics_new_model->getResearchDataAndBatchIds($obj->imported_data_id))
					{
						$query_research_data_id = $query[0]->research_data_id;
						$query_batch_id = $query[0]->batch_id;
					}

					try
					{
						$insert_id = $this->statistics_new_model->insert($obj->imported_data_id, $obj->revision, $short_description_wc, $long_description_wc, $short_seo_phrases, $long_seo_phrases, $own_price, serialize($price_diff), serialize($competitors_prices), $items_priced_higher_than_competitors, serialize($similar_products_competitors), $query_research_data_id, $query_batch_id
						);
					} catch (Exception $e)
					{
						echo 'Error', $e->getMessage(), "\n";
						$this->statistics_model->db->close();
						$this->statistics_model->db->initialize();

						$insert_id = $this->statistics_new_model->insert($obj->imported_data_id, $obj->revision, $short_description_wc, $long_description_wc, $short_seo_phrases, $long_seo_phrases, $own_price, serialize($price_diff), serialize($competitors_prices), $items_priced_higher_than_competitors, serialize($similar_products_competitors), $query_research_data_id, $query_batch_id
						);
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
		} catch (Exception $e)
		{
			echo 'Error', $e->getMessage(), "\n";
			unlink($tmp_dir . ".locked");
		}
		unlink($tmp_dir . ".locked");
		$data_arr = $this->imported_data_parsed_model->do_stats();
		$q = $this->db->select('key,description')->from('settings')->where('key', 'cron_job_offset');
		$res = $q->get()->row_array();
		$start = $res['description'];
		if (count($data_arr) > 1)
		{
			shell_exec("wget -S -O- ".site_url('/crons/do_stats_new/'.$trnc)." > /dev/null 2>/dev/null &");
		} else
		{
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

	public function do_stats_test()
	{
		exit('');
		echo "Script start working";
		$tmp_dir = sys_get_temp_dir() . '/';
		unlink($tmp_dir . ".locked");
		if (file_exists($tmp_dir . ".locked"))
		{
			exit;
		}

		touch($tmp_dir . ".locked");
		try
		{
			$this->load->model('batches_model');
			$this->load->model('research_data_model');
			$this->load->model('statistics_model');
			$this->load->model('statistics_duplicate_content_model');
			$this->load->model('imported_data_parsed_model');
			$this->statistics_model->truncate();
			$this->statistics_duplicate_content_model->truncate();
			$batches = $this->batches_model->getAll('id');
			$enable_exec = true;
			$params = parse_ini_file('./application/config/db.ini');
			$conn = mysql_connect($params['db.host'], $params['db.user'], $params['db.pass']);
			foreach ($batches as $batch)
			{
				$batch_id = $batch->id;
				$data = $this->research_data_model->do_stats($batch->id);
				error_log("Problem after do_stats query", 3, 'log.txt');
				if (count($data) > 0)
				{
					foreach ($data as $obj)
					{
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
						if (isset($data_import['parsed_attributes']) && isset($data_import['parsed_attributes']['model']))
						{
							$own_prices = $this->imported_data_parsed_model->getLastPrices($obj->imported_data_id);
							if (!empty($own_prices))
							{
								$own_price = floatval($own_prices[0]->price);
								$obj->own_price = $own_price;
								$price_diff_exists = array(); //"<input type='hidden'/>";
								$price_diff_exists['id'] = $own_prices[0]->id;
								$price_diff_exists['own_site'] = $own_site;
								$price_diff_exists['own_price'] = floatval($own_price);
								$similar_items = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['model']);
								if (!empty($similar_items))
								{
									foreach ($similar_items as $ks => $vs)
									{
										$similar_item_imported_data_id = $similar_items[$ks]['imported_data_id'];
										if ($obj->imported_data_id == $similar_item_imported_data_id)
										{
											continue;
										}
										$similar_products_competitors[] = array(
										    'imported_data_id' => $similar_item_imported_data_id,
										    'customer' => $similar_items[$ks]['customer']
										);
										$three_last_prices = $this->imported_data_parsed_model->getLastPrices($similar_item_imported_data_id);
										if (!empty($three_last_prices))
										{
											$price_scatter = $own_price * 0.03;
											$price_upper_range = $own_price + $price_scatter;
											$price_lower_range = $own_price - $price_scatter;
											$competitor_price = floatval($three_last_prices[0]->price);
											if ($competitor_price < $own_price)
											{
												$items_priced_higher_than_competitors = 1;
											}
											if ($competitor_price > $price_upper_range || $competitor_price < $price_lower_range)
											{
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
						if (is_null($obj->short_description_wc))
						{
							$this->imported_data_parsed_model->insert($obj->imported_data_id, "Description_WC", $short_description_wc);
						} else
						{
							if (intval($obj->short_description_wc) <> $short_description_wc)
							{
								$this->imported_data_parsed_model->updateValueByKey($obj->imported_data_id, "Description_WC", $short_description_wc);
							}
						}
						$time_end = microtime(true);
						$time = $time_end - $time_start;
						echo "WC Short - $time seconds\n";

						// WC Long
						$time_start = microtime(true);
						$long_description_wc = (count(preg_split('/\b/', $obj->long_description)) - 1) / 2;
						if (is_null($obj->long_description_wc))
						{
							$this->imported_data_parsed_model->insert($obj->imported_data_id, "Long_Description_WC", $long_description_wc);
						} else
						{
							if (intval($obj->long_description_wc) <> $long_description_wc)
							{
								$this->imported_data_parsed_model->updateValueByKey($obj->imported_data_id, "Long_Description_WC", $long_description_wc);
							}
						}
						$time_end = microtime(true);
						$time = $time_end - $time_start;
						echo "WC Long - $time seconds\n";

						// SEO Short phrases
						$time_start = microtime(true);
						if ($short_description_wc == $obj->short_description_wc && !is_null($obj->short_seo_phrases))
						{
							$short_seo_phrases = $obj->short_seo_phrases;
						} else
						{
							if ($enable_exec)
							{
								$cmd = $this->prepare_extract_phrases_cmd($obj->short_description);
								$output = array();
								exec($cmd, $output, $error);

								if ($error > 0)
								{
									$enable_exec = false;
								} else
								{
									$short_seo_phrases = $this->prepare_seo_phrases($output);
									if (is_null($obj->short_seo_phrases))
									{
										$this->imported_data_parsed_model->insert($obj->imported_data_id, "short_seo_phrases", $short_seo_phrases);
									} else
									{
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
						if ($long_description_wc == $obj->long_description_wc && !is_null($obj->long_seo_phrases))
						{
							$long_seo_phrases = $obj->long_seo_phrases;
						} else
						{
							if ($enable_exec)
							{
								$cmd = $this->prepare_extract_phrases_cmd($obj->long_description);
								$output = array();
								exec($cmd, $output, $error);

								if ($error > 0)
								{
									$enable_exec = false;
								} else
								{
									$long_seo_phrases = $this->prepare_seo_phrases($output);
									if (is_null($obj->long_seo_phrases))
									{
										$this->imported_data_parsed_model->insert($obj->imported_data_id, "long_seo_phrases", $long_seo_phrases);
									} else
									{
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
		} catch (Exception $e)
		{
			echo 'Error', $e->getMessage(), "\n";
			unlink($tmp_dir . ".locked");
		}
		unlink($tmp_dir . ".locked");
	}

	public function do_stats($clear = false)
	{
		exit();
		echo "Script start working";
		$tmp_dir = sys_get_temp_dir() . '/';
		unlink($tmp_dir . ".locked");
		if (file_exists($tmp_dir . ".locked"))
		{
			exit;
		}

		touch($tmp_dir . ".locked");
		try
		{
			$subject = 'Cron Job Report - do_stats started';
			$message = 'Cron job for do_stats started';
			$this->send_email_report($subject, $message);

			$this->load->model('batches_model');
			$this->load->model('research_data_model');
			$this->load->model('statistics_model');
			$this->load->model('statistics_duplicate_content_model');
			$this->load->model('imported_data_parsed_model');
			if ($clear)
			{
				$this->statistics_model->truncate();
//            	$this->statistics_duplicate_content_model->truncate();
			}
			$batches = $this->batches_model->getAll('id');
			$enable_exec = true;
			foreach ($batches as $batch)
			{
				$batch_id = $batch->id;
				try
				{
					$data = $this->research_data_model->do_stats($batch->id);
				} catch (Exception $e)
				{
					echo 'Error', $e->getMessage(), "\n";
					$this->statistics_model->db->close();
					$this->statistics_model->db->initialize();
					$data = $this->research_data_model->do_stats($batch->id);
				}
				if (count($data) > 0)
				{
					foreach ($data as $obj)
					{
						// TODO: rewrite
						if ($this->statistics_model->getbyImportedDataId($obj->imported_data_id))
						{
							continue;
						}
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

						try
						{
							$data_import = $this->imported_data_parsed_model->getByImId($obj->imported_data_id);
						} catch (Exception $e)
						{
							echo 'Error', $e->getMessage(), "\n";
							$this->statistics_model->db->close();
							$this->statistics_model->db->initialize();
							$data_import = $this->imported_data_parsed_model->getByImId($obj->imported_data_id);
						}

						$time_end = microtime(true);
						$time = $time_end - $time_start;
//                          echo "data_import - $time seconds\n";

						$time_start = microtime(true);
						if (isset($data_import['parsed_attributes']) && isset($data_import['parsed_attributes']['model']))
						{

							try
							{
								$own_prices = $this->imported_data_parsed_model->getLastPrices($obj->imported_data_id);
							} catch (Exception $e)
							{
								echo 'Error', $e->getMessage(), "\n";
								$this->statistics_model->db->close();
								$this->statistics_model->db->initialize();
								$own_prices = $this->imported_data_parsed_model->getLastPrices($obj->imported_data_id);
							}

							if (!empty($own_prices))
							{
								$own_price = floatval($own_prices[0]->price);
								$obj->own_price = $own_price;
								$price_diff_exists = array(); //"<input type='hidden'/>";
								$price_diff_exists['id'] = $own_prices[0]->id;
								$price_diff_exists['own_site'] = $own_site;
								$price_diff_exists['own_price'] = floatval($own_price);

								try
								{
									$similar_items = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['model']);
								} catch (Exception $e)
								{
									echo 'Error', $e->getMessage(), "\n";
									$this->statistics_model->db->close();
									$this->statistics_model->db->initialize();
									$similar_items = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['model']);
								}

								if (!empty($similar_items))
								{
									foreach ($similar_items as $ks => $vs)
									{
										$similar_item_imported_data_id = $similar_items[$ks]['imported_data_id'];
										if ($obj->imported_data_id == $similar_item_imported_data_id)
										{
											continue;
										}
										$similar_products_competitors[] = array(
										    'imported_data_id' => $similar_item_imported_data_id,
										    'customer' => $similar_items[$ks]['customer']
										);

										try
										{
											$three_last_prices = $this->imported_data_parsed_model->getLastPrices($similar_item_imported_data_id);
										} catch (Exception $e)
										{
											echo 'Error', $e->getMessage(), "\n";
											$this->statistics_model->db->close();
											$this->statistics_model->db->initialize();
											$three_last_prices = $this->imported_data_parsed_model->getLastPrices($similar_item_imported_data_id);
										}

										if (!empty($three_last_prices))
										{
											$price_scatter = $own_price * 0.03;
											$price_upper_range = $own_price + $price_scatter;
											$price_lower_range = $own_price - $price_scatter;
											$competitor_price = floatval($three_last_prices[0]->price);
											if ($competitor_price < $own_price)
											{
												$items_priced_higher_than_competitors = 1;
											}
											if ($competitor_price > $price_upper_range || $competitor_price < $price_lower_range)
											{
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
						if (is_null($obj->short_description_wc))
						{
							try
							{
								$this->imported_data_parsed_model->insert($obj->imported_data_id, "Description_WC", $short_description_wc);
							} catch (Exception $e)
							{
								echo 'Error', $e->getMessage(), "\n";
								$this->statistics_model->db->close();
								$this->statistics_model->db->initialize();
								$this->imported_data_parsed_model->insert($obj->imported_data_id, "Description_WC", $short_description_wc);
							}
						} else
						{
							if (intval($obj->short_description_wc) <> $short_description_wc)
							{
								try
								{
									$this->imported_data_parsed_model->updateValueByKey($obj->imported_data_id, "Description_WC", $short_description_wc);
								} catch (Exception $e)
								{
									echo 'Error', $e->getMessage(), "\n";
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
						if (is_null($obj->long_description_wc))
						{
							try
							{
								$this->imported_data_parsed_model->insert($obj->imported_data_id, "Long_Description_WC", $long_description_wc);
							} catch (Exception $e)
							{
								echo 'Error', $e->getMessage(), "\n";
								$this->statistics_model->db->close();
								$this->statistics_model->db->initialize();
								$this->imported_data_parsed_model->insert($obj->imported_data_id, "Long_Description_WC", $long_description_wc);
							}
						} else
						{
							if (intval($obj->long_description_wc) <> $long_description_wc)
							{
								try
								{
									$this->imported_data_parsed_model->updateValueByKey($obj->imported_data_id, "Long_Description_WC", $long_description_wc);
								} catch (Exception $e)
								{
									echo 'Error', $e->getMessage(), "\n";
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
						if ($short_description_wc == $obj->short_description_wc && !is_null($obj->short_seo_phrases))
						{
							$short_seo_phrases = $obj->short_seo_phrases;
						} else
						{
							if ($enable_exec)
							{
								$cmd = $this->prepare_extract_phrases_cmd($obj->short_description);
								$output = array();
								exec($cmd, $output, $error);

								if ($error > 0)
								{
									$enable_exec = false;
								} else
								{
									$short_seo_phrases = $this->prepare_seo_phrases($output);
									if (is_null($obj->short_seo_phrases))
									{
										try
										{
											$this->imported_data_parsed_model->insert($obj->imported_data_id, "short_seo_phrases", $short_seo_phrases);
										} catch (Exception $e)
										{
											echo 'Error', $e->getMessage(), "\n";
											$this->statistics_model->db->close();
											$this->statistics_model->db->initialize();
											$this->imported_data_parsed_model->insert($obj->imported_data_id, "short_seo_phrases", $short_seo_phrases);
										}
									} else
									{
										try
										{
											$this->imported_data_parsed_model->updateValueByKey($obj->imported_data_id, "short_seo_phrases", $short_seo_phrases);
										} catch (Exception $e)
										{
											echo 'Error', $e->getMessage(), "\n";
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
						if ($long_description_wc == $obj->long_description_wc && !is_null($obj->long_seo_phrases))
						{
							$long_seo_phrases = $obj->long_seo_phrases;
						} else
						{
							if ($enable_exec)
							{
								$cmd = $this->prepare_extract_phrases_cmd($obj->long_description);
								$output = array();
								exec($cmd, $output, $error);

								if ($error > 0)
								{
									$enable_exec = false;
								} else
								{
									$long_seo_phrases = $this->prepare_seo_phrases($output);
									if (is_null($obj->long_seo_phrases))
									{
										try
										{
											$this->imported_data_parsed_model->insert($obj->imported_data_id, "long_seo_phrases", $long_seo_phrases);
										} catch (Exception $e)
										{
											echo 'Error', $e->getMessage(), "\n";
											$this->statistics_model->db->close();
											$this->statistics_model->db->initialize();
											$this->imported_data_parsed_model->insert($obj->imported_data_id, "long_seo_phrases", $long_seo_phrases);
										}
									} else
									{
										try
										{
											$this->imported_data_parsed_model->updateValueByKey($obj->imported_data_id, "long_seo_phrases", $long_seo_phrases);
										} catch (Exception $e)
										{
											echo 'Error', $e->getMessage(), "\n";
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

						try
						{
							$insert_id = $this->statistics_model->insert($obj->rid, $obj->imported_data_id, $obj->research_data_id, $batch->id, $obj->product_name, $obj->url, $obj->short_description, $obj->long_description, $short_description_wc, $long_description_wc, $short_seo_phrases, $long_seo_phrases, $own_price, serialize($price_diff), serialize($competitors_prices), $items_priced_higher_than_competitors, serialize($similar_products_competitors)
							);
						} catch (Exception $e)
						{
							echo 'Error', $e->getMessage(), "\n";
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
			$subject = 'Cron Job Report - do_stats finished';
			$message = 'Cron job for do_stats finished';
			$this->send_email_report($subject, $message);
			echo "Script finish working";
			echo "Cron Job Finished";
		} catch (Exception $e)
		{
			echo 'Error', $e->getMessage(), "\n";
			unlink($tmp_dir . ".locked");
		}
		unlink($tmp_dir . ".locked");
	}

	function send_email_report($subject, $message)
	{
		$this->load->library('email');
		$this->email->from('info@dev.contentsolutionsinc.com', '!!!!');
		$this->email->to('bayclimber@gmail.com');
		$this->email->cc('max.kavelin@gmail.com');
		$this->email->subject($subject);
		$this->email->message($message);
		$this->email->send();
	}

	private function prepare_extract_phrases_cmd($text)
	{
		$text = str_replace("'", "\'", $text);
		$text = str_replace("`", "\`", $text);
		$text = str_replace('"', '\"', $text);
		$text = "\"" . $text . "\"";
		$cmd = str_replace($this->config->item('cmd_mask'), $text, $this->config->item('extract_phrases'));
		$cmd = $cmd . " 2>&1";
		return $cmd;
	}

	//*

	private function prepare_seo_phrases($seo_lines)
	{
		if (empty($seo_lines))
		{
			return "None";
		}
		$seo_phrases = array();
		$result_phrases = array();
		foreach ($seo_lines as $line)
		{
			$line_array = explode(",", $line);
			$number_repetitions = intval(str_replace("\"", "", $line_array[1]));
			if ($number_repetitions < 2)
			{
				continue;
			}
			$phrase = str_replace("\"", "", $line_array[0]);
			$seo_phrases[] = array($number_repetitions, $phrase);
		}
		if (empty($seo_phrases))
		{
			return "None";
		}
		$lines_count = 0;
		foreach ($seo_phrases as $seo_phrase)
		{
			if ($lines_count > 2)
			{
				break;
			}
			$result_phrases[] = $seo_phrase[1] . " (" . $seo_phrase[0] . ")";
			$lines_count++;
		}
		return implode(" ", $result_phrases);
	}

	public function duplicate_content()
	{
		error_reporting(E_ALL);
		ini_set('display_errors', '1');
		set_time_limit(0);
		$tmp_dir = sys_get_temp_dir() . '/';
		unlink($tmp_dir . ".locked");
		if (file_exists($tmp_dir . ".locked"))
		{
			exit;
		}

		touch($tmp_dir . ".locked");
		try
		{
			$this->load->model('batches_model');
			$this->load->model('statistics_model');
			$this->load->model('statistics_duplicate_content_model');
			$this->statistics_duplicate_content_model->truncate();
			$batches = $this->batches_model->getAll('id');
			foreach ($batches as $batch)
			{
				$params = new stdClass();
				$params->batch_id = $batch->id;
				$params->txt_filter = '';
				$stat_data = $this->statistics_model->getStatsData($params);
				if (count($stat_data) > 0)
				{
					foreach ($stat_data as $stat)
					{
						$time_start = microtime(true);
						sleep(2);
						$res_data = $this->check_duplicate_content($stat->imported_data_id);
						sleep(2);
						$time_end = microtime(true);
						$time = $time_end - $time_start;
						echo "block with check_duplicate_content - $time seconds\n";
						$time_start = $time_end;
						foreach ($res_data as $val)
						{
							$this->statistics_duplicate_content_model->insert($val['imported_data_id'], $val['product_name'], $val['description'], $val['long_description'], $val['url'], $val['features'], $val['customer'], $val['long_original'], $val['short_original']);
						}
						$time_end = microtime(true);
						$time = $time_end - $time_start;
						echo "foreach insert - $time seconds\n";
					}
					;
				}
			}
			echo "Cron Job Finished";
		} catch (Exception $e)
		{
			echo 'Error', $e->getMessage(), "\n";
			unlink($tmp_dir . ".locked");
		}
		unlink($tmp_dir . ".locked");
	}

	public function archive_imported_data_parsed()
	{
		$this->load->model('imported_data_parsed_model');
		$this->load->model('imported_data_parsed_archived_model');

		$processed = 0;
		foreach ($this->imported_data_parsed_model->getAllIds() as $row)
		{
			if ($this->imported_data_parsed_archived_model->saveToArchive($row['imported_data_id'], $row['max_revision']))
			{
				$this->imported_data_parsed_model->deleteRows($row['imported_data_id'], $row['max_revision']);
				$processed++;
			}
		}
		echo "Reviewed/archived " . $processed . " items.\n";
	}

	public function save_departments_categories()
	{
		$this->load->helper('file');
		$this->load->model('department_model');
		$this->load->model('department_members_model');
		$this->load->model('site_categories_model');
		session_start();
		// $filespath = realpath(base_url()) . "jl_import_dir";
		$filespath = $this->config->item('csv_upload_dir') . 'partial';

		if (!file_exists($filespath))
		{
			mkdir($filespath);
		}
		if ($this->uri->segment(3) && $this->uri->segment(4) && $this->uri->segment(5))
		{ //
			$_POST['site_id'] = $this->uri->segment(3);
			$_POST['site_name'] = $this->uri->segment(4) . '.' . $this->uri->segment(5);
		} else
		{
			$file = $this->config->item('csv_upload_dir') . $this->input->post('choosen_file');
			$fcont = file($file);
			$i = 1;
			$fnum = 0;
			$fobj = '';
			foreach ($fcont as $line)
			{
				if (!file_exists($filespath . '/temp_imp_jl_' . $fnum . '.jl'))
				{
					file_put_contents($filespath . '/temp_imp_jl_' . $fnum . '.jl', $line);
					$fobj = fopen($filespath . '/temp_imp_jl_' . $fnum . '.jl', 'a');
				}
				else
					fwrite($fobj, $line);
				if ($i == 500)
				{
					++$fnum;
					$i = 0;
					fclose($fobj);
				}
				++$i;
			}
		}
		$site_id = $this->input->post('site_id');
		$site_name = explode(".", strtolower($this->input->post('site_name')));
		//$file = $this->config->item('csv_upload_dir').$this->input->post('choosen_file');
		$flist = get_filenames($filespath);
		if (empty($flist))
		{
			//unset($_SESSION['mpost']);
			return;
		}
		//exit;
		$file = $filespath . '/' . $flist[0];
		$_rows = array();
//        $handle = fopen($file, "rb");
//        $contents = fread($handle, filesize($file));
//        fclose($handle);

		$cfile = file($file);
		//$data = '['.trim($contents,'"').']';
		//$json_obj = json_decode($data);

		$debug_stack = array(
		    'department_members' => array(),
		    'site_categories' => array()
		);

		// new change 1 line
		set_time_limit(1000);
		foreach ($cfile as $line)
		{
			$line = rtrim(trim($line), ',');
			$row = json_decode($line);
			// === DB table decision (start)
			$level = '';
			$work_table = "";
			if (isset($row->level) && $row->level !== NULL && $row->level !== '')
			{
				$level = $row->level;
				if ($level >= 1)
				{
					$work_table = 'department_members';
				} else
				{
					$work_table = 'site_categories';
				}
			}
			// === DB table decision (end)
			// === all possible values and default values (start)
			$special = 0;
			$department_text = "";
			$url = "";
			$text = "";
			$department_url = "";
			$description_title = "";
			$keyword_count = "";
			$description_wc = 0;
			$description_text = "";
			$keyword_density = "";
			$nr_products = 0;
			$parent_url = "";
			$parent_text = "";

			if (isset($row->special) && $row->special != '' && !is_null($row->special))
			{
				$special = $row->special;
			}
			if (isset($row->department_text) && is_array($row->department_text))
			{
				$department_text = $row->department_text[0];
			} else if (isset($row->department_text) && !is_array($row->department_text) && !is_null($row->department_text) && $row->department_text != '')
			{
				$department_text = $row->department_text;
			}
			if (isset($row->url) && is_array($row->url))
			{
				$url = addslashes($row->url[0]);
			} else if (isset($row->url) && !is_array($row->url) && !is_null($row->url))
			{
				$url = addslashes($row->url);
			}
			if (isset($row->text) && is_array($row->text))
			{
				$text = $row->text[0];
			} else if (isset($row->text) && !is_array($row->text) && !is_null($row->text))
			{
				$text = $row->text;
			}
			if (isset($row->department_url) && !is_null($row->department_url) && $row->department_url != '')
			{
				$department_url = addslashes($row->department_url);
			}
			if (isset($row->description_title) && is_array($row->description_title))
			{
				$description_title = $row->description_title[0];
			} else if (isset($row->description_title) && !is_array($row->description_title) && !is_null($row->description_title) && $row->description_title != '')
			{
				$description_title = $row->description_title;
			}
			if (isset($row->keyword_count) && is_array($row->keyword_count))
			{
				$keyword_count = $row->keyword_count[0];
			} else if (isset($row->keyword_count) && !is_array($row->keyword_count) && !is_null($row->keyword_count) && $row->keyword_count != '')
			{
				$keyword_count = json_encode($row->keyword_count);
			}
			if (isset($row->description_wc) && is_array($row->description_wc))
			{
				$description_wc = $row->description_wc[0];
			} else if (isset($row->description_wc) && !is_array($row->description_wc) && !is_null($row->description_wc) && $row->description_wc != '')
			{
				$description_wc = $row->description_wc;
			}
			if (isset($row->description_text) && is_array($row->description_text))
			{
				$description_text = $row->description_text[0];
			} else if (isset($row->description_text) && !is_array($row->description_text) && !is_null($row->description_text) && $row->description_text != '')
			{
				$description_text = $row->description_text;
			}
			if (isset($row->keyword_density) && is_array($row->keyword_density))
			{
				$keyword_density = $row->keyword_density[0];
			} else if (isset($row->keyword_density) && !is_array($row->keyword_density) && !is_null($row->keyword_density) && $row->keyword_density != '')
			{
				$keyword_density = json_encode($row->keyword_density);
			}
			if (isset($row->nr_products) && is_array($row->nr_products))
			{
				$nr_products = $row->nr_products[0];
			} else if (isset($row->nr_products) && !is_array($row->nr_products) && !is_null($row->nr_products) && $row->nr_products != '')
			{
				$nr_products = $row->nr_products;
			}
			if (isset($row->parent_url) && is_array($row->parent_url))
			{
				$parent_url = addslashes($row->parent_url[0]);
			} else if (isset($row->parent_url) && !is_array($row->parent_url) && !is_null($row->parent_url) && $row->parent_url != '')
			{
				$parent_url = addslashes($row->parent_url);
			}
			if (isset($row->parent_text) && is_array($row->parent_text))
			{
				$parent_text = $row->parent_text[0];
			} else if (isset($row->parent_text) && !is_array($row->parent_text) && !is_null($row->parent_text) && $row->parent_text != '')
			{
				$parent_text = $row->parent_text;
			}
			// === all possible values and default values (end)

			if ($work_table != "")
			{ // === work table define, ok, otherwise !!! DO NOTHING !!!
				// ==== 'department_members' DB table actions stuffs (start)
				if ($work_table == 'department_members')
				{
					// === debuging stack (start)
					$debug_stack_mid = array(
					    'status' => 'department_members',
					    'department_text' => $department_text,
					    'url' => $url,
					    'text' => $text,
					    'department_url' => $department_url,
					    'description_title' => $description_title,
					    'keyword_count' => $keyword_count,
					    'description_wc' => $description_wc,
					    'description_text' => $description_text,
					    'keyword_density' => $keyword_density,
					    'department_id' => null,
					    'check_id' => null,
					    'department_members_model_insert_id' => null,
					    'department_members_model_up_flag' => null,
					    'department_members_model_update' => null
					);
					// === debuging stack (end)
					// === insert / update decisions stuffs (start)
					try
					{
						$check_department_id = $this->department_model->checkExist($department_text);
					} catch (Exception $e)
					{
						echo 'Error: ', $e->getMessage(), "\n";
						$this->statistics_model->db->close();
						$this->statistics_model->db->initialize();
						$check_department_id = $this->department_model->checkExist($department_text);
					}
					if ($check_department_id == false)
					{
						try
						{
							$department_id = $this->department_model->insert($department_text, $department_text);
						} catch (Exception $e)
						{
							$this->department_model->db->close();
							$this->department_model->db->initialize();
							$department_id = $this->department_model->insert($department_text, $department_text);
						}
					} else
					{
						$department_id = $check_department_id;
					}
					$debug_stack_mid['department_id'] = $department_id;
					$parent_id = 0;
					try
					{
						$check_id = $this->department_members_model->checkExist($site_id, $department_text, $url);
					} catch (Exception $e)
					{
						$this->department_members_model->db->close();
						$this->department_members_model->db->initialize();
						$check_id = $this->department_members_model->checkExist($site_id, $department_text, $url);
					}
					$debug_stack_mid['check_id'] = $check_id;
					if ($check_id == false)
					{
						try
						{
							$department_members_model_insert_id = $this->department_members_model->insert($parent_id, $site_id, $department_id, $department_text, $url, $description_wc, $description_text, $keyword_count, $keyword_density, $description_title, $level);
						} catch (Exception $e)
						{
							$this->department_members_model->db->close();
							$this->department_members_model->db->initialize();
							$department_members_model_insert_id = $this->department_members_model->insert($parent_id, $site_id, $department_id, $department_text, $url, $description_wc, $description_text, $keyword_count, $keyword_density, $description_title, $level);
						}
						$debug_stack_mid['department_members_model_insert_id'] = $department_members_model_insert_id;
					} else
					{
						try
						{
							$department_members_model_up_flag = $this->department_members_model->updateFlag($site_id, $department_text);
						} catch (Exception $e)
						{
							$this->department_members_model->db->close();
							$this->department_members_model->db->initialize();
							$department_members_model_up_flag = $this->department_members_model->updateFlag($site_id, $department_text);
						}
						$debug_stack_mid['department_members_model_up_flag'] = $department_members_model_up_flag;
						try
						{
							$department_members_model_update = $this->department_members_model->update($check_id, $department_id, $description_wc, $description_text, $keyword_count, $keyword_density, $description_title, $level);
						} catch (Exception $e)
						{
							$this->department_members_model->db->close();
							$this->department_members_model->db->initialize();
							$department_members_model_update = $this->department_members_model->update($check_id, $department_id, $description_wc, $description_text, $keyword_count, $keyword_density, $description_title, $level);
						}
						$debug_stack_mid['department_members_model_update'] = $department_members_model_update;
					}
					// === insert / update decisions stuffs (end)
					$debug_stack['department_members'][] = $debug_stack_mid;
				}
				// ==== 'department_members' DB table actions stuffs (end)
				// ==== 'site_categories' DB table actions stuffs (start)
				if ($work_table == 'site_categories')
				{
					$department_members_id = 0;
					if ($department_text != '')
					{
						try
						{
							$check_id = $this->department_members_model->checkExist($site_id, $department_text);
						} catch (Exception $e)
						{
							$this->department_members_model->db->close();
							$this->department_members_model->db->initialize();
							$check_id = $this->department_members_model->checkExist($site_id, $department_text);
						}
						if ($check_id)
						{
							$department_members_id = $check_id;
						} else
						{
							$department_id = 0;
							try
							{
								$check_department_id = $this->department_model->checkExist($department_text);
							} catch (Exception $e)
							{
								echo 'Error: ', $e->getMessage(), "\n";
								$this->statistics_model->db->close();
								$this->statistics_model->db->initialize();
								$check_department_id = $this->department_model->checkExist($department_text);
							}
							if ($check_department_id == false)
							{
								try
								{
									$department_id = $this->department_model->insert($department_text, $department_text);
								} catch (Exception $e)
								{
									$this->department_model->db->close();
									$this->department_model->db->initialize();
									$department_id = $this->department_model->insert($department_text, $department_text);
								}
							} else
							{
								$department_id = $check_department_id;
							}

							try
							{
								$department_members_id = $this->department_members_model->insert_for_sc($site_id, $department_id, $department_text, $department_url);
							} catch (Exception $e)
							{
								$this->department_members_model->db->close();
								$this->department_members_model->db->initialize();
								$department_members_id = $this->department_members_model->insert_for_sc($site_id, $department_id, $department_text, $department_url);
							}
						}
					}
					// === debuging stack (start)
					$debug_stack_mid = array(
					    'status' => 'site_categories',
					    'nr_products' => $nr_products,
					    'url' => $url,
					    'text' => $text,
					    'department_url' => $department_url,
					    'description_wc' => $description_wc,
					    'parent_url' => $parent_url,
					    'parent_text' => $parent_text,
					    'department_text' => $department_text,
					    'parent_id' => 0,
					    'site_categories_model_update_flag_one' => null,
					    'department_members_id' => $department_members_id,
					    'check_site' => null,
					    'site_categories_model_insert' => null,
					    'site_categories_model_update_flag_two' => null,
					    'description_text' => $description_text,
					    'keyword_count' => $keyword_count,
					    'keyword_density' => $keyword_density,
					    'description_title' => $description_title
					);
					// === debuging stack (end)
					// === insert / update decisions stuffs (start)
					$parent_id = 0;

					if($parent_text != '') {

						// If level = 0, then parent is in the department_members table and no need to add it to the site_categories table
						// Else, try to search parent in the site_categories table

						if($level < 0) {
							$parent_id = $this->site_categories_model->checkExist($site_id, $parent_text);

							// If parent exists, update its flag
							// Else, insert parent with known site_id, department_members_id and text = parent_text

							if($parent_id !== false) {
								$this->site_categories_model->updateFlag($site_id, $parent_text, $department_members_id);
							}
							else {
								$parent_id = $this->site_categories_model->insert(0, $site_id, $parent_text, '', 0, '', $department_members_id, 0, 0, '', '', '', '', '');
							}
						}

						// If it's known parent_id and not known department_members_id, try to get department_members_id from parent row
						if($parent_id != 0 && $department_members_id == 0) {
							$res = $this->site_categories_model->checkDepartmentId($parent_id);
							$department_members_id = $res->department_members_id;
						}
					}

					if($text != '') {
						// Try to search category in the site_categories table by site_id, department_members_id and text
						// If it exists, update its flag and other data except site_id, department_members_id and text
						// Else, insert new category

						$category_id = $this->site_categories_model->checkExist($site_id, $text, $department_members_id);

						if($category_id !== false) {
							$this->site_categories_model->updateFlag($site_id, $text, $department_members_id);
							$update_data = array(
								'parent_id' => $parent_id,
								'url' => $url,
								'special' => $special,
								'parent_text' => $parent_text,
								'level' => $level,
								'nr_products' => $nr_products,
								'description_words' => $description_wc,
								'title_keyword_description_count' => $keyword_count,
								'title_keyword_description_density' => $keyword_density,
								'description_title' => $description_title,
								'description_text' => $description_text
							);
							$this->site_categories_model->update($category_id, $update_data);
						}
						else {
							$category_id = $this->site_categories_model->insert($parent_id, $site_id, 
								$text, $url, $special, $parent_text, $department_members_id, $nr_products, $description_wc, 
								$keyword_count, $keyword_density, $description_title, $description_text, $level);
						}
					}

					// if ($parent_text != '') 
					// {
					// 	try
					// 	{
					// 		$parent_id = $this->site_categories_model->checkExist($site_id, $parent_text);
					// 	} catch (Exception $e)
					// 	{
					// 		$this->site_categories_model->db->close();
					// 		$this->site_categories_model->db->initialize();
					// 		$parent_id = $this->site_categories_model->checkExist($site_id, $parent_text);
					// 	}
					// 	if ($parent_id == false)
					// 	{
					// 		try
					// 		{
					// 			$parent_id = $this->site_categories_model->insert(0, $site_id, $text, $url, $special, $parent_text, $department_members_id, $nr_products, $description_wc, $keyword_count, $keyword_density, $description_title, $description_text, $level);
					// 		} catch (Exception $e)
					// 		{
					// 			$this->site_categories_model->db->close();
					// 			$this->site_categories_model->db->initialize();
					// 			$parent_id = $this->site_categories_model->insert(0, $site_id, $text, $url, $special, $parent_text, $department_members_id, $nr_products, $description_wc, $keyword_count, $keyword_density, $description_title, $description_text, $level);
					// 		}
					// 		$debug_stack_mid['parent_id'] = $parent_id;
					// 	} else
					// 	{
					// 		try
					// 		{
					// 			$site_categories_model_update_flag_one = $this->site_categories_model->updateFlag($site_id, $parent_text, $department_members_id);
					// 		} catch (Exception $e)
					// 		{
					// 			$this->site_categories_model->db->close();
					// 			$this->site_categories_model->db->initialize();
					// 			$site_categories_model_update_flag_one = $this->site_categories_model->updateFlag($site_id, $parent_text, $department_members_id);
					// 		}
					// 		$debug_stack_mid['site_categories_model_update_flag_one'] = $site_categories_model_update_flag_one;
					// 	}
					// }

					// if ($parent_id != 0 && $department_members_id == 0)
					// {
					// 	$res = $this->site_categories_model->checkDepartmentId($parent_id);
					// 	$department_members_id = $res->department_members_id;
					// 	$debug_stack_mid['department_members_id'] = $department_members_id;
					// }

					// if ($text != '')
					// {
					// 	try
					// 	{
					// 		$check_site = $this->site_categories_model->checkExist($site_id, $text, $department_members_id);
					// 	} catch (Exception $e)
					// 	{
					// 		$this->site_categories_model->db->close();
					// 		$this->site_categories_model->db->initialize();
					// 		$check_site = $this->site_categories_model->checkExist($site_id, $text, $department_members_id);
					// 	}
					// 	$debug_stack_mid['check_site'] = $check_site;
					// 	if ($check_site == false)
					// 	{
					// 		try
					// 		{
					// 			$site_categories_model_insert = $this->site_categories_model->insert($parent_id, $site_id, $text, $url, $special, $parent_text, $department_members_id, $nr_products, $description_wc, $keyword_count, $keyword_density, $description_title, $description_text, $level);
					// 		} catch (Exception $e)
					// 		{
					// 			$this->site_categories_model->db->close();
					// 			$this->site_categories_model->db->initialize();
					// 			$site_categories_model_insert = $this->site_categories_model->insert($parent_id, $site_id, $text, $url, $special, $parent_text, $department_members_id, $nr_products, $description_wc, $keyword_count, $keyword_density, $description_title, $description_text, $level);
					// 		}
					// 		$debug_stack_mid['site_categories_model_insert'] = $site_categories_model_insert;
					// 	} else
					// 	{
					// 		try
					// 		{
					// 			$site_categories_model_update_flag_two = $this->site_categories_model->updateFlag($site_id, $text, $department_members_id);
					// 		} catch (Exception $e)
					// 		{
					// 			$this->site_categories_model->db->close();
					// 			$this->site_categories_model->db->initialize();
					// 			$site_categories_model_update_flag_two = $this->site_categories_model->updateFlag($site_id, $text, $department_members_id);
					// 		}
					// 		$debug_stack_mid['site_categories_model_update_flag_two'] = $site_categories_model_update_flag_two;
					// 	}
					// }
					// === insert / update decisions stuffs (end)
					$debug_stack['site_categories'][] = $debug_stack_mid;
				}
				// ==== 'site_categories' DB table actions stuffs (end)
			}
		}
		unlink($file);
		if (count($flist) > 0)
		{
			$sited = implode('/', $site_name);
			$call_link = base_url() . "crons/save_departments_categories/$site_id/$sited"; // > /dev/null 2>/dev/null &";
			//echo $call_link;
			echo $call_link;
			$this->site_categories_model->curl_async($call_link);
			//$srec = shell_exec("wget -S -O- ".$call_link);
			//echo $srec;
//          shell_exec("wget -S -O- ".  base_url()."system/save_department_categories > /dev/null 2>/dev/null &");
		}
		//        else{
		//unset($_SESSION['mpost']);
		$this->output->set_content_type('application/json')->set_output(json_encode($debug_stack));
//          }
	}

	//*/

	public function match_urls()
	{
		$this->load->model('temp_data_model');
		$this->load->model('site_categories_model');
		$this->load->model('settings_model');
		$this->load->model('imported_data_parsed_model');
		$process = $this->uri->segment(3);
		$linesScaned = $this->uri->segment(4);
		$notFoundUrls = $this->uri->segment(6);
		$itemsUpdated = $this->uri->segment(5);
		$itemsUnchanged = $this->uri->segment(7);
		$start = microtime(true);
		$timing = 0;
    $start_run1 = microtime(true);
    log_message('ERROR', "Start while cron");                 
		while ($timing < 200 && $urls = $this->temp_data_model->getLineFromTable('urlstomatch'))
		{
			$atuc = 2;
			$nfurls = 0;
			++$linesScaned;
			//$ms = microtime(TRUE);
			$url1 = $this->imported_data_parsed_model->getModelByUrl($urls['url1']);
			$url2 = $this->imported_data_parsed_model->getModelByUrl($urls['url2']);
			//$dur = microtime(true)-$ms;
			//exit("select data from db ".$dur);
			$model1 = '';
			$model2 = '';
                    if ($url1 === FALSE) {
                            ++$nfurls;
                            $this -> temp_data_model -> addUrlToNonFound($urls['url1'], $process);
                            $atuc -= 1;
                            //$notFoundUrlsArr[]=$urls[0];
                    }/* else {
                            $tm = false;
                            if ($url1['ph_attr']) {
                                    $tm = unserialize($url1['ph_attr']);
                            }
                            $model1 = $tm['model'] && strlen($tm['model']) > 3 ? $tm['model'] : FALSE;
                    }//*/
                    if ($url2 === FALSE) {
                            ++$nfurls;
                            $this -> temp_data_model -> addUrlToNonFound($urls['url2'], $process);
                            $atuc -= 1;
                            //$notFoundUrlsArr[]=$urls[1];
                    } /*else {
                            $tm = false;
                            if ($url2['ph_attr']) {
                                    $tm = unserialize($url2['ph_attr']);
                            }
                            $model2 = isset($tm['model']) && strlen($tm['model']) > 3 ? $tm['model'] : false;
                    }//*/
                    if ($nfurls > 0) {
                            $notFoundUrls += $nfurls;
                    } else {
                            $this -> imported_data_parsed_model -> addItem($url1['data_id'], $url2['data_id']);
                            if(($url1['model'] && strlen($url1['model']) > 3)
                                    && strval($url1['model']) !== strval($url2['model'])){
                                $this -> temp_data_model -> addUpdData($url2['data_id'], $url2['model'], $url1['model']);
                                $this -> imported_data_parsed_model -> updateModelOfItem($url2['data_id'], strval($url1['model']), $url1['rev'] + 1, $url1['data_id']);
                                ++$itemsUpdated;
                                $atuc -= 1;
                            }
                            elseif(($url2['model'] && strlen($url2['model']) > 3)
                                    && strval($url2['model']) !== strval($url1['model'])){
                                $this -> temp_data_model -> addUpdData($url1['data_id'], $url1['model'], $url2['model']);
                                $this -> imported_data_parsed_model -> updateModelOfItem($url1['data_id'], strval($url2['model']), $url2['rev'] + 1, $url2['data_id']);
                                ++$itemsUpdated;
                                $atuc -= 1;
                            }
                            elseif(!($url1['model'] && strlen($url1['model']) > 3)
                                    &&!($url2['model'] && strlen($url2['model']) > 3)){
                                $model = time();
                                $this -> temp_data_model -> addUpdData($url1['data_id'], $url1['model'], $model);
                                $this -> temp_data_model -> addUpdData($url2['data_id'], $url2['model'], $model);
                                $this -> imported_data_parsed_model -> updateModelOfItem($url1['data_id'], $model, $url2['rev'] + 1, $url2['data_id']);
                                $this -> imported_data_parsed_model -> updateModelOfItem($url2['data_id'], $model, $url1['rev'] + 1, $url1['data_id']);
                                $itemsUpdated += 2;
                                $atuc -= 2;
                            }
//                            if ($model1) {
//                                    if ($model2 && $model1 != $model2) {
//                                            if (!($url2['model'] && strlen($url2['model']) > 3) || ($url2['model'] != $model1)) {
//                                                    $this -> temp_data_model -> addUpdData($url2['data_id'], $url2['model'], $model1);
//                                                    $this -> imported_data_parsed_model -> updateModelOfItem($url2['data_id'], $model1, $url1['rev'] + 1, $url1['data_id']);
//                                                    ++$itemsUpdated;
//                                                    $atuc -= 1;
//                                            }
//                                    } elseif (!$model2 && (!($url2['model'] && strlen($url2['model']) > 3) || $model1 != $url2['model'])) {
//                                            $this -> temp_data_model -> addUpdData($url2['data_id'], $url2['model'], $model1);
//                                            $this -> imported_data_parsed_model -> updateModelOfItem($url2['data_id'], $model1, $url1['rev'] + 1, $url1['data_id']);
//                                            ++$itemsUpdated;
//                                            $atuc -= 1;
//                                    }
//                            } elseif ($model2) {
//                                    if (!($url1['model'] && strlen($url1['model']) > 3) || $model2 != $url1['model']) {
//                                            $this -> temp_data_model -> addUpdData($url1['data_id'], $url1['model'], $model2);
//                                            $this -> imported_data_parsed_model -> updateModelOfItem($url1['data_id'], $model2, $url2['rev'] + 1, $url2['data_id']);
//                                            ++$itemsUpdated;
//                                            $atuc -= 1;
//                                    }
//                            } elseif (($url1['model'] && strlen($url1['model']) > 3)) {
//                                    if (!($url2['model'] && strlen($url2['model']) > 3) || ($url1['model'] != $url2['model'])) {
//                                            $this -> temp_data_model -> addUpdData($url2['data_id'], $url2['model'], $url1['model']);
//                                            $this -> imported_data_parsed_model -> updateModelOfItem($url2['data_id'], $url1['model'], $url1['rev'] + 1, $url1['data_id']);
//                                            ++$itemsUpdated;
//                                            $atuc -= 1;
//                                    }
//                            } elseif (($url2['model'] && strlen($url2['model']) > 3)) {
//                                    $this -> temp_data_model -> addUpdData($url1['data_id'], $url1['model'], $url2['model']);
//                                    $this -> imported_data_parsed_model -> updateModelOfItem($url1['data_id'], $url2['model'], $url2['rev'] + 1, $url2['data_id']);
//                                    ++$itemsUpdated;
//                                    $atuc -= 1;
//                            } else {
//                                    $model = time();
//                                    $this -> temp_data_model -> addUpdData($url1['data_id'], $url1['model'], $model);
//                                    $this -> temp_data_model -> addUpdData($url2['data_id'], $url2['model'], $model);
//                                    $this -> imported_data_parsed_model -> updateModelOfItem($url1['data_id'], $model, $url2['rev'] + 1, $url2['data_id']);
//                                    $this -> imported_data_parsed_model -> updateModelOfItem($url2['data_id'], $model, $url1['rev'] + 1, $url1['data_id']);
//                                    $itemsUpdated += 2;
//                                    $atuc -= 1;
//                            }
                    }
			if ($atuc < 0)
			{
				exit('incrorrect ATUC');
                    }
                    $itemsUnchanged += $atuc;
                    $timing = microtime(true) - $start;
		}
		//*/
    $start_run2 = microtime(true);        
    $exec_time = $start_run2 - $start_run1;
    log_message('ERROR', "{$exec_time}sec - {$linesScaned} lines Phase 2");  
    log_message('ERROR', 'memory usage (peak) : (' . memory_get_peak_usage(). ')' . memory_get_usage()) ;                
		if ($timing < 200)
		{
			$val = "$process|$linesScaned|$notFoundUrls|$itemsUpdated|$itemsUnchanged";
			$this->settings_model->updateMatchingUrls($process, $val);
                    log_message('ERROR','Cron stoped');
		} else
		{
			$lts = $this->temp_data_model->getTableSize('urlstomatch');
			$this->settings_model->procUpdMatchingUrls($process, $lts, $itemsUnchanged);
			if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN')
			{//This part of script added for local testing and works on windows os
				$call_link = base_url() . "crons/match_urls/$process/$linesScaned/$itemsUpdated/$notFoundUrls/$itemsUnchanged";
                                //Link below works on dev server and it not useful for local testing.
				//$call_link = "http://dev.contentanalyticsinc.com/producteditor/index.php/crons/match_urls/$process/$linesScaned/$itemsUpdated/$notFoundUrls/$itemsUnchanged";
//            exit($call_link);
				$this->site_categories_model->curl_async($call_link);
			} else
			{
				// shell_exec("wget -S -O- http://tmeditor/index.php/crons/match_urls/$process/$linesScaned/$itemsUpdated/$notFoundUrls/$itemsUnchanged > /dev/null 2>/dev/null &");
				shell_exec("wget -S -O- ".site_url('/crons/match_urls/'.$process.'/'.$linesScaned.'/'.$itemsUpdated.'/'.$notFoundUrls.'/'.$itemsUnchanged)." > /dev/null 2>/dev/null &");
			}
		}
	}

    function match_urls_thread($choosen_file = null, $mode = 'Upload+Update') {
// Specific settings for server need            
//            $child_pid = pcntl_fork();
//            if ($child_pid) {
//                // Parent process
//                exit();
//            }
        // Set basic for child process
        $new_child_pid = posix_setsid();
log_message('ERROR', 'Start ' . $mode . ' ' . $choosen_file . ' pid=' . $new_child_pid);
        if ($mode !== 'Upload+Update') {
            $mode = 'Update';
        }
        $this->maxthreads = $this->config->item('thread_max');
        if ($this->maxthreads < 1) {
            $this->maxthreads = 1;
        }
        $parent_sleep = 0;
        $start_run = microtime(true);
        $start = microtime(true);
        $timing = 0;
        $old_timing = 0;
        $process = time();
        if (!$choosen_file) {
            if (defined('CMD') && CMD) {
                log_message('ERROR', 'File not defined ');
                $history_run['ERROR'] = 'File not defined ';
                $this->_save_history($history_run);
                return;
            }
            $choosen_file = $this->input->post('choosen_file');
        }
        $history_run = array(
            'start' => 'Start ' . $mode . ' ' . $choosen_file . ' with threads=' . $this->maxthreads . ' pid=' . $new_child_pid,
            'thread_pid' => $new_child_pid
        );

        $this->load->model('settings_model');
        $this->load->model('imported_data_parsed_model');
        $this->load->model('temp_data_model');
        $this->load->model('matchurls_data_model');
        if ($mode == 'Upload+Update') {
            $file = $this->config->item('csv_upload_dir') . $choosen_file;
//                $f_name = end(explode('/', $file));
        } else {
            if ($choosen_file == 'all') {
                log_message('ERROR', 'This operation (all CSV update) not permitted');
                $history_run['ERROR'] = 'This operation (all CSV update) not permitted';
                $this->_save_history($history_run);
                return;
            }
        }
        // reopen DB in child process
//            $this->db->close();
//            $this->db->initialize(); 

        $this->temp_data_model->emptyTable('notfoundurls');
//            $this -> temp_data_model -> emptyTable('urlstomatch');

        $this->temp_data_model->emptyTable('updated_items');
        $this->settings_model->deledtMatching();
        $this->matchurls_data_model->createCSVFileTables();

        $this->temp_data_model->createMatchUrlsTable();
        $this->temp_data_model->createNonFoundTable();
        $this->temp_data_model->cUpdDataTable();

        $itemsUpdated = 0;
        $itemsUnchanged = 0;
        $linesAdded = 0;
        $linesScaned = 0;
        $notFoundUrls = 0;
        $urlsCSV = array();
        $fileHandler = false;

        if ($mode == 'Upload+Update') {
            // Mode Upload+Update
            $fileHandler = fopen($file, 'r');
            if (!$fileHandler) {
                log_message('ERROR', 'File not open ' . $file);
                $history_run['ERROR'] = 'File not open ' . $file;
                $this->_save_history($history_run);
                return;
            }
            if ($fileCSV_id = $this->matchurls_data_model->getIdCSVFile($choosen_file)) {
                $this->matchurls_data_model->deleteCSV($fileCSV_id);
                log_message('ERROR', 'DB cleared for file ' . $choosen_file . ' file_id=' . $fileCSV_id);
            }
            $fileCSV_id = $this->matchurls_data_model->addCSVFile($choosen_file);
        } else {
            // Mode Update only
            $fileCSV_id = $this->matchurls_data_model->getIdCSVFile($choosen_file);
            if (!$fileCSV_id) {
                log_message('ERROR', 'File not cacher in DB ' . $choosen_file);
                $history_run['ERROR'] = 'File not cacher in DB ' . $choosen_file;
            }
            $urlsCSV = $this->matchurls_data_model->getUrlsCSVFile($fileCSV_id);
            $linesAdded = count($urlsCSV);
        }

        $this->settings_model->addMatchingUrls($mode . ' ' . $choosen_file, $process, $linesAdded);
        $this->_save_history($history_run);

        while ($urls = $this->_nextMathUrlsPair($mode, $fileHandler, $urlsCSV)) {

            ++$linesScaned;

            if ($mode == 'Upload+Update') {
                $this->matchurls_data_model->addUrlToMatch($fileCSV_id, $urls['url1'], $urls['url2']); //Add urls to table
            }
            $urls_in_1 = urlencode($urls['url1']);
            $urls_in_2 = urlencode($urls['url2']);

            if ($this->maxthreads <= 1) {
                $atuc = $this->match_urls_thread_worker($process, $urls_in_1, $urls_in_2);
            } else {
                for ($i = 0; $i < $this->maxthreads; $i++) {
                    if (!isset($this->threads[$i]) || (isset($this->threads[$i]) && !$this->_is_process_running($this->threads[$i]))) {
                        // start new worker
                        $this->threads[$i] = $this->_run_in_background("php cli.php crons match_urls_thread_worker \"$process\" " . $urls_in_1 . " " . $urls_in_1 . " ");
                        break;
                    }
                }
                while ($this->_is_all_processes_running()) {
                    // all worker is working - we waiting
                    ++$parent_sleep;
                    sleep(1);
                }
                $atuc = 0;  // normal processed with threads - not return from workers
            }

            if ($atuc < 0) {
                log_message('ERROR', 'incorrect ATUC');
                exit();
            }
//                    $itemsUnchanged += $atuc;
            $timing = microtime(true) - $start;

            if ($timing - $old_timing > 5) { // set the update interval information for frontend
                $lts = $linesScaned;
                $itemsUpdated = $this->temp_data_model->getTableSize('updated_items');
                $notFoundUrls = $this->temp_data_model->getTableSize('notfoundurls');
                $itemsUnchanged = (2 * $linesScaned) - ( $itemsUpdated + $notFoundUrls);
                $this->settings_model->procUpdMatchingUrls($process, $lts, $itemsUnchanged);
                $old_timing = $timing;
            }
        }
        if ($mode == 'Upload+Update') {
            fclose($fileHandler);
        }
        while ($this->maxthreads > 1 && !$this->_is_all_processes_stopped()) {
            // worker is working - we waiting
            sleep(1);
        }
        $start_run2 = microtime(true);
        $exec_time = $start_run2 - $start_run;
        $history_run[] = "{$exec_time} sec - {$linesScaned} lines Phase 2";
        $history_run[] = 'End all sec: ' . ($start_run2 - $start_run);
        $history_run[] = 'memory usage (peak) : (' . memory_get_peak_usage() . ')' . memory_get_usage();
        $history_run[] = ' threads=' . count($this->threads);
        $history_run[] = ' parent waited=' . $parent_sleep;
        $notFoundUrls = $this->temp_data_model->getTableSize('notfoundurls');
        $itemsUpdated = $this->temp_data_model->getTableSize('updated_items');
        $itemsUnchanged = (2 * $linesScaned) - ( $itemsUpdated + $notFoundUrls);
        $val = "$process|$linesScaned|$notFoundUrls|$itemsUpdated|$itemsUnchanged";
        $this->settings_model->updateMatchingUrls($process, $val);
        $history_run['thread_pid'] = 0;
        $this->_save_history($history_run);
        log_message('ERROR', 'MatchingUrls:' . print_r($history_run, true));
    }

    function _nextMathUrlsPair($mode, &$fileHandler, &$urlsCSV) {
        if ($mode == 'Upload+Update') {
            while ($line = fgets($fileHandler)) {
                $urls = explode(',', trim(trim($line), ','));
                if (count($urls) == 2) {
//log_message('ERROR', "mode={$mode} urls=" . print_r($urls,true));                    
                    return array('url1' => $urls[0], 'url2' => $urls[1]);
                }
            }
        } else {
            if($urls = next($urlsCSV)) {
//log_message('ERROR', "mode={$mode} urls=" . print_r($urls,true));
                return array('url1' => $urls->url1, 'url2' => $urls->url2);
            }
        }
        return false;
    }

        
        function match_urls_thread_worker( $process, $urls_in_1, $urls_in_2 ) 
        {
             
            $urls['url1'] = urldecode($urls_in_1);
            $urls['url2'] = urldecode($urls_in_2);
            $notFoundUrls = 0;
            $itemsUpdated = 0;
//            $this -> load -> model('settings_model');
            $this -> load -> model('imported_data_parsed_model');
            $this -> load -> model('temp_data_model');

            // ===== not changed logic
            
                    $atuc = 2;
                    $nfurls = 0;
                    //$ms = microtime(TRUE);
                    $url1 = $this -> imported_data_parsed_model -> getModelByUrl($urls['url1']);
                    $url2 = $this -> imported_data_parsed_model -> getModelByUrl($urls['url2']);
                    //$dur = microtime(true)-$ms;
                    //exit("select data from db ".$dur);
                    $model1 = '';
                    $model2 = '';
                    if ($url1 === FALSE) {
                            ++$nfurls;
                            $this -> temp_data_model -> addUrlToNonFound($urls['url1'], $process);
                            $atuc -= 1;
                            //$notFoundUrlsArr[]=$urls[0];
                    }/* else {
                            $tm = false;
                            if ($url1['ph_attr']) {
                                    $tm = unserialize($url1['ph_attr']);
                            }
                            $model1 = $tm['model'] && strlen($tm['model']) > 3 ? $tm['model'] : FALSE;
                    }//*/
                    if ($url2 === FALSE) {
                            ++$nfurls;
                            $this -> temp_data_model -> addUrlToNonFound($urls['url2'], $process);
                            $atuc -= 1;
                            //$notFoundUrlsArr[]=$urls[1];
                    } /*else {
                            $tm = false;
                            if ($url2['ph_attr']) {
                                    $tm = unserialize($url2['ph_attr']);
                            }
                            $model2 = isset($tm['model']) && strlen($tm['model']) > 3 ? $tm['model'] : false;
                    }//*/
                                        if ($nfurls > 0) {
                            $notFoundUrls += $nfurls;
                    } else {
                            $this -> imported_data_parsed_model -> addItem($url1['data_id'], $url2['data_id']);
                            if(($url1['model'] && strlen($url1['model']) > 3)
                                    && $url1['model'] != $url2['model']){
                                $this -> temp_data_model -> addUpdData($url2['data_id'], $url2['model'], $url1['model']);
                                $this -> imported_data_parsed_model -> updateModelOfItem($url2['data_id'], $url1['model'], $url1['rev'] + 1, $url1['data_id']);
                                ++$itemsUpdated;
                                $atuc -= 1;
                            }
                            elseif(($url2['model'] && strlen($url2['model']) > 3)
                                    && $url2['model'] != $url1['model']){
                                $this -> temp_data_model -> addUpdData($url1['data_id'], $url1['model'], $url2['model']);
                                $this -> imported_data_parsed_model -> updateModelOfItem($url1['data_id'], $url2['model'], $url2['rev'] + 1, $url2['data_id']);
                                ++$itemsUpdated;
                                $atuc -= 1;
                            }
                            elseif(!($url1['model'] && strlen($url1['model']) > 3)
                                    &&!($url2['model'] && strlen($url2['model']) > 3)){
                                $model = time();
                                $this -> temp_data_model -> addUpdData($url1['data_id'], $url1['model'], $model);
                                $this -> temp_data_model -> addUpdData($url2['data_id'], $url2['model'], $model);
                                $this -> imported_data_parsed_model -> updateModelOfItem($url1['data_id'], $model, $url2['rev'] + 1, $url2['data_id']);
                                $this -> imported_data_parsed_model -> updateModelOfItem($url2['data_id'], $model, $url1['rev'] + 1, $url1['data_id']);
                                $itemsUpdated += 2;
                                $atuc -= 2;
                            }
                    }
                // ===== not changed logic
//            return $atuc;
        }
        
        function _run_in_background($Command)
        {
            $PID = shell_exec("$Command > /dev/null 2> /dev/null & echo $!");
            return($PID);
        }
       
        function _is_process_running($PID)
        {
            $ProcessState = '';
            exec("ps $PID", $ProcessState);
            return(count($ProcessState) >= 2);
        }
        
        function _is_all_processes_running()
        {
            for($i=0; $i<$this->maxthreads;$i++) {
                if(!isset($this->threads[$i]) || (isset($this->threads[$i]) && !$this->_is_process_running($this->threads[$i])))
                {
//                    $this->threads[$i] = 0;
                    return false;
                }
            }
            return true;
        }
        
        function _is_all_processes_stopped()
        {
            for($i=0; $i<$this->maxthreads;$i++) {
                if(isset($this->threads[$i]) && $this->_is_process_running($this->threads[$i]))
                {
                    return false;
                }
            }
            return true;
        }

        function _save_history($history_run = array())
        {
            if($this -> settings_model -> get_value(-1, 'thread_history') !== false) {
                $this -> settings_model -> update_value(-1, 'thread_history', $history_run);
            } else {
                $this -> settings_model -> create(-1,'thread_history', $history_run, 'PID by upload match ');
            }
        }
        
//	function match_urls_thread()
//	{
//		ini_set('mysql.connect_timeout', 120);
//		$this->load->model('temp_data_model');
//		$this->load->model('site_categories_model');
//		$this->load->model('settings_model');
//		$this->load->model('thread_model');
//		$this->load->model('imported_data_parsed_model');
//		$process = $this->uri->segment(3);
//		$this->thread_model->updateStatus($process, 'process');
//		$process_fields = $this->thread_model->get_process_fields($process);
//		$linesScaned = $process_fields['lines_scaned'];
//		$notFoundUrls = $process_fields['not_found_urls'];
//		$itemsUpdated = $process_fields['items_updated'];
//		$itemsUnchanged = $process_fields['items_unchanged'];
//		$limitStart = $process_fields['start_limit'];
//		$limitEnd = $process_fields['end_limit'];
//		$start = microtime(true);
//		$data = $this->temp_data_model->getLineFromTableLimit('urlstomatch', $limitStart, $limitEnd);
//		$size_data = sizeof($data);
//
//		foreach ($data as $key => $urls)
//		{
//			$atuc = 2;
//			$nfurls = 0;
//			++$linesScaned;
//			$url1 = $this->imported_data_parsed_model->getModelByUrl($urls['url1']);
//			$url2 = $this->imported_data_parsed_model->getModelByUrl($urls['url2']);
//			$model1 = '';
//			$model2 = '';
//			if ($url1 === FALSE)
//			{
//				++$nfurls;
//				$this->temp_data_model->addUrlToNonFound($urls['url1'], $process);
//				$atuc -= 1;
//				//$notFoundUrlsArr[]=$urls[0];
//			} else
//			{
//				$tm = false;
//				if ($url1['ph_attr'])
//				{
//					$tm = unserialize($url1['ph_attr']);
//				}
//				$model1 = $tm['model'] && strlen($tm['model']) > 3 ? $tm['model'] : FALSE;
//			}
//			if ($url2 === FALSE)
//			{
//				++$nfurls;
//				$this->temp_data_model->addUrlToNonFound($urls['url2'], $process);
//				$atuc -= 1;
//				//$notFoundUrlsArr[]=$urls[1];
//			} else
//			{
//				$tm = false;
//				if ($url2['ph_attr'])
//				{
//					$tm = unserialize($url2['ph_attr']);
//				}
//				$model2 = $tm['model'] && strlen($tm['model']) > 3 ? $tm['model'] : false;
//			}
//			if ($nfurls > 0)
//			{
//				$notFoundUrls += $nfurls;
//			} else
//			{
//				$this->imported_data_parsed_model->addItem($url1['data_id'], $url2['data_id']);
//				if ($model1)
//				{
//					if ($model2 && $model1 != $model2)
//					{
//						if (!($url2['model'] && strlen($url2['model']) > 3) || ($url2['model'] != $model1))
//						{
//							$this->temp_data_model->addUpdData($url2['data_id'], $url2['model'], $model1);
//							$this->imported_data_parsed_model->updateModelOfItem($url2['data_id'], $model1, $url1['rev'] + 1, $url1['data_id']);
//							++$itemsUpdated;
//							$atuc -= 1;
//						}
//					} elseif (!$model2 && (!($url2['model'] && strlen($url2['model']) > 3) || $model1 != $url2['model'])
//					)
//					{
//						$this->temp_data_model->addUpdData($url2['data_id'], $url2['model'], $model1);
//						$this->imported_data_parsed_model->updateModelOfItem($url2['data_id'], $model1, $url1['rev'] + 1, $url1['data_id']);
//						++$itemsUpdated;
//						$atuc -= 1;
//					}
//				} elseif ($model2)
//				{
//					if (!($url1['model'] && strlen($url1['model']) > 3) || $model2 != $url1['model'])
//					{
//						$this->temp_data_model->addUpdData($url1['data_id'], $url1['model'], $model2);
//						$this->imported_data_parsed_model->updateModelOfItem($url1['data_id'], $model2, $url2['rev'] + 1, $url2['data_id']);
//						++$itemsUpdated;
//						$atuc -= 1;
//					}
//				} elseif (($url1['model'] && strlen($url1['model']) > 3))
//				{
//					if (!($url2['model'] && strlen($url2['model']) > 3) || ($url1['model'] != $url2['model']))
//					{
//						$this->temp_data_model->addUpdData($url2['data_id'], $url2['model'], $url1['model']);
//						$this->imported_data_parsed_model->updateModelOfItem($url2['data_id'], $url1['model'], $url1['rev'] + 1, $url1['data_id']);
//						++$itemsUpdated;
//						$atuc -= 1;
//					}
//				} elseif (($url2['model'] && strlen($url2['model']) > 3))
//				{
//					$this->temp_data_model->addUpdData($url1['data_id'], $url1['model'], $url2['model']);
//					$this->imported_data_parsed_model->updateModelOfItem($url1['data_id'], $url2['model'], $url2['rev'] + 1, $url2['data_id']);
//					++$itemsUpdated;
//					$atuc -= 1;
//				} else
//				{
//					$model = time();
//					$this->temp_data_model->addUpdData($url1['data_id'], $url1['model'], $model);
//					$this->temp_data_model->addUpdData($url2['data_id'], $url2['model'], $model);
//					$this->imported_data_parsed_model->updateModelOfItem($url1['data_id'], $model, $url2['rev'] + 1, $url2['data_id']);
//					$this->imported_data_parsed_model->updateModelOfItem($url2['data_id'], $model, $url1['rev'] + 1, $url1['data_id']);
//					$itemsUpdated += 2;
//					$atuc -= 1;
//				}
//			}
//			if ($atuc < 0)
//			{
//				exit('incrorrect ATUC');
//			}
//			$itemsUnchanged += $atuc;
//			$timing = microtime(true) - $start;
//
//			if ($timing < 60)
//			{
//				
//			} else
//			{
//				$this->thread_model->updateStatus($process, 'process', array('lines_scaned' => $linesScaned, 'items_updated' => $itemsUpdated, 'not_found_urls' => $notFoundUrls, 'items_unchanged' => $itemsUnchanged));
//				$start = microtime(true);
//				die();
//			}
//
//			if ($size_data == $linesScaned)
//			{
//				$this->thread_model->updateStatus($process, 'end', array('lines_scaned' => $linesScaned, 'items_updated' => $itemsUpdated, 'not_found_urls' => $notFoundUrls, 'items_unchanged' => $itemsUnchanged));
//				$uid = $this->session->userdata('user_id');
//				if ($this->thread_model->current_all_process($uid) == $this->thread_model->current_end_process($uid))
//				{
//					$this->thread_model->clear($uid);
//				}
//			}
//		}
//	}

	function fixawm_am($wmb, $amb)
	{
		$this->load->model('statistics_new_model');
		$this->statistics_new_model->emptyItemByBatchId($wmb);
		$this->statistics_new_model->addAmToWal($amb);
	}

	function fix_imported_data_parsed_models()
	{
		$this->load->model('site_categories_model');
		$sql = "select imported_data_id as item, `value` as parsed_attributes
            from imported_data_parsed
            where `key`='parsed_attributes' and `value` like '%\"model\"%' and model is null";
		$query = $this->db->query($sql);
		if ($query->num_rows === 0)
		{
			exit;
		}
		$i = 0;
		$start = microtime(true);
		foreach ($query->result() as $res)
		{
			$pa = unserialize($res->parsed_attributes);
			if (isset($pa['model']) && strlen($pa['model']) > 3)
			{
				$data = array(
				    'model' => $pa['model'],
				);
				$this->db->where('imported_data_id', $res->item);
				$this->db->update('imported_data_parsed', $data);
				++$i;
			}
			if (microtime(TRUE) - $start > 200)
			{
				break;
			}
		}
		if (microtime() - $start < 200 || $i == 0)
		{
			exit;
		}
		if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN')
		{
			$call_link = base_url() . "fix_imported_data_parsed_models";
			$this->site_categories_model->curl_async($call_link);
		} else
		{
			shell_exec("wget -S -O- ".site_url('/crons/fix_imported_data_parsed_models')." > /dev/null 2>/dev/null &");
		}
	}

	function fixmodel_length()
	{
		$sql = "SELECT imported_data_id as dataid, model
            FROM  `imported_data_parsed`
            WHERE CHAR_LENGTH(  `model` ) <4
            AND  `key` =  'url'";
		$query = $this->db->query($sql);
		if ($query->num_rows === 0)
		{
			exit;
		}
		foreach ($query->result() as $res)
		{
			$data = array(
			    'model' => substr(0, 8, uniqid($res->model))
			);
			$this->db->where('imported_data_id', $res->dataid);
			$this->db->update('imported_data_parsed', $data);
		}
	}

	function fix_revisions()
	{
		$sql = "select idp.imported_data_id as item, idp.`value` as url
            , idp.revision as revision, idpa.revision as old_revision
            from imported_data_parsed as idp
            left join (
            select imported_data_id, max(revision) as revision
            from imported_data_parsed_archived
            group by imported_data_id )as idpa
            on idp.imported_data_id = idpa.imported_data_id
            where ((idpa.imported_data_id is null and idp.revision !=1) or idp.revision-idpa.revision > 1)
            and idp.`key`='url'";
		$query = $this->db->query($sql);
		if ($query->num_rows === 0)
		{
			exit;
		}
		foreach ($query->result() as $res)
		{
			$data = array(
			    'revision' => $res->old_revision !== null ? $res->old_revision + 1 : 1
			);
			$this->db->where('imported_data_id', $res->item);
			$this->db->update('imported_data_parsed', $data);
		}
	}

	private function webthumb_call($url)
	{
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
	public function do_stats_bybatch()
	{
		echo "Script start working";
		$tmp_dir = sys_get_temp_dir() . '/';
		unlink($tmp_dir . ".locked");
		if (file_exists($tmp_dir . ".locked"))
		{
			exit;
		}
		$first_start = time();
		touch($tmp_dir . ".locked");
		$cjo = 0;
		try
		{
			$this->load->model('imported_data_parsed_model');
			$this->load->model('sites_model');
			$this->load->model('batches_model');
			$this->load->model('statistics_new_model');
			
			//$this->statistics_new_model->truncate();
			
			//Checking the third segment of URI for truncate flag 
			$batch_id = $this->uri->segment(3);
                        if($batch_id){
                            $batch = $this->batches_model->get($batch_id);
                            if(empty($batch)){
                                exit('incorrect batch.');
                            }
                        }
			$this->different_revissions();
			$dss = $this->imported_data_parsed_model->getDoStatsStatus(); //getting status of do_stats process
			if (!$dss) //if status info does not exists
			{
				//Set status for prevent duplicate
				$this->imported_data_parsed_model->setDoStatsStatus();
				$this->settings_model->setLastUpdate(1); //adding last update info
			} else
			{
				if ($dss->description === 'stopped') //if status info exists, and description is 'stopped'
				{
					$this->imported_data_parsed_model->updDoStatsStatus(1); //update status info
				}
				$this->settings_model->setLastUpdate(); //update status info
			}
			//Get items for scanning
			$time_start = microtime(true);
			$data_arr = $this->imported_data_parsed_model->do_stats_newupdated($batch_id);
			echo "<br>get_data ---- " . (microtime(true) - $time_start);
			if (count($data_arr) > 0) //run analyze if array does not empty
			{
				$sites_list = array();
				//Get all existing sites, generate site list
				$query_cus_res = $this->sites_model->getAll();
				if (count($query_cus_res) > 0)
				{
					foreach ($query_cus_res as $key => $value)
					{
						$n = parse_url($value->url);
						$sites_list[] = $n['host'];
					}
				}
				$this->load->model('customers_model');
				$customersList = $this->customers_model->getCustomersList();
				//end of list creating script
				//Start analize each item
				foreach ($data_arr as $obj)
				{
					$foreach_start = microtime(true);
					$own_price = 0;
					$competitors_prices = array();
					$price_diff = '';
					$items_priced_higher_than_competitors = 0;
					$short_description_wc = 0;
					$long_description_wc = 0;
					$short_seo_phrases = '?';
					$long_seo_phrases = '?';
					$similar_products_competitors = array();
					$manufacturerInfo = '';
					// Price difference
					$own_site = parse_url($obj->url, PHP_URL_HOST);
					if (!$own_site)
					{	
						$own_site = "own site";
					}
					$own_site = str_replace("www1.", "", str_replace("www.", "", $own_site));

					$short_description = '';
					$long_description = '';
					echo "<br>" . "im+daat+id= " . $obj->imported_data_id . "</br>";
					//Prepare description field
					$short_description_wc = 0;
					if (($obj->description !== null || $obj->description !== 'null') && trim($obj->description) !== "")
					{
						$short_description = $obj->description;
						//replace all tags and big spaces to single space
						$obj->description = preg_replace('#<[^>]+>#',' ', $obj->description);
						$obj->description = preg_replace('/\s+/',' ', $obj->description);
						//getting count of words in short description
						$short_description_wc = count(explode(" ", $obj->description));
					}
					//Prepare long description field
					$long_description_wc = 0;
					if (($obj->long_description !== null || $obj->long_description !== 'null') && trim($obj->long_description) !== "")
					{
						$long_description = $obj->long_description;
						//replace all tags and big spaces to single space
						$obj->long_description = preg_replace('#<[^>]+>#', ' ', $obj->long_description);
						$obj->long_description = preg_replace('/\s+/', ' ', $obj->long_description);
						//getting count of words in short description
						$long_description_wc = count(explode(" ", $obj->long_description));
					}
					//Prepare manufacturer info
					if(!empty($obj->manufacturer_url))
					{
						$manufacturerInfo = serialize(array('url'=>$obj->manufacturer_url,
						'images'=>$obj->manufacturer_images,'videos'=>$obj->manufacturer_videos));
					}	
					$hash_start = microtime(true);
                                        //Prepare Title keywords
					$title_keywords = $this->imported_data_parsed_model->checkHash($obj->imported_data_id, $obj->product_name, $short_description, $long_description);
					echo 'Check hash '.(microtime(true) - $hash_start);
					if(!$title_keywords)
					{	
						// Generate Title Keywords
						$keywords_start = microtime(true);
						$title_keywords = $this->title_keywords($obj->product_name, $short_description, $long_description);
						echo "Title Keywords -------------------- <b>".(microtime(true) - $keywords_start)." seconds</b>\n";
					}
					$modelStart = microtime(true);
					$m = '';
					//If parsed attributes are exist, finding similar items and price diff
					if (isset($obj->parsed_attributes) && isset($obj->parsed_attributes['model']) && strlen($obj->parsed_attributes['model']) > 3)
					{
						//getting model of item
$modelGet = microtime(true);
						if ($obj->model && (strlen($obj->model) > 3))
						{
							$m = $obj->model;
						} else
						{
							$m = $obj->parsed_attributes['model'];
						}
						//getting model of item
						try
						{
							//Get last existing price
							$own_prices = $this->imported_data_parsed_model->getLastPrices($obj->imported_data_id,1);
						} catch (Exception $e)
						{
							echo 'Error', $e->getMessage(), "\n";
							$own_prices = $this->imported_data_parsed_model->getLastPrices($obj->imported_data_id,1);
						}
echo '<br> - model get -- '.(microtime(true) - $modelGet);
						//if own_prices is not empty make price difference data
						if (!empty($own_prices))
						{
$getSimilar = microtime(true);
							$own_price = floatval($own_prices->price);
							$obj->own_price = $own_price;
							$price_diff_exists = array();
							$price_diff_exists['id'] = $own_prices->id;
							$price_diff_exists['own_site'] = $own_site;
							$price_diff_exists['own_price'] = $own_price;
							// getting list of similar items
							try
							{
								$similar_items = $this->imported_data_parsed_model->getByParsedAttributes($m, 0, $obj->imported_data_id,$customersList);
							} catch (Exception $e)
							{
								echo 'Error', $e->getMessage(), "\n";
								$similar_items = $this->imported_data_parsed_model->getByParsedAttributes($m, 0, $obj->imported_data_id,$customersList);
							}
echo '<br> - similar get -- '.(microtime(true) - $getSimilar);
							//If similar items was found, start comparing
							if (!empty($similar_items))
							{
$checkSimilar = microtime(true);								
								foreach ($similar_items as $ks => $vs)
								{
									$customer = "";
									//find customer of similar item
									foreach ($sites_list as $ki => $vi)
									{
										if (strpos($vs['url'], "$vi") !== false)
										{
											$customer = strtolower($this->sites_model->get_name_by_url($vi));
											break;
										}
									}
									
									$similar_products_competitors[] = array(
									    'imported_data_id' => $vs['imported_data_id'],
									    'customer' => $customer
									);
$getPrices = microtime(true);								
									//Getting a three last prices for each item
									try
									{
										$three_last_prices = $this->imported_data_parsed_model->getLastPrices($vs['imported_data_id'],1);
									} catch (Exception $e)
									{
										echo 'Error', $e->getMessage(), "\n";
										//$this->load->model('statistics_model');
										//$this->statistics_model->db->close();
										//$this->statistics_model->db->initialize();
										$three_last_prices = $this->imported_data_parsed_model->getLastPrices($vs['imported_data_id'],1);
									}
echo '<br> -- get last prices -- '.(microtime(true) - $getPrices);									
									//If last three prices are exist, define range of prices and start comparing
									if (!empty($three_last_prices))
									{
										$price_scatter = $own_price * 0.03;
										$price_upper_range = $own_price + $price_scatter;
										$price_lower_range = $own_price - $price_scatter;
										$competitor_price = floatval($three_last_prices->price);
										//If own price greater than competitor price, flag will be set,
										//or if competitor price not in the defined range, then price should be updated 
										if ($competitor_price < $own_price)
										{
											$items_priced_higher_than_competitors = 1;
										}
										if ($competitor_price > $price_upper_range || $competitor_price < $price_lower_range)
										{
											$price_diff_exists['competitor_customer'][] = $similar_items[$ks]['customer'];
											$price_diff_exists['competitor_price'][] = $competitor_price;
											$price_diff = $price_diff_exists;
											$competitors_prices[] = $competitor_price;
										}
									}
echo '<br> - similar check -- '.(microtime(true) - $checkSimilar);									
								}
							}
						} else
						{
$getSimilar2 = 	microtime(true);						
							//own priece does not exists, looking for similar items
							try
							{
								$similar_items = $this->imported_data_parsed_model->getByParsedAttributes($m, 0, $obj->imported_data_id,$customersList);
							} catch (Exception $e)
							{
								echo 'Error', $e->getMessage(), "\n";
								$similar_items = $this->imported_data_parsed_model->getByParsedAttributes($m, 0, $obj->imported_data_id,$customersList);
							}
echo '<br> - similar get 2 -- '.(microtime(true) - $getSimilar2);							
							//If similar items were found, add imported_data_id and customer to similar product competitors
							if (!empty($similar_items))
							{
$checkSimilar2 = microtime(true);								
								foreach ($similar_items as $ks => $vs)
								{
									$customer = "";
									foreach ($sites_list as $ki => $vi)
									{
										if (strpos($vs['url'], "$vi") !== false)
										{
											$customer = strtolower($this->sites_model->get_name_by_url($vi));
											break;
										}
									}
									$similar_products_competitors[] = array(
									    'imported_data_id' => $vs['imported_data_id'],
									    'customer' => $customer
									);
								}
echo '<br> - similar check 2 -- '.(microtime(true) - $checkSimilar2);								
							}
						}
						$time = microtime(true) - $modelStart;
						echo "<br>model exists_and some actions - " . $time . 'seconds';
					} else
					{
						//if parsed attributes were not found, create custom model
						$time_start = microtime(true);
						if(isset($obj->imported_data_id))
						{
							echo "<br>im+daat+id= " . $obj->imported_data_id;
							//checking for custom model
							if ($model = $this->imported_data_parsed_model->check_if_exists_custom_model($obj->imported_data_id))
							{
								echo "<br>exists custom model ------------- ";
								$same_pr = $this->imported_data_parsed_model->getByParsedAttributes($model, 0, $obj->imported_data_id,$customersList);
							} else //geterate custom model if it does not exists
							{
								echo "<br>geting custom model - ";
								$same_pr = array();
								echo "product name  = " . $obj->product_name;
								$same_pr = $this->imported_data_parsed_model->getByProductNameNew($obj->imported_data_id, $obj->product_name, '', 0, $sites_list);
								echo "<br>custom model is ready ------------ ";
							}
						}
						$time = microtime(true) - $time_start;
						echo $time . " seconds (important)";
						//looking for similar competitors
						foreach ($same_pr as $key => $val)
						{
							$customer = "";
							foreach ($sites_list as $ki => $vi)
							{
								if (strpos($val['url'], "$vi") !== false)
								{
									$customer = strtolower($this->sites_model->get_name_by_url($vi));
									break;
								}
							}
							$similar_products_competitors[] = array('imported_data_id' => $val['imported_data_id'], 'customer' => $customer);
						}
					}

					$time = microtime(true) - $time_start;
					//WC Short
					$time_start = microtime(true);
					//Get research_data_id and batch_id
					$research_and_batch_ids = $this->statistics_new_model->getResearchDataAndBatchIds($obj->imported_data_id);
					if (!$research_and_batch_ids)
					{
						//If research_data_id and batch_id were not found, define them by default
						$research_and_batch_ids = array(array(
							'research_data_id' => 0,
							'batch_id' => 0,
						        'category_id' => 0
						));
					}
					$time = microtime(true) - $time_start;
					echo "<br>research_data ---------------------- " . $time . " seconds";
					//$insertStart = microtime(true);
					//insert new statistics data to statistics_new table if it not exists in table and update if exists
					try
					{
						$insert_id = $this->statistics_new_model->insert_updated($obj->imported_data_id, $obj->revision, $short_description_wc, $long_description_wc, $title_keywords, $own_price, serialize($price_diff), serialize($competitors_prices), $items_priced_higher_than_competitors, serialize($similar_products_competitors), $research_and_batch_ids, $manufacturerInfo);
					} catch (Exception $e)
					{
						echo 'Error', $e->getMessage(), "\n";
						//$this->load->model('statistics_model');
						//$this->statistics_model->db->close();
						//$this->statistics_model->db->initialize();

						$insert_id = $this->statistics_new_model->insert_updated($obj->imported_data_id, $obj->revision, $short_description_wc, $long_description_wc, $title_keywords, $own_price, serialize($price_diff), serialize($competitors_prices), $items_priced_higher_than_competitors, serialize($similar_products_competitors), $research_and_batch_ids, $manufacturerInfo);
					}
					$endTime = microtime(true);
					//echo "<br>insert/update ----------------------- " . ($endTime - $insertStart) . " seconds<br>";
					echo "<br>global foreach --------------------- " . ($endTime - $foreach_start) . " seconds<br>";
				} //end foreach
				
				$cjo = $this->settings_model->getDescription();
				$cjo++;
				$this->settings_model->updateDescription($cjo);
			}
		} catch (Exception $e)
		{
			echo 'Error', $e->getMessage(), "\n";
			unlink($tmp_dir . ".locked");
		}
		$time = time() - $first_start;
		echo "<br>all -- " . $time . "<br>";
		unlink($tmp_dir . ".locked");
		$data_arr = $this->imported_data_parsed_model->do_stats_newupdated($batch_id); //get next 50 items to scan
		$start = $this->settings_model->getDescription();
		$stats_status = $this->settings_model->getDoStatsStatus(); //get status of do_stats
		$total_items = $this->settings_model->getLastUpdate(); //get count of all items in time of starting
		//If queque has items and status is started and count of all items bigger than count of scanned items , start script again
		if (count($data_arr) > 0 && $stats_status->description === 'started' && ($cjo - 1) * 50 < intval($total_items['description']))
		{ 
			$utd = $this->imported_data_parsed_model->getLUTimeDiff();
			echo $utd->td;  //exit;
			//make asynchronous web request to do_stats_forupdated page
                        $url_link ="wget -S -O - ".site_url('/crons/do_stats_bybatch/'.$batch_id)." > /dev/null 2>/dev/null &"; 
			shell_exec($url_link);
		} else
		{
			//Or send report about success
			$this->settings_model->setLastUpdate(); //set last update time
			$mtd = $this->imported_data_parsed_model->getTimeDif(); // timing of process
			echo $mtd->td;
			//Remove status about started state
			if ($stats_status->description === 'started') //if status is started
			{
				$this->imported_data_parsed_model->delDoStatsStatus(); //remove status info
			}
			$this->settings_model->updateDescription(0);  //reset cron_job_offset 0

			
			$this->load->library('email');
			$this->email->from('info@dev.contentsolutionsinc.com', '!!!!');
			$this->email->to('bayclimber@gmail.com');
			$this->email->subject('Cron job report');
			$this->email->message('Cron job for do_statistics_new is done.<br> Timing = ' . $mtd->td); //.'<br> Total items updated: '.$qty['description']
			$this->email->send(); 
		}
		unlink($tmp_dir . ".locked");
	}
	
	function checkUploadedFiles()
	{
		$path = dirname(__FILE__);
		echo 'Path to script: '.$path;
		$uploadFolder = $this -> config -> item('csv_upload_dir');
		echo '<br>Path to upload folder: '.$uploadFolder;
		if(is_dir($uploadFolder))
		{
			$list = scandir($uploadFolder);
			if(is_array($list) && count($list) > 2)
			{
				unset($list[0]);
				unset($list[1]);
				echo '<table border=1 cellpadding=5><tr><th>Filename</th><th>Changed</th>';
				foreach($list as $l)
				{
					echo '<tr><td>'.$l.'</td><td>  '.date('Y-m-d H:i:s',filemtime($uploadFolder.'/'.$l)).'</td><tr>';
				}
				echo '</tr></table>';
			}
		}	
	}
	
	function renameExistingFiles($suffix = '')
	{
		if(empty($suffix) || preg_match('#^[0-9]+$#',$suffix))
		{	
			$uploadFolder = $this -> config -> item('csv_upload_dir');
			if(is_dir($uploadFolder))
			{
				$list = scandir($uploadFolder);
				if(is_array($list) && count($list) > 2)
				{
					unset($list[0]);
					unset($list[1]);
					foreach($list as $l)
					{	
						$ext = end(explode('.',$l));
						$name = preg_replace('#_[0-9]+.'.$ext.'#','',$l);
						$name = str_replace('.'.$ext,'',$name);
						if(preg_match('#^[0-9]+$#',$suffix))
						{
							$suffix = '_'.$suffix;
						}	
						rename($uploadFolder.'/'.$l,$uploadFolder.'/'.$name.$suffix.'.'.$ext);
					}
				}
			}
		}
		$this->checkUploadedFiles();
	}

}
