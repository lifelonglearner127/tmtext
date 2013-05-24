<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class System extends MY_Controller {

	function __construct()
 	{
  		parent::__construct();

		$this->data['title'] = 'System Settings';

		$this->load->library('form_validation');

 	}

	public function index()
	{
		$this->data['message'] = $this->session->flashdata('message');

		$this->render();
	}

	public function system_accounts()
	{
		$this->render();
	}

	public function system_roles()
	{
		$this->render();
	}

	public function system_users()
	{
		$this->load->model('user_groups_model');
		$this->data['user_groups'] = $this->user_groups_model->getAll();
		$this->render();
	}

	public function save()
	{
		$this->form_validation->set_rules('settings[site_name]', 'Site name', 'required|xss_clean');
		$this->form_validation->set_rules('settings[company_name]', 'Company name', 'required|xss_clean');
		$this->form_validation->set_rules('settings[csv_directories]', 'CSV Directories', 'required|xss_clean');
		$this->form_validation->set_rules('settings[tag_rules_dir]', 'tagRules', 'required|xss_clean'); // Shulgin I.L.
		$this->form_validation->set_rules('settings[python_cmd]', 'Python script', 'required|xss_clean');
		$this->form_validation->set_rules('settings[java_cmd]', 'Java tools', 'required|xss_clean');
		$this->form_validation->set_rules('settings[python_input]', 'Python input', 'required|xss_clean');
		$this->form_validation->set_rules('settings[java_input]', 'Java input', 'required|xss_clean');
		$this->form_validation->set_rules('settings[title_length]', 'Default Title', 'required|integer|xss_clean');
		$this->form_validation->set_rules('settings[description_length]', 'Description Length', 'required|integer|xss_clean');

		if ($this->form_validation->run() === true) {
			$settings = $this->input->post('settings');
			// Process checkboxes
			$settings['use_files'] = (isset($settings['use_files'])?true:false);
			$settings['use_database'] = (isset($settings['use_database'])?true:false);

			$settings['java_generator'] = (isset($settings['java_generator'])?true:false);
			$settings['python_generator'] = (isset($settings['python_generator'])?true:false);

			$this->settings_model->db->trans_start();
			foreach ($settings as $key=>$value) {
				if (!$this->settings_model->update_system_value($key,$value)) {
					$this->settings_model->create_system($key, $value, $key);
				}
			}
			$this->settings_model->db->trans_complete();
		} else {
			$this->session->set_flashdata('message', (validation_errors()) ? validation_errors() : $this->session->flashdata('message'));

		}
		redirect('system/index?ajax=true');
	}

	public function csv_import() {
		$this->load->model('imported_data_model');
		$this->load->model('imported_data_parsed_model');
		$this->load->model('category_model');

		$_rows = array(); $i = 0;

		$header_replace = $this->config->item('csv_header_replace');
		// Find all unique lines in files
		foreach(explode("\n",trim($this->system_settings['csv_directories'])) as $_path) {
			if ($path = realpath($_path)) {
				$objects = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path), RecursiveIteratorIterator::SELF_FIRST);
				foreach ($objects as $name => $object){
					if ($object->isFile()) {
						$path_parts = pathinfo($object->getFilename());
						if ( in_array($path_parts['extension'], array('csv')) ) {

							// Parse company name
							/*
							  	categoryname.csv 								([^_\-]*)
								categoryname_20130521.csv 						([^_\-]*)_(\d*)
								sitename_xxxxxx_categoryname.csv 				([^_\-]*)_([^_\-]*)_([^_\-0-9]*)
								sitename_xxxxxx_categoryname_20130521.csv 		([^_\-]*)_([^_\-]*)_([^_\-]*)_(\d*)
								sitename_categoryname.csv						([^_\-]*)_([^_\-0-9]*)
								sitename_categoryname_20130521.csv				([^_\-]*)_([^_\-]*)_(\d*)
								sitename - categoryname -xxxxxx.csv				([^_\-\s]*)\s*-\s*([^_\-\s]*)\s*-\s*([^_\-\s]*)
								sitename - categoryname -xxxxxx-20130521.csv 	([^_\-\s]*)\s*-\s*([^_\-\s]*)\s*-\s*([^_\-\s]*)\s*-\s*(\d*)
							*/
							$category =''; $header = array();
							if ( preg_match('/^([^_\-]*)$/', $path_parts['filename'], $matches) && isset($matches[0][0]) ) {
								$category = $matches[1];
							} else
							if (preg_match('/^([^_\-]*)_(\d*)$/', $path_parts['filename'], $matches)) {
								$category = $matches[1];
							} else if (preg_match('/^([^_\-]*)_([^_\-]*)_([^_\-0-9]*)$/', $path_parts['filename'], $matches)) {
								$category = $matches[3];
							} else if (preg_match('/^([^_\-]*)_([^_\-]*)_([^_\-]*)_(\d*)$/', $path_parts['filename'], $matches)) {
								$category = $matches[3];
							} else if (preg_match('/^([^_\-]*)_([^_\-0-9]*)$/', $path_parts['filename'], $matches)) {
								$category = $matches[2];
							} else if (preg_match('/^([^_\-]*)_([^_\-]*)_(\d*)$/', $path_parts['filename'], $matches)) {
								$category = $matches[2];
							} else if (preg_match('/^([^_\-\s]*)\s*-\s*([^_\-\s]*)\s*-\s*([^_\-]*)$/', $path_parts['filename'], $matches)) {
								$category = $matches[2];
							} else if (preg_match('/^([^_\-\s]*)\s*-\s*([^_\-\s]*)\s*-\s*([^_\-\s]*)\s*-\s*(\d*)$/', $path_parts['filename'], $matches)) {
								$category = $matches[2];
							}

							if (($handle = fopen($name, "r")) !== FALSE) {
								$first_line = true;
								while (($parsed = fgetcsv($handle, 2000, ",", "\"")) !== false) {
									$continue = false;
									// first line is a header?
									if ($first_line) {
										$first_line = false;

										foreach($parsed as &$col) {
											if ( in_array(strtolower($col),array('url','product name', 'description')) ) {
												$continue = true;
											}
											if (isset($header_replace[$col])) {
												$col = $header_replace[$col];
											}
										}

									}
									if ($continue) {
										$header = $parsed;
										continue;
									}

									$parsed_tmp = $parsed;
									foreach($parsed_tmp as &$col) {
										$col = '"'.str_replace('"','\"', $col).'"';
									}
									$row = implode(',',$parsed_tmp);

									$key = $this->imported_data_model->_get_key($row); $i++;
									if (!array_key_exists($key, $_rows)) {
										$_rows[$key] = array(
											'row'=>$row,
											'category' => $category
										);
										// add parsed data
										if (!empty($header)) {
											foreach( $header as $i=>$h ){
												if (!empty($h)) {
													$_rows[$key]['parsed'][$h] = $parsed[$i];
												}
											}
										}

									}
								}
							}
							fclose($handle);
						}
					}
				}
			}
		}

		$imported_rows = 0;
		// Compare all rows with database rows
		if (!empty($_rows)) {
			$this->imported_data_model->db->trans_start();
			foreach ($_rows as $key=>$arr) {
				if (!$this->imported_data_model->findByKey($key)) {
					if (!empty($arr['category'])) {
						if ( ($category_id = $this->category_model->getIdByName($arr['category'])) == false ) {
							$category_id  = $this->category_model->insert($arr['category']);
						}
						$imported_id = $this->imported_data_model->insert($arr['row'], $category_id);
					} else {
						$imported_id = $this->imported_data_model->insert($arr['row']);
					}

					if (isset($arr['parsed'])) {
						foreach($arr['parsed'] as $key=>$value) {
							$this->imported_data_parsed_model->insert($imported_id, $key, $value);
						}
					}
					$imported_rows++;
				}
			}
			$this->imported_data_model->db->trans_complete();
		}

		echo json_encode(array(
			'message' => 'Imported '.$imported_rows.' rows. Total '.count($_rows).' rows.'
		));
	}
}