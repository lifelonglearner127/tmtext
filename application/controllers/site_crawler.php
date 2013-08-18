<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Site_Crawler extends MY_Controller {

	function __construct()
 	{
  		parent::__construct();

		$this->data['title'] = 'Site Crawler';

 	}

	public function index()
	{
		$this->load->model('category_model');
        $categories = $this->category_model->getAll();
        $category_list = array();
        foreach($categories as $category){
            $category_list[$category->id] = $category->name;
        }
        $this->data['category_list'] = $category_list;

		$this->load->model('batches_model');
        $batches = $this->batches_model->getAll();
        $batches_list = array(''=>'None');
        foreach($batches as $batch){
            $batches_list[$batch->id] = $batch->title;
        }

        $this->data['batches_list'] = $batches_list;

		$this->render();
	}

	function upload() {
		$this->load->library('UploadHandler');

		$this->uploadhandler->upload(array(
            'script_url' => site_url('site_crawler/upload'),
            'upload_dir' => $this->config->item('tmp_upload_dir'),
            'param_name' => 'files',
            'delete_type' => 'POST',
			'accept_file_types' => '/.+\.(csv|txt|dat)$/i',
		), false);

		$uploads = $this->uploadhandler->post(false);
		$urls = array();

		// process uploads
		if (!empty($uploads)) {
			$this->load->library('PageProcessor');
			foreach ($uploads as $upload) {
				foreach ($upload as $file) {
					$name = $this->config->item('tmp_upload_dir').'/'.$file->name;
					if (($handle = fopen($name, "r")) !== FALSE) {
						if  ($file->type == "text/csv") {
							while (($parsed = fgetcsv($handle, 2000, ",", "\"")) !== false) {
								foreach($parsed as $col) {
									$col = str_replace(array('"', "'","\r", "\n"), '', $col);
									if ($this->pageprocessor->isURL($col)) {
										$urls[] = $col;
									}
								}
							}
						} else {
							while (($line = fgets($handle)) !== false) {
								$arr = explode("\r", $line); // bug #106
								if (count($arr)>1) {
									foreach($arr as $l) {
										$line = str_replace(array('"', "'","\r", "\n"), '', $l);
										if ($this->pageprocessor->isURL($l)) {
											$urls[] = $l;
										}
									}
								} else {
									$line = str_replace(array('"', "'","\r", "\n"), '', $line);

									if ($this->pageprocessor->isURL($line)) {
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
		$this->output->set_content_type('application/json');
		echo json_encode(array(
			'response'=> $uploads,
			'urls' => $urls
		));
	}

	function add() {
		$this->load->model('crawler_list_model');
		$this->load->library('PageProcessor');

		$urls = $this->input->post('urls');
		$category_id = $this->input->post('category_id');

		$this->crawler_list_model->db->trans_start();
		foreach($urls as $url) {
			$url = str_replace(array('"', "'","\r", "\n"), '', $url);
			if ($this->pageprocessor->isURL($url)) {
				if (!$this->crawler_list_model->getByUrl($url)) {
					$this->crawler_list_model->insert($url, $category_id);
				}
			}
		}
		$this->crawler_list_model->db->trans_complete();
	}

	function delete() {
		$this->load->model('crawler_list_model');
		$id = (int) str_replace('id_', '', $this->input->post('id'));

		$this->crawler_list_model->delete($id);
	}

	function update() {
		$this->load->model('crawler_list_model');
		$id = (int) str_replace('id_', '', $this->input->post('id'));
		$url = $this->input->post('url');

		$this->crawler_list_model->updateUrl($id, $url);
	}

	function new_urls() {
		$this->load->model('crawler_list_model');

		$this->output->set_content_type('application/json');
		echo json_encode(array(
			'new_urls' => $this->crawler_list_model->getAllNew()
		));
	}

	function all_urls() {
		$this->load->model('crawler_list_model');
		$this->load->library('pagination');

        $search_crawl_data = '';
        if($this->input->get('search_crawl_data') != ''){
            $search_crawl_data = $this->input->get('search_crawl_data');
        }

        if ($this->input->get('batch_id')!=0) {
        	$total = $this->crawler_list_model->countByBatch($this->input->get('batch_id'));
        } else {
        	$total = $this->crawler_list_model->countAll(false, $search_crawl_data);
        }
		$config = array(
			'base_url' => site_url('site_crawler/all_urls'),
			'total_rows' => $total,
			'per_page' => 10,
			'uri_segment' => 3
		);

		$this->pagination->initialize($config);
		$page = ($this->uri->segment(3)) ? $this->uri->segment(3) : 0;

		if ($this->input->get('batch_id')!=0) {
        	$urls = $this->crawler_list_model->getByBatchLimit($config["per_page"], $page, $this->input->get('batch_id'));
        } else {
        	$urls = $this->crawler_list_model->getAllLimit($config["per_page"], $page, false, $search_crawl_data);
        }

		$this->output->set_content_type('application/json');
		echo json_encode(array(
            'total' => $total,
			'new' => $this->crawler_list_model->countNew(false),
			'new_urls' => $urls,
			'pager' => $this->pagination->create_links()
		));
	}

	function crawl_new() {
		$this->load->model('imported_data_model');
		$this->load->model('imported_data_parsed_model');
		$this->load->model('crawler_list_model');
		$this->load->model('crawler_list_prices_model');
		$this->load->library('PageProcessor');

		$rows = $this->crawler_list_model->getAllNew(1000, false);
		foreach( $rows as $data) {
			$this->crawler_list_model->updateStatus($data->id, 'lock');

			if ($page_data = $this->pageprocessor->get_data($data->url)) {
				$page_data['URL'] = $data->url;
				// save data
				$page_data_without_price = $page_data;
				if (isset($page_data_without_price['Price']) && !empty($page_data['Price'])) {
					unset($page_data_without_price['Price']);
					$this->crawler_list_prices_model->insert($data->id, $page_data['Price']);
				}
				$csv_row = $this->arrayToCsv($page_data_without_price);
				$key = $this->imported_data_model->_get_key($csv_row);

				if (!$this->imported_data_model->findByKey($key)) {
					$imported_id = $this->imported_data_model->insert($csv_row, $data->category_id);
					$this->crawler_list_model->updateImportedDataId($data->id, $imported_id);

					foreach($page_data_without_price as $key=>$value) {
						$value = (!is_null($value))?$value: '';
						if (!empty($value)) {
							$this->imported_data_parsed_model->insert($imported_id, $key, $value);
						}
					}

					if (($attributes = $this->pageprocessor->attributes()) !== false) {
						$this->imported_data_parsed_model->insert($imported_id, 'parsed_attributes', serialize($attributes));
					}
				}

				$this->crawler_list_model->updateStatus($data->id, 'finished');
				$this->crawler_list_model->updated($data->id);
			} else {
				$this->crawler_list_model->updateStatus($data->id, 'failed');
			}
		}
	}

	function download_one(){
		$this->load->model('imported_data_model');
		$this->load->model('imported_data_parsed_model');
		$this->load->model('crawler_list_model');
		$this->load->library('PageProcessor');

		$data = $this->crawler_list_model->getNew();
		$this->crawler_list_model->updateStatus($data->id, 'lock');

		if ($page_data = $this->pageprocessor->get_data($data->url)) {
			$page_data['URL'] = $data->url;
			// save data
			$page_data_without_price = $page_data;
			if (isset($page_data_without_price['Price'])) {
				unset($page_data_without_price['Price']);
				$this->crawler_list_prices_model->insert($data->id, $page_data['Price']);
			}
			$csv_row = $this->arrayToCsv($page_data_without_price);
			$key = $this->imported_data_model->_get_key($csv_row);

			if (!$this->imported_data_model->findByKey($key)) {
				$imported_id = $this->imported_data_model->insert($csv_row, $data->category_id);

				foreach($page_data_without_price as $key=>$value) {
					$value = (!is_null($value))?$value: '';
					$this->imported_data_parsed_model->insert($imported_id, $key, $value);
				}
			}
			$this->crawler_list_model->updateStatus($data->id, 'finished');
			return true;
		}

		$this->crawler_list_model->updateStatus($data->id, 'new');
		return false;
	}

	private function arrayToCsv( array &$fields, $delimiter = ',', $enclosure = '"', $encloseAll = false, $nullToMysqlNull = false ) {
	    $delimiter_esc = preg_quote($delimiter, '/');
	    $enclosure_esc = preg_quote($enclosure, '/');

	    $output = array();
	    foreach ( $fields as $field ) {
	        if ($field === null && $nullToMysqlNull) {
	            $output[] = 'NULL';
	            continue;
	        }

	        // Enclose fields containing $delimiter, $enclosure or whitespace
	        if ( $encloseAll || preg_match( "/(?:${delimiter_esc}|${enclosure_esc}|\s)/", $field ) ) {
	            $output[] = $enclosure . str_replace($enclosure, $enclosure . $enclosure, $field) . $enclosure;
	        }
	        else {
	            $output[] = $field;
	        }
	    }

	    return implode( $delimiter, $output );
	}

	function crawl_all() {
		$this->load->model('imported_data_model');
		$this->load->model('imported_data_parsed_model');
		$this->load->model('crawler_list_model');
		$this->load->model('crawler_list_prices_model');
		$this->load->library('PageProcessor');

		if ($this->input->post('id')) {
			$id = (int) str_replace('id_', '', $this->input->post('id'));
			$rows = $this->crawler_list_model->get($id);
		} else if ($this->input->post('ids')) {
			$rows = $this->crawler_list_model->getIds($this->input->post('ids'));
		} else {
			$rows = $this->crawler_list_model->getAll(1000, false);
		}

		foreach( $rows as $data) {
			$this->crawler_list_model->updateStatus($data->id, 'lock');

			if ($page_data = $this->pageprocessor->get_data($data->url)) {
				$page_data['URL'] = $data->url;
				// save data
				$page_data_without_price = $page_data;
				if (isset($page_data_without_price['Price'])) {
					unset($page_data_without_price['Price']);
					$this->crawler_list_prices_model->insert($data->id, $page_data['Price']);
				}
				$csv_row = $this->arrayToCsv($page_data_without_price);
				$key = $this->imported_data_model->_get_key($csv_row);

				$revision = 1;
				if ((!$this->imported_data_model->findByKey($key)) && ($data->imported_data_id == null)) {
					$imported_id = $this->imported_data_model->insert($csv_row, $data->category_id);
					$this->crawler_list_model->updateImportedDataId($data->id, $imported_id);
				} else if ($data->imported_data_id !== null) {
					$imported_id = $data->imported_data_id;
					$revision = $this->imported_data_parsed_model->getMaxRevision($imported_id);
					$revision++;
				}

				foreach($page_data_without_price as $key=>$value) {
					$value = (!is_null($value))?$value: '';
					$this->imported_data_parsed_model->insert($imported_id, $key, $value, $revision);
				}

				if (($attributes = $this->pageprocessor->attributes()) !== false) {
					$this->imported_data_parsed_model->insert($imported_id, 'parsed_attributes', serialize($attributes), $revision);
				}

				$this->crawler_list_model->updateStatus($data->id, 'finished');
				$this->crawler_list_model->updated($data->id);
			} else {
				$this->crawler_list_model->updateStatus($data->id, 'new');
			}
		}


	}
}
