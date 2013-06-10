<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Measure extends MY_Controller {

    function __construct()
    {
        parent::__construct();

        $this->load->library('form_validation');
        $this->load->library('helpers');
        $this->data['title'] = 'Measure';

        if (!$this->ion_auth->logged_in())
        {
            //redirect them to the login page
            redirect('auth/login', 'refresh');
        }
    }

    public function index()
    {
        $this->data['category_list'] = $this->category_full_list();
        $this->data['customers_list'] = $this->category_customers_list();
        $this->render();
    }

    private function category_full_list() {
        $this->load->model('category_model');
        $categories = $this->category_model->getAll();
        return $categories;
    }

    private function category_customers_list() {
        $this->load->model('customers_model');
        $output = array();
        $customers_init_list = $this->customers_model->getAll();
        if(count($customers_init_list) > 0) {
            foreach ($customers_init_list as $key => $value) {
                $n = strtolower($value->name);
                $output[] = $n;
            }
        }
        $output = array_unique($output);
        return $output;
    }

    // public function gridview() {
    //     $s = $this->input->post('s');
    //     $data = array(
    //         'search_results' => array()
    //     );
    //     $this->load->view('measure/gridview', $data);
    // }

    public function getcustomerslist() {
        $this->load->model('customers_model');
        $output = array();
        $customers_init_list = $this->customers_model->getAll();
        if(count($customers_init_list) > 0) {
            foreach ($customers_init_list as $key => $value) {
                $n = strtolower($value->name);
                $output[] = $n;
            }
        }
        $output = array_unique($output);
        $this->output->set_content_type('application/json')->set_output(json_encode($output));
    }

    public function analyzestring() {
        $clean_t = $this->input->post('clean_t');
        $output = $this->helpers->measure_analyzer_start_v2($clean_t);
        $this->output->set_content_type('application/json')->set_output(json_encode($output));
    }

    public function analyzekeywords() {
        $primary_ph = $this->input->post('primary_ph');
        $secondary_ph = $this->input->post('secondary_ph');
        $tertiary_ph = $this->input->post('tertiary_ph');
        $short_desc = $this->input->post('short_desc');
        $long_desc = $this->input->post('long_desc');
        $output = $this->helpers->measure_analyzer_keywords($primary_ph, $secondary_ph, $tertiary_ph, $short_desc, $long_desc);
        $this->output->set_content_type('application/json')->set_output(json_encode($output));
    }

    public function searchmeasuredball() {
        $s = $this->input->post('s');
        $sl = $this->input->post('sl');
        $cat_id = $this->input->post('cat');
        $this->load->model('imported_data_parsed_model');
        $data = array(
            'search_results' => array()
        );
        $opt_ids = array();
        if($cat_id != 'all') {
            $this->load->model('imported_data_model');
            $opt = $this->imported_data_model->getByCateggoryId($cat_id);
            if(count($opt) > 0) {
                foreach ($opt as $key => $value) {
                    $opt_ids[] = $value->id;
                }
            }
        }
        $data_import = $this->imported_data_parsed_model->getByValueLikeGroupCat($s, $sl, $opt_ids);
     	if (empty($data_import)) {
            $this->load->library('PageProcessor');
			if ($this->pageprocessor->isURL($this->input->post('s'))) {
				$parsed_data = $this->pageprocessor->get_data($this->input->post('s'));
				$data_import[0] = $parsed_data;
				$data_import[0]['url'] = $this->input->post('s');
				$data_import[0]['imported_data_id'] = 0;
			}
		}

        $data['search_results'] = $data_import;
        $this->load->view('measure/searchmeasuredball', $data);
    }

    public function attributesmeasure() {

        $s = $this->input->post('s');

        $data = array('search_results'=>'', 'file_id'=>'', 'product_descriptions' => '', 'product_title' => '');
        $attributes = array();

        $attr_path = $this->config->item('attr_path');

        if ($path = realpath($attr_path)) {
            $objects = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path), RecursiveIteratorIterator::SELF_FIRST);
            foreach ($objects as $name => $object){
                if (!$object->isDir()) {
                    if ($object->getFilename() == 'attributes.dat') {
                        if ($content= file_get_contents($name)) {
                            if (preg_match("/$s/i",$content,$matches)) {

                                $part = str_ireplace($attr_path, '', $object->getPath());
                                if (preg_match('/\D*(\d*)/i',$part,$matches)) {
                                    $data['file_id'] = $matches[1];
                                }

                                foreach ($this->config->item('attr_replace') as $replacement) {
                                    $content = str_replace(array_keys($replacement), array_values($replacement), $content);
                                }

                                $data['search_results'] = nl2br($content);

                                if (preg_match_all('/\s?(\S*)\s*(.*)/i', $content, $matches)) {
                                    foreach($matches[1] as $i=>$v) {
                                        if (!empty($v))
                                        $attributes[strtoupper($v)] = $matches[2][$i];
                                    }
                                }

                                if (!empty($attributes)) {
                                    $title = array();
                                    foreach ($this->settings['product_title'] as $v) {
                                        if (isset($attributes[strtoupper($v)]))
                                            $title[] = $attributes[strtoupper($v)   ];
                                    }
                                    $data['product_title'] = implode(' ', $title);
                                    $data['attributes'] = $attributes;
                                }
                                break;
                            }
                        }
                    }
                }
            }
        }

        if ($this->system_settings['java_generator']) {
            $descCmd = str_replace($this->config->item('cmd_mask'), $data['file_id'] ,$this->system_settings['java_cmd']);
            if ($result = shell_exec($descCmd)) {
                if (preg_match_all('/\(.*\)\: "(.*)"/i',$result,$matches) && isset($matches[1]) && count($matches[1])>0) {
                    if( is_array($data['product_descriptions']) )
                        $data['product_descriptions'] = array_merge($data['product_descriptions'], $matches[1]);
                    else
                        $data['product_descriptions'] = $matches[1];
                }
            }
        }
        if ($this->system_settings['python_generator']) {
            $descCmd = str_replace($this->config->item('cmd_mask'), $s ,$this->system_settings['python_cmd']);
            if ($result = shell_exec($descCmd)) {
                if (preg_match_all('/.*ELECTR_DESCRIPTION:\s*(.*)\s*-{5,}/',$result,$matches)) {
                    if( is_array($data['product_descriptions']) )
                        $data['product_descriptions'] = array_merge($data['product_descriptions'], $matches[1]);
                    else
                        $data['product_descriptions'] = $matches[1];
                }
            }
        }

        if(!empty($this->exceptions) && !empty($data['attributes'])){
            foreach ($data['attributes'] as $key => $value) {
                foreach ($this->exceptions as $exception) {
                    if($exception['attribute_name'] == $key AND $exception['attribute_value'] == $value){
                        foreach ($data['product_descriptions'] as $pd_key => $product_description) {
                            foreach ($exception['exception_values'] as $exception_value) {
                                if (stristr($product_description, $exception_value)) {
                                    unset($data['product_descriptions'][$pd_key]);
                                }
                            }
                        }
                        sort($data['product_descriptions']);
                    }
                }
            }
        }

        $this->output->set_content_type('application/json')
            ->set_output(json_encode($data));

    }

}