<?php if($img_av !== false) { ?>
	<button onclick='openScreensModalSlider()' class='btn btn-primary'><i class='icon-eye-open icon-white'></i>&nbsp;View All</button>
	<div class="modal hide fade screens_modal_slider" id='screens_modal_slider'>
		<div class="modal-body">
			<ul id='screens_slider'>
				<?php foreach($img_av as $ka => $va) { ?>
					<li><div class='ss_slider_item_wrapper'><img src="<?php echo $va->img; ?>"></div></li>
				<?php } ?>
			</ul>
		</div>
	</div>
<?php } else { ?>
	<button class='btn btn-primary disabled'><i class='icon-eye-open icon-white'></i>&nbsp;View All</button>
<?php } ?>