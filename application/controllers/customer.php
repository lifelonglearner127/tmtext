<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Customer extends MY_Controller {

	function __construct()
 	{
  		parent::__construct();

  		$this->load->library('form_validation');
		$this->data['title'] = 'Customer Settings';

 		if (!$this->ion_auth->logged_in())
		{
			//redirect them to the login page
			redirect('auth/login', 'refresh');
		}
 	}

	public function index()
	{
        $info = $this->ion_auth->get_user_data();
        $this->data['email'] = $info['email'];
        $this->data['identity'] = $info['identity'];
        $this->data['title'] = 'Customer Settings';
		$this->render();
	}

    public function product_description()
    {
        if (!$this->ion_auth->is_editor($this->ion_auth->get_user_id())) {
            $this->data['title'] = 'Customer Settings';
            $this->render();
        }
    }
}