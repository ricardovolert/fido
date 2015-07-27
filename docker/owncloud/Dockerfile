FROM ubuntu:trusty
MAINTAINER Matthew Turk "matthewturk@gmail.com"

ENV DEBIAN_FRONTEND=noninteractive owncloudpassword=testpassword ocdbhost=db2
RUN apt-get -q update && apt-get -qyV install \
     curl libcurl3 bzip2 wget openssl ssl-cert sharutils libmcrypt4 \
     ffmpegthumbnailer smbclient php5 php5-fpm php5-gd php-xml-parser php5-intl \
     php5-pgsql php5-curl liboauth-php libphp-pclzip libphp-phpmailer php-file \
     php-aws-sdk php-crypt-blowfish php-doctrine-common php-dompdf php-dropbox \
     php-font-lib php-getid3 php-google-api-php-client php-guzzle php-irods-prods \
     php-opencloud php-patchwork-utf8 php-pear php-phpdocx php-sabre-dav \
     php-sabre-vobject php-seclib php-services-json php-symfony-console \
     php-symfony-eventdispatcher php-symfony-routing php-fpdf php5-apcu php5-cli \
     php5-common php5-imagick php-net-ftp php5-gmp php5-json php5-ldap php5-mcrypt \
     php5-oauth php5-readline php5-tidy php5-xsl sdop zend-framework \
     zend-framework-bin libzend-framework-php apache2 libapache2-mod-php5 \
     supervisor unzip &&\
   apt-get clean &&\
   rm -rf /var/lib/apt/lists/*

RUN cd /tmp && \
   wget https://download.owncloud.org/community/owncloud-8.0.2.tar.bz2 && \
   tar xvf owncloud-8.0.2.tar.bz2 -C /var/www/ && \
   chown -R www-data:www-data /var/www/owncloud && \
   rm -rf owncloud-8.0.2.tar.bz2

RUN cd /tmp && \
   wget https://github.com/MatthewTurk/user-otp/archive/ldap_interop.zip && \
   unzip ldap_interop.zip && \
   mv user-otp-ldap_interop/user_otp /var/www/owncloud/apps/ && \
   chown -R www-data:www-data /var/www/owncloud && \
   rm -rf ldap_inter*

RUN cd /var/ww/owncloud/themes && \
   wget https://bitbucket.org/yt_analysis/hub_theme/get/tip.zip && \
   unzip tip.zip && rm -rf tip.zip && \
   mv yt_analysis* hub_theme && \
   sed -i -e "/theme/ s/''/'hub_theme'/" /var/www/owncloud/config/config.php && \
   chown -R www-data:www-data /var/www/owncloud/themes

ADD owncloud.conf /etc/apache2/conf-available/owncloud.conf
ADD htaccess /var/www/owncloud/.htaccess
RUN ln -s ../conf-available/owncloud.conf /etc/apache2/conf-enabled/owncloud.conf && \
   chown -R www-data:www-data /var/www/owncloud

ADD setup_owncloud.sh /usr/local/bin/setup_owncloud.sh
ADD http_override.php /var/www/owncloud/lib/private/user/http.php
ADD supervisord.conf /etc/supervisor/supervisord.conf
ADD apache2.conf /etc/supervisor/conf.d/apache2.conf

VOLUME ["/var/www/owncloud/config", "/var/www/owncloud/data"]

CMD ["supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
