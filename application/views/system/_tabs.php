<?php
	$this->load->helper('crawler_instances_helper');
	$tabs = array(
		array(
			'site_url' => 'system',
			'label' => 'General'
		),
		array(
			'site_url' => 'system/sites_view',
			'label' => 'Sites'
		),
		array(
			'site_url' => 'site_crawler',
			'label' => 'Site Crawler'
		),
		array(
			'site_url' => 'site_crawler/instances_list',
			'label' => 'Crawler Instances ' . crawler_instances_number(),
		),
		array(
			'site_url' => 'system/system_uploadmatchurls',
			'label' => 'Upload Match URLs'
		),
		array(
			'site_url' => 'system/system_dostatsmonitor',
			'label' => 'Do_stats Monitor'
		),
               array(
			'site_url' => 'system/workflow',
			'label' => 'Workflow'
		),
		array(
			'site_url' => 'brand/import',
			'label' => 'Brands'
		),
		array(
			'site_url' => 'system/batch_review',
			'label' => 'Batch Review'
		),
		array(
			'site_url' => 'system/system_compare',
			'label' => 'Product Compare'
		),
		array(
			'site_url' => 'system/system_productsmatch',
			'label' => 'Product Match'
		),
		array(
			'site_url' => 'system/system_reports',
			'label' => 'Reports'
		),
		array(
			'site_url' => 'system/system_logins',
			'label' => 'Logins'
		),
		array(
			'site_url' => 'system/keywords',
			'label' => 'Keywords'
		),
		array(
			'site_url' => 'system/system_rankings',
			'label' => 'Rankings'
		),
		array(
			'site_url' => 'measure/measure_pricing',
			'label' => 'Pricing'
		),
		array(
			'site_url' => 'measure/product_models',
			'label' => 'Product models'
		),
		array(
			'site_url' => 'system/snapshot_queue',
			'label' => 'Snapshot Queue'
		),
		array(
			'site_url' => 'system/sync_keyword_status',
			'label' => 'Sync Keyword Status'
		),
		array(
			'site_url' => 'system/bad_matches',
			'label' => 'Bad Matches'
		),
		array(
			'site_url' => 'system/filters',
			'label' => 'Filters'
		),
	);	
?>	
<ul class="nav nav-tabs jq-system-tabs">
	<?php foreach ($tabs as $tab): ?>
		<li class="<?php echo $tab['site_url'] == $active_tab ? 'active' : '' ?>">
			<a data-toggle="tab" href="<?php echo site_url($tab['site_url']);?>">
				<?php echo $tab['label'] ?>
			</a>
		</li>		
	<?php endforeach ?>
</ul>