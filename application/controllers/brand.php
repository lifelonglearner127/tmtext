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
        $brand_type = $this->input->post('brand_types', null);
        $brand_data_csv = $this->input->post('brand_data_csv', null);
        $company_data_csv = $this->input->post('company_data_csv', null);
        echo $brand_data_csv."\t".$company_data_csv."\t".$brand_type; exit;
        
//        if($company_data_csv != '' && file_exists(dirname($this->get_server_var('SCRIPT_FILENAME')).'/webroot/uploads/'.$company_data_csv)) {
//            if (($handle = fopen(dirname($this->get_server_var('SCRIPT_FILENAME')).'/webroot/uploads/'.$company_data_csv, "r")) !== FALSE) {
//                    $first_line = true;
//                    while (($parsed = fgetcsv($handle, 2000, ",", "\"")) !== false) {
//                            $continue = false;
//                            // first line is a header?
//                            if ($first_line) {
//                                    $first_line = false;
//
//                                    foreach($parsed as &$col) {
//                                            if ( in_array(strtolower($col),array('url','product name', 'description')) ) {
//                                                    $continue = true;
//                                            }
//                                            if (isset($header_replace[$col])) {
//                                                    $col = $header_replace[$col];
//                                            }
//                                    }
//
//                            }
//                            if ($continue) {
//                                    $header = $parsed;
//                                    continue;
//                            }
//
//                            $parsed_tmp = $parsed;
//                            foreach($parsed_tmp as &$col) {
//                                    $col = '"'.str_replace('"','\"', $col).'"';
//                            }
//                            $row = implode(',',$parsed_tmp);
//
//                            $key = $this->imported_data_model->_get_key($row); $i++;
//                            if (!array_key_exists($key, $_rows)) {
//                                    $_rows[$key] = array(
//                                            'row'=>$row,
//                                            'category' => $category
//                                    );
//                                    // add parsed data
//                                    if (!empty($header)) {
//                                            foreach( $header as $i=>$h ){
//                                                    if (!empty($h)) {
//                                                            $_rows[$key]['parsed'][$h] = $parsed[$i];
//                                                    }
//                                            }
//                                    }
//
//                            }
//                    }
//            }
//            fclose($handle);
//        }
    }
}
