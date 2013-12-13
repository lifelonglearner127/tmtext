<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');
if ( ! function_exists('render_filter_item'))
{
	function render_filter_item($filter_id, $icon, $label, $batch_class_number = '')
	{
		$r = '
			<div class="mt_10 ml_15 ui-widget-content ' . $batch_class_number . '" data-filterid="' . $filter_id . '">
				<div class="mr_10">
					<table>
						<tr>
							<td>
								<img src="' . base_url() . 'img/' . $icon . '" class="' . $filter_id . '_icon" />
							</td>
							<td>
								' . $label . '
								<span class="' . $filter_id . ' mr_10" ></span>
							</td>
						</tr>
					</table>
				</div>
			</div>
		';
		
		return $r;
	}
}
