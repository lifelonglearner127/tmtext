<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Customer extends MY_Controller {

	function __construct()
 	{
  		parent::__construct();

  		$this->load->library('form_validation');
                $this->load->library('helpers');
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
    public function style_guide()
    {
        if (!$this->ion_auth->is_editor($this->ion_auth->get_user_id())) {
            $this->data['title'] = 'Customer Settings';
            if($this->ion_auth->is_admin($this->ion_auth->get_user_id())){
                $this->data['customer_list'] = $this->getCustomersByUserId();
            }
            $this->render();
        }
    }
    
    public function getCustomersByUserId(){
        $this->load->model('customers_model');
        $this->load->model('users_to_customers_model');
        $customers = $this->users_to_customers_model->getByUserId($this->ion_auth->get_user_id());
        if(count($customers) == 0){
            $customers = $this->customers_model->getAll();
        }
        $customer_list = array(''=>'Select Customer');
        foreach($customers as $customer){
            array_push($customer_list, $customer->name);
        }

        return $customer_list;

    }
    public function upload_style()
    {
	$this->load->library('UploadHandler');

	$this->output->set_content_type('application/json');
	$this->uploadhandler->upload(array(
            'script_url' => site_url('customer/upload_style'),
            'upload_dir' => $this->config->item('style_upload_dir'),
            'param_name' => 'files',
            'delete_type' => 'POST',
            'accept_file_types' => '/.+\.txt$/i',
            ));
    }
}