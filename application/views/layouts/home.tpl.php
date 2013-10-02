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
                        <li class="active"><a href="#">HOME</a></li>
                        <li><a href="#">REPORTS</a></li>
                        <li><a href="#">NEWS</a></li>
                        <li><a href="#">ABOUT</a></li>
                        <li><a href="#">THE BOOK</a></li>
                        <li><a href="#">CONTACT</a></li>
                        <li><a href="<?php echo base_url() ?>index.php/auth/login">SIGN IN</a></li>
                        <!-- <li class="pull-right"><a href="http://dev.contentanalyticsinc.com/producteditor/index.php/auth/login<?php //echo site_url('auth/login');?>">SIGN IN</a></li> -->
                    </ul>
                </div>
            </div>
        </div>
    </div>
    <div class="below-nav">
           <div class="container">
                <div class="left_block">
                        <span class="txt_container">REAL-TIME INSIGHT</span><br /><br />
                        <span class="txt_container">FOR <span class="txt_or_container">ECOMMERCE</span></span>
                        <p>Product Pricing, Selection and Content Marketing</p>
                        <a href="javascript:void(0)">LEARN MORE</a>
                </div>
           </div>
        <div class="right_block">
        </div>
    </div>
    <div class="content-container">
        <div class="container">
            <div class="row-fluid posts">
                <div class="span6">
                    <img src="<?php echo base_url() ?>img/cart-icon.jpg"><div class="mid-title">For Ecommerce<br />
                        <span>Lorem ispums</span></div>
                    <p>Find out which content is SEO optimized and which isn’t, so you know what to work on and where to invest time and money. Easily find out which product descriptions and category landing pages are effective, and which ones contain poor, unoptimized content., descriptions that are too short or too long, or contain mis-spellings.</p>
                    <a href="javascript:void(0)" class="learn_more">LEARN MORE</a>
                </div>
                <div class="span6">
                    <img src="<?php echo base_url() ?>img/brand-icon.jpg"><div class="mid-title">For Branding<br />
                        <span>Lorem ispums</span></div>
                    <p>Find out which content is SEO optimized and which isn’t, so you know what to work on and where to invest time and money. Easily find out which product descriptions and category landing pages are effective, and which ones contain poor, unoptimized content., descriptions that are too short or too long, or contain mis-spellings.</p>
                    <a href="javascript:void(0)" class="learn_more">LEARN MORE</a>
                </div>
            </div>
        </div>
        <div class="container">
            <div class="row-fluid general_posts">
                    <div class="span7">
                        <div class="mid-title">About Us</div>
                        <p>Find out which content is SEO optimized and which isn’t, so you know what to work on and where to invest time and money.</p>
                        <p>Easily find out which product descriptions and category landing pages are effective, and which ones contain poor, unoptimized content, descriptions that are too short or too long, or contain mis-spellings.</p>
                    </div>
                    <div class="span5">
                        <div class="mid-title">
                            News
                            <div class="pull-right">
                                <a href="javascript:void(0)"><img src="<?php echo base_url() ?>img/left-arrow.jpg"></a>
                                <a href="javascript:void(0)"><img src="<?php echo base_url() ?>img/right-arrow.jpg"></a>
                            </div>
                        </div>
                        <i>August 2012</i><br/>
                        <span class="sub-title">Lorem ispums content ispums content ispums content</span>
                        <p>Find out which content is SEO optimized and which isn’t, so you know what to work on and where to invest time and money.</p>
                        <p>Easily find out which product descriptions and category landing pages are effective, and which ones contain poor, unoptimized content, descriptions that are too short or too long, or contain mis-spellings.</p>
                    </div>
                    <!--div class="span12 ml_0 general_clients">
                        <div class="mid-title">Clients That Trust Us</div>
                        <a href="javascript:void(0)"><img src="<?php echo base_url() ?>img/splunk-icon.jpg"></a>
                        <a href="javascript:void(0)"><img src="<?php echo base_url() ?>img/qlik-icon.jpg"></a>
                        <a href="javascript:void(0)"><img src="<?php echo base_url() ?>img/recom-icon.jpg"></a>
                        <a href="javascript:void(0)"><img src="<?php echo base_url() ?>img/cloudera-icon.jpg"></a>
                        <a href="javascript:void(0)"><img src="<?php echo base_url() ?>img/mapr-icon.jpg"></a>
                    </div-->
        </div>
	</div>
    </div>
    <div class="clearfix"></div>

    <div class="home-footer">
        <div class="container margin-top-50">
            <div class="row-fluid">
                <div class="span7">
                    &COPY; <?php echo date('Y'); ?>. <?php echo isset($settings['company_name'])? $settings['company_name']:'' ?> All Rights Reserved.
                </div>
                <div class="span5">
                    We are social:
                    <a href="javascript:void(0)"><img src="<?php echo base_url() ?>img/facebook-hover-icon.jpg"></a>
                    <a href="javascript:void(0)"><img src="<?php echo base_url() ?>img/twitter-icon.jpg"></a>
                    <a href="javascript:void(0)"><img src="<?php echo base_url() ?>img/youtube-icon.jpg"></a>
                </div>
            </div>
        </div> 
    </div>
</body>
</html>