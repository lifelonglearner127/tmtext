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
        $this->load->model('brand_types_model');
        $this->load->helper('functions_helper');
        
//        $this->data['customer_list'] = $this->getCustomersByUserId();
//        $this->data['brands_list'] = $this->brands_list();
        $this->data['brand_types'] = $this->brand_types_model->getAll();
        $this->data['days'] = get_days();
        $this->data['months'] = get_months();
        $this->data['years'] = get_years();
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
    
    public function addtype()
    {
        $this->load->model('brand_types_model');
        
        $brand_type = $this->input->post('brand_type', null);
        $output = array('value'=>'', 'name'=>$brand_type);
        $id = $this->brand_types_model->insert($brand_type);
        if($id) {
            $output['value'] = $id;
        }
        
        $this->output->set_content_type('application/json')
                ->set_output(json_encode($output));
    }
    
    public function rankings()
    {
        $this->load->model('brands_model');
        
        $brand_list = $this->brands_model->rankings();
        
        if (!empty($brand_list['total_rows'])) {
            $total_rows = $brand_list['total_rows'];
        } else {
            $total_rows = 0;
        }

        $output = array(
            "sEcho" => intval($_GET['sEcho']),
            "iTotalRecords" => $total_rows,
            "iTotalDisplayRecords" => $total_rows,
            "iDisplayLength" => $brand_list['display_length'],
            "aaData" => array()
        );

        if (!empty($brand_list['result'])) {
            foreach ($brand_list['result'] as $brand_list) {
                //$social_rank = 0.25 * $brand_list->tweets + 0.25 * $brand_list->followers + 0.25 * $brand_list->videos + 0.25 * $brand_list->views;
//                $parsed_attributes = unserialize($price->parsed_attributes);
//                $model = (!empty($parsed_attributes['model']) ? $parsed_attributes['model'] : $parsed_attributes['UPC/EAN/ISBN']);
                $output['aaData'][] = array(
                    number_format($brand_list->social_rank),
                    number_format($brand_list->IR500Rank),
                    $brand_list->name,
                    number_format($brand_list->tweets),
                    number_format($brand_list->total_tweets),
                    number_format($brand_list->followers),
                    number_format($brand_list->following),
                    number_format($brand_list->videos),
                    number_format($brand_list->views),
                    number_format($brand_list->total_youtube_views),
                    round($brand_list->views / $brand_list->videos, 2),
                    number_format($brand_list->total_youtube_videos),
                );
            }
        }

        $this->output->set_content_type('application/json')
                ->set_output(json_encode($output));
        
    }
    
    public function import() {
        $this->load->model('brand_types_model');
        $brand_types = $this->brand_types_model->getAll();
        $this->data['brand_types'] = $brand_types;
        
        $this->render();
    }
    
    public function csv_upload() {
        $this->load->library('UploadHandler');

        $this->output->set_content_type('application/json');
        $this->uploadhandler->upload(array(
            'script_url' => site_url('brand/csv_upload'),
            'upload_dir' => 'webroot/img/',
            'param_name' => 'files',
            'delete_type' => 'POST',
            'accept_file_types' => '/.+\.(csv|txt)$/i',
        ));
    }
    
    public function csv_import() {
        $this->load->helper('csv_helper');
        $this->load->model('brands_model');
        $this->load->model('company_model');
        $this->load->model('brand_data_model');
        $this->load->model('brand_data_summary_model');
        $this->load->model('brand_types_model');
        
        $brand_type_id = $this->input->post('brand_types', null);
        $brand_data_csv = $this->input->post('brand_data_csv', null);
        $company_data_csv = $this->input->post('company_data_csv', null);
        
        $brandHeader = array('IR500Rank', 'Brand', 'Twitter', 'Youtube');
        $companyHeader = array('Date', 'Brand', 'Followers', 'Following','Tweets','All_Tweets',
            'YT_Videos','YT_All_Videos','YT_Views','YT_All_Views');
        
        $brand_type = $this->brand_types_model->get($brand_type_id);
        if(empty($brand_type)) {
            return;
        }
        
        if($company_data_csv != null) {
            $data = csv_to_array($company_data_csv, $companyHeader, ',');
            if(!empty($data)) {
                $i = 1;
                foreach($data as $key=>$value) {
                    if($i > 1) { 
                        $params = $value['parsed'];
                        $brandName = $params['Brand'];
                        $date = date('Y-m-d', strtotime(str_replace('-', '/', $params['Date'])));
                        $tweets = ($params['Tweets'] == null)?0:(int)$params['Tweets'];
                        $total_tweets = ($params['All_Tweets'] == null)?0:(int)$params['All_Tweets'];
                        $followers = ($params['Followers'] == null)?0:(int)$params['Followers'];
                        $youtube_videos = ($params['YT_Videos'] == null)?0:(int)$params['YT_Videos'];
                        $total_youtube_videos = ($params['YT_All_Videos'] == null)?0:(int)$params['YT_All_Videos'];
                        $youtube_views = ($params['YT_Views'] == null)?0:(int)$params['YT_Views'];
                        $total_youtube_views = ($params['YT_All_Views'] == null)?0:(int)$params['YT_All_Views'];
                        $following = ($params['Following'] == null)?0:(int)$params['Following'];

                        $brand = $this->brands_model->getByName($brandName);
                        $brand_id = $brand->id;
                        $this->brand_data_model->insert($brand_id, $date, $tweets, $followers, $following, $youtube_videos, $youtube_views,
                            $total_tweets, $total_tweets, $total_youtube_videos, $total_youtube_views);
                        $this->brand_data_summary_model->updateByBrandId($brand_id, $total_tweets, $total_youtube_videos, $total_youtube_views);

                        //Insert new company
//                      $company_id = $this->brand_types_model->insert($params['CompanyName'], '', '', $params['IR500Rank'], $params['Twitter'], $params['Youtube']);
                    }
                    $i++;
                }
            }
        }
        
        if($brand_data_csv != null) {
            $data = csv_to_array($brand_data_csv, $brandHeader, ',');
            
            if(!empty($data)) {
                $i = 1;
                foreach($data as $key=>$value) {
                    if($i > 1) { 
                        $params = $value['parsed'];
                        $brandName = $params['Brand'];
                        $brand = $this->brands_model->getByName($brandName);
                        if(!empty($brand)) {
                            $this->brands_model->update($brand->id, $brand->name, $brand->company_id, $brand_type->id, $brand->created);
                            $brand_id = $brand->id;
                        } else {
                            $brand_id = $this->brands_model->insert($params['Brand'], 0, $brand_type->id);
                        }
                        $this->brand_types_model->update($brand_type->id, $brand_type->name);                        
                        $this->brand_data_summary_model->updateByRankBrandId($brand_id, $params['IR500Rank']);
                    }
                    $i++;
                }
            }
        }
        
        
    }
}
