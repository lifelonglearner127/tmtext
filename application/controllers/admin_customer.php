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
//		var_dump($this->user_settings);

		$this->data['user_settings'] = $this->user_settings;

		$this->render();
	}

	public function save() {

	}
}