node 'node1', 'node2', 'node3', 'node4', 'node5', 'node6', 'node7', 'node8', 'node9', 'node10' {


	service { "networking":
    	provider => 'base',
	    path => '/etc/init.d/networking',
	    start => '/etc/init.d/networking start',
    	ensure => 'running',
  	}

	exec { 'apt-update-1':
		command => '/usr/bin/apt-get update',
		require => service['networking'],
	}

	package { 'git':
		ensure => present,
		require => exec['apt-update-1'],
	}
	
	package { 'python-pip':
		ensure => present,
		require => exec['apt-update-1'],
	}

	package { 'python-dev':
		ensure => present,
		require => exec['apt-update-1'],
	}

	package {'libxslt1-dev':
   		ensure => present,
 		require => exec['apt-update-1']
	}

	package {'sshfs':
   		ensure => present,
 		require => exec['apt-update-1']
	}

	exec { 'pip-scrapy':
		command => '/usr/bin/pip install scrapy',
		require => [package['python-pip'], package['python-dev'], package['libxslt1-dev']],
	}

	exec { 'pip-nltk':
		command => '/usr/bin/pip install nltk',
		require => package['python-pip'],
	}

	exec { 'pip-selenium':
		command => '/usr/bin/pip install selenium',
		require => package['python-pip'],
	}


	# ssh keys
	file { "/home/ubuntu/.ssh":
    	ensure => "directory",
    	owner  => "ubuntu",
    	group  => "ubuntu",
    	mode   => 600,
  	}

	file { "/home/ubuntu/.ssh/id_rsa":
		source => "puppet:///modules/common/id_rsa",
		mode => 600,
		owner => ubuntu,
		group => ubuntu,
	}

	file { "/home/ubuntu/.ssh/id_rsa.pub":
		source => "puppet:///modules/common/id_rsa.pub",
		mode => 644,
		owner => ubuntu,
		group => ubuntu,
	}

	# clone repo if it doesn't exist
	exec {"clone-tmtext":
		creates => "/home/ubuntu/tmtext",
		cwd => "/home/ubuntu",
		user => "ubuntu",
		command => "git clone -q git@bitbucket.org:dfeinleib/tmtext.git",
		require => package['git'],
	}

	# make sure repo directory belongs to ubuntu user
	file { "/home/ubuntu/tmtext":
		owner => ubuntu,
		group => ubuntu,
		recurse => true,
	}


	# make sure root has access to repo (to pull at startup)
	file { "/root/.ssh/config":
	    source => "puppet:///modules/common/ssh_config",
    	owner => root,
    	group => root,
    	mode => 644
  	}

  	# startup script - pulling from repo
  	file { "/home/ubuntu/startup_script.sh":
    	source => "puppet:///modules/common/startup_script.sh",
    	owner => root,
    	group => root,
    	mode => 777
  	}

}