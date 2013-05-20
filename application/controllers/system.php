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

		$_rows = array(); $i = 0;

		// Find all unique lines in files
		foreach(explode("\n",trim($this->system_settings['csv_directories'])) as $_path) {
			if ($path = realpath($_path)) {
				$objects = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path), RecursiveIteratorIterator::SELF_FIRST);
				foreach ($objects as $name => $object){
					if ($object->isFile()) {
						$path_parts = pathinfo($object->getFilename());
						if ( in_array($path_parts['extension'], array('csv')) ) {
							if (($handle = fopen($name, "r")) !== FALSE) {
								while (($row = fgets($handle)) !== false) {
									$key = $this->imported_data_model->_get_key($row); $i++;
									if (!array_key_exists($key, $_rows)) {
										$_rows[$key] = $row;
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
			foreach ($_rows as $key=>$row) {
				if (!$this->imported_data_model->findByKey($key)) {
					$this->imported_data_model->insert($row);
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