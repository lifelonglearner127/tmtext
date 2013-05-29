<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Admin_Tag_Editor extends MY_Controller {

    function __construct()
    {
        parent::__construct();

        $this->load->library('form_validation');
        $this->data['title'] = 'Admin Tag Editor Setting';

        if ($generators = $this->session->userdata('generators')) {
            $this->config->set_item('generators',$generators);
        }

        if (!$this->ion_auth->logged_in())
        {
            //redirect them to the login page
            redirect('auth/login', 'refresh');
        }

    }

    public function index()
    {
        $this->data['category_list'] = $this->category_list();
        $this->data['tagrules_data'] = $this->file_data($this->data['files'][0]);
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

    public function file_data($category = '')
    {
        $this->load->model('category_model');
        $this->load->model('tag_editor_rules_model');
        if($category == ''){
            $category = $this->input->post('category');
        }
        $category_id = $this->category_model->getIdByName($category);

        $data = array();
        if($category_id > 0) {
            if($category == 'All'){
                $results = $this->tag_editor_rules_model->getAll();
            } else {
                $results = $this->tag_editor_rules_model->getAllByCategoryId($category_id);
            }
            foreach($results as $result){
                array_push($data, '<span>'. $result->rule . '</span>');
            }
        } else {
            $path = $this->config->item('tag_rules_dir').'/'.$category.'.dat';
            $lines = explode("\n", file_get_contents($path));
            $data = array();
            foreach($lines as $key => $line){
                if($line != ''){
                    array_push($data, '<span>'. $line . '</span>');
                }
            }
        }
        if(isset($_POST) && !empty($_POST)) {
            echo ul($data, array('id' => 'items_list'));
        } else {
            return $data;
        }
    }

    public function get_product_description()
    {
        $description = array();
        $this->load->model('category_model');
        $this->load->model('tag_editor_descriptions_model');
        $category_id = '';

        if($this->input->post('category') != 'All'){
            $category_id = $this->category_model->getIdByName($this->input->post('category'));
            $data = $this->tag_editor_descriptions_model->get($this->ion_auth->get_user_id(), $category_id);
        } else {
            $all = $this->category_model->getAll();
            $data = array();
            foreach($all as $item){
                $desc = $this->tag_editor_descriptions_model->get($this->ion_auth->get_user_id(), $item->id);
                if(empty($desc)){
                    $desc = $this->category_model->getAllCategoryDescriptions($item->id);
                }
                array_push($data, $desc);
            }
        }
        //die;
        if(empty($data)){
            $descriptions = $this->category_model->getAllCategoryDescriptions($category_id);
            $result = array();
            foreach($descriptions as $desc){
                array_push($result, $desc->description);
            }
            /*$row = 1;
            $file = $this->config->item('attr_path').'/tiger/all.csv';
            if (($handle = fopen($file, "r")) !== FALSE) {
                while (($data = fgetcsv($handle, 2000, "\n")) !== FALSE) {
                    $num = count($data);
                    $row++;
                    for ($c=0; $c < $num; $c++) {
                        if($data[$c]!='') {
                            $line = iconv( "Windows-1252", "UTF-8", $data[$c] );
                            array_push($description, str_replace(',,,,', '', $line));
                        }
                    }
                }
                fclose($handle);
            }*/
            echo ul($result, array('id'=>'desc_count_'.count($descriptions)));
        } else {

            $this->output->set_content_type('application/json')
                ->set_output(json_encode($data));
        }
    }

    public function save_file_data()
    {
        $this->load->model('category_model');
        $this->load->model('tag_editor_rules_model');
        if($this->input->post('category')!=''){
            $category = $this->input->post('category');

            $category_id = $this->category_model->getIdByName($category);
            if($category_id == false) {
                $category_id = $this->category_model->insert($category);
            }
            $this->tag_editor_rules_model->delete($category_id);
            foreach(explode("\n", $this->input->post('data')) as $line) {
                if($line != ''){
                    $this->tag_editor_rules_model->insert( $line, $category_id);
                }
            }
            $path = $this->config->item('tag_rules_dir').'/'.$category.'.dat';
            file_put_contents($path, $this->input->post('data'));
        }
    }

    public function delete_file()
    {
        $this->load->model('category_model');

        if($this->input->post('category')!='') {
            $category_id = $this->category_model->getIdByName($this->input->post('category'));
            $this->category_model->delete($category_id);
            $path = $this->config->item('tag_rules_dir').'/'.$this->input->post('category').'.dat';
            unlink($path);
        }
    }

    public function save()
    {
        $this->load->model('tag_editor_descriptions_model');
        $this->load->model('category_model');

        $this->ion_auth->get_user_id();
        $this->form_validation->set_rules('description', 'Description', 'required|xss_clean');

        if ($this->form_validation->run() === true) {
            $category_id = $this->category_model->getIdByName($this->input->post('category'));
            $data = $this->tag_editor_descriptions_model->get($this->ion_auth->get_user_id(), $category_id);
            if(empty($data)){
                $data['tag_description_id'] = $this->tag_editor_descriptions_model->insert($this->input->post('description'), $category_id);
            } else {
                $data['tag_description_id'] = $this->tag_editor_descriptions_model->update($this->ion_auth->get_user_id(), $category_id,
                    $this->input->post('description'));
            }
        } else {
            $data['message'] = (validation_errors() ? validation_errors() : $this->session->flashdata('message'));
        }

        $this->output->set_content_type('application/json')
            ->set_output(json_encode($data));

    }

    public function delete()
    {
        $this->load->model('tag_editor_descriptions_model');
        $this->load->model('category_model');

        $this->ion_auth->get_user_id();
        $this->form_validation->set_rules('description', 'Description', 'required|xss_clean');
        $category_id = $this->category_model->getIdByName($this->input->post('category'));

        if ($this->form_validation->run() === true) {
            $data = $this->tag_editor_descriptions_model->delete($this->ion_auth->get_user_id(), $category_id);
        } else {
            $data['message'] = (validation_errors() ? validation_errors() : $this->session->flashdata('message'));
        }

        $this->output->set_content_type('application/json')
            ->set_output(json_encode($data));

    }

    public function import_rules()
    {
        $this->load->model('category_model');
        $this->load->model('tag_editor_rules_model');
        $dir = $this->config->item('tag_rules_dir');
        if (is_dir($dir)) {
            if ($dh = opendir($dir)) {
                while (($file = readdir($dh)) !== false) {
                   if($file != '.' && $file != '..'){
                       $category_name = str_replace('.dat', '', $file);
                       $category_id = $this->category_model->getIdByName($category_name);
                       $path = $this->config->item('tag_rules_dir').'/'.$file;
                       if(file_exists($path)){
                           $lines = explode("\n", file_get_contents($path));
                           foreach($lines as $key => $line){
                               if($line != ''){
                                   if($category_id == false){
                                       $category_id = $this->category_model->insert($category_name);
                                   }
                                   if( $this->tag_editor_rules_model->getByRule($line, $category_id) == false) {
                                       $this->tag_editor_rules_model->insert($line, $category_id);
                                   }
                               }
                           }
                       }
                   }
                }
                closedir($dh);
            }
        }
    }


}