<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Home extends MY_Controller {

	public $exceptions = array();

	function __construct()
 	{
  		parent::__construct();

		$this->data['title'] = 'Home';

		$this->ion_auth->add_auth_rules(array(
  			'index' => true,
  			'phpinfo' => true,
  		));
 	}

	public function index()
	{
		$this->render('home');
	}
	
	public function phpinfo()
	{
		phpinfo();
	}
}
