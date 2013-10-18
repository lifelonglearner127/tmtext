<h1>Groups</h1>
<p>Below is a list of the groups.</p>

<div id="infoMessage"><?php echo $message;?></div>

<table cellpadding=0 cellspacing=10>
	<tr>
		<th><?php echo lang('index_groups_th');?></th>
		<th><?php echo lang('index_action_th');?></th>
	</tr>
	<?php foreach ($groups as $group):?>
		<tr>
			<td>
				<?php echo anchor("auth/edit_group/".$group->id, $group->name) ;?><br />
			</td>
			<td><?php echo anchor("auth/reset_auth_rules/".$group->id, 'Reset Auth Rules') ;?></td>
		</tr>
	<?php endforeach;?>
</table>
