<div class="container">
		<div class="row-fluid">
			<p class="pull-left mb_40">
				<small>Copyright &copy; 2013 <?php echo isset($settings['company_name'])? $settings['company_name']:'' ?> All Rights Reserved. </small>
			</p>
			<p class="pull-right mb_40">
				<small>Page rendered in <strong>{elapsed_time}</strong> seconds</small>
				<small><?php $this->load->view('elements/version.php');?></small>
			</p>
		</div>
	</div>
<script type="text/javascript">
	$(function(){
  	$(window).scroll(setTimeout(function(){
		      $('table#tblAssess').floatThead('reflow');	
  		}, 500));
	});
</script>