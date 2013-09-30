<html lang="en">
<?php $this->load->view('elements/header.php');?>
<body>
    <div class="logo-bg">
        <div class="container">
            <div class="row-fluid">
                <div class="pull-left">
                    <div class="solution-logo-page"></div>
                </div>
            </div>
        </div>
    </div>
    <div class="navigation">
        <div class="container">
            <div class="row-fluid">
                <ul class="top-navigation">
                    <li class="pull-left"><a href="#">HOME</a></li>
                    <li class="pull-left"><a href="#">PRODUCT</a></li>
                    <li class="pull-left"><a href="#">COMPANY</a></li>
                    <li class="pull-right"><a href="<?php echo base_url() ?>index.php/auth/login">SIGN IN</a></li>
                    <!-- <li class="pull-right"><a href="http://dev.contentanalyticsinc.com/producteditor/index.php/auth/login<?php //echo site_url('auth/login');?>">SIGN IN</a></li> -->
                </ul>
            </div>
        </div>
    </div>
    <div class="below-nav">
        <div class="container">
            <div class="row-fluid right-bg">
                <div class="span8">
                    <div class="chart-img"></div>
                </div>
                <div class="span4 ">
                    <div class="text-center text-color-white">
                        Your Real-Time Content Solution
                    </div>
                    <div class="text-center">
                        <a href="#">
                            <?php echo img('../img/request-demo-btn.png', TRUE); ?>
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="bottom-border"></div>
	<div class="content-container">
        <div class="container margin-top-50">
            <div class="row-fluid" style="padding-left: 60px;">
                <div class="span4">
                    <?php echo img('../img/graphic.png', TRUE); ?>
                </div>
                <div class="span6">
                    <div class="mid-title">Assess the effectiveness of your existing content</div>
                    <p>Find out which content is SEO optimized and which isn’t, so you know what to work on and where to invest time and money.</p>
                    <p>Easily find out which product descriptions and category landing pages are effective, and which ones contain poor, unoptimized content, descriptions that are too short or too long, or contain mis-spellings.</p>
                </div>
            </div>
        </div>
	</div>
    <div class="ideas margin-top-50">
        <div class="container">
            <div class="row-fluid">
                <div class="span4 border-box">
                    <div class="ideas-title">Research the Competition</div>
                    <p>Compare your home page, department pages, category landing pages, and individual product pages to your competition.</p>
                    <a href="#" class="learn-more-btn">
                        <?php echo img('../img/bottom-button.png', TRUE); ?>
                    </a>
                    <div class="box-shadow-img"></div>
                </div>
                <div class="span4 border-box">
                    <div class="ideas-title">Create and Refresh Content</div>
                    <p>Designed for content creation, optimization, and refresh at scale, our workflow system manages thousands of content creators and editors.</p>
                    <a href="#" class="learn-more-btn">
                        <?php echo img('../img/bottom-button.png', TRUE); ?>
                    </a>
                    <div class="box-shadow-img"></div>
                </div>
                <div class="span4 border-box" style="min-height: 244px;">
                    <div class="ideas-title">Bring Meaning To Unstructured Web Site Data</div>
                    <p>Extract, compare, assess pricing and product information.</p>
                    <a href="#" class="learn-more-btn">
                        <?php echo img('../img/bottom-button.png', TRUE); ?>
                    </a>
                    <div class="box-shadow-img"></div>
                </div>
            </div>
        </div>
    </div>
    <div class="home-footer">
        <div class="container margin-top-50">
            <div class="row-fluid text-center">
                Copyright &COPY; <?php echo date('Y'); ?>. <b><?php echo isset($settings['company_name'])? $settings['company_name']:'' ?></b> All Rights Reserved.
            </div>
        </div> 
    </div>
</body>
</html>