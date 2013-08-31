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
    
    public function import() {
        $this->load->model('brand_types_model');
        $brand_types = $this->brand_types_model->getAll();
        $this->data['brand_types'] = $brand_types;
        
        $this->render();
    }
    
    public function csv_upload() {
        $this->load->library('UploadHandler');

        $first_key = key($_FILES);
        $this->output->set_content_type('application/json');
        $this->uploadhandler->upload(array(
            'script_url' => site_url('brand/csv_upload'),
            'param_name' => $first_key,
            'delete_type' => 'POST',
            'accept_file_types' => '/.+\.csv$/i',
        ));
    }
    
    public function csv_import() {
        $this->load->helper('csv_helper');
        $this->load->model('brands_model');
        $this->load->model('company_model');
        $this->load->model('brand_data_model');
        $this->load->model('brand_data_summary_model');
        
        $brand_type = $this->input->post('brand_types', null);
        $brand_data_csv = $this->input->post('brand_data_csv', null);
        $company_data_csv = $this->input->post('company_data_csv', null);
        
        $brandHeader = array('Date', 'Brand', 'Tweets', 'Followers', 'YT_Videos', 'YT_Views');
        $companyHeader = array('IR500Rank', 'CompanyName', 'Twitter', 'Youtube', 'Brand');
        
        if($company_data_csv != null) {
            $data = csv_to_array($company_data_csv, $companyHeader, ';');
            
            if(!empty($data)) {
                $i = 1;
                foreach($data as $key=>$value) {
                    if($i > 1) { 
                        $params = $value['parsed'];

                        //Insert new company
                        $company_id = $this->company_model->insert($params['CompanyName'], '', '', $params['IR500Rank'], $params['Twitter'], $params['Youtube']);

                        //Update brands table set company_id=$company_id
                        $brand = $this->brands_model->getByName($params['Brand']);
                        if(!empty($brand) && $company_id) {
                            $this->brands_model->update($brand->id, $brand->name, $company_id, $brand->brand_type);
                        }
                    }
                    $i++;
                }
            }
        }
        
        if($brand_data_csv != null && $brand_type != null) {
            $data = csv_to_array($brand_data_csv, $brandHeader, ';');
            
            if(!empty($data)) {
                $i = 1;
                foreach($data as $key=>$value) {
                    if($i > 1) { 
                        $params = $value['parsed'];
                        
                        $brandName = $params['Brand'];
                        $date = date('Y-m-d', strtotime($params['Date']));
                        $tweets = $params['Tweets'];
                        $followers = $params['Followers'];
                        $youtube_videos = $params['YT_Videos'];
                        $youtube_views = $params['YT_Views'];
                        
                        $brand = $this->brands_model->getByName($brandName);
                        if(!empty($brand)) {
                            $this->brands_model->update($brand->id, $brand->name, $brand->company_id, $brand_type);
                            $this->brand_data_model->insert($brand->id, $date, $tweets, $followers, $youtube_videos, $youtube_views);
                            $this->brand_data_summary_model->updateByBrandId($brand->id, $tweets, $youtube_videos, $youtube_views);
                        }
                    }
                    $i++;
                }
            }
        }
        
        
    }
}
