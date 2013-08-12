<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Brand extends MY_Controller {

    function __construct()
    {
        parent::__construct();

        $this->load->library('form_validation');
        $this->load->library('helpers');
        $this->data['title'] = 'Brand';

        if (!$this->ion_auth->logged_in())
        {
            //redirect them to the login page
            redirect('auth/login', 'refresh');
        }
    }

    public function index()
    {
        $this->data['customer_list'] = $this->getCustomersByUserId();
        $this->data['brands_list'] = $this->brands_list();
        $this->render();
    }

    public function getCustomersByUserId(){
        $this->load->model('customers_model');
        $this->load->model('users_to_customers_model');

        $customers = $this->users_to_customers_model->getByUserId($this->ion_auth->get_user_id());
        if(!$this->ion_auth->is_admin($this->ion_auth->get_user_id())){
            if(count($customers) == 0){
                $customer_list = array();
            }else{
                $customer_list = array(''=>'Select Site');
            }
            foreach($customers as $customer){
                array_push($customer_list, $customer->name);
            }
        }else{
            if(count($customers) == 0){
                $customers = $this->customers_model->getAll();
            }
            $customer_list = array(''=>'Select Site');
            foreach($customers as $customer){
                array_push($customer_list, $customer->name);
            }
        }
        return $customer_list;

    }

    public function brands_list()
    {
        $this->load->model('brands_model');
        $brands = $this->brands_model->getAll();
        $brands_list = array(''=>'Clorox');
        foreach($brands as $brand){
            array_push($brands_list, $brand->name);
        }
        return $brands_list;
    }
}
