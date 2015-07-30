#!/bin/bash

if [ ! -e /var/www/owncloud/config/config.php ] ; then
cat >> /var/www/owncloud/config/autoconfig.php << EOF
<?php
\$AUTOCONFIG = array (
  'directory' => '/var/www/owncloud/data',
  'dbtype' => 'pgsql',
  'dbname' => 'owncloud',
  'dbhost' => '${ocdbhost}',
  'dbtableprefix' => 'oc_',
  'dbuser' => 'ocadmin',
  'dbpass' => '${owncloudpassword}',
  'installed' => false,
);
EOF
fi

if [ ! -e /var/www/owncloud/config/nds.config.php ] ; then 
cat >> /var/www/owncloud/config/nds.config.php << EOF
<?php
\$CONFIG = array (
  'overwritewebroot' => '/owncloud',
  'irodsresturl' => 'http://irodsrest/irods-rest/rest/server',
  'user_backends' => array(
    array(
      'class'=>'OC_User_Database',
      'arguments'=>array(),
    ),
    array(
      'class'=>'OC_User_HTTP',
      'arguments'=>array(),
    ),
  ),
);
EOF
fi

chown www-data:www-data -R /var/www/owncloud
supervisorctl start apache2
