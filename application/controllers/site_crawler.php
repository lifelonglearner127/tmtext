<?php
if (!defined('BASEPATH'))
	exit('No direct script access allowed');

class Site_Crawler extends MY_Controller {

	function __construct() {
		parent::__construct();

		$this -> data['title'] = 'Site Crawler';

	}

	public function index() {
		$this -> load -> model('category_model');
		$categories = $this -> category_model -> getAll();
		$category_list = array();
		foreach ($categories as $category) {
			$category_list[$category -> id] = $category -> name;
		}
		$this -> data['category_list'] = $category_list;

		$this -> load -> model('batches_model');
		$batches = $this -> batches_model -> getAll();
		$batches_list = array('' => 'None');
		foreach ($batches as $batch) {
			$batches_list[$batch -> id] = $batch -> title;
		}

		$this -> data['batches_list'] = $batches_list;

		$this -> render();
	}

	function upload() {
		$this -> load -> library('UploadHandler');

		$this -> uploadhandler -> upload(array('script_url' => site_url('site_crawler/upload'), 'upload_dir' => $this -> config -> item('tmp_upload_dir'), 'param_name' => 'files', 'delete_type' => 'POST', 'accept_file_types' => '/.+\.(csv|txt|dat)$/i', ), false);

		$uploads = $this -> uploadhandler -> post(false);
		$urls = array();

		// process uploads
		if (!empty($uploads)) {
			$this -> load -> library('PageProcessor');
			foreach ($uploads as $upload) {
				foreach ($upload as $file) {
					$name = $this -> config -> item('tmp_upload_dir') . '/' . $file -> name;
					if (($handle = fopen($name, "r")) !== FALSE) {
						if ($file -> type == "text/csv") {
							while (($parsed = fgetcsv($handle, 2000, ",", "\"")) !== false) {
								foreach ($parsed as $col) {
									$col = str_replace(array('"', "'", "\r", "\n"), '', $col);
									if ($this -> pageprocessor -> isURL($col)) {
										$urls[] = $col;
									}
								}
							}
						} else {
							while (($line = fgets($handle)) !== false) {
								$arr = explode("\r", $line);
								// bug #106
								if (count($arr) > 1) {
									foreach ($arr as $l) {
										$line = str_replace(array('"', "'", "\r", "\n"), '', $l);
										if ($this -> pageprocessor -> isURL($l)) {
											$urls[] = $l;
										}
									}
								} else {
									$line = str_replace(array('"', "'", "\r", "\n"), '', $line);

									if ($this -> pageprocessor -> isURL($line)) {
										$urls[] = $line;
									}
								}
							}
						}
						fclose($handle);
						unlink($name);
					}
				}
			}
		}
		$this -> output -> set_content_type('application/json');
		echo json_encode(array('response' => $uploads, 'urls' => $urls));
	}

	function add() {
		$this -> load -> model('crawler_list_model');
		$this -> load -> library('PageProcessor');

		$urls = $this -> input -> post('urls');
		$category_id = $this -> input -> post('category_id');

		$this -> crawler_list_model -> db -> trans_start();
		foreach ($urls as $url) {
			$url = str_replace(array('"', "'", "\r", "\n"), '', $url);
			if ($this -> pageprocessor -> isURL($url)) {
				if (!$this -> crawler_list_model -> getByUrl($url)) {
					$this -> crawler_list_model -> insert($url, $category_id);
				}
			}
		}
		$this -> crawler_list_model -> db -> trans_complete();
	}

	function delete() {
		$this -> load -> model('crawler_list_model');
		$id = (int) str_replace('id_', '', $this -> input -> post('id'));

		$this -> crawler_list_model -> delete($id);
	}

	function update() {
		$this -> load -> model('crawler_list_model');
		$id = (int) str_replace('id_', '', $this -> input -> post('id'));
		$url = $this -> input -> post('url');

		$this -> crawler_list_model -> updateUrl($id, $url);
	}

	function new_urls() {
		$this -> load -> model('crawler_list_model');

		$this -> output -> set_content_type('application/json');
		echo json_encode(array('new_urls' => $this -> crawler_list_model -> getAllNew()));
	}

	function lock_to_qa() {
		$this -> load -> model('crawler_list_model');
		$batch_id = $this -> input -> post('batch_id');
		$res_data = array('status' => false, 'msg' => '', 'd' => null, 'batch_id' => $batch_id, 'urls' => null, 'ids_for_update' => null);
		$ids_for_update = array();
		if ($batch_id !== null) {// === take according to batch
			$urls = $this -> crawler_list_model -> getByBatchUrls($batch_id);
		} else {// === take all
			$urls = $this -> crawler_list_model -> getUrlsWithoutBatch();
		}
		// === collect ids for update (start)
		foreach ($urls as $k => $v) {
			if ($v -> status === "lock")
				$ids_for_update[] = $v -> id;
		}
		// === collect ids for update (end)
		// === mass 'lockedToQue' update (start)
		if (count($ids_for_update) > 0) {
			foreach ($ids_for_update as $ids) {
				$this -> crawler_list_model -> lockedToQue($ids);
			}
		}
		// === mass 'lockedToQue' update (end)
		$res_data['urls'] = $urls;
		$res_data['ids_for_update'] = $ids_for_update;
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($res_data));
	}

	function all_urls() {
		$this -> load -> model('crawler_list_model');
		$this -> load -> model('webshoots_model');
		$this -> load -> library('pagination');

		$search_crawl_data = '';
		if ($this -> input -> get('search_crawl_data') != '') {
			$search_crawl_data = $this -> input -> get('search_crawl_data');
		}

		if ($this -> input -> get('batch_id') != 0) {
			$total = $this -> crawler_list_model -> countByBatch($this -> input -> get('batch_id'), $this -> input -> get('status_radio'));
			$total_finished = $this -> crawler_list_model -> countByBatchWithStatus($this -> input -> get('batch_id'), 'finished');
			$total_failed = $this -> crawler_list_model -> countByBatchWithStatus($this -> input -> get('batch_id'), 'failed');
			$total_lock = $this -> crawler_list_model -> countByBatchWithStatus($this -> input -> get('batch_id'), 'lock');
			$total_queued = $this -> crawler_list_model -> countByBatchWithStatus($this -> input -> get('batch_id'), 'queued');
			$total_new = $this -> crawler_list_model -> countByBatchWithStatus($this -> input -> get('batch_id'), 'new');
		} else {
			$total = $this -> crawler_list_model -> countAll(false, $search_crawl_data, $this -> input -> get('status_radio'));
			$total_finished = $this -> crawler_list_model -> countAllWithStatus(false, $search_crawl_data, 'finished');
			$total_failed = $this -> crawler_list_model -> countAllWithStatus(false, $search_crawl_data, 'failed');
			$total_lock = $this -> crawler_list_model -> countAllWithStatus(false, $search_crawl_data, 'lock');
			$total_queued = $this -> crawler_list_model -> countAllWithStatus(false, $search_crawl_data, 'queued');
			$total_new = $this -> crawler_list_model -> countAllWithStatus(false, $search_crawl_data, 'new');
		}
		$config = array('base_url' => site_url('site_crawler/all_urls'), 'total_rows' => $total, 'per_page' => 10, 'uri_segment' => 3);

		$this -> pagination -> initialize($config);
		$page = ($this -> uri -> segment(3)) ? $this -> uri -> segment(3) : 0;

		if ($this -> input -> get('batch_id') != 0) {
			$urls = $this -> crawler_list_model -> getByBatchLimit($config["per_page"], $page, $this -> input -> get('batch_id'), $this -> input -> get('status_radio'));
		} else {
			$urls = $this -> crawler_list_model -> getAllLimit($config["per_page"], $page, false, $search_crawl_data, $this -> input -> get('status_radio'));
		}
                
                if($search_crawl_data != '' && $this -> input -> get('batch_id') != 0){
                    
                    $check = 0;
                    foreach ($urls as $key => $value) {
                        if($value->url != $search_crawl_data){
                            unset($urls[$key]);
                        }
                        else{
                            $check = 1; 
                        }
                        if($check == 1){
                            $total = $this -> crawler_list_model -> countAll(false, $search_crawl_data, $this -> input -> get('failed'));
                            $total_finished = $this -> crawler_list_model -> countAllWithStatus(false, $search_crawl_data, 'finished');
                            $total_failed = $this -> crawler_list_model -> countAllWithStatus(false, $search_crawl_data, 'failed');
                            $total_lock = $this -> crawler_list_model -> countAllWithStatus(false, $search_crawl_data, 'lock');
                            $total_queued = $this -> crawler_list_model -> countAllWithStatus(false, $search_crawl_data, 'queued');
                            $total_new = $this -> crawler_list_model -> countAllWithStatus(false, $search_crawl_data, 'new');
                        }
                        else{
                            $total = 0;
                            $total_finished = 0;
                            $total_failed = 0;
                            $total_lock = 0;
                            $total_queued = 0;
                            $total_new = 0;
                        }
                        $config = array('base_url' => site_url('site_crawler/all_urls'), 'total_rows' => $total, 'per_page' => 10, 'uri_segment' => 3);
                        $this -> pagination -> initialize($config);
                        $page = ($this -> uri -> segment(3)) ? $this -> uri -> segment(3) : 0;               
                    }
                }

		// === screenshots alive scanner (start)
		$re_query_data = false;
		if (count($urls) > 0) {
			foreach ($urls as $ks => $vs) {
				$id = $vs -> id;
				$url = $vs -> url;
				$snap = $vs -> snap;
				if ($snap !== null && trim($snap) !== "") {
					$file_size = realpath(BASEPATH . "../webroot/webshoots/$snap");
					$fs = filesize($file_size);
					if ($fs === false || $fs < 10000) {// === so re-craw it
						if (!$re_query_data)
							$re_query_data = true;
						@unlink(realpath(BASEPATH . "../webroot/webshoots/$snap"));
						$url = preg_replace('#^https?://#', '', $url);
						$api_key = $this -> config -> item('snapito_api_secret');
						$call_url = "http://api.snapito.com/web/$api_key/mc/$url";
						$snap_res = $this -> webshoots_model -> crawl_webshoot($call_url, $id, 'crawl_snap-');
						$this -> webshoots_model -> updateCrawlListWithSnap($id, $snap_res['img'], null);
					}
				}
			}
		}
		if ($re_query_data) {
			if ($this -> input -> get('batch_id') != 0) {
				$urls = $this -> crawler_list_model -> getByBatchLimit($config["per_page"], $page, $this -> input -> get('batch_id'), $this -> input -> get('status_radio'));
			} else {
				$urls = $this -> crawler_list_model -> getAllLimit($config["per_page"], $page, false, $search_crawl_data, $this -> input -> get('status_radio'));
			}
		}
		// === screenshots alive scanner (end)

		$this -> output -> set_content_type('application/json') -> set_output(json_encode(array('total' => $total, 'total_finished' => $total_finished, 'total_failed' => $total_failed, 'total_lock' => $total_lock, 'total_queued' => $total_queued,
		// 'new' => $this->crawler_list_model->countNew(false),
		'new' => $total_new, 'new_urls' => $urls, 'pager' => $this -> pagination -> create_links(14))));
	}

	function crawl_new() {
		$this -> load -> model('imported_data_model');
		$this -> load -> model('imported_data_parsed_model');
		$this -> load -> model('crawler_list_model');
		$this -> load -> model('crawler_list_prices_model');
		$this -> load -> library('PageProcessor');

		$rows = $this -> crawler_list_model -> getAllNew(1000, false);
		foreach ($rows as $data) {
			$this -> crawler_list_model -> updateStatus($data -> id, 'lock');

			if ($page_data = $this -> pageprocessor -> get_data($data -> url)) {
				$page_data['URL'] = $data -> url;
				// save data
				$page_data_without_price = $page_data;
				if (isset($page_data_without_price['Price']) && !empty($page_data['Price'])) {
					unset($page_data_without_price['Price']);
					$this -> crawler_list_prices_model -> insert($data -> id, $page_data['Price']);
				}
				$csv_row = $this -> arrayToCsv($page_data_without_price);
				$key = $this -> imported_data_model -> _get_key($csv_row);

				if (!$this -> imported_data_model -> findByKey($key)) {
					$imported_id = $this -> imported_data_model -> insert($csv_row, $data -> category_id);
					$this -> crawler_list_model -> updateImportedDataId($data -> id, $imported_id);

					foreach ($page_data_without_price as $key => $value) {
						$value = (!is_null($value)) ? $value : '';
						if (!empty($value)) {
							$this -> imported_data_parsed_model -> insert($imported_id, $key, $value);
						}
					}

					if (($attributes = $this -> pageprocessor -> attributes()) !== false) {
						$this -> imported_data_parsed_model -> insert($imported_id, 'parsed_attributes', serialize($attributes));
					}

					if (($meta = $this -> pageprocessor -> meta()) !== false) {
						$this -> imported_data_parsed_model -> insert($imported_id, 'parsed_meta', serialize($meta), $revision);
					}
				}

				$this -> crawler_list_model -> updateStatus($data -> id, 'finished');
				$this -> crawler_list_model -> updated($data -> id);
			} else {
				$this -> crawler_list_model -> updateStatus($data -> id, 'failed');
			}
		}
	}

	function download_one() {
		$this -> load -> model('imported_data_model');
		$this -> load -> model('imported_data_parsed_model');
		$this -> load -> model('crawler_list_model');
		$this -> load -> library('PageProcessor');

		$data = $this -> crawler_list_model -> getNew();
		$this -> crawler_list_model -> updateStatus($data -> id, 'lock');

		if ($page_data = $this -> pageprocessor -> get_data($data -> url)) {
			$page_data['URL'] = $data -> url;
			// save data
			$page_data_without_price = $page_data;
			if (isset($page_data_without_price['Price'])) {
				unset($page_data_without_price['Price']);
				$this -> crawler_list_prices_model -> insert($data -> id, $page_data['Price']);
			}
			$csv_row = $this -> arrayToCsv($page_data_without_price);
			$key = $this -> imported_data_model -> _get_key($csv_row);

			if (!$this -> imported_data_model -> findByKey($key)) {
				$imported_id = $this -> imported_data_model -> insert($csv_row, $data -> category_id);

				foreach ($page_data_without_price as $key => $value) {
					$value = (!is_null($value)) ? $value : '';
					$this -> imported_data_parsed_model -> insert($imported_id, $key, $value);
				}
			}
			$this -> crawler_list_model -> updateStatus($data -> id, 'finished');
			return true;
		}

		$this -> crawler_list_model -> updateStatus($data -> id, 'new');
		return false;
	}

	private function arrayToCsv(array &$fields, $delimiter = ',', $enclosure = '"', $encloseAll = false, $nullToMysqlNull = false) {
		$delimiter_esc = preg_quote($delimiter, '/');
		$enclosure_esc = preg_quote($enclosure, '/');

		$output = array();
		foreach ($fields as $field) {
			if ($field === null && $nullToMysqlNull) {
				$output[] = 'NULL';
				continue;
			}

			// Enclose fields containing $delimiter, $enclosure or whitespace
			if ($encloseAll || preg_match("/(?:${delimiter_esc}|${enclosure_esc}|\s)/", $field)) {
				$output[] = $enclosure . str_replace($enclosure, $enclosure . $enclosure, $field) . $enclosure;
			} else {
				$output[] = $field;
			}
		}

		return implode($delimiter, $output);
	}

	function crawl_all() {
		$this -> load -> model('imported_data_model');
		$this -> load -> model('imported_data_parsed_model');
		$this -> load -> model('imported_data_parsed_archived_model');
		$this -> load -> model('crawler_list_model');
		$this -> load -> model('crawler_list_prices_model');
		$this -> load -> library('PageProcessor');

		if ($this -> input -> post('id')) {
			$id = (int) str_replace('id_', '', $this -> input -> post('id'));
			$rows = $this -> crawler_list_model -> get($id);
		} else if ($this -> input -> post('ids')) {
			$rows = $this -> crawler_list_model -> getIds($this -> input -> post('ids'));
		} else if ($this -> input -> post('url') && $this -> input -> post('recrawl')) {
			$id = $this -> crawler_list_model -> getByUrl($this -> input -> post('url'));
			$rows = $this -> crawler_list_model -> getIds($id);
		} else if ($this -> input -> post('batch_id')) {
			if ($this -> input -> post('recrawl')) {
				//$rows = $this->crawler_list_model->getByBatchId($this->input->post('batch_id'));
				$rows = $this -> crawler_list_model -> getOldByBatchId($this -> input -> post('batch_id'));
			} else {
				$rows = $this -> crawler_list_model -> getNewByBatchId($this -> input -> post('batch_id'));
			}
		} else {
			$rows = $this -> crawler_list_model -> getAll(1000, false);
		}

		$ids = array();
		foreach ($rows as $data) {
			$ids[] = $data->id;
		}

		if ($this -> input -> post('crawl') && ($this -> input -> post('crawl') == 'true')) {
			$this -> crawler_list_model -> updateStatusEx($ids, 'lock');

			foreach ($rows as $data) {
				if ($page_data = $this -> pageprocessor -> get_data($data -> url)) {
					$page_data['URL'] = $data -> url;
					// save data
					$page_data_without_price = $page_data;
					if (isset($page_data_without_price['Price'])) {
						unset($page_data_without_price['Price']);
						$this -> crawler_list_prices_model -> insert($data -> id, $page_data['Price']);
					}
					$csv_row = $this -> arrayToCsv($page_data_without_price);
					$key = $this -> imported_data_model -> _get_key($csv_row);

					$revision = 1;
					if ((!$this -> imported_data_model -> findByKey($key)) && ($data -> imported_data_id == null)) {
						$imported_id = $this -> imported_data_model -> insert($csv_row, $data -> category_id);
						$this -> crawler_list_model -> updateImportedDataId($data -> id, $imported_id);
					} else if ($data -> imported_data_id !== null) {
						$imported_id = $data -> imported_data_id;
						$revision = $this -> imported_data_parsed_model -> getMaxRevision($imported_id);

						$revision++;
					}

					$model = null;
                                        if($m = $this -> imported_data_parsed_model -> get_model($imported_id) && strlen($m)>3){
                                           $model = $m;
                                        }
					if (($attributes = $this -> pageprocessor -> attributes()) !== false) {
						if (!is_null($model) && isset($attributes['model']) && strlen($attributes['model'])>3) {
							$model = $attributes['model'];
						}
						$this -> imported_data_parsed_model -> insert($imported_id, 'parsed_attributes', serialize($attributes), $revision, $model);
					}

					foreach ($page_data_without_price as $key => $value) {
						$value = (!is_null($value)) ? $value : '';
						$this -> imported_data_parsed_model -> insert($imported_id, $key, $value, $revision, $model);
					}

					if (($meta = $this -> pageprocessor -> meta()) !== false) {
						$this -> imported_data_parsed_model -> insert($imported_id, 'parsed_meta', serialize($meta), $revision);
					}

					if ($revision !== 1) {
						if ($this -> imported_data_parsed_archived_model -> saveToArchive($imported_id, $revision)) {
							$this -> imported_data_parsed_model -> deleteRows($imported_id, $revision);
						}
					}

					$this -> crawler_list_model -> updateStatus($data -> id, 'finished');
					$this -> crawler_list_model -> updated($data -> id);
				} else {
					$this -> crawler_list_model -> updateStatus($data -> id, 'failed');
				}
			}
		} else {
			// Don't crawl only mark 'queued'
			$this -> crawler_list_model -> updateStatusEx($ids, 'queued');
		}

		// === add right hand side to queue (start)
		$url_right = $this -> input -> post('url_right');
		if (isset($url_right) && trim($url_right) !== "") {
			$id_r = $this -> crawler_list_model -> getByUrl($url_right);
			$rows_r = $this -> crawler_list_model -> getIds($id_r);
			foreach ($rows_r as $data_r) {
				$this -> crawler_list_model -> updateStatus($data_r -> id, 'queued');
			}
		}
		// === add right hand side to queue (end)

	}

	public function instances_list() {
		$this -> data['instances'] = $instances;
		$this -> render();
	}

	public function get_instances() {
		$this -> load -> model('crawler_instances_model');

		$this -> output -> set_content_type('application/json') -> set_output(json_encode(array('instances' => $this -> crawler_instances_model -> getNotTerminated(), )));
	}

	public function run_instances() {
		$quantity = 1;
		$started = false;

		if ($this -> input -> post('quantity')) {
			$quantity = $this -> input -> post('quantity');
		}

		$this -> load -> model('crawler_instances_model');
		$this -> load -> library('awslib');

		if ($result = $this -> awslib -> run($quantity, $quantity)) {
			$ids = $result -> getPath('Instances/*/InstanceId');
			$instances = $result -> getPath('Instances');

			foreach ($instances as $instance) {
				$this -> crawler_instances_model -> insert($instance['InstanceId'], $instance['InstanceType'], $instance['State']['Name'], $instance['PublicDnsName']);
			}
			$started = true;
		}

		$this -> output -> set_content_type('application/json') -> set_output(json_encode(array('started' => $started, 'ids' => $ids)));
	}

	public function terminate_instances() {
		$this -> load -> model('crawler_instances_model');
		$this -> load -> library('awslib');

		$stopping = false;
		if ($this -> input -> post('ids')) {
			$ids = $this -> input -> post('ids');

			if ($result = $this -> awslib -> terminate($ids)) {
				$ids = $result -> getPath('TerminatingInstances/*/InstanceId');
				$instances = $result -> getPath('TerminatingInstances');

				//				foreach($instances as $instance) {
				//					$this->crawler_instances_model->updateState($instance['InstanceId'], $instance['CurrentState']['Name']);
				//				}

				$stopping = true;
			}

			$this -> output -> set_content_type('application/json') -> set_output(json_encode(array('stopping' => $stopping, 'ids' => $ids)));

		}
	}

	public function wait_start_instances() {
		$this -> load -> model('crawler_instances_model');
		$this -> load -> library('awslib');

		if ($this -> input -> post('ids')) {
			$ids = $this -> input -> post('ids');

			$this -> awslib -> waitRunning($ids);

			if ($result = $this -> awslib -> describe($ids)) {
				$instances = $result -> getPath('Reservations/*/Instances');
				//				var_dump($result, $instances);

				foreach ($instances as $instance) {
					$this -> crawler_instances_model -> update($instance['InstanceId'], $instance['InstanceType'], $instance['State']['Name'], $instance['PublicDnsName']);
				}
			}
		}
	}

	public function wait_terminate_instances() {
		$this -> load -> model('crawler_instances_model');
		$this -> load -> library('awslib');

		if ($this -> input -> post('ids')) {
			$ids = $this -> input -> post('ids');

			$this -> awslib -> waitTerminated($ids);

			if ($result = $this -> awslib -> describe($ids)) {
				$instances = $result -> getPath('Reservations/*/Instances');
				//				var_dump($result, $instances);

				foreach ($instances as $instance) {
					$this -> crawler_instances_model -> update($instance['InstanceId'], $instance['InstanceType'], $instance['State']['Name'], $instance['PublicDnsName']);
				}
			}
		}
	}

	public function queue_locked() {
		$this -> load -> model('crawler_list_model');

		$this -> crawler_list_model -> queue_locked();
	}

}
