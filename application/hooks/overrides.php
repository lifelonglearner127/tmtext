<?php if (!defined('BASEPATH')) exit('No direct script access allowed');
class Overrides {

	function _is_allowed() {
    	$CI =& get_instance();
		$_allowed = false;

		if (!$_allowed = $CI->ion_auth->_allowed($CI->router->fetch_method())) {
        	if (!$CI->ion_auth->logged_in())
			{
				redirect('auth/login', 'refresh');
			} else {
				$CI->ion_auth->load_current_user_auth_rules();
				if ( !$_allowed = $CI->ion_auth->current_user_allowed($CI->router->fetch_class(), $CI->router->fetch_method()) ) {
					$redirect = '/';
					if (isset($CI->previous_controller_name) ) {
						$redirect = $CI->previous_controller_name.'/';
						if (isset($CI->previous_action_name) ) {
							$redirect .= $CI->previous_action_name;
						}
					}
					redirect($redirect, 'refresh');
				}
			}
        }
    }

}