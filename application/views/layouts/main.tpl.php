<html lang="en">
<?php $this->load->view('elements/header.php');?>
<body>
	<div class="container">
		<div class="row-fluid">
			<div class="header_container">
				<div class="pull-left">
					<a href="<?php echo base_url();?>" class="logo_title">TrillionMonkeys</a>
				</div>
				<div class="pull-right">
					<a href="<?php echo base_url();?>auth/logout" class="log_out">Log Out</a>
				</div>
			</div>
		</div>
	</div>
	<div class="container">
		<div class="row-fluid">
			<div class="main_container">
				<?php $this->load->view('elements/left_nav.php');?>
				<?php $this->load->view('elements/right_nav.php');?>
				<div class="clearfix"></div>
				<div class="main_content">
					<?php echo $content;?>
				</div>
			</div>
		</div>
	</div>
	<?php $this->load->view('elements/footer.php');?>
</body>
</html>