<?php  if (!defined('BASEPATH')) exit('No direct script access allowed');
if (!function_exists('crawler_instances_number')) {
	function crawler_instances_number() {
		$CI = &get_instance();
		$CI->load->model("crawler_instances_model");
		$cnt = count($CI->crawler_instances_model->getNotTerminated());
		return ($cnt > 0) ? "(" . $cnt . ")" : "";
	}
}
