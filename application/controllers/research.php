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
        $this->data['customer_list'] = $this->getCustomersByUserId();
        $this->data['category_list'] = $this->category_list();
        if(!empty($this->data['customer_list'])){
             $this->data['batches_list'] = $this->batches_list();
        }
        
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
            if($this->input->post('category') != '' && $this->input->post('category') != 'All categories'){
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

    public function create_batch(){

        $this->data['customer_list'] = $this->getCustomersByUserId();
        if(!empty($this->data['customer_list'])){
            $this->data['batches_list'] = array('')+$this->batches_list();
        }
        $this->render();
    }

    public function research_batches(){
        $this->load->model('settings_model');
        $this->data['customer_list'] = $this->getCustomersByUserId();
        if(!empty($this->data['customer_list'])){
            $this->data['batches_list'] = $this->batches_list();
        }
		$user_id = $this->ion_auth->get_user_id();
        $key = 'research_review';

        $columns = $this->settings_model->get_value($user_id, $key);

        // if columns empty set default values for columns
        if(empty($columns)) {
            $columns = array (
                'editor'                        => 'true',
                'product_name'                  => 'true',
                'url'                           => 'true',
                'short_description'             => 'true',
                'short_description_wc'          => 'false',
                'long_description'              => 'true',
                'long_description_wc'           => 'false',
                'actions'                       => 'true',
            );
        }
        $this->data['columns'] = $columns;
        $this->render();
    }
    
    public function research_reports(){
        $this->render();
    }

    public function new_batch()
    {
        $this->load->model('customers_model');
        $this->load->model('batches_model');
        if($this->input->post('batch')!=''){
            $batch = $this->input->post('batch');
            $customer_id = '';
            if($this->input->post('customer_name') != 'Customer'){
                $customer_id = $this->customers_model->getIdByName($this->input->post('customer_name'));
            }
            $batch_id = $this->batches_model->getIdByName($batch);
            if($batch_id == false) {
                $batch_id = $this->batches_model->insert($batch, $customer_id);
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
        $data = '';
        if($this->input->get('search_text') != ''){
            $data = $this->input->get('search_text');
        }
        $results = $this->research_data_model->getInfoFromResearchData($data);

        // change '0' value to '-'
        foreach($results as $result) {
            if($result->short_description_wc == '0') {
                $result->short_description_wc = '-';
            }
            if($result->long_description_wc == '0') {
                $result->long_description_wc = '-';
            }
        }

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
            // count words
            $short_description_wc = $this->input->post('short_description_wc');
            $long_description_wc = $this->input->post('long_description_wc');
            $this->research_data_model->updateItem($id, $product_name, $url, $short_description, $long_description, $short_description_wc, $long_description_wc);
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
            $short_description_wc = $this->input->post('short_description_wc');
            $long_description = $this->input->post('long_description');
            $long_description_wc = $this->input->post('long_description_wc');
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
                    $keyword3, $meta_title, $meta_description, $meta_keywords, $short_description, $short_description_wc, $long_description, $long_description_wc, $revision);
            } else {
                $data['research_data_id'] = $this->research_data_model->update($results[0]->id, $batch_id, $url, $product_name, $short_description, $short_description_wc, $long_description, $long_description_wc, $keyword1, $keyword2,
                    $keyword3, $meta_title, $meta_description, $meta_keywords, $revision);
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
        if(!$this->ion_auth->is_admin($this->ion_auth->get_user_id())){
            if(count($customers) == 0){
                $customer_list = array();
            }else{
                $customer_list = array(''=>'All Customers');
            }
            foreach($customers as $customer){
                array_push($customer_list, $customer->name);
            }
        }else{
            if(count($customers) == 0){
            $customers = $this->customers_model->getAll();
            }
            $customer_list = array(''=>'All Customers');
            foreach($customers as $customer){
                array_push($customer_list, $customer->name);
            }
        }
        return $customer_list;

    }

    public function generateDesc(){
        $s = $this->input->post('product_name');

        $this->load->library('pagination');
        $pagination_config['base_url'] = $this->config->site_url().'/research/generateDesc';
        $pagination_config['per_page'] = 0;

        $data = array(
            's' => $s,
            'search_results' => array()
        );

        $attr_path = $this->config->item('attr_path');

        $csv_rows = array();

        // Search in files
        if ( isset($this->settings['use_files']) && $this->settings['use_files']) {
            if ($path = realpath($attr_path)) {
                $objects = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path), RecursiveIteratorIterator::SELF_FIRST);
                foreach($objects as $name => $object){
                    if (!$object->isDir()) {
                        if (preg_match("/.*\.csv/i",$object->getFilename(),$matches)) {
                            $_rows = array();
                            if (($handle = fopen($name, "r")) !== FALSE) {
                                while (($row = fgets($handle, 1000)) !== false) {
                                    if (preg_match("/$s/i",$row,$matches)) {
                                        $_rows[] = $row;
                                    }
                                }
                            }
                            fclose($handle);

                            foreach (array_keys(array_count_values($_rows)) as $row){
                                $csv_rows[] = str_getcsv($row, ",", "\"");
                            }
                            unset($_rows);
                        }
                    }
                }
            }
        }

        // Search in database
        if ( isset($this->settings['use_database']) && $this->settings['use_database']) {
            $this->load->model('imported_data_model');
            if (( $_rows = $this->imported_data_model->findByData($s))!== false) {
                foreach($_rows as $row) {
                    $csv_rows[] = str_getcsv($row['data'], ",", "\"");
                }
            }
        }

        if (!empty($csv_rows)) {
            $current_row = 0;
            foreach($csv_rows as $row) {
                if ($current_row < (int)$this->uri->segment(3)) {
                    $current_row++;
                    continue;
                }
                foreach ($row as $col) {
                    if (preg_match("/^http:\/\/*/i",$col,$matches)) {
                        $row['url'] = $col;
                    } else if ( mb_strlen($col) <= 250) {
                        $row['title'] = $col;
                    } else if (empty($row['description'])){
                        $row['description'] = substr($col, 0, strpos(wordwrap($col, 200), "\n"));

                    }
                }

                if (!empty($row['url']) && !empty($row['title'])) {
                    $data['search_results'][] =  '<a href="'.$row['url'].'">'.$row['title'].'</a><br/>'.$row['description'];
                } else if (!empty($row['description'])) {
                    $data['search_results'][] =  $row['description'];
                }
                if (count($data['search_results']) == $pagination_config['per_page']) break;
            }
        }

        $pagination_config['total_rows'] = count($csv_rows);
        $this->pagination->initialize($pagination_config);
        $data['pagination']= $this->pagination->create_links();

        $this->output->set_content_type('application/json')
            ->set_output(json_encode($data));
    }

    public function filterCustomerByBatch(){
        $this->load->model('batches_model');
        $batch = $this->input->post('batch');
        $customer_name = $this->batches_model->getCustomerByBatch($batch);
        $this->output->set_content_type('application/json')
            ->set_output(json_encode(strtolower($customer_name)));
    }

    public function filterBatchByCustomer(){
        $this->load->model('batches_model');
        $this->load->model('customers_model');
        $customer_id = $this->customers_model->getIdByName($this->input->post('customer_name'));
        $batches = $this->batches_model->getAllByCustomer($customer_id);
        if($this->input->post('customer_name') ==  "All Customers"){
            $batches = $this->batches_model->getAll();
        }
        $batches_list = array();
        if(!empty($batches)){
            foreach($batches as $batch){
                array_push($batches_list, $batch->title);
            }
        }
        $this->output->set_content_type('application/json')
            ->set_output(json_encode($batches_list));
    }
    
    public function filterStyleByCustomer(){
        $this->load->model('customers_model');
        $this->load->model('style_guide_model');
        if($this->input->post('customer_name')!=='All Customers'){
            $customer_id = $this->customers_model->getIdByName($this->input->post('customer_name'));
            $style = $this->style_guide_model->getStyleByCustomerId($customer_id);
            $this->output->set_content_type('application/json')
               ->set_output(json_encode($style[0]->style));
        }
    }

    public function upload_csv(){
        $this->load->library('UploadHandler');

        $this->output->set_content_type('application/json');
        $this->uploadhandler->upload(array(
            'script_url' => site_url('research/upload_csv'),
            'upload_dir' => $this->config->item('csv_upload_dir'),
            'param_name' => 'files',
            'delete_type' => 'POST',
            'accept_file_types' => '/.+\.csv$/i',
        ));
    }

    public function csv_import() {
        $this->load->model('batches_model');
        $this->load->model('customers_model');
        $this->load->model('items_model');

        $file = $this->config->item('csv_upload_dir').$this->input->post('choosen_file');
        $_rows = array();
        if (($handle = fopen($file, "r")) !== FALSE) {
            while (($data = fgetcsv($handle, 1000, ",")) !== FALSE) {
                if(!is_null($data[0]) && $data[0]!='URL' && $data[0]!=''){
                    $_rows[] = $data[0];
                }
            }
            fclose($handle);
        }
        $batch_id = $this->batches_model->getIdByName($this->input->post('batch_name'));
        $customer_id = $this->customers_model->getIdByName($this->input->post('customer_name'));
        foreach($_rows as $_row){
            $this->items_model->insert($batch_id, $customer_id, $_row);
        }
        $str = count($_rows);
        if(count($_rows)==1){
            $str .= ' record';
        } else if(count($_rows)>1){
            $str .= ' records';
        }
        
        $response['message'] = $str .' added to batch';
         $this->output->set_content_type('application/json')
                ->set_output(json_encode($response));
    }

    public function delete_batch(){
        $this->load->model('batches_model');
        $batch_id =  $this->batches_model->getIdByName($this->input->post('batch_name'));
        $this->batches_model->delete($batch_id);
    }
}