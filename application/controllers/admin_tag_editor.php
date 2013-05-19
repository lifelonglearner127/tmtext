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
        $this->data['files'] = $this->file_list();
        $this->data['tagrules_data'] = $this->file_data($this->data['files'][0]);
        $this->data['description'] = $this->get_product_description();
        $this->render();
    }

    public function file_list()
    {
        $file_list = array();
        $files_path = $this->config->item('tag_rules_dir');
        if ($path = realpath($files_path)) {
            $objects = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path), RecursiveIteratorIterator::SELF_FIRST);
            foreach ($objects as $name => $object){
                if (!$object->isDir()) {
                    $filename = str_replace('.dat', '', $object->getFilename());
                    array_push($file_list, $filename);
                }
            }
        }
        return $file_list;
    }

    public function file_data($filename = '')
    {
        if($filename == ''){
            $filename = $this->input->post('filename');
        }
        $path = $this->config->item('tag_rules_dir').'/'.$filename.'.dat';
        $lines = explode("\n", file_get_contents($path));
        foreach($lines as $key => $line){
            $lines[$key] = '<span>'. $line . '</span>';
        }
        if(isset($_POST) && !empty($_POST)) {
            echo ul($lines, array('id' => 'items_list'));
        } else {
            return $lines;
        }

    }

    public function get_product_description()
    {
        $description = array();
        $this->load->model('tag_editor_descriptions_model');
        $data = $this->tag_editor_descriptions_model->get($this->ion_auth->get_user_id());
        if(empty($data)){
            $row = 1;
            $file = $this->config->item('attr_path').'/tiger/all.csv';
            if (($handle = fopen($file, "r")) !== FALSE) {
                while (($data = fgetcsv($handle, 1000, ";")) !== FALSE) {
                    $num = count($data);
                    $row++;
                    for ($c=0; $c < $num; $c++) {
                        if($data[$c]!='') {
                            $line = iconv( "Windows-1252", "UTF-8", $data[$c] );
                            array_push($description, $line);
                        }
                    }
                }
                fclose($handle);
            }
        }
        return $description;
    }

    public function save_file_data()
    {
        if($this->input->post('filename')!=''){
            $filename = $this->input->post('filename');
            $path = $this->config->item('tag_rules_dir').'/'.$filename.'.dat';
            file_put_contents($path, $this->input->post('data'));
        }
    }

    public function delete_file()
    {
        if($this->input->post('filename')!='') {
            $path = $this->config->item('tag_rules_dir').'/'.$this->input->post('filename').'.dat';
            unlink($path);
        }
    }

    public function save()
    {
        $this->load->model('tag_editor_descriptions_model');

        $this->ion_auth->get_user_id();
        $this->form_validation->set_rules('description', 'Description', 'required|xss_clean');

        if ($this->form_validation->run() === true) {
            $data = $this->tag_editor_descriptions_model->get($this->ion_auth->get_user_id());
            if(empty($data)){
                $data['tag_description_id'] = $this->tag_editor_descriptions_model->insert($this->input->post('description'));
            } else {
                $data['tag_description_id'] = $this->tag_editor_descriptions_model->update($this->ion_auth->get_user_id(),
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

        $this->ion_auth->get_user_id();
        $this->form_validation->set_rules('description', 'Description', 'required|xss_clean');

        if ($this->form_validation->run() === true) {
           $data = $this->tag_editor_descriptions_model->delete($this->ion_auth->get_user_id());
        } else {
            $data['message'] = (validation_errors() ? validation_errors() : $this->session->flashdata('message'));
        }

        $this->output->set_content_type('application/json')
            ->set_output(json_encode($data));

    }


}