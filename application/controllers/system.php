<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class System extends MY_Controller {

	function __construct()
 	{
  		parent::__construct();

		$this->data['title'] = 'System Settings';

		$this->load->library('form_validation');

		if ($generators = $this->session->userdata('generators')) {
			$this->config->set_item('generators',$generators);
		}

 		if (!$this->ion_auth->logged_in())
		{
			//redirect them to the login page
			redirect('auth/login', 'refresh');
		}
 	}

	public function index()
	{
		$this->render();
	}

	public function save()
	{
		$this->load->model('settings_model');

		$this->form_validation->set_rules('settings[site_name]', 'Site name', 'required|xss_clean');
		$this->form_validation->set_rules('settings[company_name]', 'Company name', 'required|xss_clean');
		$this->form_validation->set_rules('settings[tag_rules_dir]', 'tagRules', 'required|xss_clean'); // Shulgin I.L.

		if ($this->form_validation->run() === true) {
			$generators = $this->config->item('generators');
			foreach($generators as &$generator) {
				$generator[2] = (bool) $this->input->post($generator[1]);

			}

			$this->session->set_userdata('generators', $generators);
			die(var_dump($this->input->post('settings')));

			foreach ($this->input->post('settings') as $key=>$value) {
				if (!$this->settings_model->update_system_value($key,$value)) {
					$this->settings_model->create_system($key, $value, $key);
				}
			}

		}
		redirect('system/index?ajax=true');
	}
}