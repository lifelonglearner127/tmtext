<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Admin_Customer extends MY_Controller {

	function __construct()
 	{
  		parent::__construct();

  		$this->load->library('form_validation');
		$this->data['title'] = 'Admin Customer Setting';

 	}

	public function index()
	{
		$this->data['message'] = $this->session->flashdata('message');
		$this->data['user_settings'] = $this->user_settings;

		$this->render();
	}

	public function save() {
		$this->form_validation->set_rules('user_settings[customer_name]', 'Customer name', 'required|xss_clean');
		$this->form_validation->set_rules('user_settings[csv_directories]', 'CSV Directories', 'required|xss_clean');
		$this->form_validation->set_rules('user_settings[title_length]', 'Default Title', 'required|integer|xss_clean');
		$this->form_validation->set_rules('user_settings[description_length]', 'Description Length', 'required|integer|xss_clean');

		if ($this->form_validation->run() === true) {
			$settings = $this->input->post('user_settings');

			$settings['use_files'] = (isset($settings['use_files'])?true:false);
			$settings['use_database'] = (isset($settings['use_database'])?true:false);

			$this->settings_model->db->trans_start();
			foreach ($settings as $key=>$value) {
				if (!$this->settings_model->update_value($this->ion_auth->get_user_id(), $key,$value)) {
					$this->settings_model->create($this->ion_auth->get_user_id(), $key, $value, $key);
				}
			}
			$this->settings_model->db->trans_complete();
		} else {
			$this->session->set_flashdata('message', (validation_errors()) ? validation_errors() : $this->session->flashdata('message'));

		}
		redirect('admin_customer/index?ajax=true');
	}
}