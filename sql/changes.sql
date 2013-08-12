# 08/08 Tatiana
CREATE TABLE IF NOT EXISTS `brands` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `created` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=81 ;

# 07/31 Tatiana
CREATE TABLE IF NOT EXISTS `site_categories` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `site_id` int(11) NOT NULL,
  `text` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `url` text COLLATE utf8_unicode_ci NOT NULL,
  `special` int(11) NOT NULL,
  `parent_text` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=269 ;

# 07/30 Tatiana
CREATE TABLE IF NOT EXISTS `best_sellers` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `date` datetime NOT NULL,
  `page_title` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `url` text COLLATE utf8_unicode_ci NOT NULL,
  `price` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `department` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `list_name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `product_name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;

ALTER TABLE `department_members` ADD `customer_id` INT NOT NULL AFTER `site_id`;
update `department_members` set `customer_id`=15 where `site`='amazon';
update `department_members` set `customer_id`=13 where `site`='overstock';
update `department_members` set `customer_id`=3 where `site`='bjs';
update `department_members` set `customer_id`=1 where `site`='walmart';
update `department_members` set `customer_id`=19 where `site`='bestbuy';
update `department_members` set `customer_id`=21 where `site`='wayfair';

# 07/17 Ruslan
# data in another file
 
CREATE TABLE IF NOT EXISTS `departments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(2000) COLLATE utf8_unicode_ci NOT NULL,
  `level` int(11) NOT NULL DEFAULT '0',
  `short_name` varchar(300) COLLATE utf8_unicode_ci NOT NULL,
  `parent_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=64 ;

CREATE TABLE IF NOT EXISTS `department_members` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `department_id` int(11) NOT NULL,
  `site` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `site_id` int(11) DEFAULT NULL,
  `text` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(2000) COLLATE utf8_unicode_ci NOT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `level` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=686 ;

# 07/15 Ruslan
CREATE TABLE IF NOT EXISTS `research_data_to_crawler_list` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `research_data_id` int(11) NOT NULL,
  `crawler_list_id` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;

# 07/14 Ruslan
INSERT INTO  `sites` (`id` ,`name` ,`url` ,`image_url`) VALUES (NULL ,  'OfficeDepot.com',  'http://www.officedepot.com',  'office-logo.png');

#07/09 Bojan
UPDATE  `setting_values` SET  `value` =  'Content Solutions, Inc.' WHERE  `setting_values`.`id` =1;
UPDATE  `setting_values` SET  `value` =  'Content Solutions, Inc.' WHERE  `setting_values`.`id` =2;
UPDATE  `setting_values` SET  `value` =  'Content Solutions' WHERE  `setting_values`.`id` =1 LIMIT 1
#07/08
CREATE TABLE IF NOT EXISTS `sites` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(256) NOT NULL,
  `url` varchar(255) NOT NULL,
  `image_url` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=20 ;

INSERT INTO `sites` (`id`, `name`, `url`, `image_url`) VALUES
(1, 'Walmart.com', 'http://walmart.com', 'walmart-logo.png'),
(2, 'Sears.com', 'http://sears.com', 'sears-logo.png'),
(3, 'BJs.com', 'http://bjs.com', 'bjs-logo.gif'),
(4, 'Staples.com', 'http://staples.com', 'staples-logo.png'),
(5, 'Overstock.com', 'http://overstock.com', 'overstock-logo.png'),
(6, 'TigerDirect.com', 'http://tigerdirect.com', 'tigerdirect-logo.jpg'),
(7, 'Amazon.com', 'http://amazon.com', 'amazon-logo.jpg'),
(8, 'toysrus.com', 'http://toysrus.com', 'toysrus-logo.gif'),
(9, 'bloomingdales.com', 'http://bloomingdales.com', 'bloomingdales-logo.gif'),
(10, 'bestbuy.com', 'http://bestbuy.com', 'bestbuy-logo.jpg');

#07/07 Tatiana
CREATE TABLE IF NOT EXISTS `items` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `batch_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `product_name` varchar(255) CHARACTER SET utf8 NOT NULL,
  `url` text CHARACTER SET utf8 NOT NULL,
  `short_description` text CHARACTER SET utf8 NOT NULL,
  `long_description` text CHARACTER SET utf8 NOT NULL,
  `priority` int(11) NOT NULL DEFAULT '50',
  `status` enum('created','edited','reviewed','delivered','customer_reviewed','customer_published') CHARACTER SET utf8 NOT NULL DEFAULT 'created',
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=5 ;

ALTER TABLE `customers` ADD `url` VARCHAR( 255 ) NOT NULL AFTER `name`;
UPDATE `customers` SET `url` = 'http://walmart.com' WHERE `customers`.`id` =1;
UPDATE `customers` SET `url` = 'http://sears.com' WHERE `customers`.`id` =2;
UPDATE `customers` SET `url` = 'http://bjs.com' WHERE `customers`.`id` =3;
UPDATE `customers` SET `url` = 'http://staples.com' WHERE `customers`.`id` =4;
UPDATE `customers` SET `url` = 'http://overstock.com' WHERE `customers`.`id` =13;
UPDATE `customers` SET `url` = 'http://tigerdirect.com' WHERE `customers`.`id` =14;
UPDATE `customers` SET `url` = 'http://amazon.com' WHERE `customers`.`id` =15;
UPDATE `customers` SET `url` = 'http://toysrus.com' WHERE `customers`.`id` =16;
UPDATE `customers` SET `url` = 'http://bloomingdales.com' WHERE `customers`.`id` =17;
INSERT INTO `c38_devtrillionmonkeyscom`.`customers` (`id`, `name`, `url`, `description`, `image_url`) VALUES (NULL, 'bestbuy.com', 'http://bestbuy.com', '0', 'bestbuy-logo.jpg');


INSERT INTO `customers` (`id`, `name`, `description`, `image_url`) VALUES (NULL , 'toysrus.com', '0', 'toysrus-logo.gif');
INSERT INTO `customers` (`id`, `name`, `description`, `image_url`) VALUES (NULL, 'bloomingdales.com', '', 'bloomingdales-logo.gif');

# 07/06 Tatiana
ALTER TABLE `customers` ADD `image_url` VARCHAR( 255 ) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL AFTER `description`;
UPDATE `customers` SET `image_url` = 'walmart-logo.png' WHERE `customers`.`id` =1;
UPDATE `customers` SET `image_url` = 'sears-logo.png' WHERE `customers`.`id` =2;
UPDATE `customers` SET `image_url` = 'bjs-logo.gif' WHERE `customers`.`id` =3;
UPDATE `customers` SET `image_url` = 'staples-logo.png' WHERE `customers`.`id` =4;
UPDATE `customers` SET `image_url` = 'overstock-logo.png' WHERE `customers`.`id` =13;
UPDATE `customers` SET `image_url` = 'tigerdirect-logo.jpg' WHERE `customers`.`id` =14;
INSERT INTO `customers` (`id` , `name`, `description`, `image_url`) VALUES (NULL , 'Amazon.com', '0', 'amazon-logo.jpg');

# 07/02 Ilya

CREATE TABLE IF NOT EXISTS `product_match_collections` (
  `id` INT NOT NULL ,
  `cid` VARCHAR(128) NULL ,
  `imported_data_id` INT NULL ,
  `url` TEXT NULL ,
  `sku` TEXT NULL ,
  PRIMARY KEY (`id`) 
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;

# 07/01 Tatiana
ALTER TABLE  `research_data` ADD  `short_description_wc` INT NOT NULL AFTER  `short_description`;
ALTER TABLE  `research_data` ADD  `long_description_wc` INT NOT NULL AFTER  `long_description`;

# 07/01 Pavel
CREATE TABLE IF NOT EXISTS `style_guide` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `style` text NOT NULL,
  `customer_id` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

# 07/01 Ruslan 

CREATE TABLE IF NOT EXISTS `similar_imported_data` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `imported_data_id` int(11) NOT NULL,
  `similar_group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;

CREATE TABLE IF NOT EXISTS `similar_groups` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `similarity` tinyint(1) NOT NULL,
  `percent` tinyint(2) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;


# 06/26 Ruslan
ALTER TABLE  `crawler_list` ADD  `updated` DATETIME NULL AFTER  `status`;
ALTER TABLE  `crawler_list` ADD  `imported_data_id` INT NULL AFTER  `category_id`;
ALTER TABLE  `imported_data_parsed` ADD  `revision` TINYINT NOT NULL DEFAULT  '1' AFTER  `value`;

# 06/24 Ruslan

CREATE TABLE IF NOT EXISTS `crawler_list_prices` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `price` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `crawler_list_id` int(10) unsigned NOT NULL,
  `created` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;

ALTER TABLE  `crawler_list` ADD  `category_id` INT UNSIGNED NOT NULL AFTER  `user_id`;


# 06/21 Tatiana
ALTER TABLE `batches` ADD `customer_id` INT NOT NULL AFTER `user_id`

# 06/16 Ilya
CREATE TABLE IF NOT EXISTS `products_compare` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `im_pr_f` INT NULL ,
  `im_pr_s` INT NULL ,
  `rate` TINYINT NULL ,
  `stamp` DATETIME NULL ,
  PRIMARY KEY (`id`) 
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;

# 06/15 Ruslan
CREATE TABLE IF NOT EXISTS `crawler_list` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `url` varchar(2000) COLLATE utf8_unicode_ci NOT NULL,
  `user_id` int(11) NOT NULL,
  `status` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `created` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;

# 06/12 Tatiana
UPDATE `groups` SET `default_controller` = 'measure/index' WHERE `groups`.`id` =1;
UPDATE `groups` SET `default_controller` = 'validate/index' WHERE `groups`.`id` =3;
UPDATE `groups` SET `default_controller` = 'measure/index' WHERE `groups`.`id` =4;
UPDATE `groups` SET `default_controller` = 'measure/index' WHERE `groups`.`id` =5;
UPDATE `groups` SET `default_controller` = 'measure/index' WHERE `groups`.`id` =6;

# 06/10 Tatiana
CREATE TABLE IF NOT EXISTS `research_box_position` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `position` varchar(100) CHARACTER SET utf8 NOT NULL,
  `box_id` varchar(255) CHARACTER SET utf8 NOT NULL,
  `width` int(11) NOT NULL DEFAULT '0',
  `height` int(11) NOT NULL DEFAULT '0',
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=9 ;

--
-- Dumping data for table `research_box_position`
--

INSERT INTO `research_box_position` (`id`, `user_id`, `position`, `box_id`, `width`, `height`, `created`, `modified`) VALUES
(1, 4, 'left', 'main_research_box', 0, 0, '2013-06-11 01:40:16', '2013-06-11 01:40:16'),
(2, 4, 'left', 'page_elements', 0, 0, '2013-06-11 01:40:32', '2013-06-11 01:40:32'),
(3, 4, 'left', 'related_keywords', 0, 0, '2013-06-11 01:43:29', '2013-06-11 01:43:29'),
(4, 4, 'left', 'seo_phrases', 0, 0, '2013-06-11 01:43:29', '2013-06-11 01:43:29'),
(5, 4, 'right', 'main_edit_box', 0, 0, '2013-06-11 01:44:39', '2013-06-11 01:44:39'),
(6, 4, 'right', 'keywords', 0, 0, '2013-06-11 01:44:39', '2013-06-11 01:44:39'),
(7, 4, 'right', 'results', 0, 0, '2013-06-11 01:45:33', '2013-06-11 01:45:33'),
(8, 4, 'right', 'descriptions', 0, 0, '2013-06-11 01:45:33', '2013-06-11 01:45:33');

# 06/05 Tatiana
CREATE TABLE IF NOT EXISTS `batches` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `title` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `user_id` int(11) NOT NULL,
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=3 ;


CREATE TABLE IF NOT EXISTS `research_data` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `batch_id` int(11) unsigned NOT NULL,
  `user_id` int(11) unsigned NOT NULL,
  `url` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `product_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `keyword1` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `keyword2` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `keyword3` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `meta_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `meta_description` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `meta_keywords` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `short_description` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `long_description` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `revision` tinyint(4) NOT NULL DEFAULT '0',
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `batch_id` (`batch_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ;

# 05/31 Tatiana
ALTER TABLE `groups` ADD `default_controller` VARCHAR( 255 ) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL AFTER `auth_rules`;
UPDATE `groups` SET `default_controller` = 'editor/index' WHERE `groups`.`id` =1;
UPDATE `groups` SET `default_controller` = 'validate/index' WHERE `groups`.`id` =3;
UPDATE `groups` SET `default_controller` = 'editor/index' WHERE `groups`.`id` =4;
UPDATE `groups` SET `default_controller` = 'editor/index' WHERE `groups`.`id` =5;
UPDATE `groups` SET `default_controller` = 'editor/index' WHERE `groups`.`id` =6;

# 05/30 Andrew <-- start
INSERT INTO `tmeditor.dev`.`customers` (`id` , `name` , `description`) VALUES ( NULL , 'Overstock.com', '0');
# 05/30 --> end

# 05/26 Tatiana <-- start
CREATE TABLE IF NOT EXISTS `tag_editor_rules` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `rule` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `category_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=34 ;
# 05/26 --> end

# 05/ 25
DELETE FROM `users_groups` WHERE `group_id`=2;

# 05/24 Andrew <-- start
DELETE FROM `tmeditor.dev`.`groups` WHERE `groups`.`id` = 2;

INSERT INTO `groups` (`id`, `name`, `description`, `auth_rules`) VALUES
(3, 'customer', 'Customer', 'a:14:{s:14:"admin_customer";a:4:{s:5:"index";b:1;s:13:"customer_list";b:1;s:4:"save";b:1;s:10:"upload_csv";b:1;}s:12:"admin_editor";a:1:{s:5:"index";b:1;}s:16:"admin_tag_editor";a:11:{s:5:"index";b:1;s:13:"category_list";b:1;s:9:"file_data";b:1;s:23:"get_product_description";b:1;s:14:"save_file_data";b:1;s:11:"delete_file";b:1;s:4:"save";b:1;s:6:"delete";b:1;s:10:"upload_dat";b:1;s:12:"import_rules";b:1;s:12:"export_rules";b:1;}s:4:"auth";a:24:{s:5:"index";b:1;s:17:"debug_seo_phrases";b:1;s:17:"ajaxcheckregemail";b:1;s:13:"ajaxregclient";b:1;s:9:"clientreg";b:1;s:13:"ajaxregwriter";b:1;s:8:"writereg";b:1;s:5:"login";b:1;s:6:"logout";b:1;s:15:"change_password";b:1;s:15:"forgot_password";b:1;s:14:"reset_password";b:1;s:8:"activate";b:1;s:10:"deactivate";b:1;s:11:"create_user";b:1;s:9:"edit_user";b:1;s:12:"create_group";b:1;s:10:"edit_group";b:1;s:15:"_get_csrf_nonce";b:1;s:17:"_valid_csrf_nonce";b:1;s:12:"_render_page";b:1;s:16:"reset_auth_rules";b:1;s:6:"groups";b:1;s:11:"getUserById";b:1;}s:8:"customer";a:7:{s:5:"index";b:1;s:19:"product_description";b:1;s:11:"style_guide";b:1;s:20:"getCustomersByUserId";b:1;s:12:"upload_style";b:1;s:18:"getStyleByCustomer";b:1;s:12:"saveTheStyle";b:1;}s:6:"editor";a:9:{s:5:"index";b:1;s:4:"save";b:1;s:13:"searchmeasure";b:1;s:15:"searchmeasuredb";b:1;s:13:"refreshheader";b:1;s:6:"search";b:1;s:10:"attributes";b:1;s:8:"validate";b:1;s:4:"home";b:1;}s:9:"job_board";a:3:{s:5:"index";b:1;s:15:"individual_jobs";b:1;s:7:"my_jobs";b:1;}s:7:"measure";a:20:{s:5:"index";b:1;s:8:"webshoot";b:1;s:14:"testscreenshot";b:1;s:19:"gethomepageyeardata";b:1;s:19:"gethomepageweekdata";b:1;s:16:"measure_products";b:1;s:19:"measure_departments";b:1;s:18:"measure_categories";b:1;s:15:"measure_pricing";b:1;s:17:"get_product_price";b:1;s:24:"getcustomerslist_general";b:1;s:13:"cisearchteram";b:1;s:8:"gridview";b:1;s:20:"getcustomerslist_new";b:1;s:16:"getsiteslist_new";b:1;s:16:"getcustomerslist";b:1;s:13:"analyzestring";b:1;s:15:"analyzekeywords";b:1;s:18:"searchmeasuredball";b:1;s:17:"attributesmeasure";b:1;}s:9:"page_test";a:1:{s:5:"index";b:1;}s:8:"research";a:30:{s:21:"search_results_bathes";b:1;s:5:"index";b:1;s:13:"category_list";b:1;s:12:"batches_list";b:1;s:14:"search_results";b:1;s:12:"create_batch";b:1;s:25:"assess_save_columns_state";b:1;s:15:"research_assess";b:1;s:15:"get_assess_info";b:1;s:16:"research_batches";b:1;s:16:"research_reports";b:1;s:9:"new_batch";b:1;s:17:"change_batch_name";b:1;s:17:"get_research_data";b:1;s:17:"get_research_info";b:1;s:20:"update_research_info";b:1;s:20:"delete_research_info";b:1;s:13:"save_in_batch";b:1;s:7:"getById";b:1;s:6:"export";b:1;s:10:"getBoxData";b:1;s:20:"delete_research_data";b:1;s:20:"getCustomersByUserId";b:1;s:12:"generateDesc";b:1;s:21:"filterCustomerByBatch";b:1;s:21:"filterBatchByCustomer";b:1;s:21:"filterStyleByCustomer";b:1;s:10:"upload_csv";b:1;s:10:"csv_import";b:1;s:12:"delete_batch";b:1;}s:8:"services";a:9:{s:21:"get_data_from_url_get";b:1;s:23:"get_data_from_text_post";b:1;s:6:"_remap";b:1;s:8:"response";b:1;s:3:"get";b:1;s:4:"post";b:1;s:3:"put";b:1;s:6:"delete";b:1;s:17:"validation_errors";b:1;}s:8:"settings";a:3:{s:5:"index";b:1;s:8:"examples";b:1;s:18:"save_columns_state";b:1;}s:12:"site_crawler";a:10:{s:5:"index";b:1;s:6:"upload";b:1;s:3:"add";b:1;s:6:"delete";b:1;s:6:"update";b:1;s:8:"new_urls";b:1;s:8:"all_urls";b:1;s:9:"crawl_new";b:1;s:12:"download_one";b:1;s:9:"crawl_all";b:1;}s:6:"system";a:39:{s:5:"index";b:1;s:16:"recordcollection";b:1;s:17:"testattributesext";b:1;s:23:"deleteproductsvotedpair";b:1;s:33:"renewcomparerightsidefromdropdown";b:1;s:21:"renewcomparerightside";b:1;s:20:"renewallcomparesides";b:1;s:20:"getmatchnowinterface";b:1;s:23:"getproductscomparevoted";b:1;s:19:"votecompareproducts";b:1;s:18:"getcompareproducts";b:1;s:20:"system_productsmatch";b:1;s:14:"system_compare";b:1;s:15:"system_accounts";b:1;s:12:"system_roles";b:1;s:12:"system_users";b:1;s:4:"save";b:1;s:21:"save_account_deafults";b:1;s:10:"csv_import";b:1;s:13:"save_new_user";b:1;s:10:"save_roles";b:1;s:18:"jqueryAutocomplete";b:1;s:11:"update_user";b:1;s:10:"upload_csv";b:1;s:10:"upload_img";b:1;s:16:"get_batch_review";b:1;s:19:"update_batch_review";b:1;s:19:"delete_batch_review";b:1;s:12:"getBatchById";b:1;s:12:"batch_review";b:1;s:10:"sites_view";b:1;s:19:"generate_attributes";b:1;s:22:"similarity_calculation";b:1;s:13:"get_site_info";b:1;s:12:"add_new_site";b:1;s:11:"delete_site";b:1;s:16:"update_site_logo";b:1;s:16:"update_site_info";b:1;s:15:"delete_sitelogo";b:1;}}'),
(4, 'customer_owner', 'Customer Account Owner', 'a:10:{s:14:"admin_customer";a:2:{s:5:"index";i:1;s:4:"save";i:1;}s:12:"admin_editor";a:1:{s:5:"index";i:1;}s:16:"admin_tag_editor";a:8:{s:5:"index";i:1;s:9:"file_list";i:1;s:9:"file_data";i:1;s:23:"get_product_description";i:1;s:14:"save_file_data";i:1;s:11:"delete_file";i:1;s:4:"save";i:1;s:6:"delete";i:1;}s:4:"auth";a:17:{s:5:"index";i:1;s:5:"login";i:1;s:6:"logout";i:1;s:15:"change_password";i:1;s:15:"forgot_password";i:1;s:14:"reset_password";i:1;s:8:"activate";i:1;s:10:"deactivate";i:1;s:11:"create_user";i:1;s:9:"edit_user";i:1;s:12:"create_group";i:1;s:10:"edit_group";i:1;s:15:"_get_csrf_nonce";i:1;s:17:"_valid_csrf_nonce";i:1;s:12:"_render_page";i:1;s:16:"reset_auth_rules";i:1;s:6:"groups";i:1;}s:8:"customer";a:1:{s:5:"index";i:1;}s:6:"editor";a:5:{s:5:"index";i:1;s:4:"save";i:1;s:6:"search";i:1;s:10:"attributes";i:1;s:8:"validate";i:1;}s:7:"measure";a:2:{s:5:"index";i:1;s:13:"analyzestring";i:1;}s:8:"settings";a:2:{s:5:"index";i:1;s:8:"examples";i:1;}s:6:"system";a:8:{s:5:"index";i:1;s:15:"system_accounts";i:1;s:12:"system_roles";i:1;s:12:"system_users";i:1;s:4:"save";i:1;s:10:"csv_import";i:1;s:13:"save_new_user";i:1;s:10:"save_roles";i:1;}s:8:"validate";a:4:{s:5:"index";i:1;s:4:"save";i:1;s:6:"search";i:1;s:10:"attributes";i:1;}}'),
(5, 'editor', 'Editor', 'a:10:{s:14:"admin_customer";a:2:{s:5:"index";i:1;s:4:"save";i:1;}s:12:"admin_editor";a:1:{s:5:"index";i:1;}s:16:"admin_tag_editor";a:8:{s:5:"index";i:1;s:9:"file_list";i:1;s:9:"file_data";i:1;s:23:"get_product_description";i:1;s:14:"save_file_data";i:1;s:11:"delete_file";i:1;s:4:"save";i:1;s:6:"delete";i:1;}s:4:"auth";a:17:{s:5:"index";i:1;s:5:"login";i:1;s:6:"logout";i:1;s:15:"change_password";i:1;s:15:"forgot_password";i:1;s:14:"reset_password";i:1;s:8:"activate";i:1;s:10:"deactivate";i:1;s:11:"create_user";i:1;s:9:"edit_user";i:1;s:12:"create_group";i:1;s:10:"edit_group";i:1;s:15:"_get_csrf_nonce";i:1;s:17:"_valid_csrf_nonce";i:1;s:12:"_render_page";i:1;s:16:"reset_auth_rules";i:1;s:6:"groups";i:1;}s:8:"customer";a:1:{s:5:"index";i:1;}s:6:"editor";a:5:{s:5:"index";i:1;s:4:"save";i:1;s:6:"search";i:1;s:10:"attributes";i:1;s:8:"validate";i:1;}s:7:"measure";a:2:{s:5:"index";i:0;s:13:"analyzestring";i:0;}s:8:"settings";a:2:{s:5:"index";i:1;s:8:"examples";i:1;}s:6:"system";a:8:{s:5:"index";i:1;s:15:"system_accounts";i:1;s:12:"system_roles";i:1;s:12:"system_users";i:1;s:4:"save";i:1;s:10:"csv_import";i:1;s:13:"save_new_user";i:1;s:10:"save_roles";i:1;}s:8:"validate";a:4:{s:5:"index";i:1;s:4:"save";i:1;s:6:"search";i:1;s:10:"attributes";i:1;}}'),
(6, 'editor_owner', 'Editor Account Owner', 'a:10:{s:14:"admin_customer";a:2:{s:5:"index";i:1;s:4:"save";i:1;}s:12:"admin_editor";a:1:{s:5:"index";i:1;}s:16:"admin_tag_editor";a:8:{s:5:"index";i:1;s:9:"file_list";i:1;s:9:"file_data";i:1;s:23:"get_product_description";i:1;s:14:"save_file_data";i:1;s:11:"delete_file";i:1;s:4:"save";i:1;s:6:"delete";i:1;}s:4:"auth";a:17:{s:5:"index";i:1;s:5:"login";i:1;s:6:"logout";i:1;s:15:"change_password";i:1;s:15:"forgot_password";i:1;s:14:"reset_password";i:1;s:8:"activate";i:1;s:10:"deactivate";i:1;s:11:"create_user";i:1;s:9:"edit_user";i:1;s:12:"create_group";i:1;s:10:"edit_group";i:1;s:15:"_get_csrf_nonce";i:1;s:17:"_valid_csrf_nonce";i:1;s:12:"_render_page";i:1;s:16:"reset_auth_rules";i:1;s:6:"groups";i:1;}s:8:"customer";a:1:{s:5:"index";i:1;}s:6:"editor";a:5:{s:5:"index";i:1;s:4:"save";i:1;s:6:"search";i:1;s:10:"attributes";i:1;s:8:"validate";i:1;}s:7:"measure";a:2:{s:5:"index";i:0;s:13:"analyzestring";i:0;}s:8:"settings";a:2:{s:5:"index";i:1;s:8:"examples";i:1;}s:6:"system";a:8:{s:5:"index";i:1;s:15:"system_accounts";i:1;s:12:"system_roles";i:1;s:12:"system_users";i:1;s:4:"save";i:1;s:10:"csv_import";i:1;s:13:"save_new_user";i:1;s:10:"save_roles";i:1;}s:8:"validate";a:4:{s:5:"index";i:1;s:4:"save";i:1;s:6:"search";i:1;s:10:"attributes";i:1;}}');
# 05/24 --> end

# 05/24 Ruslan
ALTER TABLE  `imported_data` CHANGE  `company_id`  `company_id` INT( 11 ) NULL;

ALTER TABLE  `imported_data` ADD  `category_id` INT UNSIGNED NULL AFTER  `company_id`;
 
CREATE TABLE IF NOT EXISTS `categories` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;

# 05/23 Andrew <-- start
CREATE TABLE IF NOT EXISTS `customers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(256) NOT NULL,
  `description` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

INSERT INTO `customers` (`id`, `name`, `description`) VALUES
(1, 'Walmart.com', 0),
(2, 'Sears.com', 0),
(3, 'BJs.com', 0),
(4, 'Staples.com', 0);

CREATE TABLE IF NOT EXISTS `users_to_customers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`,`customer_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;
# 05/23 --> end

# 05/22 Ruslan
ALTER TABLE  `imported_data` ADD  `company_id` INT NOT NULL AFTER  `imported_data_attribute_id`

CREATE TABLE IF NOT EXISTS `companies` (
  `id` int(10) unsigned NOT NULL DEFAULT '0',
  `name` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  `description` varchar(1000) COLLATE utf8_unicode_ci NOT NULL,
  `image` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE IF NOT EXISTS `imported_data_parsed` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `imported_data_id` int(10) unsigned NOT NULL,
  `key` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `value` text COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `imported_data_id` (`imported_data_id`,`key`),
  KEY `imported_data_id_2` (`imported_data_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;

CREATE TABLE IF NOT EXISTS `tag_editor_descriptions` (
 `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
 `user_id` int(11) NOT NULL,
 `description` text COLLATE utf8_unicode_ci NOT NULL,
 `created` datetime NOT NULL,
 `modified` datetime NOT NULL,
 PRIMARY KEY (`id`),
 KEY `user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;

# 05/18
CREATE TABLE IF NOT EXISTS `imported_data` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `key` varchar(40) COLLATE utf8_unicode_ci NOT NULL,
  `imported_data_attribute_id` int(11) unsigned DEFAULT NULL,
  `data` text COLLATE utf8_unicode_ci NOT NULL,
  `created` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `key` (`key`),
  KEY `imported_data_attribute_id` (`imported_data_attribute_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE IF NOT EXISTS `imported_data_attributes` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `attributes` text COLLATE utf8_unicode_ci NOT NULL,
  `created` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# 05/13 Ruslan
ALTER TABLE  `groups` ADD  `auth_rules` TEXT NOT NULL DEFAULT  '';

# 05/16 Ruslan
UPDATE  `groups` SET  `auth_rules` = 'a:8:{s:14:"admin_customer";a:1:{s:5:"index";b:1;}s:12:"admin_editor";a:1:{s:5:"index";b:1;}s:16:"admin_tag_editor";a:5:{s:5:"index";b:1;s:9:"file_list";b:1;s:9:"file_data";b:1;s:23:"get_product_description";b:1;s:14:"save_file_data";b:1;}s:4:"auth";a:15:{s:5:"index";b:1;s:5:"login";b:1;s:6:"logout";b:1;s:15:"change_password";b:1;s:15:"forgot_password";b:1;s:14:"reset_password";b:1;s:8:"activate";b:1;s:10:"deactivate";b:1;s:11:"create_user";b:1;s:9:"edit_user";b:1;s:12:"create_group";b:1;s:10:"edit_group";b:1;s:15:"_get_csrf_nonce";b:1;s:17:"_valid_csrf_nonce";b:1;s:12:"_render_page";b:1;}s:8:"customer";a:1:{s:5:"index";b:1;}s:6:"editor";a:5:{s:5:"index";b:1;s:4:"save";b:1;s:6:"search";b:1;s:10:"attributes";b:1;s:8:"validate";b:1;}s:8:"settings";a:2:{s:5:"index";b:1;s:8:"examples";b:1;}s:6:"system";a:2:{s:5:"index";b:1;s:4:"save";b:1;}}' WHERE  `groups`.`id` =1;

# 05/12 
ALTER TABLE  `saved_descriptions` CHANGE  `key`  `parent_id` INT UNSIGNED NOT NULL DEFAULT  '0';


#08/06 Max
DROP TABLE `similar_product_groups`;
CREATE TABLE  `tmeditor`.`similar_product_groups` (
`id` INT NOT NULL
) ENGINE = MYISAM ;


#08/07 Max
ALTER TABLE  `similar_product_groups` ADD UNIQUE (
`id`
)

#08/11 Max

DROP TABLE IF EXISTS `similar_product_groups`;

CREATE TABLE `similar_product_groups` (
  `ipd_id` int(10) unsigned NOT NULL,
  UNIQUE KEY `fk_imp_id` (`ipd_id`),
  CONSTRAINT `fk_imp_id_group_id` FOREIGN KEY (`ipd_id`) REFERENCES `imported_data` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;




DROP TABLE IF EXISTS `similar_data`;

CREATE TABLE `similar_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imported_data_id` int(11) NOT NULL,
  `group_id` int(10) unsigned NOT NULL,
  `black_list` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_group_id` (`group_id`),
  CONSTRAINT `fk_group_id` FOREIGN KEY (`group_id`) REFERENCES `imported_data` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=948 DEFAULT CHARSET=utf8;


CREATE TABLE IF NOT EXISTS `reports` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `body` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=2 ;

INSERT INTO `reports` (`id`, `name`, `body`) VALUES
(1, 'Assess', '<h1>eCommerce Report Prepared for #customer name#</h1>\n#date#<br />\n<h2>Overview</h2>\n<p>The Content Analytics eCommerce Product Report provides you with detailed insight into:</p>\n<ul>\n• On-site content marketing effectiveness for selected products and product categories<br />\n• Pricing competitiveness<br />\n• Product selection vis a vis competitors on a category by category and best-seller basis<br />\n<p>No more investing time and effort to optimize your product content only to have visitors bounce because your prices\naren’t competitive. Understand how your product catalog compares so you can offer the best selection possible.</p>\n<p>Additional reports are available for Departments & Categories, Home Pages, and selected Brands.</p>\n<b>On-site content marketing effectiveness</b><br />\nFocus on products and pages most in need of content optimization using detailed analysis of duplicate content, SEO\nkeyword density, and product description length<br /><br />\n<b>Pricing competitiveness</b><br />\nPrice is one of the main reasons that users bounce off eCommerce sites. With our price analysis you can ensure your\nproducts are priced neither too high--nor too low.<br /><br />\n<b>Product selection</b><br />\nCompeting in a given category? We monitor competitor sites so you can ensure you carry the proper mix of products in\na given category, especially those products that are best-sellers on other sites.<br /><br />');
