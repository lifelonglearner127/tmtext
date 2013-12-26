<?php $filter_items = get_filters() ?>

<div id="summary_filters_configuration_wrapper" title="Select filters" style="height: 205px !important;">
    <div>
        <form action="" method="post">					
<!--			
            <div id="horizontal" class="horizontal_vertical_icon" style="position: absolute; margin-top: -10px; margin-left: 55px; max-width: 25px;"><img src ="<?php echo base_url() ?>/img/horizontal.png" /></div>
            <div id="vertical" class="horizontal_vertical_icon" style="position: absolute; margin-top: -10px; margin-left: 55px; max-width: 25px;  visibility: hidden;"><img src ="<?php echo base_url() ?>/img/vertical.png" /></div>
			-->
            <div id="columns_checking">
				<ul>
				<?php foreach($filter_items as $filter_item): ?>
                                    <li style="margin: 0 0 10px;">
						<input type="checkbox" class="<?php echo $filter_item['data_filter_id'] ?>_config_class summary_filter_config_item" name="<?php echo $filter_item['data_filter_id'] ?>_config_name" id="<?php echo $filter_item['data_filter_id'] ?>_config_id" value="1" <?php echo isset($filter_item['is_default']) && $filter_item['is_default'] ? 'checked' : '' ?> data-realfilterid="<?php echo $filter_item['data_filter_id'] ?>"/>
						<label for="<?php echo $filter_item['data_filter_id'] ?>_config_id" style="display: inline">
							<?php echo rtrim($filter_item['label'], ':') ?>
						</label>
					</li>
				<?php endforeach ?>
                                </ul>
							
            </div>
            
        </form>
    </div>
</div>