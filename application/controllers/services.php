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

    function get_data_from_url_get()
    {
    	$url = urldecode($this->get('url'));

		$this->load->library('PageProcessor');
		$data = $this->pageprocessor->get_data($url);

		$this->response($data);
    }

    function get_data_from_text_post()
    {
    	$text = $this->post('text');

		$this->load->library('PageProcessor');
		$this->pageprocessor->loadHtml($text);
		$data = $this->pageprocessor->process();

		$this->response($data);
    }


}
