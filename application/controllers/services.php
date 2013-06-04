<?php
require(APPPATH.'libraries/REST_Controller.php');

class Services extends REST_Controller {

	public function __construct() {
        parent::__construct();
        $this->load->library(array('session','ion_auth'));
        $this->load->helper(array('url'));

		$this->ion_auth->add_auth_rules(array(
  			'get_product_data' => true,
  		));
	}

    function get_product_data_get()
    {
    	$url = urldecode($this->get('url'));

		$this->load->library('PageProcessor');
		$data = $this->pageprocessor->get_data($url);

		$this->response($data);
    }

}
