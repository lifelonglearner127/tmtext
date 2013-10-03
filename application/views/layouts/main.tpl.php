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
                    <ul class="menu">
                        <!--li class="active"><a href="#">HOME</a></li>
                        <li><a href="#">REPORTS</a></li>
                        <li><a href="#">NEWS</a></li>
                        <li><a href="#">ABOUT</a></li>
                        <li><a href="#">THE BOOK</a></li>
                        <li><a href="#">CONTACT</a></li-->
                        <li><a href="<?php echo site_url('auth/logout');?>">LOG OUT</a></li>
                        <!-- <li class="pull-right"><a href="http://dev.contentanalyticsinc.com/producteditor/index.php/auth/login<?php //echo site_url('auth/login');?>">SIGN IN</a></li> -->
                    </ul>
                </div>
            </div>
        </div>
    </div>
	<div class="container">
		<div class="row-fluid">
			<div class="main_container">
				<?php 
					$this->load->view('elements/left_nav.php');
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