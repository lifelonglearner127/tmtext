<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Editor extends MY_Controller {

	public $exceptions = array();

	function __construct()
 	{
  		parent::__construct();

  		$this->load->library('form_validation');
		$this->data['title'] = 'Editor';

		$this->exceptions[] = array(
			'attribute_name' => 'MANU',
			'attribute_value' => 'Samsung',
			'exception_values' => array(
				'Viewsonic',  'Sony', 'Dell'
			)
		);
		$this->exceptions[] = array(
			'attribute_name' => 'RESOLUTION',
			'attribute_value' => '1080p',
			'exception_values' => array(
				'720p',  '1280p'
			)
		);

 	}

	public function index()
	{
		$this->render();
	}

	public function save()
	{
		$this->load->model('searches_model');
		$this->load->model('saved_description_model');

		$this->ion_auth->get_user_id();

		$this->form_validation->set_rules('attribs', 'Atributes', 'required|xss_clean');
		$this->form_validation->set_rules('search', 'Search', 'required|alpha_dash|xss_clean');
		$this->form_validation->set_rules('current', 'Current description', 'required|integer');
		$this->form_validation->set_rules('title', 'Title', 'required|xss_clean');
		$this->form_validation->set_rules('description', 'Description', 'required|xss_clean');
		$this->form_validation->set_rules('search_id', 'Old search id', 'integer');
		$this->form_validation->set_rules('parent_id', 'Old id', 'integer');
		$this->form_validation->set_rules('revision', 'Revision', 'integer');

		if ($this->form_validation->run() === true) {
			if (!($search_id = $this->input->post('search_id'))) {
				$search_id = $this->searches_model->insert($this->input->post('search'), serialize($this->input->post('attribs')));
			}
			if (!($parent_id = $this->input->post('parent_id'))) {
				$parent_id = 0;
			}
			if (!($revision = $this->input->post('revision'))) {
				$revision = 1;
			}

			$data['saved_description_id'] = $this->saved_description_model->insert($this->input->post('title'), $this->input->post('description'), $revision,  $search_id, $parent_id);

			if ($parent_id == 0) {
				$parent_id = $data['saved_description_id'];
			}
			$data['parent_id'] = $parent_id;
			$data['search_id'] = $search_id;
			$data['revision'] = $revision;
		} else {
			$data['message'] = (validation_errors() ? validation_errors() : $this->session->flashdata('message'));
		}


		$this->output->set_content_type('application/json')
    			->set_output(json_encode($data));

	}

	public function searchmeasure() {

		$s = $this->input->post('s');

		$data = array(
			's' => $s,
			'search_results' => array()
		);

		$attr_path = $this->config->item('attr_path');

		$csv_rows = array();

		// Search in files
		if ( isset($this->settings['use_files']) && $this->settings['use_files']) {
			if ($path = realpath($attr_path)) {
				$objects = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path), RecursiveIteratorIterator::SELF_FIRST);
				foreach($objects as $name => $object){
					if (!$object->isDir()) {
						if (preg_match("/.*\.csv/i",$object->getFilename(),$matches)) {
							$_rows = array();
							if (($handle = fopen($name, "r")) !== FALSE) {
								while (($row = fgets($handle)) !== false) {
									if (preg_match("/$s/i",$row,$matches)) {
										$_rows[] = $row;
									}
								}
							}
							fclose($handle);

							foreach (array_keys(array_count_values($_rows)) as $row){
								$csv_rows[] = str_getcsv($row, ",", "\"");
							}
							unset($_rows);
						}
					}
				}
			}
		}

		// Search in database
		if ( isset($this->settings['use_database']) && $this->settings['use_database']) {
			$this->load->model('imported_data_model');
			if (( $_rows = $this->imported_data_model->findByData($s))!== false) {
				foreach($_rows as $row) {
					$csv_rows[] = str_getcsv($row['data'], ",", "\"");
				}
			}
		}

		if (!empty($csv_rows)) {
			$row = $csv_rows[0];
			foreach ($row as $col) {
				if (preg_match("/^http:\/\/*/i",$col,$matches)) {
					$row['url'] = $col;
				} else if ( mb_strlen($col) <= 250) {
					$row['title'] = $col;
				} else if (empty($row['description'])) {
					$row['description'] = $col;
				}
			}

			if (!empty($row['url']) && !empty($row['title'])) {
				$data['search_results'][] =  '<a id="link_m_title" href="'.$row['url'].'">'.$row['title'].'</a><br/>'.$row['description'];
			} else if (!empty($row['description'])) {
				$data['search_results'][] =  $row['description'];
			}
		}

		$this->load->view('editor/searchmeasure', $data);
	}

	public function searchmeasuredb() {
		$s = $this->input->post('s');
		$sl = $this->input->post('sl');

		$data = array(
			'search_flag' => '',
			'search_results' => array()
		);

		$this->load->model('imported_data_parsed_model');
		$files_data_flag = false;
		$data_import = $this->imported_data_parsed_model->getByValueLikeGroup($s, $sl);
		if($data_import !== false) { // ---- DB DATA
			if(count($data_import) > 0) {
				$res = array('product_name' => '', 'short_desc' => '', 'long_desc' => '', 'url' => '');
				foreach ($data_import as $k => $v) {
					if(isset($v['key']) && isset($v['value'])) {
						switch ($v['key']) {
							case 'Description':
								// $res['short_desc'] = $v['value'];
								// $res['short_desc'] = preg_replace('/[^A-Za-z0-9\-]\"\./', ' ', $v['value']);
								$res['short_desc'] = str_replace(array(';'), array(','), $v['value']);
								break;
							case 'Long_Description':
								// $res['long_desc'] = $v['value'];
								// $res['long_desc'] = preg_replace('/[^A-Za-z0-9\-]\"\./', ' ', $v['value']);
								$res['long_desc'] = str_replace(array(';'), array(','), $v['value']); 
								break;
							case 'Product Name':
								$res['product_name'] = $v['value'];
								break;
							case 'URL':
								$res['url'] = $v['value'];
								break;
						}
					}
				}
				$data['search_results'] = $res;
				$data['search_flag'] = 'db';
			}
		}

		$this->load->view('editor/searchmeasure', $data);
	}

	public function refreshheader() {
		$title_dyn = $this->input->post('t');

		$data = array(
			'title_dyn' =>  $title_dyn
		);

		$this->load->view('editor/refreshheader', $data);
	}

	public function search()
	{
		$this->form_validation->set_rules('s', 'Search', 'required|alpha_dash|xss_clean');
		if ($this->form_validation->run() == true) {

			$s = $this->input->post('s');

			$this->load->library('pagination');
			$pagination_config['base_url'] = $this->config->site_url().'/editor/search';
			$pagination_config['per_page'] = 0;

			$data = array(
				's' => $s,
				'search_results' => array()
			);

			$attr_path = $this->config->item('attr_path');

			$csv_rows = array();

			// Search in files
			if ( isset($this->settings['use_files']) && $this->settings['use_files']) {
				if ($path = realpath($attr_path)) {
					$objects = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path), RecursiveIteratorIterator::SELF_FIRST);
					foreach($objects as $name => $object){
						if (!$object->isDir()) {
							if (preg_match("/.*\.csv/i",$object->getFilename(),$matches)) {
								$_rows = array();
								if (($handle = fopen($name, "r")) !== FALSE) {
									while (($row = fgets($handle, 1000)) !== false) {
										if (preg_match("/$s/i",$row,$matches)) {
											$_rows[] = $row;
										}
									}
								}
								fclose($handle);

								foreach (array_keys(array_count_values($_rows)) as $row){
									$csv_rows[] = str_getcsv($row, ",", "\"");
								}
								unset($_rows);
							}
						}
					}
				}
			}

			// Search in database
			if ( isset($this->settings['use_database']) && $this->settings['use_database']) {
				$this->load->model('imported_data_model');
				if (( $_rows = $this->imported_data_model->findByData($s))!== false) {
					foreach($_rows as $row) {
						$csv_rows[] = str_getcsv($row['data'], ",", "\"");
					}
				}
			}

			if (!empty($csv_rows)) {
				$current_row = 0;
				foreach($csv_rows as $row) {
					if ($current_row < (int)$this->uri->segment(3)) {
						$current_row++;
						continue;
					}
					foreach ($row as $col) {
						if (preg_match("/^http:\/\/*/i",$col,$matches)) {
							$row['url'] = $col;
						} else if ( mb_strlen($col) <= 250) {
							$row['title'] = $col;
						} else if (empty($row['description'])){
							$row['description'] = substr($col, 0, strpos(wordwrap($col, 200), "\n"));

						}
					}

					if (!empty($row['url']) && !empty($row['title'])) {
						$data['search_results'][] =  '<a href="'.$row['url'].'">'.$row['title'].'</a><br/>'.$row['description'];
					} else if (!empty($row['description'])) {
						$data['search_results'][] =  $row['description'];
					}
					if (count($data['search_results']) == $pagination_config['per_page']) break;
				}
			}

			$pagination_config['total_rows'] = count($csv_rows);
			$this->pagination->initialize($pagination_config);
			$data['pagination']= $this->pagination->create_links();

			$this->load->view('editor/search',$data);
		}
	}

	public function attributes()
	{
		$data['product_descriptions'] = array();

		$this->form_validation->set_rules('s', 'Search', 'required|alpha_dash|xss_clean');

		if ($this->form_validation->run() == true) {
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
												$title[] = $attributes[strtoupper($v)	];
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

	public function validate(){
		$this->form_validation->set_rules('description', 'Description', 'required|xss_clean');

		$output = array();

		if ($this->form_validation->run() == true) {
			$description = str_replace("'","'\''",$this->input->post('description'));

			$this->load->library('hunspell');
			$this->hunspell->check($description);

			$a = $this->hunspell->get();
			$output['spellcheck'] = $a;

    		$descCmd = str_replace($this->config->item('cmd_mask'), $description ,$this->config->item('tsv_cmd'));
			if ($result = shell_exec($descCmd)) {
				$output['attributes'] = json_decode(json_encode(simplexml_load_string($result)),1);
				if (isset($output['attributes']['description']['attributes']['attribute'])) {
					foreach($output['attributes']['description']['attributes']['attribute'] as &$attrib) {
						$a = $attrib['@attributes']['value'];
						$attrib['@attributes']['value'] = array();
						$attrib['@attributes']['value'][] = $a;
                        if (array_key_exists($a, $output['spellcheck'])) {
                            unset($output['spellcheck'][$a]);
                        }
						foreach ($this->config->item('attr_replace_validate') as $replacement) {
							if ( str_replace(array_keys($replacement), array_values($replacement), $a) != $a ) {
                                if (array_key_exists($a, $output['spellcheck'])) {
                                    unset($output['spellcheck'][$a]);
                                }
								$attrib['@attributes']['value'][] = str_replace(array_keys($replacement), array_values($replacement), $a);
							}
						}
					}
				}
			}
		}

		$this->output->set_content_type('application/json')
    			->set_output(json_encode($output));
	}
}
