SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";

drop database ninuxuu;
CREATE database ninuxuu;
USE ninuxuu;

CREATE TABLE IF NOT EXISTS `resources` (
--  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `uri` varchar(700) NOT NULL,
  `filetype` varchar(20),
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`uri`)
) ENGINE=InnoDB DEFAULT CHARSET=ascii;

CREATE TABLE IF NOT EXISTS `tags` (
  `uri` varchar(700) NOT NULL,
  `tag` varchar(50) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
--  `resource_id` bigint(20) NOT NULL,
  PRIMARY KEY (`uri`,`tag`)
) ENGINE=InnoDB DEFAULT CHARSET=ascii;
