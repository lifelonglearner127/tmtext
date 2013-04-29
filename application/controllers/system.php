<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class System extends MY_Controller {

	function __construct()
 	{
  		parent::__construct();

		$this->data['title'] = 'System Setting';

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
		if ($this->input->server('REQUEST_METHOD') === 'POST')
		{
			$generators = $this->config->item('generators');
			foreach($generators as &$generator) {
				$generator[2] = (bool) $this->input->post($generator[1]);

			}

			$this->session->set_userdata('generators', $generators);
			//$this->config->set_item('generators', $generators);
		}
		redirect('system/index', 'refresh');
	}
}