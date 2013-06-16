<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Site_Crawler extends MY_Controller {

	function __construct()
 	{
  		parent::__construct();

		$this->data['title'] = 'Site Crawler';

 	}

	public function index()
	{
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
								$line = str_replace(array('"', "'","\r", "\n"), '', $line);
								if ($this->pageprocessor->isURL($line)) {
									$urls[] = $line;
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

		$this->crawler_list_model->db->trans_start();
		foreach($urls as $url) {
			$url = str_replace(array('"', "'","\r", "\n"), '', $url);
			if ($this->pageprocessor->isURL($url)) {
				if (!$this->crawler_list_model->getByUrl($url)) {
					$this->crawler_list_model->insert($url);
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

	function crawl_now() {
		$this->load->model('imported_data_model');
		$this->load->model('imported_data_parsed_model');
		$this->load->model('crawler_list_model');
		$this->load->library('PageProcessor');

		$rows = $this->crawler_list_model->getAllNew();
		foreach( $rows as $data) {
			$this->crawler_list_model->updateStatus($data->id, 'lock');

			if ($page_data = $this->pageprocessor->get_data($data->url)) {
				$page_data['URL'] = $data->url;
				// save data
				$csv_row = $this->arrayToCsv($page_data);
				$key = $this->imported_data_model->_get_key($csv_row);

				if (!$this->imported_data_model->findByKey($key)) {
					$imported_id = $this->imported_data_model->insert($csv_row);

					foreach($page_data as $key=>$value) {
						$value = (!is_null($value))?$value: '';
						$this->imported_data_parsed_model->insert($imported_id, $key, $value);
					}
				}
				$this->crawler_list_model->updateStatus($data->id, 'finished');
			} else {
				$this->crawler_list_model->updateStatus($data->id, 'new');
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
			$csv_row = $this->arrayToCsv($page_data);
			$key = $this->imported_data_model->_get_key($csv_row);

			if (!$this->imported_data_model->findByKey($key)) {
				$imported_id = $this->imported_data_model->insert($csv_row);

				foreach($page_data as $key=>$value) {
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
}
