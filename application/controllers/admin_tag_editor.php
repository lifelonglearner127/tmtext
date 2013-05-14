<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Admin_Tag_Editor extends MY_Controller {

    function __construct()
    {
        parent::__construct();

        $this->load->library('form_validation');
        $this->data['title'] = 'Admin Tag Editor Setting';
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
            $filename = $_POST['filename'];
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

    public function get_product_description() {
        $row = 1;
        $description = array();
        $file = $this->config->item('attr_path').'/tiger/all.csv';
        if (($handle = fopen($file, "r")) !== FALSE) {
            while (($data = fgetcsv($handle, 1000, ",")) !== FALSE) {
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
        return $description;
    }

    public function save_file_data() {
        if(isset($_POST) && !empty($_POST)){
            $filename = $_POST['filename'];
            $path = $this->config->item('tag_rules_dir').'/'.$filename.'.dat';
            file_put_contents($path, $_POST['data']);
        }
    }

}