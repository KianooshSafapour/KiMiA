CREATE TABLE IF NOT EXISTS `accounts` (
  `id` int(10) NOT NULL DEFAULT 0,
  `name` varchar(16) NOT NULL,
  `number` varchar(20) NOT NULL,
  `bank` varchar(20) NOT NULL DEFAULT '0',
  `card` varchar(16) NOT NULL,
  `username` varchar(16) NOT NULL,
  `password` varchar(64) NOT NULL,
  `host` int(10) NOT NULL DEFAULT 0,
  `status` varchar(50) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `banks` (
  `id` int(10) NOT NULL DEFAULT 0,
  `name` varchar(16) NOT NULL,
  `config` text NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `configs` (
  `id` int(10) NOT NULL DEFAULT 0,
  `name` varchar(16) NOT NULL,
  `config` text NOT NULL,
  `status` varchar(20) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `logs` (
  `id` int(10) NOT NULL,
  `time` varchar(20) NOT NULL,
  `level` varchar(8) NOT NULL,
  `message` text NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `nodes` (
  `id` tinyint(3) NOT NULL DEFAULT 0,
  `name` varchar(16) NOT NULL DEFAULT '0',
  `ip` varchar(15) NOT NULL DEFAULT '0',
  `username` varchar(16) NOT NULL DEFAULT '0',
  `password` varchar(64) NOT NULL DEFAULT '0',
  `secret` varchar(256) NOT NULL DEFAULT '0',
  `config` tinyint(3) NOT NULL,
  `status` varchar(20) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `settings` (
  `id` int(10) NOT NULL DEFAULT 0,
  `name` varchar(16) NOT NULL,
  `value` text NOT NULL
);

CREATE TABLE IF NOT EXISTS `transactions` (
  `id` int(10) NOT NULL,
  `ccn` varchar(16) NOT NULL,
  `acn` varchar(16) NOT NULL,
  `tcn` varchar(20) NOT NULL,
  `date` varchar(8) NOT NULL,
  `time` varchar(4) NOT NULL,
  `status` varchar(20) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
);
