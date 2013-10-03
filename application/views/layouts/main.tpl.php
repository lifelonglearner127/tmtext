<html lang="en">
<?php $this->load->view('elements/header.php');?>
<body>
    <div class="logo-bg">
        <div class="container">
            <div class="row-fluid">
                <div class="pull-left">
                    <div class="solution-logo-page"></div>
                </div>
                <div class="pull-right">
                    <?php
                        $this->load->view('elements/left_nav.php');
                    ?>
                </div>
            </div>
        </div>
    </div>
	<div class="container">
		<div class="row-fluid">
			<div class="main_container">
				<?php 
					//$this->load->view('elements/left_nav.php');
					if ($this->ion_auth->is_admin($this->ion_auth->get_user_id())) {
						$this->load->view('elements/right_nav.php');
					}
				?>
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