CREATE TABLE IF NOT EXISTS `batches` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `title` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `user_id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=148 ;
CREATE TABLE IF NOT EXISTS `best_sellers` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `site_id` int(11) NOT NULL,
  `date` datetime NOT NULL,
  `page_title` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `url` text COLLATE utf8_unicode_ci NOT NULL,
  `brand` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `price` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `rank` int(11) NOT NULL,
  `department` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `list_name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `product_name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `listprice` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=4448 ;
CREATE TABLE IF NOT EXISTS `brands` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `created` datetime NOT NULL,
  `company_id` int(11) NOT NULL,
  `brand_type` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `brand_type` (`brand_type`),
  KEY `company_id` (`company_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=24 ;
CREATE TABLE IF NOT EXISTS `brand_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `brand_id` int(11) unsigned NOT NULL,
  `date` date NOT NULL,
  `tweet_count` int(11) NOT NULL,
  `twitter_followers` int(11) NOT NULL,
  `following` int(11) NOT NULL,
  `youtube_video_count` int(11) NOT NULL,
  `youtube_view_count` int(11) NOT NULL,
  `total_tweets` int(11) NOT NULL,
  `total_youtube_videos` int(11) NOT NULL,
  `total_youtube_views` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `brand_id` (`brand_id`),
  KEY `brand_id_2` (`brand_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=30 ;
CREATE TABLE IF NOT EXISTS `brand_data_summary` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `brand_id` int(11) unsigned NOT NULL,
  `total_tweets` int(11) NOT NULL DEFAULT '0',
  `total_youtube_videos` int(11) NOT NULL DEFAULT '0',
  `total_youtube_views` int(11) NOT NULL DEFAULT '0',
  `IR500Rank` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `brand_id` (`brand_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=11 ;
CREATE TABLE IF NOT EXISTS `brand_types` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=3 ;
CREATE TABLE IF NOT EXISTS `categories` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=10 ;
CREATE TABLE IF NOT EXISTS `ci_home_page_recipients` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(512) COLLATE utf8_unicode_ci DEFAULT NULL,
  `day` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL,
  `stamp` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=33 ;
CREATE TABLE IF NOT EXISTS `companies` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  `description` varchar(1000) COLLATE utf8_unicode_ci NOT NULL,
  `image` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `IR500Rank` int(11) NOT NULL DEFAULT '0',
  `Twitter` varchar(32) COLLATE utf8_unicode_ci DEFAULT NULL,
  `Youtube` varchar(32) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;
CREATE TABLE IF NOT EXISTS `crawler_instances` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `instance_id` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `instance_type` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `state_name` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `public_dns_name` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=182 ;
CREATE TABLE IF NOT EXISTS `crawler_list` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `url` varchar(2000) COLLATE utf8_unicode_ci NOT NULL,
  `user_id` int(11) NOT NULL,
  `category_id` int(10) unsigned NOT NULL,
  `imported_data_id` int(11) DEFAULT NULL,
  `status` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `updated` datetime DEFAULT NULL,
  `created` datetime NOT NULL,
  `snap` varchar(512) COLLATE utf8_unicode_ci DEFAULT NULL,
  `snap_date` datetime DEFAULT NULL,
  `snap_state` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `crawler_list_imp_data_id` (`imported_data_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=52537 ;
CREATE TABLE IF NOT EXISTS `crawler_list_prices` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `price` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `crawler_list_id` int(10) unsigned NOT NULL,
  `created` datetime NOT NULL,
  `revision` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=185786 ;
CREATE TABLE IF NOT EXISTS `customers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(256) NOT NULL,
  `url` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `image_url` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=30 ;
CREATE TABLE IF NOT EXISTS `departments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(2000) COLLATE utf8_unicode_ci NOT NULL,
  `level` int(11) NOT NULL DEFAULT '0',
  `short_name` varchar(300) COLLATE utf8_unicode_ci NOT NULL,
  `parent_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=288 ;
CREATE TABLE IF NOT EXISTS `department_members` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `department_id` int(11) NOT NULL,
  `site_id` int(11) DEFAULT NULL,
  `customer_id` int(11) NOT NULL,
  `text` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(2000) COLLATE utf8_unicode_ci NOT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `level` int(11) DEFAULT NULL,
  `description_words` int(11) NOT NULL,
  `title_seo_keywords` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `title_keyword_description_count` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `title_keyword_description_density` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `user_seo_keywords` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `user_keyword_description_count` varchar(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '0',
  `user_keyword_description_density` double NOT NULL DEFAULT '0',
  `description_text` text COLLATE utf8_unicode_ci NOT NULL,
  `description_title` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `flag` enum('ready','deleted') COLLATE utf8_unicode_ci NOT NULL DEFAULT 'ready',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=5555 ;
CREATE TABLE IF NOT EXISTS `duplicate_content_new` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imported_data_id` int(11) NOT NULL,
  `long_original` float NOT NULL,
  `short_original` float NOT NULL,
  `revision` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=5645 ;
CREATE TABLE IF NOT EXISTS `groups` (
  `id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `description` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `auth_rules` text COLLATE utf8_unicode_ci NOT NULL,
  `default_controller` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=7 ;
CREATE TABLE IF NOT EXISTS `home_pages_config` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(256) COLLATE utf8_unicode_ci DEFAULT NULL,
  `value` varchar(256) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=4 ;
CREATE TABLE IF NOT EXISTS `imported_data` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `key` varchar(40) COLLATE utf8_unicode_ci NOT NULL,
  `imported_data_attribute_id` int(11) unsigned DEFAULT NULL,
  `company_id` int(11) DEFAULT NULL,
  `category_id` int(10) unsigned DEFAULT NULL,
  `data` text COLLATE utf8_unicode_ci NOT NULL,
  `created` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `key` (`key`),
  KEY `imported_data_attribute_id` (`imported_data_attribute_id`),
  KEY `company_id` (`company_id`),
  KEY `category_id` (`category_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=60288 ;
CREATE TABLE IF NOT EXISTS `imported_data_attributes` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `attributes` text COLLATE utf8_unicode_ci NOT NULL,
  `created` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;
CREATE TABLE IF NOT EXISTS `imported_data_parsed` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `imported_data_id` int(10) unsigned NOT NULL,
  `key` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `value` text COLLATE utf8_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `revision` tinyint(4) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `imported_data_id` (`imported_data_id`,`key`),
  KEY `imported_data_id_2` (`imported_data_id`),
  KEY `key` (`key`),
  KEY `model` (`model`),
  KEY `revision` (`revision`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1732673 ;
CREATE TABLE IF NOT EXISTS `imported_data_parsed_archived` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `imported_data_id` int(10) unsigned NOT NULL,
  `key` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `value` text COLLATE utf8_unicode_ci NOT NULL,
  `model` varchar(40) COLLATE utf8_unicode_ci DEFAULT NULL,
  `revision` tinyint(4) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `imported_data_id` (`imported_data_id`,`key`),
  KEY `imported_data_id_2` (`imported_data_id`),
  KEY `key` (`key`),
  KEY `model` (`model`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=2171213 ;
CREATE TABLE IF NOT EXISTS `imported_data_parsed_copy` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `imported_data_id` int(10) unsigned NOT NULL,
  `key` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `value` text COLLATE utf8_unicode_ci NOT NULL,
  `model` varchar(40) COLLATE utf8_unicode_ci DEFAULT NULL,
  `revision` tinyint(4) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `imported_data_id` (`imported_data_id`,`key`),
  KEY `imported_data_id_2` (`imported_data_id`),
  KEY `key` (`key`),
  KEY `model` (`model`),
  KEY `revision` (`revision`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=492153 ;
CREATE TABLE IF NOT EXISTS `items` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `batch_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `product_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `keyword1` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `keyword2` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `keyword3` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `meta_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `meta_keywords` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `meta_description` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `short_description` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `short_description_wc` int(11) NOT NULL,
  `long_description` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `long_description_wc` int(11) NOT NULL,
  `priority` int(11) NOT NULL DEFAULT '50',
  `status` enum('created','edited','reviewed','delivered','customer_reviewed','customer_published') CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL DEFAULT 'created',
  `revision` tinyint(4) NOT NULL,
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=34 ;
CREATE TABLE IF NOT EXISTS `keywords` (
  `id` int(50) NOT NULL AUTO_INCREMENT,
  `imported_data_id` int(50) NOT NULL,
  `word_num` int(50) NOT NULL,
  `keyword` varchar(70) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=20 ;
CREATE TABLE IF NOT EXISTS `keywords_new` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imported_data_id` int(11) NOT NULL,
  `primary` varchar(30) NOT NULL,
  `secondary` varchar(50) NOT NULL,
  `tertiary` varchar(60) NOT NULL,
  `revision` int(11) NOT NULL,
  `create_date` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=88 ;
CREATE TABLE IF NOT EXISTS `keyword_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `keyword` varchar(255) NOT NULL,
  `volume` int(11) NOT NULL,
  `search_engine` int(11) NOT NULL,
  `region` int(11) NOT NULL,
  `create_date` int(11) NOT NULL,
  `data_source_id` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=8 ;
CREATE TABLE IF NOT EXISTS `keyword_data_sources` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `data_source_name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ;
CREATE TABLE IF NOT EXISTS `kwsync_queue_list` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `meta_kw_rank_source_id` int(11) DEFAULT NULL,
  `kw` varchar(512) COLLATE utf8_unicode_ci DEFAULT NULL,
  `url` varchar(512) COLLATE utf8_unicode_ci DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `stamp` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=4 ;
CREATE TABLE IF NOT EXISTS `meta_kw_rank_source` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imported_data_id` int(11) DEFAULT NULL,
  `url` varchar(512) COLLATE utf8_unicode_ci DEFAULT NULL,
  `statistics_new_id` int(11) DEFAULT NULL,
  `batch_id` int(11) DEFAULT NULL,
  `kw` varchar(256) COLLATE utf8_unicode_ci DEFAULT NULL,
  `kw_prc` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL,
  `kw_count` int(11) DEFAULT NULL,
  `rank_json_encode` text COLLATE utf8_unicode_ci,
  `highest_rank` text COLLATE utf8_unicode_ci,
  `rank` int(11) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `stamp` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=19 ;
CREATE TABLE IF NOT EXISTS `migrations` (
  `version` int(3) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
CREATE TABLE IF NOT EXISTS `nb_email_notify` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(512) COLLATE utf8_unicode_ci DEFAULT NULL,
  `stamp` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=4 ;
CREATE TABLE IF NOT EXISTS `notfoundurls` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(5000) DEFAULT NULL,
  `proc` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;
CREATE TABLE IF NOT EXISTS `pages` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `title` varchar(50) DEFAULT NULL,
  `controller` varchar(50) DEFAULT NULL,
  `view` varchar(50) DEFAULT '',
  `url` varchar(50) DEFAULT NULL,
  `menu` varchar(50) DEFAULT NULL,
  `order` int(2) unsigned DEFAULT NULL,
  `require_login` int(1) unsigned DEFAULT '0',
  `group_id` int(10) unsigned DEFAULT '0',
  `parent_id` int(10) unsigned DEFAULT NULL,
  `active` int(1) unsigned DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=17 ;
CREATE TABLE IF NOT EXISTS `products_compare` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `im_pr_f` int(11) DEFAULT NULL,
  `im_pr_s` int(11) DEFAULT NULL,
  `rate` tinyint(4) DEFAULT NULL,
  `stamp` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;
CREATE TABLE IF NOT EXISTS `product_match_collections` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cid` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `imported_data_id` int(11) DEFAULT NULL,
  `url` text COLLATE utf8_unicode_ci,
  `sku` text COLLATE utf8_unicode_ci,
  `crawl_st` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;
CREATE TABLE IF NOT EXISTS `ranking_api_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `site` varchar(512) COLLATE utf8_unicode_ci DEFAULT NULL,
  `keyword` varchar(512) COLLATE utf8_unicode_ci DEFAULT NULL,
  `location` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL,
  `engine` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL,
  `rank_json_encode` text COLLATE utf8_unicode_ci,
  `rank` int(11) DEFAULT NULL,
  `stamp` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=101 ;
CREATE TABLE IF NOT EXISTS `regions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `region` varchar(255) CHARACTER SET utf8 NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=173 ;
CREATE TABLE IF NOT EXISTS `reports` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `cover_page_name` varchar(100) NOT NULL,
  `cover_page_order` int(11) NOT NULL DEFAULT '1',
  `cover_page_layout` enum('L','P') NOT NULL DEFAULT 'L',
  `cover_page_body` text NOT NULL,
  `recommendations_page_name` varchar(100) NOT NULL,
  `recommendations_page_order` int(11) NOT NULL DEFAULT '9998',
  `recommendations_page_layout` enum('L','P') NOT NULL DEFAULT 'L',
  `recommendations_page_body` text NOT NULL,
  `about_page_name` varchar(100) NOT NULL,
  `about_page_order` int(11) NOT NULL DEFAULT '9999',
  `about_page_layout` enum('L','P') NOT NULL DEFAULT 'L',
  `about_page_body` text NOT NULL,
  `parts` varchar(1000) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=2 ;
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
  `short_description_wc` int(11) NOT NULL,
  `long_description` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `long_description_wc` int(11) NOT NULL,
  `priority` int(11) NOT NULL DEFAULT '50',
  `status` enum('created','edited','reviewed','delivered','customer_reviewed','customer_published') CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL DEFAULT 'created',
  `revision` tinyint(4) NOT NULL DEFAULT '0',
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  `include_in_assess_report` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `batch_id` (`batch_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=98474 ;
CREATE TABLE IF NOT EXISTS `research_data_to_crawler_list` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `research_data_id` int(11) NOT NULL,
  `crawler_list_id` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=98371 ;
CREATE TABLE IF NOT EXISTS `rules` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `original_sentence` text NOT NULL,
  `rule` varchar(2000) NOT NULL,
  `template_sentence` text NOT NULL,
  `url` varchar(400) NOT NULL,
  `sentence_position` int(11) NOT NULL,
  `rule_intensity` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1899 ;
CREATE TABLE IF NOT EXISTS `saved_descriptions` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `parent_id` int(10) unsigned NOT NULL DEFAULT '0',
  `title` varchar(250) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `description` text COLLATE utf8_unicode_ci NOT NULL,
  `revision` tinyint(4) NOT NULL DEFAULT '0',
  `user_id` int(10) unsigned NOT NULL,
  `search_id` int(10) unsigned NOT NULL DEFAULT '0',
  `created` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `users_id` (`user_id`,`search_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;
CREATE TABLE IF NOT EXISTS `searches` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `search` varchar(45) COLLATE utf8_unicode_ci NOT NULL,
  `attributes` text COLLATE utf8_unicode_ci NOT NULL,
  `created` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=3 ;
CREATE TABLE IF NOT EXISTS `search_engine` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `search_engine` varchar(30) CHARACTER SET utf8 NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=4 ;
CREATE TABLE IF NOT EXISTS `settings` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `key` varchar(150) COLLATE utf8_unicode_ci NOT NULL,
  `description` varchar(1000) COLLATE utf8_unicode_ci NOT NULL,
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=269 ;
CREATE TABLE IF NOT EXISTS `setting_values` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `setting_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `value` varchar(3000) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=45 ;
CREATE TABLE IF NOT EXISTS `similar_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imported_data_id` int(11) NOT NULL,
  `group_id` int(10) unsigned NOT NULL,
  `black_list` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_group_id` (`group_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=3240 ;
CREATE TABLE IF NOT EXISTS `similar_groups` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `similarity` tinyint(1) NOT NULL,
  `percent` tinyint(2) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=156 ;
CREATE TABLE IF NOT EXISTS `similar_imported_data` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `imported_data_id` int(11) NOT NULL,
  `similar_group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=473 ;
CREATE TABLE IF NOT EXISTS `similar_item` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `item1` int(10) unsigned NOT NULL,
  `item2` int(10) unsigned NOT NULL,
  `same` int(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `item1` (`item1`,`item2`),
  KEY `item2` (`item2`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=6827 ;
CREATE TABLE IF NOT EXISTS `similar_product_groups` (
  `ipd_id` int(10) unsigned NOT NULL,
  UNIQUE KEY `fk_imp_id` (`ipd_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
CREATE TABLE IF NOT EXISTS `sites` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(256) NOT NULL,
  `url` varchar(255) NOT NULL,
  `image_url` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=36 ;
CREATE TABLE IF NOT EXISTS `site_categories` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `parent_id` int(11) NOT NULL,
  `site_id` int(11) NOT NULL,
  `text` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `url` text COLLATE utf8_unicode_ci NOT NULL,
  `special` int(11) NOT NULL,
  `parent_text` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `department_members_id` int(11) NOT NULL,
  `level` int(11) NOT NULL,
  `nr_products` int(11) NOT NULL,
  `description_words` int(11) NOT NULL,
  `title_seo_keywords` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `title_keyword_description_count` text COLLATE utf8_unicode_ci NOT NULL,
  `title_keyword_description_density` text COLLATE utf8_unicode_ci NOT NULL,
  `user_seo_keywords` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `user_keyword_description_count` int(11) NOT NULL DEFAULT '0',
  `user_keyword_description_density` double NOT NULL DEFAULT '0',
  `description_text` text COLLATE utf8_unicode_ci NOT NULL,
  `description_title` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `flag` enum('ready','deleted') COLLATE utf8_unicode_ci NOT NULL DEFAULT 'ready',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=106868 ;
CREATE TABLE IF NOT EXISTS `site_categories_snaps` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cat_id` int(11) DEFAULT NULL,
  `snap_name` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `snap_path` varchar(512) COLLATE utf8_unicode_ci DEFAULT NULL,
  `snap_dir` varchar(512) COLLATE utf8_unicode_ci DEFAULT NULL,
  `http_status` int(11) DEFAULT NULL,
  `stamp` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=9 ;

CREATE TABLE IF NOT EXISTS `site_departments_reports` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` int(11) DEFAULT NULL,
  `set_id` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL,
  `main_choose_dep` int(11) DEFAULT NULL,
  `main_choose_site` int(11) DEFAULT NULL,
  `json_encode_com` text COLLATE utf8_unicode_ci,
  `stamp` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=6 ;
CREATE TABLE IF NOT EXISTS `site_departments_snaps` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dep_id` int(11) DEFAULT NULL,
  `snap_name` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `snap_path` varchar(512) COLLATE utf8_unicode_ci DEFAULT NULL,
  `snap_dir` varchar(512) COLLATE utf8_unicode_ci DEFAULT NULL,
  `http_status` int(11) DEFAULT NULL,
  `stamp` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=198 ;
CREATE TABLE IF NOT EXISTS `snapshot_queue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `process` int(11) DEFAULT '0',
  `done` int(11) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;
CREATE TABLE IF NOT EXISTS `snapshot_queue_list` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `snapshot_id` int(11) DEFAULT NULL,
  `site_name` varchar(255) DEFAULT NULL,
  `url` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  `time_added` datetime DEFAULT NULL,
  KEY `id` (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=2000 ;
CREATE TABLE IF NOT EXISTS `statistics` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `rid` int(11) NOT NULL,
  `imported_data_id` int(11) NOT NULL,
  `created` datetime NOT NULL,
  `batch_id` int(11) NOT NULL,
  `product_name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `url` text COLLATE utf8_unicode_ci NOT NULL,
  `short_description` text COLLATE utf8_unicode_ci NOT NULL,
  `long_description` text COLLATE utf8_unicode_ci NOT NULL,
  `short_description_wc` int(11) NOT NULL,
  `long_description_wc` int(11) NOT NULL,
  `short_seo_phrases` varchar(500) COLLATE utf8_unicode_ci NOT NULL,
  `long_seo_phrases` varchar(500) COLLATE utf8_unicode_ci NOT NULL,
  `research_data_id` int(11) NOT NULL,
  `own_price` float NOT NULL,
  `competitors_prices` text COLLATE utf8_unicode_ci NOT NULL,
  `price_diff` text COLLATE utf8_unicode_ci NOT NULL,
  `items_priced_higher_than_competitors` int(11) NOT NULL,
  `similar_products_competitors` text COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=3980 ;
CREATE TABLE IF NOT EXISTS `statistics_duplicate_content` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `imported_data_id` int(11) NOT NULL,
  `product_name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `description` text COLLATE utf8_unicode_ci NOT NULL,
  `long_description` text COLLATE utf8_unicode_ci NOT NULL,
  `url` text COLLATE utf8_unicode_ci NOT NULL,
  `features` text COLLATE utf8_unicode_ci NOT NULL,
  `customer` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `long_original` float(10,1) NOT NULL,
  `short_original` float(10,1) NOT NULL,
  `created` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;
CREATE TABLE IF NOT EXISTS `statistics_new` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `imported_data_id` int(11) NOT NULL,
  `batch_id` int(11) DEFAULT NULL,
  `research_data_id` int(11) DEFAULT NULL,
  `created` datetime NOT NULL,
  `revision` int(11) NOT NULL,
  `short_description_wc` int(11) NOT NULL,
  `long_description_wc` int(11) NOT NULL,
  `title_keywords` varchar(8000) COLLATE utf8_unicode_ci NOT NULL,
  `own_price` float NOT NULL,
  `competitors_prices` text COLLATE utf8_unicode_ci NOT NULL,
  `price_diff` text COLLATE utf8_unicode_ci NOT NULL,
  `items_priced_higher_than_competitors` int(11) NOT NULL,
  `similar_products_competitors` text COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `imported_data_id` (`imported_data_id`),
  KEY `batch_id` (`batch_id`),
  KEY `research_data_id` (`research_data_id`),
  KEY `revision` (`revision`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=32221 ;
CREATE TABLE IF NOT EXISTS `statistics_new_archiv` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `imported_data_id` int(11) NOT NULL,
  `batch_id` int(11) DEFAULT NULL,
  `research_data_id` int(11) DEFAULT NULL,
  `created` datetime NOT NULL,
  `revision` int(11) NOT NULL,
  `short_description_wc` int(11) NOT NULL,
  `long_description_wc` int(11) NOT NULL,
  `short_seo_phrases` varchar(8000) COLLATE utf8_unicode_ci NOT NULL,
  `long_seo_phrases` varchar(8000) COLLATE utf8_unicode_ci NOT NULL,
  `own_price` float NOT NULL,
  `competitors_prices` text COLLATE utf8_unicode_ci NOT NULL,
  `price_diff` text COLLATE utf8_unicode_ci NOT NULL,
  `items_priced_higher_than_competitors` int(11) NOT NULL,
  `similar_products_competitors` text COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `imported_data_id` (`imported_data_id`),
  KEY `batch_id` (`batch_id`),
  KEY `research_data_id` (`research_data_id`),
  KEY `revision` (`revision`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;
CREATE TABLE IF NOT EXISTS `style_guide` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `style` text NOT NULL,
  `customer_id` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=2 ;
CREATE TABLE IF NOT EXISTS `tag_editor_descriptions` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(11) unsigned NOT NULL,
  `category_id` int(11) unsigned NOT NULL,
  `description` longtext COLLATE utf8_unicode_ci NOT NULL,
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `category_id` (`category_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=7 ;
CREATE TABLE IF NOT EXISTS `tag_editor_rules` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `rule` text COLLATE utf8_unicode_ci NOT NULL,
  `category_id` int(11) unsigned NOT NULL,
  `user_id` int(11) NOT NULL,
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `category_id` (`category_id`),
  KEY `category_id_2` (`category_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=2027 ;
CREATE TABLE IF NOT EXISTS `thread_process_info` (
  `id_thread` int(11) NOT NULL AUTO_INCREMENT,
  `name_process` varchar(255) NOT NULL,
  `start_limit` bigint(20) NOT NULL,
  `end_limit` bigint(20) NOT NULL,
  `added` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` enum('start','process','end','error') NOT NULL,
  `lines_scaned` bigint(20) DEFAULT '0',
  `items_updated` bigint(20) DEFAULT '0',
  `not_found_urls` bigint(20) DEFAULT '0',
  `items_unchanged` bigint(20) DEFAULT '0',
  `uid` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_thread`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=5 ;
CREATE TABLE IF NOT EXISTS `updated_items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `itemid` int(11) NOT NULL,
  `old_model` varchar(100) DEFAULT NULL,
  `new_model` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;
CREATE TABLE IF NOT EXISTS `urls` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `actual_url` varchar(1000) NOT NULL,
  `friendly_url` varchar(1000) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=71 ;
CREATE TABLE IF NOT EXISTS `urlstomatch` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url1` varchar(5000) DEFAULT NULL,
  `url2` varchar(5000) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;
CREATE TABLE IF NOT EXISTS `users` (
  `id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `ip_address` int(10) unsigned NOT NULL,
  `username` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `password` varchar(40) COLLATE utf8_unicode_ci NOT NULL,
  `salt` varchar(40) COLLATE utf8_unicode_ci DEFAULT NULL,
  `email` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `activation_code` varchar(40) COLLATE utf8_unicode_ci DEFAULT NULL,
  `forgotten_password_code` varchar(40) COLLATE utf8_unicode_ci DEFAULT NULL,
  `remember_code` varchar(40) COLLATE utf8_unicode_ci DEFAULT NULL,
  `created_on` int(11) unsigned NOT NULL,
  `last_login` int(11) unsigned DEFAULT NULL,
  `active` tinyint(1) unsigned DEFAULT NULL,
  `first_name` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `last_name` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `company` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `phone` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=53 ;
CREATE TABLE IF NOT EXISTS `users_groups` (
  `id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` mediumint(8) unsigned NOT NULL,
  `group_id` mediumint(8) unsigned NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=63 ;
CREATE TABLE IF NOT EXISTS `users_to_customers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`,`customer_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=139 ;
CREATE TABLE IF NOT EXISTS `user_summary_settings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `setting_id` int(11) NOT NULL,
  `setting_value` varchar(1024) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `user_ip` varchar(16) NOT NULL,
  `create_time` int(11) NOT NULL,
  `update_time` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=6 ;
CREATE TABLE IF NOT EXISTS `webshoots` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(256) COLLATE utf8_unicode_ci DEFAULT NULL,
  `img` text COLLATE utf8_unicode_ci,
  `thumb` text COLLATE utf8_unicode_ci,
  `dir_thumb` text COLLATE utf8_unicode_ci NOT NULL,
  `dir_img` text COLLATE utf8_unicode_ci NOT NULL,
  `stamp` datetime DEFAULT NULL,
  `uid` int(11) DEFAULT NULL,
  `year` int(11) DEFAULT NULL,
  `week` int(11) DEFAULT NULL,
  `pos` int(11) DEFAULT NULL,
  `shot_name` varchar(256) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=198 ;
CREATE TABLE IF NOT EXISTS `webshoots_select` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `screen_id` int(11) DEFAULT NULL,
  `uid` int(11) DEFAULT NULL,
  `pos` int(11) DEFAULT NULL,
  `year` int(11) DEFAULT NULL,
  `week` int(11) DEFAULT NULL,
  `img` varchar(512) COLLATE utf8_unicode_ci DEFAULT NULL,
  `thumb` varchar(512) COLLATE utf8_unicode_ci DEFAULT NULL,
  `stamp` datetime DEFAULT NULL,
  `screen_stamp` datetime DEFAULT NULL,
  `site` varchar(256) COLLATE utf8_unicode_ci DEFAULT NULL,
  `label` varchar(512) COLLATE utf8_unicode_ci DEFAULT NULL,
  `reset` int(11) NOT NULL DEFAULT '0',
  `shot_name` varchar(256) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=621 ;
ALTER TABLE `brands`
  ADD CONSTRAINT `brands_ibfk_1` FOREIGN KEY (`brand_type`) REFERENCES `brand_types` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE `brand_data`
  ADD CONSTRAINT `brand_data_ibfk_1` FOREIGN KEY (`brand_id`) REFERENCES `brands` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE `brand_data_summary`
  ADD CONSTRAINT `brand_data_summary_ibfk_1` FOREIGN KEY (`brand_id`) REFERENCES `brands` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE `imported_data_parsed`
  ADD CONSTRAINT `fk_imported_data_parsed_imported_data` FOREIGN KEY (`imported_data_id`) REFERENCES `imported_data` (`id`);
ALTER TABLE `similar_data`
  ADD CONSTRAINT `fk_group_id` FOREIGN KEY (`group_id`) REFERENCES `imported_data` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION;
ALTER TABLE `similar_item`
  ADD CONSTRAINT `similar_item_ibfk_1` FOREIGN KEY (`item1`) REFERENCES `imported_data` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `similar_item_ibfk_2` FOREIGN KEY (`item2`) REFERENCES `imported_data` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE `similar_product_groups`
  ADD CONSTRAINT `fk_imp_id_group_id` FOREIGN KEY (`ipd_id`) REFERENCES `imported_data` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION;
ALTER TABLE `tag_editor_descriptions`
  ADD CONSTRAINT `tag_editor_descriptions_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE `tag_editor_rules`
  ADD CONSTRAINT `tag_editor_rules_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;