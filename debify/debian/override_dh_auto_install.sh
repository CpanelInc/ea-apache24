#!/bin/bash

source debian/vars.sh

set -x

echo "FILE LIST"
echo `pwd`
ls -R *
find . -name suexec_log -print
echo "FILE LIST END"

rm -rf $DEB_INSTALL_ROOT
mkdir -p $DEB_INSTALL_ROOT/var/run/apache2/htcacheclean
mkdir -p $DEB_INSTALL_ROOT/var/lib/dav
make DESTDIR=$DEB_INSTALL_ROOT install
# install the forensic script
install -m 755 support/check_forensic $DEB_INSTALL_ROOT$_sbindir
# install systemd service file for CentOS 7 and up
mkdir -p $DEB_INSTALL_ROOT$_unitdir
for s in httpd.service htcacheclean.service; do
  install -p -m 644 $RPM_SOURCE_DIR/${s} \
                    $DEB_INSTALL_ROOT$_unitdir/${s}
done
# install conf file/directory
mkdir $DEB_INSTALL_ROOT/etc/apache2/conf.d \
      $DEB_INSTALL_ROOT/etc/apache2/conf.modules.d \
      $DEB_INSTALL_ROOT/etc/apache2/conf.d/includes \
      $DEB_INSTALL_ROOT/etc/apache2/bin
install -m 644 $RPM_SOURCE_DIR/README.confd \
    $DEB_INSTALL_ROOT/etc/apache2/conf.d/README
for f in brotli.conf cgid.conf manual.conf cperror.conf autoindex.conf ; do
  install -m 644 -p $RPM_SOURCE_DIR/$f \
        $DEB_INSTALL_ROOT/etc/apache2/conf.d/$f
done
install -m 644 -p $RPM_SOURCE_DIR/http2.conf $DEB_INSTALL_ROOT/etc/apache2/conf.d/http2.conf
# Extra config trimmed:
rm -v docs/conf/extra/httpd-{ssl,userdir}.conf
rm $DEB_INSTALL_ROOT/etc/apache2/conf/*.conf
install -m 644 -p $RPM_SOURCE_DIR/httpd.conf \
   $DEB_INSTALL_ROOT/etc/apache2/conf/httpd.conf
mkdir $DEB_INSTALL_ROOT/etc/sysconfig
for s in httpd htcacheclean; do
  install -m 644 -p $RPM_SOURCE_DIR/${s}.sysconf \
                    $DEB_INSTALL_ROOT/etc/sysconfig/${s}
done
# tmpfiles.d configuration
mkdir -p $DEB_INSTALL_ROOT$_prefix/lib/tmpfiles.d
install -m 644 -p $RPM_SOURCE_DIR/apache2.tmpfiles \
   $DEB_INSTALL_ROOT$_prefix/lib/tmpfiles.d/apache2.conf
# Other directories
mkdir -p $DEB_INSTALL_ROOT$_localstatedir/lib/dav \
         $DEB_INSTALL_ROOT$_localstatedir/run/apache2/htcacheclean
# Create cache directory
mkdir -p $DEB_INSTALL_ROOT$_localstatedir/cache/apache2 \
         $DEB_INSTALL_ROOT$_localstatedir/cache/apache2/proxy \
         $DEB_INSTALL_ROOT$_localstatedir/cache/apache2/ssl
# Make the MMN accessible to module packages
echo $mmnisa > $DEB_INSTALL_ROOT$_includedir/apache2/.mmn
mkdir -p $DEB_INSTALL_ROOT/etc/rpm
cat > $DEB_INSTALL_ROOT/etc/rpm/macros.apache2 <<EOF
EOF
# Handle contentdir
mkdir $DEB_INSTALL_ROOT$contentdir/noindex
tar xzf $RPM_SOURCE_DIR/centos-noindex.tar.gz \
        -C $DEB_INSTALL_ROOT$contentdir/noindex/ \
        --strip-components=1
rm -rf $contentdir/htdocs
# remove manual sources
find $DEB_INSTALL_ROOT$contentdir/manual \( \
    -name \*.xml -o -name \*.xml.* -o -name \*.ent -o -name \*.xsl -o -name \*.dtd \
    \) -print0 | xargs -0 rm -f
# Strip the manual down just to English and replace the typemaps with flat files:
set +x
for f in `find $DEB_INSTALL_ROOT$contentdir/manual -name \*.html -type f`; do
   if test -f ${f}.en; then
      cp ${f}.en ${f}
      rm ${f}.*
   fi
done
set -x
# Clean Document Root
rm -v $DEB_INSTALL_ROOT$docroot/html/*.html \
      $DEB_INSTALL_ROOT$docroot/cgi-bin/*
mkdir -p $DEB_INSTALL_ROOT/etc/apache2
mkdir $DEB_INSTALL_ROOT/var/log/apache2
chmod 711 $DEB_INSTALL_ROOT/var/log/apache2

# Symlink for the powered-by-$DISTRO image:
ln -s ../noindex/images/poweredby.png \
        $DEB_INSTALL_ROOT$contentdir/icons/poweredby.png
# symlinks for /etc/httpd
ln -s ../..$_localstatedir/log/apache2 $DEB_INSTALL_ROOT/etc/apache2/logs
ln -s ../..$_localstatedir/run/apache2 $DEB_INSTALL_ROOT/etc/apache2/run
ln -s ../..$_libdir/apache2/modules $DEB_INSTALL_ROOT/etc/apache2/modules
touch $DEB_INSTALL_ROOT/var/log/apache2/suexec_log
chmod 644 $DEB_INSTALL_ROOT/var/log/apache2/suexec_log
chown root:nobody $DEB_INSTALL_ROOT/var/log/apache2/suexec_log

# fix man page paths
sed -e "s|/usr/local/apache2/conf/httpd.conf|/etc/apache2/conf/httpd.conf|" \
    -e "s|/usr/local/apache2/conf/mime.types|/etc/mime.types|" \
    -e "s|/usr/local/apache2/conf/magic|/etc/apache2/conf/magic|" \
    -e "s|/usr/local/apache2/logs/error_log|/var/log/apache2/error_log|" \
    -e "s|/usr/local/apache2/logs/access_log|/var/log/apache2/access_log|" \
    -e "s|/usr/local/apache2/logs/suexec_log|/var/log/apache2/suexec_log|" \
    -e "s|/usr/local/apache2/logs/httpd.pid|/var/run/apache2/httpd.pid|" \
    -e "s|/usr/local/apache2|/etc/apache2|" < docs/man/httpd.8 \
  > $DEB_INSTALL_ROOT$_mandir/man8/httpd.8
# Make ap_config_layout.h libdir-agnostic
sed -i '/.*DEFAULT_..._LIBEXECDIR/d;/DEFAULT_..._INSTALLBUILDDIR/d' \
    $DEB_INSTALL_ROOT$_includedir/apache2/ap_config_layout.h
# Fix path to instdso in special.mk
sed -i '/instdso/s,top_srcdir,top_builddir,' \
    $DEB_INSTALL_ROOT$_libdir/apache2/build/special.mk
# Make individual module package files
# We'll number the conf.modules.d files, so we can force load order,
# and since there's a lot of them, we'll use 3 digits
# Systemd should be in the first batch to be loaded
for mod in systemd
do
    printf -v modname "000_mod_%s.conf" $mod
    cat > $DEB_INSTALL_ROOT/etc/apache2/conf.modules.d/${modname} <<EOF
# Enable mod_${mod}
LoadModule ${mod}_module modules/mod_${mod}.so
EOF
    cat > files.${mod} <<EOF
EOF
done
# MPMs are mutually exclusive, and should be loaded first
for mod in mpm_event mpm_prefork mpm_worker
do
    printf -v modname "000_mod_%s.conf" $mod
    cat > $DEB_INSTALL_ROOT/etc/apache2/conf.modules.d/${modname} <<EOF
# Enable mod_${mod}
LoadModule ${mod}_module modules/mod_${mod}.so
EOF
    if [ "${mod}" = "mpm_prefork" ]; then
        cat >> $DEB_INSTALL_ROOT/etc/apache2/conf.modules.d/${modname} <<EOF
Mutex sysvsem
EOF
    fi
    cat > files.${mod} <<EOF
EOF
done
# CGIs are also mutually exclusive
for mod in cgi cgid
do
    printf -v modname "005_mod_%s.conf" $mod
    cat > $DEB_INSTALL_ROOT/etc/apache2/conf.modules.d/${modname} <<EOF
# Enable mod_${mod}
LoadModule ${mod}_module modules/mod_${mod}.so
EOF
    cat > files.${mod} <<EOF
EOF
done
modnum=10
for mod in \
  access_compat actions alias allowmethods asis auth_basic auth_digest \
  authn_core authn_anon authn_dbd authn_dbm authn_file authn_socache \
  authz_core authz_dbd authz_dbm authz_groupfile authz_host authz_owner \
  authz_user autoindex brotli buffer cache cache_disk cache_socache \
  charset_lite data dav dav_fs dav_lock dbd deflate dialup dir dumpio \
  env expires ext_filter file_cache filter headers \
  imagemap include info log_config log_debug log_forensic logio lua \
  macro mime mime_magic negotiation \
  proxy lbmethod_bybusyness lbmethod_byrequests lbmethod_bytraffic \
  lbmethod_heartbeat proxy_ajp proxy_balancer proxy_connect \
  proxy_express proxy_fcgi proxy_fdpass proxy_ftp proxy_http proxy_scgi \
  proxy_wstunnel proxy_uwsgi ratelimit reflector remoteip reqtimeout request rewrite \
  sed setenvif slotmem_plain slotmem_shm socache_dbm socache_memcache \
  socache_shmcb socache_redis speling status substitute suexec unique_id unixd userdir \
  usertrack version vhost_alias watchdog heartbeat heartmonitor \
  ssl \
  http2 \
  proxy_html xml2enc \
  ldap authnz_ldap \
  session session_cookie session_dbd auth_form session_crypto proxy_hcheck
do
    printf -v modname "%03d_mod_%s.conf" $modnum $mod
    # add to the condition to have comment-disabled modules
    if [ "${mod}" = "info" ]; then
      cat > $DEB_INSTALL_ROOT/etc/apache2/conf.modules.d/${modname} <<EOF
# Once mod_info is loaded into the server, its handler capability is available
# in all configuration files, including per-directory files (e.g., .htaccess).
# This may have security-related ramifications for your server. In particular,
# this module can leak sensitive information from the configuration directives
# of other Apache modules such as system paths, usernames/passwords, database
# names, etc. Therefore, this module should only be used in a controlled
# environment and always with caution.
#
# If you still want to use this module, uncomment the LoadModule directive below.
#LoadModule ${mod}_module modules/mod_${mod}.so
EOF
    elif [ "${mod}" = "lua" ]; then
      cat > $DEB_INSTALL_ROOT/etc/apache2/conf.modules.d/${modname} <<EOF
# This module holds a great deal of power over httpd, which is both a strength
# and a potential security risk. It is not recommended that you use this module
# on a server that is shared with users you do not trust, as it can be abused
# to change the internal workings of httpd.
#
# If you still want to use this module, uncomment the LoadModule directive below.
#LoadModule ${mod}_module modules/mod_${mod}.so
EOF
    else
      cat > $DEB_INSTALL_ROOT/etc/apache2/conf.modules.d/${modname} <<EOF
# Enable mod_${mod}
LoadModule ${mod}_module modules/mod_${mod}.so
EOF
    fi
    if [ "${mod}" = "reqtimeout" ]; then
      cat >> $DEB_INSTALL_ROOT/etc/apache2/conf.modules.d/${modname} <<EOF
RequestReadTimeout handshake=0 header=20-40,MinRate=500 body=20,MinRate=500
EOF
    fi
    if [ "${mod}" = "info" ]; then
        cat > files.${mod} <<EOF
EOF
    elif [ "${mod}" = "http2" ]; then
    	cat > files.${mod} <<EOF
EOF
    else
        cat > files.${mod} <<EOF
EOF
    fi
    # Let's stride by 5, in case there is need to insert things
    # between two modules
    modnum=$(($modnum+5))
done
# proxy_html package needs xml2enc
cat files.xml2enc >> files.proxy_html
# Session-related modules
cat files.session_cookie files.session_dbd files.auth_form \
  files.session_crypto >> files.session
# The rest of the modules, into the main list
cat files.access_compat files.actions files.alias files.auth_basic \
  files.authn_core files.authn_file files.authz_core \
  files.authz_groupfile files.authz_host files.authz_user \
  files.autoindex files.dir files.filter files.include \
  files.log_config files.logio files.mime files.negotiation \
  files.rewrite files.setenvif files.slotmem_shm files.socache_dbm \
  files.socache_shmcb files.status files.unixd \
  files.userdir > files.httpd
cat files.systemd >> files.httpd
# Remove unpackaged files
rm -vf \
      $DEB_INSTALL_ROOT$_libdir/*.exp \
      $DEB_INSTALL_ROOT$_libdir/apache2/modules/*.exp \
      $DEB_INSTALL_ROOT$_libdir/apache2/build/config.nice \
      $DEB_INSTALL_ROOT$_bindir/{ap?-config,dbmmanage} \
      $DEB_INSTALL_ROOT$_sbindir/{checkgid,envvars*} \
      $DEB_INSTALL_ROOT$contentdir/htdocs/* \
      $DEB_INSTALL_ROOT$_mandir/man1/dbmmanage.* \
      $DEB_INSTALL_ROOT$contentdir/cgi-bin/*
rm -rf $DEB_INSTALL_ROOT/etc/apache2/conf/{original,extra}

# Some special debian things

mkdir -p $DEB_INSTALL_ROOT/usr/share/doc/$name/
mkdir -p $DEB_INSTALL_ROOT/usr/share/man/man8
mkdir -p $DEB_INSTALL_ROOT/usr/share/man/man1
mkdir -p $DEB_INSTALL_ROOT/var/cache/apache2/proxy
mkdir -p $DEB_INSTALL_ROOT/usr/share/doc/$name-mod_info/
mkdir -p $DEB_INSTALL_ROOT/usr/share/doc/$name-tools/

# consistify for old to new %doc behavior
mkdir -p $DEB_INSTALL_ROOT/usr/share/doc/ea-apache24
mkdir -p $DEB_INSTALL_ROOT/usr/share/doc/ea-apache24/docs/conf/extra

for f in ABOUT_APACHE README CHANGES LICENSE VERSIONING NOTICE; do
    cp $buildroot//$f $DEB_INSTALL_ROOT/usr/share/doc/ea-apache24/
done

for fd in httpd-dav.conf httpd-default.conf httpd-languages.conf httpd-manual.conf httpd-mpm.conf httpd-multilang-errordoc.conf httpd-vhosts.conf proxy-html.conf; do
    cp $buildroot/docs/conf/extra/$fd $DEB_INSTALL_ROOT/usr/share/doc/ea-apache24/docs/conf/extra/$fd
done

cp $buildroot/docs/conf/extra/httpd-info.conf $DEB_INSTALL_ROOT/usr/share/doc/$name-mod_info/

gzip $buildroot/docs/man/*

cp $buildroot/docs/man/apachectl.8.gz $DEB_INSTALL_ROOT/usr/share/man/man8
cp $buildroot/docs/man/fcgistarter.8.gz $DEB_INSTALL_ROOT/usr/share/man/man8
cp $buildroot/docs/man/htcacheclean.8.gz $DEB_INSTALL_ROOT/usr/share/man/man8
cp $buildroot/docs/man/httpd.8.gz $DEB_INSTALL_ROOT/usr/share/man/man8
cp $buildroot/docs/man/rotatelogs.8.gz $DEB_INSTALL_ROOT/usr/share/man/man8
cp $buildroot/docs/man/suexec.8.gz $DEB_INSTALL_ROOT/usr/share/man/man8

cp $buildroot/docs/man/ab.1.gz $DEB_INSTALL_ROOT/usr/share/man/man1
cp $buildroot/docs/man/apxs.1.gz $DEB_INSTALL_ROOT/usr/share/man/man1
cp $buildroot/docs/man/htdbm.1.gz $DEB_INSTALL_ROOT/usr/share/man/man1
cp $buildroot/docs/man/htdigest.1.gz $DEB_INSTALL_ROOT/usr/share/man/man1
cp $buildroot/docs/man/htpasswd.1.gz $DEB_INSTALL_ROOT/usr/share/man/man1
cp $buildroot/docs/man/httxt2dbm.1.gz $DEB_INSTALL_ROOT/usr/share/man/man1
cp $buildroot/docs/man/logresolve.1.gz $DEB_INSTALL_ROOT/usr/share/man/man1

cp $buildroot/LICENSE $DEB_INSTALL_ROOT/usr/share/doc/$name-tools/
cp $buildroot/NOTICE $DEB_INSTALL_ROOT/usr/share/doc/$name-tools/

mkdir -p $DEB_INSTALL_ROOT/var/cache/apache2/ssl

perl -pi -e 's{^#!/bin/sh}{#!/bin/bash}' $DEB_INSTALL_ROOT$_sbindir/apachectl

# Prune .install entries for files absent from this build (handles upstream removals)
for ifile in debian/*.install; do
    [[ -f "$ifile" ]] || continue
    tmpfile=$(mktemp)
    while IFS= read -r line || [[ -n "$line" ]]; do
        src=$(awk '{print $1}' <<< "$line")
        if [[ -z "$src" ]] || [[ "$src" == \#* ]] || compgen -G "$src" > /dev/null 2>&1; then
            echo "$line" >> "$tmpfile"
        fi
    done < "$ifile"
    \mv "$tmpfile" "$ifile"
done
