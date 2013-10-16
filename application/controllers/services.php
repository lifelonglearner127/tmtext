<?php
require(APPPATH.'libraries/REST_Controller.php');

class Services extends REST_Controller {

	public function __construct() {
        parent::__construct();
        $this->load->library(array('session','ion_auth'));
        $this->load->helper(array('url'));

		$this->ion_auth->add_auth_rules(array(
			'get_data_from_url' => true,
			'get_data_from_text' => true,
			'get_new_urls' => true,
			'get_queued_urls' => true,
			'save_parsed_from_text' => true,
			'url_load_failed' => true
  		));
	}

    function get_data_from_url_get()
    {
    	$url = urldecode($this->get('url'));

		$this->load->library('PageProcessor');
		$data = $this->pageprocessor->get_data($url);

		$this->response($data);
    }

    function get_data_from_text_post()
    {
    	$text = $this->post('text', false);
    	$url = $this->post('url', false);

    	$this->load->library('PageProcessor');
		$this->pageprocessor->loadHtml($text, $url);
		$data = $this->pageprocessor->process();

		$this->response($data);
    }

    function get_new_urls_get()
    {
    	$this->load->model('crawler_list_model');

    	$limit = $this->get('limit');
    	$block = $this->get('block');
		$rows = $this->crawler_list_model->getAllNew($limit, false);

		if ($block) {
			foreach( $rows as $data) {
				$this->crawler_list_model->updateStatus($data->id, 'lock');
			}
		}

		$this->response($rows);
    }

    function get_queued_urls_get()
    {
    	$this->load->model('crawler_list_model');

    	$limit = $this->get('limit');
    	$block = $this->get('block');
		$rows = $this->crawler_list_model->getAllQueued($limit, false);

		if ($block) {
			foreach( $rows as $data) {
				$this->crawler_list_model->updateStatus($data->id, 'lock');
			}
		}

		$this->response($rows);
    }

    function save_parsed_from_text_post()
    {
    	$text = $this->post('text', false);
    	$url = $this->post('url', false);
    	$id = $this->post('id');
    	$imported_data_id  = $this->post('imported_data_id');
    	$category_id  = $this->post('category_id');
    	$info = $this->post('info');

    	$this->load->model('imported_data_model');
		$this->load->model('imported_data_parsed_model');
		$this->load->model('imported_data_parsed_archived_model');
		$this->load->model('crawler_list_model');
		$this->load->model('crawler_list_prices_model');
    	$this->load->library('PageProcessor');

    	$this->pageprocessor->loadHtml($text, $url);
		$this->pageprocessor->setLoadTime($info);

		if ($page_data = $this->pageprocessor->process()) {
			$page_data['URL'] = $url;
			// save data
			$page_data_without_price = $page_data;
			if (isset($page_data_without_price['Price'])) {
				unset($page_data_without_price['Price']);
				$this->crawler_list_prices_model->insert($id, $page_data['Price']);
			}
			$csv_row = $this->arrayToCsv($page_data_without_price);
			$key = $this->imported_data_model->_get_key($csv_row);

			$revision = 1;
			if ((!$this->imported_data_model->findByKey($key)) && ($imported_data_id == null)) {
				$imported_id = $this->imported_data_model->insert($csv_row, $category_id);
				$this->crawler_list_model->updateImportedDataId($id, $imported_id);
			} else if ($imported_data_id !== null) {
				$imported_id = $imported_data_id;
				$revision = $this->imported_data_parsed_model->getMaxRevision($imported_id);
				$revision++;
			}

			$model = null;
			if (($attributes = $this->pageprocessor->attributes()) !== false) {
				if (isset($attributes['model'])) {
					$model = $attributes['model'];
				}
				$this->imported_data_parsed_model->insert($imported_id, 'parsed_attributes', serialize($attributes), $revision, $model);
			}

			foreach($page_data_without_price as $key=>$value) {
				$value = (!is_null($value))?$value: '';
				$this->imported_data_parsed_model->insert($imported_id, $key, $value, $revision, $model);
			}

			if (($meta = $this->pageprocessor->meta()) !== false) {
				$this->imported_data_parsed_model->insert($imported_id, 'parsed_meta', serialize($meta), $revision);
			}

			if ($revision!==1) {
				if($this->imported_data_parsed_archived_model->saveToArchive($imported_id,$revision)) {
					$this->imported_data_parsed_model->deleteRows($imported_id,$revision);
				}
			}

			$this->crawler_list_model->updateStatus($id, 'finished');
			$this->crawler_list_model->updated($id);
			$this->response($imported_id);
		} else {
			$this->crawler_list_model->updateStatus($id, 'failed');
		}

		$this->response(false);
    }

    function url_load_failed_post()
    {
    	$id = $this->post('id');

    	$this->load->model('crawler_list_model');
    	$this->crawler_list_model->updateStatus($id, 'failed');
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
