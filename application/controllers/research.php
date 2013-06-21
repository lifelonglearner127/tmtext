<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Research extends MY_Controller {

    function __construct()
    {
        parent::__construct();

        $this->load->library('form_validation');
        $this->load->library('helpers');
        $this->data['title'] = 'Research & Edit';

        if (!$this->ion_auth->logged_in())
        {
            //redirect them to the login page
            redirect('auth/login', 'refresh');
        }
    }

    public function index()
    {
        $this->data['category_list'] = $this->category_list();
        $this->data['batches_list'] = $this->batches_list();
        $this->render();
    }

    public function category_list()
    {
        $this->load->model('category_model');
        $categories = $this->category_model->getAll();
        $category_list = array();
        foreach($categories as $category){
            array_push($category_list, $category->name);
        }
        return $category_list;
    }

    public function batches_list()
    {
        $this->load->model('batches_model');
        $batches = $this->batches_model->getAll();
        $batches_list = array();
        foreach($batches as $batch){
            array_push($batches_list, $batch->title);
        }
        return $batches_list;
    }

    public function search_results()
    {
        $this->load->model('imported_data_parsed_model');
        $this->load->model('category_model');

        if($this->input->post('search_data') != '') {

            $category_id = '';
            $limit = '';
            if($this->input->post('category') != '' && $this->input->post('category') != 'All'){
                $category_id = $this->category_model->getIdByName($this->input->post('category'));
            }
            if($this->input->post('limit')!=''){
                $limit = $this->input->post('limit');
            }

            $imported_data_parsed = $this->imported_data_parsed_model->getData($this->input->post('search_data'), $this->input->post('website'), $category_id, $limit);
            if (empty($imported_data_parsed)) {
            	$this->load->library('PageProcessor');
				if ($this->pageprocessor->isURL($this->input->post('search_data'))) {
					$parsed_data = $this->pageprocessor->get_data($this->input->post('search_data'));
					$imported_data_parsed[0] = $parsed_data;
					$imported_data_parsed[0]['url'] = $this->input->post('search_data');
					$imported_data_parsed[0]['imported_data_id'] = 0;
				}
            }
            $this->output->set_content_type('application/json')
                ->set_output(json_encode($imported_data_parsed));
        }
    }

    public function research_batches(){
        $this->data['batches_list'] = $this->batches_list();
        $this->data['customer_list'] = $this->getCustomersByUserId();
        $this->render();
    }

    public function new_batch()
    {
        $this->load->model('batches_model');
        if($this->input->post('batch')!=''){
            $batch = $this->input->post('batch');
            $batch_id = $this->batches_model->getIdByName($batch);
            if($batch_id == false) {
                $batch_id = $this->batches_model->insert($batch);
            }
        }
    }
    public function change_batch_name(){
        $this->load->model('research_data_model');
        $this->load->model('batches_model');
        $batch = $this->input->post('old_batch_name');
        $batch_id = $this->batches_model->getIdByName($batch);
        if($this->batches_model->update($batch_id, $this->input->post('new_batch_name'))){
            $response['message'] = 'success';
        } else {
            $response['message'] = 'error';
        }
        $this->output->set_content_type('application/json')
            ->set_output(json_encode($response));
    }

    public function get_research_data()
    {
        $this->load->model('research_data_model');
        $this->load->model('batches_model');
        $batch = $this->input->post('batch');
        $batch_id = $this->batches_model->getIdByName($batch);
        if($batch_id == false && $batch != '') {
            $batch_id = $this->batches_model->insert($batch);
        }
        $results = $this->research_data_model->getAllByProductName($this->input->post('product_name'), $batch_id);
        $this->output->set_content_type('application/json')
            ->set_output(json_encode($results));
    }

    public function get_research_info()
    {
        $this->load->model('research_data_model');
        $this->load->model('batches_model');
        $batch = trim($this->input->get('choosen_batch'));
        $batch_id = $this->batches_model->getIdByName($batch);

        $results = $this->research_data_model->getDataByBatchId($this->input->get('search_text'), $batch_id);

        $this->output->set_content_type('application/json')
            ->set_output(json_encode($results));
    }

    public function update_research_info()
    {
        $this->load->model('research_data_model');
        if( !empty( $_POST ) ) {
            $id = $this->input->post('id');
            $url = $this->input->post('url');
            $product_name = $this->input->post('product_name');
            $short_description = $this->input->post('short_description');
            $long_description = $this->input->post('long_description');
            $this->research_data_model->updateItem($id, $product_name, $url, $short_description, $long_description);
            echo 'Record updated successfully!';
        }
    }

    public function delete_research_info()
    {
        $this->load->model('research_data_model');
        $id = $this->input->post('id');
        if( is_null( $id ) ) {
            echo 'ERROR: Id not provided.';
            return;
        }
        $this->research_data_model->delete( $id );
        echo 'Records deleted successfully';
    }

    public function save_in_batch()
    {
        $this->load->model('research_data_model');
        $this->load->model('batches_model');

        $this->form_validation->set_rules('product_name', 'Product Name', 'required|xss_clean');
        /*$this->form_validation->set_rules('keyword1', 'Keyword1', 'required|xss_clean');
        $this->form_validation->set_rules('keyword2', 'Keyword2', 'required|xss_clean');
        $this->form_validation->set_rules('keyword3', 'Keyword3', 'required|xss_clean');
        $this->form_validation->set_rules('meta_title', 'Meta title', 'required|xss_clean');
        $this->form_validation->set_rules('meta_description', 'Meta description', 'required|xss_clean');
        $this->form_validation->set_rules('meta_keywords', 'Meta keywords', 'required|xss_clean');
        $this->form_validation->set_rules('short_description', 'Short Description', 'required|xss_clean');
        $this->form_validation->set_rules('long_description', 'Long Description', 'required|xss_clean');
        $this->form_validation->set_rules('revision', 'Revision', 'integer');*/

        if ($this->form_validation->run() === true) {
            $batch = $this->input->post('batch');
            $batch_id = $this->batches_model->getIdByName($batch);
            if($batch_id == false) {
                $batch_id = $this->batches_model->insert($batch);
            }
            $url = $this->input->post('url');
            $product_name = $this->input->post('product_name');
            $keyword1 = $this->input->post('keyword1');
            $keyword2 = $this->input->post('keyword2');
            $keyword3 = $this->input->post('keyword3');
            $meta_title = $this->input->post('meta_title');
            $meta_description = $this->input->post('meta_description');
            $meta_keywords = $this->input->post('meta_keywords');
            $short_description = $this->input->post('short_description');
            $long_description = $this->input->post('long_description');
            if ($this->input->post('revision')=='') {
                $last_revision = $this->research_data_model->getLastRevision();
                if(!empty($last_revision)){
                    $revision = $last_revision[0]->revision + 1;
                } else {
                    $revision = 1;
                }
            } else {
                $revision = $this->input->post('revision');
            }
            $results = $this->research_data_model->getAllByProductName($product_name, $batch_id);
            if(empty($results)){
                $data['research_data_id'] = $this->research_data_model->insert($batch_id, $url, $product_name, $keyword1, $keyword2,
                    $keyword3, $meta_title, $meta_description, $meta_keywords, $short_description, $long_description, $revision);
            } else {
                $data['research_data_id'] = $this->research_data_model->update($results[0]->id, $batch_id, $url, $product_name, $keyword1, $keyword2,
                    $keyword3, $meta_title, $meta_description, $meta_keywords, $short_description, $long_description, $revision);
            }
            $data['revision'] = $revision;
        } else {
            $data['message'] = (validation_errors() ? validation_errors() : $this->session->flashdata('message'));
        }

        $this->output->set_content_type('application/json')
            ->set_output(json_encode($data));
    }

    public function getById( $id ) {
        $this->load->model('research_data_model');
        if( isset( $id ) )
            echo json_encode( $this->research_data_model->get( $id ) );
    }

    public function export()
    {
        $this->load->model('batches_model');
        $batch_id = $this->batches_model->getIdByName($this->input->get('batch'));
        $this->load->database();
        $query = $this->db->where('batch_id', $batch_id)->get('research_data');
        $this->load->helper('csv');
        query_to_csv($query, TRUE, $this->input->get('batch').'.csv');
    }

    public function getBoxData()
    {
        $this->load->model('research_box_position_model');
        $data = $this->research_box_position_model->getDataByUserId();
        $this->output->set_content_type('application/json')
            ->set_output(json_encode($data));
    }

    public function delete_research_data()
    {
        $this->research_data_model->delete($this->input->post('id'));
    }

    public function getCustomersByUserId(){
        $this->load->model('customers_model');
        $this->load->model('users_to_customers_model');
        $customers = $this->users_to_customers_model->getByUserId($this->ion_auth->get_user_id());
        if(count($customers) == 0){
            $customers = $this->customers_model->getAll();
        }
        $customer_list = array(''=>'Select');
        foreach($customers as $customer){
            array_push($customer_list, $customer->name);
        }

        return $customer_list;

    }
}