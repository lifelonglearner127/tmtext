<?php if(count($img_av) !== 0) { ?>
	<button onclick='openScreensModalSlider()' class='btn btn-primary enabled-view-all'><i class='icon-eye-open icon-white'></i>&nbsp;View All</button>
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
	<button class='btn btn-primary disabled-view-all disabled'><i class='icon-eye-open icon-white'></i>&nbsp;View All</button>
<?php } ?>

<script type="text/javascript">
	$(document).ready(function() {
		$(".disabled-view-all").tooltip({
			placement: 'bottom',
			title: 'No images on current/selected week'
		});
	});
</script>