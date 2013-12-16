<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');
if ( ! function_exists('render_filter_item'))
{
	function render_filter_item($filter_id, $icon, $label, $batch_class_number = '', $is_extended_partial = true, array $question = array())
	{
		// $icon_td_width = $batch_class_number ? '10%' : '7.5%';
		$icon_td_width = '45px';
		$question_td_width = $batch_class_number ? '3%' : '1.5%';		
		$question_content = isset($question['explanation']) ? $question['explanation'] : '';
		$question_title = isset($question['title']) ? $question['title'] : 'Explanation';		
		
		$question_mark = $question_content ? '
		<span data-content="' . $question_content . '" title="' . $question_title . '<a class=\'popover_close_btn\' href=\'#\' onclick=\'close_popover(this); return false;\'>x</a>" data-placement="left" data-original-title="' . $question_title . '" class="question_mark" data-popover-uniqueid="' . $filter_id . '">
			<i class="icon-large icon-question-sign" ></i>
		</span>' : '';
								
		$r = '
			<div class="mt_10 ml_15 item_line ' . ($is_extended_partial ? 'ui-widget-content' : 'non-selectable') . ' ' . ($batch_class_number) . '" data-filterid="' . $filter_id . '">
				<div class="mr_10">
					<table width="100%">
						<tr>
							<td width="' . $icon_td_width . '">
								<img src="' . base_url() . 'img/' . $icon . '" class="' . $filter_id . '_icon" />
							</td>
							<td>
								' . $label . '
								<span class="' . $filter_id . ' mr_10" ></span>
							</td>
							<td width="' . $question_td_width . '">
								' . $question_mark . '
							</td>
						</tr>
					</table>
				</div>
			</div>
		';
		
		return $r;
	}
}
