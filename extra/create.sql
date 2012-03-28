DROP TABLE IF EXISTS `downloads`;

CREATE TABLE `downloads` (
  `name` varchar(255) NOT NULL,
  `chksum` varchar(255) NOT NULL,
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

