# 05/31 Tatiana
ALTER TABLE `groups` ADD `default_controller` VARCHAR( 255 ) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL AFTER `auth_rules`;
UPDATE `tmeditor`.`groups` SET `default_controller` = 'editor/index' WHERE `groups`.`id` =1;
UPDATE `tmeditor`.`groups` SET `default_controller` = 'validate/index' WHERE `groups`.`id` =3;
UPDATE `tmeditor`.`groups` SET `default_controller` = 'editor/index' WHERE `groups`.`id` =4;
UPDATE `tmeditor`.`groups` SET `default_controller` = 'editor/index' WHERE `groups`.`id` =5;
UPDATE `tmeditor`.`groups` SET `default_controller` = 'editor/index' WHERE `groups`.`id` =6;

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
(3, 'customer', 'Customer', 'a:10:{s:14:"admin_customer";a:2:{s:5:"index";i:1;s:4:"save";i:1;}s:12:"admin_editor";a:1:{s:5:"index";i:1;}s:16:"admin_tag_editor";a:8:{s:5:"index";i:1;s:9:"file_list";i:1;s:9:"file_data";i:1;s:23:"get_product_description";i:1;s:14:"save_file_data";i:1;s:11:"delete_file";i:1;s:4:"save";i:1;s:6:"delete";i:1;}s:4:"auth";a:17:{s:5:"index";i:1;s:5:"login";i:1;s:6:"logout";i:1;s:15:"change_password";i:1;s:15:"forgot_password";i:1;s:14:"reset_password";i:1;s:8:"activate";i:1;s:10:"deactivate";i:1;s:11:"create_user";i:1;s:9:"edit_user";i:1;s:12:"create_group";i:1;s:10:"edit_group";i:1;s:15:"_get_csrf_nonce";i:1;s:17:"_valid_csrf_nonce";i:1;s:12:"_render_page";i:1;s:16:"reset_auth_rules";i:1;s:6:"groups";i:1;}s:8:"customer";a:1:{s:5:"index";i:1;}s:6:"editor";a:5:{s:5:"index";i:1;s:4:"save";i:1;s:6:"search";i:1;s:10:"attributes";i:1;s:8:"validate";i:1;}s:7:"measure";a:2:{s:5:"index";i:1;s:13:"analyzestring";i:1;}s:8:"settings";a:2:{s:5:"index";i:1;s:8:"examples";i:1;}s:6:"system";a:8:{s:5:"index";i:1;s:15:"system_accounts";i:1;s:12:"system_roles";i:1;s:12:"system_users";i:1;s:4:"save";i:1;s:10:"csv_import";i:1;s:13:"save_new_user";i:1;s:10:"save_roles";i:1;}s:8:"validate";a:4:{s:5:"index";i:1;s:4:"save";i:1;s:6:"search";i:1;s:10:"attributes";i:1;}}'),
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