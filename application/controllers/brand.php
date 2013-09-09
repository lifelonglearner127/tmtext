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
            $rank = 1;
            $result = array();
            foreach ($brand_list['result'] as $brand_list) {
                $row = new stdClass();
                $row->social_rank = $rank;
                $row->IR500Rank = intval($brand_list->IR500Rank);
                $row->name = $brand_list->name;
                $row->tweets = intval($brand_list->tweets);
                $row->total_tweets = intval($brand_list->total_tweets);
                $row->followers = intval($brand_list->followers);
                $row->following = intval($brand_list->following);
                $row->videos = intval($brand_list->videos);
                $row->views = intval($brand_list->views);
                $row->total_youtube_views = intval($brand_list->total_youtube_views);
                $row->avarage = round(intval($brand_list->views) / intval($brand_list->videos), 2);
                $row->total_youtube_videos = intval($brand_list->total_youtube_videos);
                $result[] = $row;

                $rank++;
            }

            $this->sort_direction = $this->input->get('sSortDir_0', TRUE);
            $all_columns = $this->input->get('sColumns');
            $sort_columns = $this->input->get('iSortCol_0');
            $s_columns = explode(',', $all_columns);
            $s_column_index = intval($sort_columns);
            $s_column = $s_columns[$s_column_index];
            $this->sort_column = $s_column;
            $this->sort_type = is_numeric($result[0]->$s_column) ? "num" : "";
            usort($result, array("Brand", "brand_sort"));

            foreach ($result as $brand) {
                $output['aaData'][] = array(
                    $brand->social_rank,
                    $brand->name,
                    number_format($brand->IR500Rank),
                    number_format($brand->tweets),
                    number_format($brand->total_tweets),
                    number_format($brand->followers),
                    number_format($brand->following),
                    number_format($brand->videos),
                    number_format($brand->views),
                    number_format($brand->total_youtube_views),
                    number_format($brand->avarage),
                    number_format($brand->total_youtube_videos),
                );
            }
        }

        $this->output->set_content_type('application/json')
                ->set_output(json_encode($output));
        
    }

    private function brand_sort($a, $b) {
        $column = $this->sort_column;
        $key1 = $a->$column;
        $key2 = $b->$column;

        if ($this->sort_type == "num") {
            $result = intval($key1) - intval($key2);
        } else {
            $result = strcmp(strval($key1), strval($key2));
        }

        if ($this->sort_direction == "asc") {
            return $result;
        } else {
            return -$result;
        }
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
