<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');
if ( ! function_exists('render_filter_item'))
{
	function render_filter_item($filter_id, $icon, $label, $batch_class_number = '', $is_extended_partial = true, array $question = array())
	{
		$icon_td_width = $batch_class_number ? '10%' : '5%';
		$question_td_width = $batch_class_number ? '3%' : '1.5%';		
		$question_content = isset($question['explanation']) ? $question['explanation'] : 'No information.';
		$question_title = isset($question['title']) ? $question['title'] : 'Explanation:';		
		
		$r = '
			<div class="mt_10 ml_15 ' . ($is_extended_partial ? 'ui-widget-content' : 'non-selectable') . ' ' . $batch_class_number . '" data-filterid="' . $filter_id . '">
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
								<span data-content="' . $question_content . '" title="' . $question_title . '" data-original-title="' . $question_title . '" class="question_mark">
									<i class="icon-large icon-question-sign" ></i>
								</span>
							</td>
						</tr>
					</table>
				</div>
			</div>
		';
		
		return $r;
	}
}
