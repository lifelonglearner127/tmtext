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
            //'upload_dir' => $this->config->item('csv_upload_dir'),
            'param_name' => 'files',
            'delete_type' => 'POST',
            'accept_file_types' => '/.+\.txt$/i',
            ));
        
        if(!$this->ion_auth->is_admin($this->ion_auth->get_user_id())){
            $this->load->model('users_to_customers_model');
            $id = $this->users_to_customers_model->getByUserId($this->ion_auth->get_user_id());
            $customer_id = $id[0]->customer_id;
        }else{
            $this->load->model('customers_model');
            $this->input->post('customerName');
            if($this->input->post('customerName')!=='Select Customer'){
                $customer_id = $this->customers_model->getIdByName($this->input->post('customerName'));
            }else{
                exit;
            }
        }
        
        $txtcontent = file_get_contents(base_url().'webroot/uploads/'.$_FILES['files']['name'][0]);
        $this->load->model('style_guide_model');
        if(empty($customer_id) || $customer_id==null || $customer_id==''){
            $response = array(
              'error' => 'There are no customers'   
            );
            $this->output->set_content_type('application/json')
                ->set_output(json_encode($response));
        }else{
            $this->style_guide_model->insertStyle($txtcontent, $customer_id);
        }
    }
    
    public function getStyleByCustomer()
    {
        
        $this->load->model('customers_model');
        $this->load->model('style_guide_model');
        if(!$this->ion_auth->is_admin($this->ion_auth->get_user_id())){
            $this->load->model('users_to_customers_model');
            $id = $this->users_to_customers_model->getByUserId($this->ion_auth->get_user_id());
            $customer_id = $id[0]->customer_id;
        }else{
            $customer_id = $this->customers_model->getIdByName($this->input->post('customer_name'));
        }
        
        $style = $this->style_guide_model->getStyleByCustomerId($customer_id);
        
        $this->output->set_content_type('application/json')
            ->set_output(json_encode($style[0]->style));
    }
    public function saveTheStyle()
    {
        $this->load->model('style_guide_model');
        $this->load->model('customers_model');
        
        $txtcontent = $this->input->post('txtcontent');
        $customerName = $this->input->post('customerName');
        $customer_id = $this->customers_model->getIdByName($customerName);
        
        if(!$this->ion_auth->is_admin($this->ion_auth->get_user_id())){
            $this->load->model('users_to_customers_model');
            $id = $this->users_to_customers_model->getByUserId($this->ion_auth->get_user_id());
            $customer_id = $id[0]->customer_id;
            
            if($customer_id == null){ 
                $this->output->set_content_type('application/json')
                ->set_output(json_encode('There are no customers'));
            }else{
                $this->style_guide_model->insertStyle($txtcontent, $customer_id);
                $this->output->set_content_type('application/json')
                ->set_output(json_encode('The style guide has been saved.'));
            }
            
        }else{
            $this->style_guide_model->insertStyle($txtcontent, $customer_id);
             $this->output->set_content_type('application/json')
            ->set_output(json_encode('The style guide has been saved.'));
        }
       
        
    }
}
