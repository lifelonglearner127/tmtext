<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Page_Test extends MY_Controller {

	var $a = array();
	var $ac = array();
	var $access = array(
		'index' => false
	);

	function __construct()
 	{
  		parent::__construct();

		$this->load->library('controllerlist');

		$this->ion_auth->add_auth_rules(array(
  			'index' => true,
  		));

  		$this->output->enable_profiler(TRUE);

 	}

 	public function index()
	{
		$this->load->library('PageProcessor');
		$url = 'http://www.sears.com/panasonic-55inch-class-1080p-600hz-viera-reg-3d-plasma/p-05771535000P?prdNo=2';

		var_dump($this->pageprocessor->get_data($url));
		var_dump($this->pageprocessor->attributes());

	}
}