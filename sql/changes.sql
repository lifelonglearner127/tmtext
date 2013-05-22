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

#--
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