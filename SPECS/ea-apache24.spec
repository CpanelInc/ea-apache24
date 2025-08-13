%define contentdir %{_datadir}/apache2
%define docroot /var/www
%define suexec_caller nobody
%define mmn 20120211
%define oldmmnisa %{mmn}-%{__isa_name}-%{__isa_bits}
%define mmnisa %{mmn}%{__isa_name}%{__isa_bits}
%define vstring cPanel
%define ea_openssl_ver 1.1.1d-1

# Drop automatic provides for module DSOs
%{?filter_setup:
%filter_provides_in %{_libdir}/apache2/modules/.*\.so$
%filter_setup
}

# Don't build HTTP2 module if we're 32bit
%ifarch x86_64
%global with_http2   1
%else
%global with_http2   0
%endif

%if 0%{?rhel} >= 10
# https://docs.fedoraproject.org/en-US/packaging-guidelines/#_brp_buildroot_policy_scripts
%global __brp_check_rpaths %{nil}
%endif

Summary: Apache HTTP Server
Name: ea-apache24
Version: 2.4.65
# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4544 for more details
%define release_prefix 4
Release: %{release_prefix}%{?dist}.cpanel
Vendor: cPanel, Inc.
URL: http://httpd.apache.org/
Source0: http://www.apache.org/dist/httpd/httpd-%{version}.tar.bz2
Source1: centos-noindex.tar.gz
Source3: httpd.sysconf
Source5: apache2.tmpfiles
Source6: httpd.init

Source10: httpd.conf
Source11: autoindex.conf
# Source21: reuse this as needed
Source22: cgid.conf
Source23: manual.conf
Source43: cperror.conf
Source44: brotli.conf
%if %{with_http2}
Source53: http2.conf
%endif
# Documentation
Source30: README.confd
Source40: htcacheclean.init
Source41: htcacheclean.sysconf

# Systemd service file
Source42: httpd.service
Source45: htcacheclean.service

# Common pre/post scripts
Source46: pkg.preinst
Source47: pkg.ea-apache24.postinst
Source48: pkg.prerm

# build/scripts patches
Patch1: 0001-Apachectl-additions-and-options.patch
Patch3: 0002-Remove-libs-dependency-in-AP_LIBS.patch
Patch5: 0003-Add-cPanel-layout.patch

# Features/functional changes
Patch24: 0004-Bump-coresize-limit-if-coredumpdirectory-is-configur.patch
Patch27: 0005-Update-Icon-configuration-in-autoindex.conf.patch

Patch30: 0006-Update-CacheMaxExpire-to-have-a-hard-option.patch

# Bug fixes

# cPanel-specific patches
Patch301: 0007-Update-Apachectl-to-reference-cpanel.config-Addition.patch
Patch302: 0008-Update-suexec-to-allow-trusted-scripts.patch
Patch303: 0009-Update-suexec-to-work-with-cPanel-Mailman-installati.patch
Patch304: 0010-Update-suexec-to-allow-execution-for-httpusergroup-m.patch
Patch305: 0011-Update-apxs-to-automatically-generate-module-conf-fi.patch
Patch306: 0012-Add-SymlinkProtect-and-SymlinkProtectRoot-functional.patch

# cPanel Performance Patches
Patch401: 0013-Increase-random-seed-size.patch
Patch403: 0014-Downgrade-loglevel-for-long-lost-pid-warnings.patch

# cPanel Security Patches
# removed: fixed upstream Patch500: 0016-Apply-mod_ratelimit-fix-from-trunk.patch
Patch500: 0015-Ensure-that-Paths-configured-as-Aliases-are-exempt-f.patch

# Performance Patches
Patch601: 0016-Optimize-finding-a-module.-ap_find_linked_module-was.patch

Patch701: 0017-Update-apxs-to-use-the-correct-path-for-top_builddir.patch

Patch801: 0018-Add-instructions-to-install-elinks.patch

Patch902: 0019-Change-Accept-mutex-from-DEBUG-to-INFO-so-techs-can-.patch

License: ASL 2.0
Group: System Environment/Daemons
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

%if 0%{?rhel} < 8
BuildRequires: ea-openssl11 >= %{ea_openssl_ver}, ea-openssl11-devel >= %{ea_openssl_ver}
Requires: ea-openssl11 >= %{ea_openssl_ver}
%else
# In C8 we use system openssl. See DESIGN.md in ea-openssl11 git repo for details
BuildRequires: openssl, openssl-devel
Requires: openssl
%endif

BuildRequires: autoconf, perl, pkgconfig, findutils, xmlto
BuildRequires: zlib-devel, libselinux-devel, lua-devel
BuildRequires: ea-apr-devel >= 1.6.3-1, ea-apr-util-devel >= 1.6.1-1

%if 0%{?rhel} >= 10
BuildRequires: libxml2 libxml2-devel
BuildRequires: pcre2-devel
%else
BuildRequires: ea-libxml2 ea-libxml2-devel
BuildRequires: pcre-devel >= 5.0
%endif

%if %{with_http2}
    %if 0%{?rhel} >= 10
BuildRequires: nghttp2 libnghttp2
    %else
BuildRequires: ea-nghttp2 ea-libnghttp2
    %endif
%endif

%if 0%{?rhel} >=7
BuildRequires: systemd-devel
%endif

Requires: ea-apr%{?_isa} >= 1.7.0-1
Requires: ea-apr-util%{?_isa} >= 1.6.1-1
Requires: system-logos >= 7.92.1-1
Requires: ea-apache24-mpm
Requires: ea-apache24-mod_ssl
Requires: ea-documentroot
Requires: ea-apache24-tools
Requires: ea-apache24-config
Requires: ea-apache24-config-runtime
Requires: ea-apache24-mod_bwlimited
Requires: ea-apache24-mod_proxy_wstunnel
Requires: ea-apache24-mod_headers
Requires: ea-apache24-mod_remoteip

Obsoletes: httpd-suexec
Conflicts: httpd-mmn
Provides: ea-webserver
Provides: ea-apache24-suexec = %{version}-%{release}
Provides: ea-apache24-mmn = %{mmn}, ea-apache24-mmn = %{mmnisa}

%if 0%{?rhel} >=7
Requires(preun): systemd-units
Requires(postun): systemd-units
Requires(post): systemd-units
%endif

%if 0%{?rhel} < 8
# This is apparently a syntax error
# 20120211-x86-64
Provides: ea-apache24-mmn = %{oldmmnisa}
%endif

Requires: ea-apache24-tools = %{version}-%{release}
Requires: ea-apache24-mod_proxy_http
Requires: ea-apache24-mod_proxy


%if 0%{?rhel} == 10
# ea-cpanel-tools needs cpanel perl which is not yet available on Almalinux 10
%else
Requires: ea-cpanel-tools
%endif

%if 0%{?rhel} < 8
Requires: elinks
%endif
Requires(post): chkconfig

%description
The Apache HTTP Server is a powerful, efficient, and extensible
web server.

%package devel
Group: Development/Libraries
Summary: Development interfaces for the Apache HTTP server
Obsoletes: secureweb-devel, apache-devel, stronghold-apache-devel, httpd-devel
Requires: ea-apr-devel >= 1.6.3-1, ea-apr-util-devel, pkgconfig
Requires: ea-apache24 = %{version}-%{release}

%description devel
The ea-apache24-devel package contains the APXS binary and other files
that you need to build Dynamic Shared Objects (DSOs) for the
Apache HTTP Server.

If you are installing the Apache HTTP server and you want to be
able to compile or develop additional modules for Apache, you need
to install this package.

%package manual
Group: Documentation
Summary: Documentation for the Apache HTTP server
Requires: ea-apache24 = %{version}-%{release}
Obsoletes: secureweb-manual, apache-manual, httpd-manual
BuildArch: noarch

%description manual
The ea-apache24-manual package contains the complete manual and
reference guide for the Apache HTTP server. The information can
also be found at http://httpd.apache.org/docs/2.4/.

%if %{with_http2}
%package -n ea-apache24-mod_http2
Group: System Environment/Daemons
Summary: HTTP2 module for Apache HTTP Server
%if 0%{?rhel} >= 10
BuildRequires: libnghttp2-devel
%else
BuildRequires: ea-libnghttp2-devel
%endif

%if 0%{?rhel} < 8
BuildRequires: ea-openssl11 >= %{ea_openssl_ver}, ea-openssl11-devel >= %{ea_openssl_ver}
Requires: ea-openssl11 >= %{ea_openssl_ver}
%else
# In C8 we use system openssl. See DESIGN.md in ea-openssl11 git repo for details
BuildRequires: openssl, openssl-devel
Requires: openssl
%endif

%if 0%{?rhel} >= 10
Requires: nghttp2
%else
Requires: ea-nghttp2
%endif

Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Conflicts: ea-apache24-mod_mpm_itk, ea-apache24-mod_mpm_prefork

%description -n ea-apache24-mod_http2
This module sets up http2
%endif

%package tools
Group: System Environment/Daemons
Summary: Tools for use with the Apache HTTP Server

%description tools
The ea-apache24-tools package contains tools which can be used with
the Apache HTTP Server.

%package -n ea-apache24-mod_mpm_event
Group: System Environment/Daemons
Summary: Threaded event Multi-Processing Module for Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Provides: ea-apache24-mpm = threaded
Conflicts: ea-apache24-mpm = forked, ea-apache24-mod_mpm_worker, ea-apache24-mod_mpm_prefork
Conflicts: ea-apache24-mod_cgi
Requires: ea-apache24-mod_cgid

%description -n ea-apache24-mod_mpm_event
The Event MPM provides a threaded model for workers, with the additional
feature that all keepalive connections are handled by a single thread.

%package -n ea-apache24-mod_mpm_prefork
Group: System Environment/Daemons
Summary: Prefork Multi-Processing Module for Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Provides: ea-apache24-mpm = forked
Conflicts: ea-apache24-mpm = threaded, ea-apache24-mod_mpm_worker, ea-apache24-mod_mpm_event
Conflicts: ea-apache24-mod_cgid, ea-apache24-mod_http2
Requires: ea-apache24-mod_cgi

%description -n ea-apache24-mod_mpm_prefork
The traditional forked worker model.

%package -n ea-apache24-mod_mpm_worker
Group: System Environment/Daemons
Summary: Threaded worker Multi-Processing Module for Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Provides: ea-apache24-mpm = threaded
Conflicts: ea-apache24-mpm = forked, ea-apache24-mod_mpm_event, ea-apache24-mod_mpm_prefork
Conflicts: ea-apache24-mod_cgi
Requires: ea-apache24-mod_cgid

%description -n ea-apache24-mod_mpm_worker
The Worker MPM provides a threaded worker model.

%package -n ea-apache24-mod_allowmethods
Group: System Environment/Daemons
Summary: HTTP request method restriction module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_allowmethods
The mod_allowmethods module makes it easy to restrict what HTTP
methods can used on an server.

%package -n ea-apache24-mod_asis
Group: System Environment/Daemons
Summary: As-is provider module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_asis
The mod_asis module provides the handler send-as-is which causes
Apache HTTP Server to send the document without adding most of the
usual HTTP headers.

%package -n ea-apache24-mod_auth_digest
Group: System Environment/Daemons
Summary: HTTP Digest Authentication module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-authn, ea-apache24-authz

%description -n ea-apache24-mod_auth_digest
The mod_auth_digest module implements HTTP Digest Authentication
(RFC2617), and provides an alternative to mod_auth_basic where the
password is not transmitted as cleartext. However, this does not lead
to a significant security advantage over basic authentication. On the
other hand, the password storage on the server is much less secure
with digest authentication than with basic authentication. Therefore,
using basic auth and encrypting the whole connection using mod_ssl is
a much better alternative.

mod_auth_digest requires at least one authentication provider module,
and one authorization provider module.

%package -n ea-apache24-mod_authn_anon
Group: System Environment/Daemons
Summary: Anonymous-user authentication module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Provides: ea-apache24-authn = anon

%description -n ea-apache24-mod_authn_anon
The mod_authn_anon module provides authentication front-ends such as
mod_auth_basic to authenticate users similar to anonymous-ftp sites,
i.e. have a 'magic' user id 'anonymous' and the email address as a
password. These email addresses can be logged.

Combined with other (database) access control methods, this allows for
effective user tracking and customization according to a user profile
while still keeping the site open for 'unregistered' users. One
advantage of using Auth-based user tracking is that, unlike
magic-cookies and funny URL pre/postfixes, it is completely browser
independent and it allows users to share URLs.

%package -n ea-apache24-mod_authn_dbd
Group: System Environment/Daemons
Summary: DBD-based authentication module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mod_dbd = 0:%{version}-%{release}
Provides: ea-apache24-authn = dbd

%description -n ea-apache24-mod_authn_dbd
The mod_authn_dbd module provides authentication front-ends such as
mod_auth_digest and mod_auth_basic to authenticate users by looking up
users in SQL tables. Similar functionality is provided by, for
example, mod_authn_file.

%package -n ea-apache24-mod_authn_dbm
Group: System Environment/Daemons
Summary: DBM-based authentication module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mod_dbd = 0:%{version}-%{release}
Provides: ea-apache24-authn = dbm

%description -n ea-apache24-mod_authn_dbm
The mod_authn_dbm module provides authentication front-ends such as
mod_auth_digest and mod_auth_basic to authenticate users by looking up
users in dbm password files. Similar functionality is provided by
mod_authn_file.

%package -n ea-apache24-mod_authn_socache
Group: System Environment/Daemons
Summary: Shared-memory authentication caching module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-authn

%description -n ea-apache24-mod_authn_socache
The mod_authn_socache module maintains a cache of authentication
credentials, so that a new backend lookup is not required for every
authenticated request.

%package -n ea-apache24-mod_authnz_ldap
Group: System Environment/Daemons
Summary: LDAP authentication/authorization module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mod_ldap = 0:%{version}-%{release}
Provides: ea-apache24-authn = ldap, ea-apache24-authz = ldap

%description -n ea-apache24-mod_authnz_ldap
The mod_authnz_ldap module allows authentication front-ends such as
mod_auth_basic to authenticate users through an LDAP directory.

%package -n ea-apache24-mod_authz_dbd
Group: System Environment/Daemons
Summary: DBD-based group authorization module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mod_dbd = 0:%{version}-%{release}
Provides: ea-apache24-authz = dbd

%description -n ea-apache24-mod_authz_dbd
The mod_authz_dbd module provides authorization capabilities so that
authenticated users can be allowed or denied access to portions of the
web site by group membership. Similar functionality is provided by
mod_authz_groupfile and mod_authz_dbm, with the exception that this
module queries a SQL database to determine whether a user is a member
of a group.

%package -n ea-apache24-mod_authz_dbm
Group: System Environment/Daemons
Summary: DBM-based group authorization module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Provides: ea-apache24-authz = dbm

%description -n ea-apache24-mod_authz_dbm
The mod_authz_dbm module provides authorization capabilities so that
authenticated users can be allowed or denied access to portions of the
web site by group membership. Similar functionality is provided by
mod_authz_groupfile.

%package -n ea-apache24-mod_authz_owner
Group: System Environment/Daemons
Summary: Ownership-based authorization module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Provides: ea-apache24-authz = owner

%description -n ea-apache24-mod_authz_owner
The mod_authz_owner module authorizes access to files by comparing the
userid used for HTTP authentication (the web userid) with the
file-system owner or group of the requested file. The supplied
username and password must be already properly verified by an
authentication module, such as mod_auth_basic or mod_auth_digest.

%package -n ea-apache24-mod_brotli
Group: System Environment/Daemons
Summary: Compress content via Brotli before it is delivered to the client
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
%if 0%{?rhel} >= 10
Requires: brotli
BuildRequires: brotli-devel
%else
Requires: ea-brotli
BuildRequires: ea-brotli-devel
%endif

%description -n ea-apache24-mod_brotli
The mod_brotli module provides the BROTLI_COMPRESS output filter that allows
output from your server to be compressed using the brotli compression format
before being sent to the client over the network.

%package -n ea-apache24-mod_buffer
Group: System Environment/Daemons
Summary: Request buffering module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_buffer
The mod_buffer module provides the ability to buffer the input and
output filter stacks.

Under certain circumstances, content generators might create content
in small chunks. In order to promote memory reuse, in memory chunks
are always 8k in size, regardless of the size of the chunk
itself. When many small chunks are generated by a request, this can
create a large memory footprint while the request is being processed,
and an unnecessarily large amount of data on the wire. The addition of
a buffer collapses the response into the fewest chunks possible.

When httpd is used in front of an expensive content generator,
buffering the response may allow the backend to complete processing
and release resources sooner, depending on how the backend is
designed.

%package -n ea-apache24-mod_cache
Group: System Environment/Daemons
Summary: Content caching module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_cache
The mod_cache module implements an RFC 2616 compliant HTTP content
caching filter, with support for the caching of content negotiated
responses containing the Vary header.

RFC 2616 compliant caching provides a mechanism to verify whether
stale or expired content is still fresh, and can represent a
significant performance boost when the origin server supports
conditional requests by honouring the If-None-Match HTTP request
header. Content is only regenerated from scratch when the content has
changed, and not when the cached entry expires.

As a filter, mod_cache can be placed in front of content originating
from any handler, including flat files (served from a slow disk cached
on a fast disk), the output of a CGI script or dynamic content
generator, or content proxied from another server.

In the default configuration, mod_cache inserts the caching filter as
far forward as possible within the filter stack, utilising the quick
handler to bypass all per request processing when returning content to
the client. In this mode of operation, mod_cache may be thought of as
a caching proxy server bolted to the front of the webserver, while
running within the webserver itself.

%package -n ea-apache24-mod_cache_disk
Group: System Environment/Daemons
Summary: Disk-based caching module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mod_cache = 0:%{version}-%{release}

%description -n ea-apache24-mod_cache_disk
The mod_cache_disk module implements a disk based storage manager for
mod_cache.

The headers and bodies of cached responses are stored separately on
disk, in a directory structure derived from the md5 hash of the cached
URL.

Multiple content negotiated responses can be stored concurrently,
however the caching of partial content is not yet supported by this
module.

Atomic cache updates to both header and body files are achieved
without the need for locking by storing the device and inode numbers
of the body file within the header file. This has the side effect that
cache entries manually moved into the cache will be ignored.

The htcacheclean tool is provided to list cached URLs, remove cached
URLs, or to maintain the size of the disk cache within size and/or
inode limits. The tool can be run on demand, or can be daemonized to
offer continuous monitoring of directory sizes.

%package -n ea-apache24-mod_cache_socache
Group: System Environment/Daemons
Summary: Shared-memory caching module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mod_cache = 0:%{version}-%{release}

%description -n ea-apache24-mod_cache_socache
The mod_cache_socache module implements a shared object cache
(socache) based storage manager for mod_cache.

The headers and bodies of cached responses are combined, and stored
underneath a single key in the shared object cache. A number of
implementations of shared object caches are available to choose from.

Multiple content negotiated responses can be stored concurrently,
however the caching of partial content is not yet supported by this
module.

%package -n ea-apache24-mod_cgi
Group: System Environment/Daemons
Summary: CGI module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mpm = forked
Conflicts: ea-apache24-mod_cgid, ea-apache24-mod_mpm_event, ea-apache24-mod_mpm_worker
Provides: ea-apache24-cgi

%description -n ea-apache24-mod_cgi
The mod_cgi module adds a handler for executing CGI scripts. This
module is meant for a forked MPM; for threaded MPMs, mod_cgid should
be used.

%package -n ea-apache24-mod_cgid
Group: System Environment/Daemons
Summary: CGI module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mpm = threaded
Conflicts: ea-apache24-mod_cgi, ea-apache24-mod_mpm_prefork
Provides: ea-apache24-cgi

%description -n ea-apache24-mod_cgid
The mod_cgid module adds a handler for executing CGI scripts. This
module is meant for threaded MPMs; for forked MPMs, mod_cgi should be
used.

%package -n ea-apache24-mod_charset_lite
Group: System Environment/Daemons
Summary: Character set conversion module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_charset_lite
The mod_charset_lite module allows the server to change the character
set of responses before sending them to the client.

%package -n ea-apache24-mod_data
Group: System Environment/Daemons
Summary: RFC2379 data URL generation module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_data
The mod_data module provides the ability to convert a response into an
RFC2397 data URL.

Data URLs can be embedded inline within web pages using something like
the mod_include module, to remove the need for clients to make
separate connections to fetch what may potentially be many small
images. Data URLs may also be included into pages generated by
scripting languages such as PHP.

%package -n ea-apache24-mod_dav
Group: System Environment/Daemons
Summary: DAV module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_dav
The mod_dav module provides class 1 and class 2 WebDAV ('Web-based
Distributed Authoring and Versioning') functionality for Apache. This
extension to the HTTP protocol allows creating, moving, copying, and
deleting resources and collections on a remote web server.

%package -n ea-apache24-mod_dav_fs
Group: System Environment/Daemons
Summary: DAV filesystem provider module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mod_dav = 0:%{version}-%{release}

%description -n ea-apache24-mod_dav_fs
The mod_dav_fs module acts as a support module for mod_dav and
provides access to resources located in the file system.  The formal
name of this provider is filesystem.

%package -n ea-apache24-mod_dav_lock
Group: System Environment/Daemons
Summary: Generic DAV locking module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mod_dav = 0:%{version}-%{release}

%description -n ea-apache24-mod_dav_lock
The mod_dav_lock module implements a generic locking API which can be
used by any backend provider of mod_dav.  Without a backend provider
which makes use of it, however, it should not be loaded into the
server.

%package -n ea-apache24-mod_dbd
Group: System Environment/Daemons
Summary: Database connection module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_dbd
The mod_dbd module manages SQL database connections using APR. It
provides database connections on request to modules requiring SQL
database functions, and takes care of managing databases with optimal
efficiency and scalability for both threaded and non-threaded MPMs.

%package -n ea-apache24-mod_deflate
Group: System Environment/Daemons
Summary: Compression filter module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_deflate
The mod_deflate module provides the DEFLATE output filter that allows
output from your server to be compressed before being sent to the
client over the network.

%package -n ea-apache24-mod_dialup
Group: System Environment/Daemons
Summary: Bandwidth rate limiting module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_dialup
It is a module that sends static content at a bandwidth rate limit,
defined by the various old modem standards.

%package -n ea-apache24-mod_dumpio
Group: System Environment/Daemons
Summary: Debug logging module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_dumpio
The mod_dumpio module allows for the logging of all input received by
Apache and/or all output sent by Apache to be logged (dumped) to the
error.log file.

The data logging is done right after SSL decoding (for input) and
right before SSL encoding (for output). As can be expected, this can
produce extreme volumes of data, and should only be used when
debugging problems.

%package -n ea-apache24-mod_env
Group: System Environment/Daemons
Summary: Environment variable module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_env
The mod_env module allows for control of internal environment
variables that are used by various Apache HTTP Server modules. These
variables are also provided to CGI scripts as native system
environment variables, and available for use in SSI pages. Environment
variables may be passed from the shell which invoked the httpd
process. Alternatively, environment variables may be set or unset
within the configuration process.

%package -n ea-apache24-mod_expires
Group: System Environment/Daemons
Summary: Client-side cache control module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_expires
The mod_expires module controls the setting of the Expires HTTP header
and the max-age directive of the Cache-Control HTTP header in server
responses. The expiration date can set to be relative to either the
time the source file was last modified, or to the time of the client
access.

%package -n ea-apache24-mod_ext_filter
Group: System Environment/Daemons
Summary: Generic filter module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_ext_filter
The mod_ext_filter module presents a simple and familiar programming
model for filters. With this module, a program which reads from stdin
and writes to stdout (i.e., a Unix-style filter command) can be a
filter for Apache.

%package -n ea-apache24-mod_file_cache
Group: System Environment/Daemons
Summary: Static file caching module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_file_cache
The mod_file_cache module provides two techniques for caching
frequently requested static files. Through configuration directives,
you can direct mod_file_cache to either open then mmap() a file, or to
pre-open a file and save the open file handle. Both techniques reduce
server load when processing requests for these files by doing part of
the work (specifically, the file I/O) for serving the file when the
server is started rather than during each request.

This cannot be used for speeding up CGI programs or other files which
are served by special content handlers. It can only be used for
regular files which are usually served by the Apache core content
handler.

%package -n ea-apache24-mod_headers
Group: System Environment/Daemons
Summary: Header control module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_headers
The mod_headers module provides directives to control and modify HTTP
request and response headers. Headers can be merged, replaced or
removed.

%package -n ea-apache24-mod_heartbeat
Group: System Environment/Daemons
Summary: Status reporting module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mod_watchdog = 0:%{version}-%{release}

%description -n ea-apache24-mod_heartbeat
The mod_heartbeat module sends multicast messages to a
mod_heartmonitor listener that advertises the servers current
connection count. Usually, mod_heartmonitor will be running on a proxy
server with mod_lbmethod_heartbeat loaded, which allows ProxyPass to
use the "heartbeat" lbmethod inside of ProxyPass.

mod_heartbeat itself is loaded on the origin server(s) that serve
requests through the proxy server(s).

%package -n ea-apache24-mod_heartmonitor
Group: System Environment/Daemons
Summary: Heartbeat monitoring module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mod_watchdog = 0:%{version}-%{release}

%description -n ea-apache24-mod_heartmonitor
The mod_heartmonitor module listens for server status messages
generated by mod_heartbeat enabled origin servers and makes their
status available to mod_lbmethod_heartbeat. This allows ProxyPass to
use the "heartbeat" lbmethod inside of ProxyPass.

This module uses the services of mod_slotmem_shm when available
instead of flat-file storage. No configuration is required to use
mod_slotmem_shm.

%package -n ea-apache24-mod_imagemap
Group: System Environment/Daemons
Summary: Server-side imagemap module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_imagemap
The mod_imagemap module processes .map files, thereby replacing the
functionality of the imagemap CGI program. Any directory or document
type configured to use the handler imap-file (using either AddHandler
or SetHandler) will be processed by this module.

%package -n ea-apache24-mod_info
Group: System Environment/Daemons
Summary: Extension providing a comprehensive overview of server configuration (NOT RECOMMENDED FOR SHARED SERVERS)
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_info
The mod_info module adds a server-info handler to the apache configuration,
allowing a detailed description of the current server configuration state.
It is not appropriate for shared hosting systems.

%package -n ea-apache24-mod_lbmethod_bybusyness
Group: System Environment/Daemons
Summary: Busyness load-balancing module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mod_proxy_balancer = 0:%{version}-%{release}
Provides: ea-apache24-lbmethod = bybusyness

%description -n ea-apache24-mod_lbmethod_bybusyness
The mod_lbmethod_bybusyness module keeps track of how many requests
each worker is currently assigned at present. A new request is
automatically assigned to the worker with the lowest number of active
requests. This is useful in the case of workers that queue incoming
requests independently of Apache, to ensure that queue length stays
even and a request is always given to the worker most likely to
service it the fastest and reduce latency.

%package -n ea-apache24-mod_lbmethod_byrequests
Group: System Environment/Daemons
Summary: Request load-balancing module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mod_proxy_balancer = 0:%{version}-%{release}
Provides: ea-apache24-lbmethod = byrequests

%description -n ea-apache24-mod_lbmethod_byrequests
The mod_lbmethod_byrequests module distributes requests among the
various workers to ensure that each gets their configured share of the
number of requests.

%package -n ea-apache24-mod_lbmethod_bytraffic
Group: System Environment/Daemons
Summary: Traffic load-balancing module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mod_proxy_balancer = 0:%{version}-%{release}
Provides: ea-apache24-lbmethod = bytraffic

%description -n ea-apache24-mod_lbmethod_bytraffic
The mod_lbmethod_bytraffic module distributes requests among the
various workers to ensure that each gets their configured share of the
number of requests.  In contrast to mod_lbmethod_byrequests, which has
a similar balancing logic, bytraffic weights each request by the
number of bytes in the request.

%package -n ea-apache24-mod_lbmethod_heartbeat
Group: System Environment/Daemons
Summary: Heartbeat load-balancing module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mod_proxy_balancer = 0:%{version}-%{release}
Requires: ea-apache24-mod_heartmonitor = 0:%{version}-%{release}
Provides: ea-apache24-lbmethod = heartbeat

%description -n ea-apache24-mod_lbmethod_heartbeat
The mod_lbmethod_heartbeat module uses the services of
mod_heartmonitor to balance between origin servers that are providing
heartbeat info via the mod_heartbeat module.

This load balancing algorithm favors servers with more ready (idle)
capacity over time, but does not select the server with the most ready
capacity every time. Servers that have 0 active clients are penalized,
with the assumption that they are not fully initialized.

%package -n ea-apache24-mod_ldap
Group: System Environment/Daemons
Summary: LDAP connection-handling module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apr-util-ldap

%description -n ea-apache24-mod_ldap
The mod_ldap module was created to improve the performance of websites
relying on backend connections to LDAP servers. In addition to the
functions provided by the standard LDAP libraries, this module adds an
LDAP connection pool and an LDAP shared memory cache.

%package -n ea-apache24-mod_log_debug
Group: System Environment/Daemons
Summary: Debug logging module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_log_debug
The mod_log_debug module provides a LogMessage directive which may be
used to log arbitrary data.

%package -n ea-apache24-mod_log_forensic
Group: System Environment/Daemons
Summary: Forensic logging module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_log_forensic
The mod_log_forensic module provides for forensic logging of client
requests. Logging is done before and after processing a request, so
the forensic log contains two log lines for each request. The forensic
logger is very strict, which means:

  - The format is fixed. You cannot modify the logging format at
    runtime.
  - If it cannot write its data, the child process exits immediately
    and may dump core (depending on your CoreDumpDirectory
    configuration).

The check_forensic script may be helpful in evaluating the forensic
log output.

%package -n ea-apache24-mod_lua
Group: System Environment/Daemons
Summary: Lua language extension module for the Apache HTTP Server (NOT RECOMMENDED FOR SHARED SERVERS)
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_lua
The mod_lua module allows the server to be extended with scripts
written in the Lua programming language. The extension points (hooks)
available with mod_lua include many of the hooks available to natively
compiled Apache HTTP Server modules, such as mapping requests to
files, generating dynamic responses, access control, authentication,
and authorization

%package -n ea-apache24-mod_macro
Group: System Environment/Daemons
Summary: Configuration macro module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_macro
The mod_macro module provides macros within Apache httpd runtime
configuration files, to ease the process of creating numerous similar
configuration blocks. When the server starts up, the macros are
expanded using the provided parameters, and the result is processed as
along with the rest of the configuration file.

%package -n ea-apache24-mod_mime_magic
Group: System Environment/Daemons
Summary: MIME-type autosensing module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_mime_magic
The mod_mime_magic module determines the MIME type of files in the
same way the Unix file(1) command works: it looks at the first few
bytes of the file. It is intended as a "second line of defense" for
cases that mod_mime cannot resolve.

%package -n ea-apache24-mod_proxy
Group: System Environment/Daemons
Summary: Proxy server module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_proxy
The mod_proxy module implements a proxy/gateway for Apache HTTP
Server, supporting a number of popular protocols as well as several
different load balancing algorithms. Third-party modules can add
support for additional protocols and load balancing algorithms.

%package -n ea-apache24-mod_proxy_ajp
Group: System Environment/Daemons
Summary: Apache JServ Protocol 1.3 proxy module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mod_proxy = 0:%{version}-%{release}

%description -n ea-apache24-mod_proxy_ajp
The mod_proxy_ajp module provides proxy support for the Apache JServ
Protocol version 1.3.

%package -n ea-apache24-mod_proxy_balancer
Group: System Environment/Daemons
Summary: Load-balancing module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mod_proxy = 0:%{version}-%{release}
Requires: ea-apache24-lbmethod

%description -n ea-apache24-mod_proxy_balancer
The mod_proxy_balancer module provides load balancing support for
HTTP, FTP and AJP13 protocols.  Load balancing scheduler algorithms
are not provided by this module but by the mod_lbmethod_* modules.

%package -n ea-apache24-mod_proxy_connect
Group: System Environment/Daemons
Summary: CONNECT HTTP method proxy module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mod_proxy = 0:%{version}-%{release}

%description -n ea-apache24-mod_proxy_connect
The mod_proxy_connect module provides support for the CONNECT HTTP
method. This method is mainly used to tunnel SSL requests through
proxy servers.

%package -n ea-apache24-mod_proxy_express
Group: System Environment/Daemons
Summary: Dynamic reverse-proxy module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mod_proxy = 0:%{version}-%{release}

%description -n ea-apache24-mod_proxy_express
The mod_proxy_express module creates dynamically configured mass
reverse proxies, by mapping the Host: header of the HTTP request to a
server name and backend URL stored in a DBM file. This allows for easy
use of a huge number of reverse proxies with no configuration
changes. It is much less feature-full than mod_proxy_balancer, which
also provides dynamic growth, but is intended to handle much, much
larger numbers of backends. It is ideally suited as a front-end HTTP
switch.

%package -n ea-apache24-mod_proxy_fcgi
Group: System Environment/Daemons
Summary: FastCGI proxy module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mod_proxy = 0:%{version}-%{release}

%description -n ea-apache24-mod_proxy_fcgi
The mod_proxy_fcgi module provides support for the FastCGI
protocol. Unlike mod_fcgid and mod_fastcgi, mod_proxy_fcgi has no
provision for starting the application process; fcgistarter is
provided (on some platforms) for that purpose. Alternatively, external
launching or process management may be available in the FastCGI
application framework in use.

%package -n ea-apache24-mod_proxy_fdpass
Group: System Environment/Daemons
Summary: File descriptor-passing proxy module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mod_proxy = 0:%{version}-%{release}

%description -n ea-apache24-mod_proxy_fdpass
The mod_proxy_fdpass module provides support for the passing the
socket of the client to another process.

mod_proxy_fdpass uses the ability of AF_UNIX domain sockets to pass an
open file descriptor to allow another process to finish handling a
request.

The module has a proxy_fdpass_flusher provider interface, which allows
another module to optionally send the response headers, or even the
start of the response body. The default flush provider disables
keep-alive, and sends the response headers, letting the external
process just send a response body.

At this time the only data passed to the external process is the
client socket. To receive a client socket, call recvfrom with an
allocated struct cmsghdr. Future versions of this module may include
more data after the client socket, but this is not implemented at this
time.

%package -n ea-apache24-mod_proxy_ftp
Group: System Environment/Daemons
Summary: FTP proxy module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mod_proxy = 0:%{version}-%{release}

%description -n ea-apache24-mod_proxy_ftp
The mod_proxy_ftp module provides support for the proxying FTP
sites. Note that FTP support is currently limited to the GET method.

%package -n ea-apache24-mod_proxy_hcheck
Group: System Environment/Daemons
Summary: Dynamic health check of Balancer members (workers) for mod_proxy
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mod_proxy = 0:%{version}-%{release}
Requires: ea-apache24-mod_watchdog = 0:%{version}-%{release}
Conflicts: ea-apache24-mpm = forked

%description -n ea-apache24-mod_proxy_hcheck
The mod_proxy_hcheck module provides support for dynamic health checking of
balancer members (workers).  This can be enabled on a worker-by-worker basis.
The health check is done independently of the actual revers proxy requests.

%package -n ea-apache24-mod_proxy_html
Group: System Environment/Daemons
Summary: HTML and XML content filters for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mod_proxy = 0:%{version}-%{release}
%if 0%{?rhel} >= 10
BuildRequires: libxml2 libxml2-devel
%else
BuildRequires: ea-libxml2 ea-libxml2-devel
%endif
Obsoletes: mod_proxy_html

%description -n ea-apache24-mod_proxy_html
The mod_proxy_html and mod_xml2enc modules provide filters which can
transform and modify HTML and XML content.

%package -n ea-apache24-mod_proxy_http
Group: System Environment/Daemons
Summary: HTTP/HTTPS proxy module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mod_proxy = 0:%{version}-%{release}

%description -n ea-apache24-mod_proxy_http
The mod_proxy_http module provides the features used for proxying HTTP
and HTTPS requests. mod_proxy_http supports HTTP/0.9, HTTP/1.0 and
HTTP/1.1. It does not provide any caching abilities. If you want to
set up a caching proxy, you might want to use the additional service
of the mod_cache module.

%package -n ea-apache24-mod_proxy_scgi
Group: System Environment/Daemons
Summary: SCGI module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mod_proxy = 0:%{version}-%{release}

%description -n ea-apache24-mod_proxy_scgi
The mod_proxy_scgi module provides support for the SCGI protocol,
version 1.

%package -n ea-apache24-mod_proxy_wstunnel
Group: System Environment/Daemons
Summary: Websockets proxy module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mod_proxy = 0:%{version}-%{release}

%description -n ea-apache24-mod_proxy_wstunnel
The mod_proxy_wstunnel module provides support for the tunnelling of
web socket connections to a backend websockets server. The connection
is automagically upgraded to a websocket connection.

%package -n ea-apache24-mod_proxy_uwsgi
Group: System Environment/Daemons
Summary: Websockets proxy module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mod_proxy = 0:%{version}-%{release}

%description -n ea-apache24-mod_proxy_uwsgi
The uWSGI project provides application servers (for various programming languages and protocols
like perl (PSGI), python (WSGI), ruby (Rack), Lua WSAPI, CGI, PHP, and Go ... to name a few),
proxies, process managers and monitors.
All implemented using a common api and a common configuration style.

%package -n ea-apache24-mod_ratelimit
Group: System Environment/Daemons
Summary: Client bandwidth limiting module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_ratelimit
The mod_ratelimit module provides a filter named RATE_LIMIT to limit
client bandwidth. The connection speed to be simulated is specified,
in KiB/s, using the environment variable rate-limit.

%package -n ea-apache24-mod_reflector
Group: System Environment/Daemons
Summary: Filter-as-service module for the Apache HTTP server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_reflector
The mod_reflector module allows request bodies to be reflected back to
the client, in the process passing the request through the output
filter stack. A suitably configured chain of filters can be used to
transform the request into a response. This module can be used to turn
an output filter into an HTTP service.

%package -n ea-apache24-mod_remoteip
Group: System Environment/Daemons
Summary: IP replacement module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_remoteip
The mod_remoteip module is used to treat the useragent which initiated
the request as the originating useragent as identified by httpd for
the purposes of authorization and logging, even where that useragent
is behind a load balancer, front end server, or proxy server.

The module overrides the client IP address for the connection with the
useragent IP address reported in the request header configured with
the RemoteIPHeader directive.

Once replaced as instructed, this overridden useragent IP address is
then used for the mod_authz_host Require ip feature, is reported by
mod_status, and is recorded by mod_log_config %a and core %a format
strings. The underlying client IP of the connection is available in
the %{c}a format string.

%package -n ea-apache24-mod_reqtimeout
Group: System Environment/Daemons
Summary: Request timeout module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_reqtimeout
The mod_reqtimeout module can set various timeouts for receiving the
request headers and the request body from the client. If the client
fails to send headers or body within the configured time, a 408
REQUEST TIME OUT error is sent.

%package -n ea-apache24-mod_request
Group: System Environment/Daemons
Summary: Request body retention module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_request
The mod_request module makes request bodies available to applications,
where they may normally be discarded, i.e. during GET requests.

%package -n ea-apache24-mod_sed
Group: System Environment/Daemons
Summary: Regex replacement content filter module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_sed
The mod_sed module is an in-process content filter. The mod_sed filter
implements the sed editing commands implemented by the Solaris 10 sed
program as described in the manual page. However, unlike sed, mod_sed
does not take data from standard input. Instead, the filter acts on
the entity data sent between client and server. mod_sed can be used as
an input or output filter. mod_sed is a content filter, which means
that it cannot be used to modify client or server http headers.

The mod_sed output filter accepts a chunk of data, executes the sed
scripts on the data, and generates the output which is passed to the
next filter in the chain.

The mod_sed input filter reads the data from the next filter in the
chain, executes the sed scripts, and returns the generated data to the
caller filter in the filter chain.

Both the input and output filters only process the data if newline
characters are seen in the content. At the end of the data, the rest
of the data is treated as the last line.

%package -n ea-apache24-mod_session
Group: System Environment/Daemons
Summary: Session interface for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Requires: ea-apache24-mod_request
Requires: ea-apr-util-openssl

%description -n ea-apache24-mod_session
The mod_session module and associated backends provide an abstract
interface for storing and accessing per-user session data.

%package -n ea-apache24-mod_slotmem_plain
Group: System Environment/Daemons
Summary: Slot-based memory module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_slotmem_plain
The mod_slotmem_plain module provides for creation and access to a
plain memory segment in which the datasets are organized in "slots."

%package -n ea-apache24-mod_socache_memcache
Group: System Environment/Daemons
Summary: Memcache-based object cache module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_socache_memcache
The mod_socache_memcache module is a shared object cache provider
which provides for creation and access to a cache backed by the
memcached high-performance, distributed memory object caching system.

%package -n ea-apache24-mod_socache_redis
Group: System Environment/Daemons
Summary: shared object cache provider which provides access to a cache backed by Redis
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_socache_redis
mod_socache_redis is a shared object cache provider which provides for creation
and access to a cache backed by the Redis high-performance, distributed memory object caching system.

%package -n ea-apache24-mod_speling
Group: System Environment/Daemons
Summary: URL fallback module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_speling
The mod_speling module addresses the problem that requests to
documents sometimes cannot be served by the core apache server because
the request was misspelled or miscapitalized.  mod_speling tries to
find a matching document, even after all other modules gave up. It
does its work by comparing each document name in the requested
directory against the requested document name without regard to case,
and allowing up to one misspelling (character insertion / omission /
transposition or wrong character). A list is built with all document
names which were matched using this strategy.

%package -n ea-apache24-mod_ssl
Group: System Environment/Daemons
Summary: SSL/TLS module for the Apache HTTP Server
%if 0%{?rhel} < 8
BuildRequires: ea-openssl11 >= %{ea_openssl_ver}, ea-openssl11-devel >= %{ea_openssl_ver}
Requires(post): ea-openssl11 >= %{ea_openssl_ver}
%else
# In C8 we use system openssl. See DESIGN.md in ea-openssl11 git repo for details
BuildRequires: openssl, openssl-devel
Requires(post): openssl
%endif

%if 0%{?rhel} >= 10
Requires(post): /usr/bin/cat
%else
Requires(post): /bin/cat
%endif

Requires(pre): ea-apache24
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Obsoletes: stronghold-mod_ssl, mod_ssl

%description -n ea-apache24-mod_ssl
The mod_ssl module provides strong cryptography for the Apache Web
server via the Secure Sockets Layer (SSL) and Transport Layer
Security (TLS) protocols.

%package -n ea-apache24-mod_substitute
Group: System Environment/Daemons
Summary: Response body substitution module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_substitute
The mod_substitute module provides a mechanism to perform both regular
expression and fixed string substitutions on response bodies.

%package -n ea-apache24-mod_suexec
Group: System Environment/Daemons
Summary: Per-user/group execution module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}
Provides: ea-apache24-exec_code_asuser
Conflicts: ea-apache24-exec_code_asuser
Conflicts: ea-apache24-mod_itk ea-apache24-mod_ruid2

%description -n ea-apache24-mod_suexec
The mod_suexec module allows CGI scripts to run as a specified user
and group.  The suexec support program is contained within the
ea-apache24 package.

%package -n ea-apache24-mod_unique_id
Group: System Environment/Daemons
Summary: Unique request identifier module for the Apache HTTP Server (causes noticeable performance degradation)
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_unique_id
The mod_unique_id module provides a magic token for each request which
is guaranteed to be unique across all requests under very specific
conditions. The unique identifier is even unique across multiple
machines in a properly configured cluster of machines. The environment
variable UNIQUE_ID is set to the identifier for each request.

%package -n ea-apache24-mod_usertrack
Group: System Environment/Daemons
Summary: Cookie tracking module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_usertrack
The mod_usertrack module provides tracking of a users through websites
via browser cookies.

%package -n ea-apache24-mod_version
Group: System Environment/Daemons
Summary: Version comparing module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_version
The mod_version module is designed for the use in test suites and
large networks which have to deal with different httpd versions and
different configurations. It provides a new container -- <IfVersion>,
which allows a flexible version checking including numeric comparisons
and regular expressions.

%package -n ea-apache24-mod_vhost_alias
Group: System Environment/Daemons
Summary: Dynamic mass virtual hosting module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_vhost_alias
The mod_vhost_alias module creates dynamically configured virtual
hosts, by allowing the IP address and/or the Host: header of the HTTP
request to be used as part of the pathname to determine what files to
serve. This allows for easy use of a huge number of virtual hosts with
similar configurations.

%package -n ea-apache24-mod_watchdog
Group: System Environment/Daemons
Summary: Periodic task module for the Apache HTTP Server
Requires: ea-apache24 = 0:%{version}-%{release}, ea-apache24-mmn = %{mmnisa}

%description -n ea-apache24-mod_watchdog
The mod_watchdog module defines programmatic hooks for other modules
to periodically run tasks. These modules can register handlers for
mod_watchdog hooks.

%prep
%setup -q -n httpd-%{version}
%patch1 -p1 -b .apctl
%patch3 -p1 -b .deplibs
%patch5 -p1 -b .layout

%patch24 -p1 -b .corelimit
%patch27 -p1 -b .icons

%patch30 -p1 -b .cachehardmax


%patch301 -p1 -b .cpapachectl
%patch302 -p1 -b .cpsuexec1
%patch303 -p1 -b .cpsuexec2
%patch304 -p1 -b .cpsuexec3
%patch305 -p1 -b .cpapxs
%patch306 -p1 -b .symlink

%patch401 -p1 -b .randomsstartupperformance
%patch403 -p1 -b .longlostpids

%patch500 -p1 -b .aliassymlink
%patch601 -p1 -b .speedupmodulelookup

%patch701 -p1 -b .apxsfixtopbuilddir

%if 0%{?rhel} >= 8
%patch801 -p1 -b .instructaboutelinks
%endif

# Patch in the vendor string and the release string
sed -i '/^#define PLATFORM/s/Unix/%{vstring}/' os/unix/os.h
sed -i 's/@RELEASE@/%{release}/' server/core.c

# Prevent use of setcap in "install-suexec-caps" target.
sed -i '/suexec/s,setcap ,echo Skipping setcap for ,' Makefile.in

# Safety check: prevent build if defined MMN does not equal upstream MMN.
vmmn=`echo MODULE_MAGIC_NUMBER_MAJOR | cpp -include include/ap_mmn.h | sed -n '/^2/p'`
if test "x${vmmn}" != "x%{mmn}"; then
   : Error: Upstream MMN is now ${vmmn}, packaged MMN is %{mmn}
   : Update the mmn macro and rebuild.
   exit 1
fi

: Building with MMN %{mmn}, MMN-ISA %{mmnisa} and vendor string '%{vstring}'

%build
# Force dependency resolution to pick /usr/bin/perl instead of /bin/perl
# This helps downstream users of our RPMS (see: EA-7468)
export PATH="/usr/bin:$PATH"
# forcibly prevent use of bundled apr, apr-util, pcre
rm -rf srclib/{apr,apr-util,pcre}

# regenerate configure scripts
autoheader && autoconf || exit 1

# Before configure; fix location of build dir in generated apxs
%{__perl} -pi -e "s:\@exp_installbuilddir\@:%{_libdir}/apache2/build:g" support/apxs.in

export CFLAGS="$RPM_OPT_FLAGS"
export LDFLAGS="-Wl,-z,relro,-z,now"

%ifarch ppc64
CFLAGS="$CFLAGS -O3"
%endif

# Hard-code path to links to avoid unnecessary builddep
export LYNX_PATH=/usr/bin/links

# Build the daemon
./configure \
    --prefix=%{_sysconfdir}/apache2 \
    --exec-prefix=%{_prefix} \
    --bindir=%{_bindir} \
    --sbindir=%{_sbindir} \
    --mandir=%{_mandir} \
    --libdir=%{_libdir} \
    --sysconfdir=%{_sysconfdir}/apache2/conf \
    --includedir=%{_includedir}/apache2 \
    --libexecdir=%{_libdir}/apache2/modules \
    --datadir=%{contentdir} \
    --enable-layout=cPanel \
    --with-installbuilddir=%{_libdir}/apache2/build \
    --enable-mpms-shared=all \
    --with-apr=%{ea_apr_dir} --with-apr-util=%{ea_apu_dir} \
    --enable-suexec --with-suexec \
    --enable-suexec-capabilities \
    --with-suexec-caller=%{suexec_caller} \
    --with-suexec-docroot=/ \
    --with-suexec-logfile=%{_sysconfdir}/apache2/logs/suexec_log \
    --with-suexec-bin=%{_sbindir}/suexec \
    --with-suexec-uidmin=100 --with-suexec-gidmin=100 \
    --enable-pie \
    --with-pcre \
    --enable-mods-shared=all \
%if 0%{?rhel} >= 7
    --enable-systemd \
%endif
%if %{with_http2}
%if 0%{?rhel} < 8
    --enable-ssl --with-ssl=/opt/cpanel/ea-openssl11/ \
%else
    --enable-ssl --with-ssl \
%endif
    --enable-ssl-staticlib-deps \
%if 0%{?rhel} >= 10
    --with-nghttp2 \
%else
    --with-nghttp2=/opt/cpanel/nghttp2/ \
%endif
    --enable-nghttp2-staticlib-deps \
%else
    --enable-ssl --with-ssl \
%endif
    --disable-distcache \
    --enable-proxy \
    --enable-proxy-fdpass \
    --enable-cache \
    --enable-disk-cache \
    --enable-ldap \
    --enable-authnz-ldap \
    --enable-cgid --enable-cgi \
    --enable-authn-anon \
    --enable-authn-alias \
    --enable-imagemap \
    --disable-echo \
    --enable-brotli \
%if 0%{?rhel} >= 10
    --enable-libxml2 \
%else
    --with-libxml2=/opt/cpanel/ea-libxml2/include/libxml2 \
    --with-brotli=/opt/cpanel/ea-brotli \
%endif
    --disable-v4-mapped \
%if 0%{?rhel} >= 10
%else
    MOD_PROXY_HTML_LDADD="-L/opt/cpanel/ea-libxml2/%{_lib} -R/opt/cpanel/ea-libxml2/%{_lib}" \
    MOD_XML2ENC_LDADD="-L/opt/cpanel/ea-libxml2/%{_lib} -R/opt/cpanel/ea-libxml2/%{_lib}" \
    MOD_BROTLI_LDADD="-L/opt/cpanel/ea-brotli/lib -R/opt/cpanel/ea-brotli/lib" \
%if 0%{?rhel} < 8
    MOD_SSL_LDADD="-L/opt/cpanel/ea-openssl11/%{_lib} -R/opt/cpanel/ea-openssl11/%{_lib}" \
    UTIL_LDFLAGS="-L/opt/cpanel/ea-openssl11/%{_lib} -R/opt/cpanel/ea-openssl11/%{_lib}" \
%if %{with_http2}
    MOD_HTTP2_LDADD="-L/opt/cpanel/ea-openssl11/%{_lib} -R/opt/cpanel/ea-openssl11/%{_lib}" \
%endif
%endif
%endif
    $*

%if 0%{?rhel} >= 8
%if 0%{?rhel} < 10
# This is ugly, very ugly.
# ZC-6833 was created to eventually come up with a proper solution for these
# linking issues.
# But some of the command line programs of Apache, link with libdb, that is
# Berkley DB.  And Berkley DB on CentOS 8, links against system openssl.
# The key fix here is -rpath-link, telling the linker that sub programs can
# link against the system directory, then -l:libcrypto.so.1.1 I am telling it
# to link that particular library in.

cat support/Makefile >> support/Makefile.tmp
cp -f support/Makefile.tmp support/Makefile

# PROGRAM_LDADD will satisfy almost all of them
sed -i '/^.*PROGRAM_LDADD[ \t]*=.*$/ s/$/ $(SYS_OPENSSL)/' support/Makefile

# ab, does it's own thing so I need to do our thing
sed -i '/^.*$(LT_LDFLAGS) $(ALL_LDFLAGS) -o $@ $(ab_LTFLAGS) $(ab_OBJECTS) $(ab_LDADD).*$/ s/$/ $(SYS_OPENSSL)/' support/Makefile
%endif
%endif

make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT

make DESTDIR=$RPM_BUILD_ROOT install

# install the forensic script
install -m 755 support/check_forensic $RPM_BUILD_ROOT%{_sbindir}

%if 0%{?rhel} < 7
# install SYSV init stuff
mkdir -p $RPM_BUILD_ROOT%{_initrddir}
for s in httpd htcacheclean; do
    install -p -m 755 $RPM_SOURCE_DIR/${s}.init \
        $RPM_BUILD_ROOT%{_initrddir}/${s}
done
%endif

# install systemd service file for CentOS 7 and up
%if 0%{?rhel} >= 7
mkdir -p $RPM_BUILD_ROOT%{_unitdir}
for s in httpd.service htcacheclean.service; do
  install -p -m 644 $RPM_SOURCE_DIR/${s} \
                    $RPM_BUILD_ROOT%{_unitdir}/${s}
done
%endif

# install conf file/directory
mkdir $RPM_BUILD_ROOT%{_sysconfdir}/apache2/conf.d \
      $RPM_BUILD_ROOT%{_sysconfdir}/apache2/conf.modules.d \
      $RPM_BUILD_ROOT%{_sysconfdir}/apache2/conf.d/includes \
      $RPM_BUILD_ROOT%{_sysconfdir}/apache2/bin

install -m 644 $RPM_SOURCE_DIR/README.confd \
    $RPM_BUILD_ROOT%{_sysconfdir}/apache2/conf.d/README

for f in brotli.conf cgid.conf manual.conf cperror.conf autoindex.conf ; do
  install -m 644 -p $RPM_SOURCE_DIR/$f \
        $RPM_BUILD_ROOT%{_sysconfdir}/apache2/conf.d/$f
done

%if %{with_http2}
install -m 644 -p $RPM_SOURCE_DIR/http2.conf $RPM_BUILD_ROOT%{_sysconfdir}/apache2/conf.d/http2.conf
%endif

# Extra config trimmed:
rm -v docs/conf/extra/httpd-{ssl,userdir}.conf

rm $RPM_BUILD_ROOT%{_sysconfdir}/apache2/conf/*.conf
install -m 644 -p $RPM_SOURCE_DIR/httpd.conf \
   $RPM_BUILD_ROOT%{_sysconfdir}/apache2/conf/httpd.conf

mkdir $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
for s in httpd htcacheclean; do
  install -m 644 -p $RPM_SOURCE_DIR/${s}.sysconf \
                    $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/${s}
done

# tmpfiles.d configuration
%if 0%{?rhel} >= 7
mkdir -p $RPM_BUILD_ROOT%{_prefix}/lib/tmpfiles.d
install -m 644 -p $RPM_SOURCE_DIR/apache2.tmpfiles \
   $RPM_BUILD_ROOT%{_prefix}/lib/tmpfiles.d/apache2.conf
%endif

# Other directories
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/dav \
         $RPM_BUILD_ROOT%{_localstatedir}/run/apache2/htcacheclean

# Create cache directory
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/cache/apache2 \
         $RPM_BUILD_ROOT%{_localstatedir}/cache/apache2/proxy \
         $RPM_BUILD_ROOT%{_localstatedir}/cache/apache2/ssl

# Make the MMN accessible to module packages
echo %{mmnisa} > $RPM_BUILD_ROOT%{_includedir}/apache2/.mmn
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/rpm
cat > $RPM_BUILD_ROOT%{_sysconfdir}/rpm/macros.apache2 <<EOF
%%_httpd_mmn %{mmnisa}
%%_httpd_apxs %{_bindir}/apxs
%%_httpd_dir %{_sysconfdir}/apache2
%%_httpd_bindir %{_httpd_dir}/bin
%%_httpd_modconfdir %{_httpd_dir}/conf.modules.d
%%_httpd_confdir %{_httpd_dir}/conf.d
%%_httpd_contentdir %{contentdir}
%%_httpd_moddir %{_libdir}/apache2/modules
EOF

# Handle contentdir
mkdir $RPM_BUILD_ROOT%{contentdir}/noindex
tar xzf $RPM_SOURCE_DIR/centos-noindex.tar.gz \
        -C $RPM_BUILD_ROOT%{contentdir}/noindex/ \
        --strip-components=1

rm -rf %{contentdir}/htdocs

# remove manual sources
find $RPM_BUILD_ROOT%{contentdir}/manual \( \
    -name \*.xml -o -name \*.xml.* -o -name \*.ent -o -name \*.xsl -o -name \*.dtd \
    \) -print0 | xargs -0 rm -f

# Strip the manual down just to English and replace the typemaps with flat files:
set +x
for f in `find $RPM_BUILD_ROOT%{contentdir}/manual -name \*.html -type f`; do
   if test -f ${f}.en; then
      cp ${f}.en ${f}
      rm ${f}.*
   fi
done
set -x

# Clean Document Root
rm -v $RPM_BUILD_ROOT%{docroot}/html/*.html \
      $RPM_BUILD_ROOT%{docroot}/cgi-bin/*

# Symlink for the powered-by-$DISTRO image:
ln -s ../noindex/images/poweredby.png \
        $RPM_BUILD_ROOT%{contentdir}/icons/poweredby.png

# symlinks for /etc/httpd
ln -s ../..%{_localstatedir}/log/apache2 $RPM_BUILD_ROOT/etc/apache2/logs
ln -s ../..%{_localstatedir}/run/apache2 $RPM_BUILD_ROOT/etc/apache2/run
ln -s ../..%{_libdir}/apache2/modules $RPM_BUILD_ROOT/etc/apache2/modules

mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/apache2/logs
touch $RPM_BUILD_ROOT/%{_sysconfdir}/apache2/logs/suexec_log

# fix man page paths
sed -e "s|/usr/local/apache2/conf/httpd.conf|/etc/apache2/conf/httpd.conf|" \
    -e "s|/usr/local/apache2/conf/mime.types|/etc/mime.types|" \
    -e "s|/usr/local/apache2/conf/magic|/etc/apache2/conf/magic|" \
    -e "s|/usr/local/apache2/logs/error_log|/var/log/apache2/error_log|" \
    -e "s|/usr/local/apache2/logs/access_log|/var/log/apache2/access_log|" \
    -e "s|/usr/local/apache2/logs/suexec_log|/var/log/apache2/suexec_log|" \
    -e "s|/usr/local/apache2/logs/httpd.pid|/var/run/apache2/httpd.pid|" \
    -e "s|/usr/local/apache2|/etc/apache2|" < docs/man/httpd.8 \
  > $RPM_BUILD_ROOT%{_mandir}/man8/httpd.8

# Make ap_config_layout.h libdir-agnostic
sed -i '/.*DEFAULT_..._LIBEXECDIR/d;/DEFAULT_..._INSTALLBUILDDIR/d' \
    $RPM_BUILD_ROOT%{_includedir}/apache2/ap_config_layout.h

# Fix path to instdso in special.mk
sed -i '/instdso/s,top_srcdir,top_builddir,' \
    $RPM_BUILD_ROOT%{_libdir}/apache2/build/special.mk

# Make individual module package files
# We'll number the conf.modules.d files, so we can force load order,
# and since there's a lot of them, we'll use 3 digits

# Systemd should be in the first batch to be loaded
%if 0%{?rhel} >= 7
for mod in systemd
do
    printf -v modname "000_mod_%s.conf" $mod
    cat > $RPM_BUILD_ROOT%{_sysconfdir}/apache2/conf.modules.d/${modname} <<EOF
# Enable mod_${mod}
LoadModule ${mod}_module modules/mod_${mod}.so
EOF
    cat > files.${mod} <<EOF
%attr(755,root,root) %{_libdir}/apache2/modules/mod_${mod}.so
%config(noreplace) %attr(644,root,root) %{_sysconfdir}/apache2/conf.modules.d/${modname}
EOF
done
%endif

# MPMs are mutually exclusive, and should be loaded first
for mod in mpm_event mpm_prefork mpm_worker
do
    printf -v modname "000_mod_%s.conf" $mod
    cat > $RPM_BUILD_ROOT%{_sysconfdir}/apache2/conf.modules.d/${modname} <<EOF
# Enable mod_${mod}
LoadModule ${mod}_module modules/mod_${mod}.so
EOF
    if [ "${mod}" = "mpm_prefork" ]; then
        cat >> $RPM_BUILD_ROOT%{_sysconfdir}/apache2/conf.modules.d/${modname} <<EOF
Mutex sysvsem
EOF
    fi
    cat > files.${mod} <<EOF
%attr(755,root,root) %{_libdir}/apache2/modules/mod_${mod}.so
%config(noreplace) %attr(644,root,root) %{_sysconfdir}/apache2/conf.modules.d/${modname}
EOF
done

# CGIs are also mutually exclusive
for mod in cgi cgid
do
    printf -v modname "005_mod_%s.conf" $mod
    cat > $RPM_BUILD_ROOT%{_sysconfdir}/apache2/conf.modules.d/${modname} <<EOF
# Enable mod_${mod}
LoadModule ${mod}_module modules/mod_${mod}.so
EOF
    cat > files.${mod} <<EOF
%attr(755,root,root) %{_libdir}/apache2/modules/mod_${mod}.so
%config(noreplace) %attr(644,root,root) %{_sysconfdir}/apache2/conf.modules.d/${modname}
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
%if %{with_http2}
  http2 \
%endif
  proxy_html xml2enc \
  ldap authnz_ldap \
  session session_cookie session_dbd auth_form session_crypto proxy_hcheck
do
    printf -v modname "%03d_mod_%s.conf" $modnum $mod
    # add to the condition to have comment-disabled modules
    if [ "${mod}" = "info" ]; then
      cat > $RPM_BUILD_ROOT%{_sysconfdir}/apache2/conf.modules.d/${modname} <<EOF
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
      cat > $RPM_BUILD_ROOT%{_sysconfdir}/apache2/conf.modules.d/${modname} <<EOF
# This module holds a great deal of power over httpd, which is both a strength
# and a potential security risk. It is not recommended that you use this module
# on a server that is shared with users you do not trust, as it can be abused
# to change the internal workings of httpd.
#
# If you still want to use this module, uncomment the LoadModule directive below.
#LoadModule ${mod}_module modules/mod_${mod}.so
EOF
    else
      cat > $RPM_BUILD_ROOT%{_sysconfdir}/apache2/conf.modules.d/${modname} <<EOF
# Enable mod_${mod}
LoadModule ${mod}_module modules/mod_${mod}.so
EOF
    fi
    if [ "${mod}" = "reqtimeout" ]; then
      cat >> $RPM_BUILD_ROOT%{_sysconfdir}/apache2/conf.modules.d/${modname} <<EOF
RequestReadTimeout handshake=0 header=20-40,MinRate=500 body=20,MinRate=500
EOF
    fi
    if [ "${mod}" = "info" ]; then
        cat > files.${mod} <<EOF
%attr(755,root,root) %{_libdir}/apache2/modules/mod_${mod}.so
%config(noreplace) %attr(644,root,root) %{_sysconfdir}/apache2/conf.modules.d/${modname}
%doc docs/conf/extra/httpd-info.conf
EOF
    elif [ "${mod}" = "http2" ]; then
    	cat > files.${mod} <<EOF
%attr(755,root,root) %{_libdir}/apache2/modules/mod_${mod}.so
%config(noreplace) %attr(644,root,root) %{_sysconfdir}/apache2/conf.modules.d/${modname}
EOF
    else
        cat > files.${mod} <<EOF
%attr(755,root,root) %{_libdir}/apache2/modules/mod_${mod}.so
%config(noreplace) %attr(644,root,root) %{_sysconfdir}/apache2/conf.modules.d/${modname}
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

%if 0%{?rhel} >= 7
cat files.systemd >> files.httpd
%endif

# Remove unpackaged files
rm -vf \
      $RPM_BUILD_ROOT%{_libdir}/*.exp \
      $RPM_BUILD_ROOT%{_libdir}/apache2/modules/*.exp \
      $RPM_BUILD_ROOT%{_libdir}/apache2/build/config.nice \
      $RPM_BUILD_ROOT%{_bindir}/{ap?-config,dbmmanage} \
      $RPM_BUILD_ROOT%{_sbindir}/{checkgid,envvars*} \
      $RPM_BUILD_ROOT%{contentdir}/htdocs/* \
      $RPM_BUILD_ROOT%{_mandir}/man1/dbmmanage.* \
      $RPM_BUILD_ROOT%{contentdir}/cgi-bin/*

rm -rf $RPM_BUILD_ROOT/etc/apache2/conf/{original,extra}

# consistify for old to new %doc behavior
mkdir -p $RPM_BUILD_ROOT/usr/share/doc/ea-apache24
mkdir -p $RPM_BUILD_ROOT/usr/share/doc/ea-apache24/docs/conf/extra

for f in ABOUT_APACHE README CHANGES LICENSE VERSIONING NOTICE; do
    cp ./$f $RPM_BUILD_ROOT/usr/share/doc/ea-apache24/
done

for fd in httpd-dav.conf httpd-default.conf httpd-languages.conf httpd-manual.conf httpd-mpm.conf httpd-multilang-errordoc.conf httpd-vhosts.conf proxy-html.conf; do
    cp docs/conf/extra/$fd $RPM_BUILD_ROOT/usr/share/doc/ea-apache24/docs/conf/extra/$fd
done

echo "APACHEMODULES" $RPM_BUILD_ROOT $RPM_BUILD_ROOT/%{_libdir} $RPM_BUILD_ROOT/%{_libdir}/apache2/modules
ls -ld $RPM_BUILD_ROOT/%{_libdir}/apache2/modules/* || /bin/true

%pre
%include %{SOURCE46}

%post
%if 0%{?rhel} >= 7
%include %{SOURCE47}
%else
# Register the httpd service
/sbin/chkconfig --add httpd
/sbin/chkconfig --level 35 httpd on >/dev/null 2>&1 ||:
%endif

%preun
%if 0%{?rhel} >= 7
%include %{SOURCE48}
%else
if [ $1 = 0 ]; then
        /sbin/service httpd stop > /dev/null 2>&1
        /sbin/chkconfig --del httpd
        /sbin/service htcacheclean stop > /dev/null 2>&1
        /sbin/chkconfig --del htcacheclean
fi
%endif

# no need for %systemd_postun in %postun when 0%{?rhel} >= 7
# because it is a noop: https://fossies.org/linux/systemd/src/rpm/macros.systemd.in#l_77

%posttrans
test -f /etc/sysconfig/httpd-disable-posttrans || \
%if 0%{?rhel} >= 7
  /bin/systemctl try-restart httpd.service htcacheclean.service >/dev/null 2>&1 || :
%else
  /sbin/service httpd condrestart >/dev/null 2>&1 || :
  /sbin/service htcacheclean condrestart >/dev/null 2>&1 || :
%endif

%check
# Check the built modules are all PIC
if readelf -d $RPM_BUILD_ROOT%{_libdir}/apache2/modules/*.so | grep TEXTREL; then
   : modules contain non-relocatable code
   exit 1
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files -f files.httpd
%defattr(-,root,root)

%doc /usr/share/doc/ea-apache24/ABOUT_APACHE
%doc /usr/share/doc/ea-apache24/README
%doc /usr/share/doc/ea-apache24/CHANGES
%doc /usr/share/doc/ea-apache24/LICENSE
%doc /usr/share/doc/ea-apache24/VERSIONING
%doc /usr/share/doc/ea-apache24/NOTICE
%doc /usr/share/doc/ea-apache24/docs/conf/extra/httpd-dav.conf
%doc /usr/share/doc/ea-apache24/docs/conf/extra/httpd-default.conf
%doc /usr/share/doc/ea-apache24/docs/conf/extra/httpd-languages.conf
%doc /usr/share/doc/ea-apache24/docs/conf/extra/httpd-manual.conf
%doc /usr/share/doc/ea-apache24/docs/conf/extra/httpd-mpm.conf
%doc /usr/share/doc/ea-apache24/docs/conf/extra/httpd-multilang-errordoc.conf
%doc /usr/share/doc/ea-apache24/docs/conf/extra/httpd-vhosts.conf
%doc /usr/share/doc/ea-apache24/docs/conf/extra/proxy-html.conf

%dir %{_sysconfdir}/apache2
%{_sysconfdir}/apache2/modules
%{_sysconfdir}/apache2/logs
%attr(644,root,%{suexec_caller}) /var/log/apache2/suexec_log
%{_sysconfdir}/apache2/run
%dir %{_sysconfdir}/apache2/conf
%config(noreplace) %{_sysconfdir}/apache2/conf/httpd.conf
%config(noreplace) %{_sysconfdir}/apache2/conf/magic
%config(noreplace) %{_sysconfdir}/apache2/conf/mime.types

%if 0%{?rhel} < 7
%config %{_initrddir}/httpd
%{_initrddir}/htcacheclean
%endif

%dir %{_sysconfdir}/apache2/conf.d
%dir %{_sysconfdir}/apache2/conf.d/includes
%{_sysconfdir}/apache2/conf.d/README
%config(noreplace) %{_sysconfdir}/apache2/conf.d/*.conf
%exclude %{_sysconfdir}/apache2/conf.d/brotli.conf
%exclude %{_sysconfdir}/apache2/conf.d/cgid.conf
%exclude %{_sysconfdir}/apache2/conf.d/manual.conf

%if 0%{?rhel} >= 7
%{_unitdir}/httpd.service
%{_unitdir}/htcacheclean.service
%config(noreplace) %{_sysconfdir}/sysconfig/ht*
%{_prefix}/lib/tmpfiles.d/apache2.conf
%endif

%dir %{_sysconfdir}/apache2/conf.modules.d
%dir %{_sysconfdir}/apache2/bin

%config(noreplace) %{_sysconfdir}/sysconfig/ht*

%{_sbindir}/ht*
%{_sbindir}/apachectl
%{_sbindir}/rotatelogs
%caps(cap_setuid,cap_setgid+pe) %attr(4755,root,%{suexec_caller}) %{_sbindir}/suexec

%dir %{_libdir}/apache2
%dir %{_libdir}/apache2/modules

%dir %{contentdir}
%dir %{contentdir}/icons
%dir %{contentdir}/error
%dir %{contentdir}/error/include
%dir %{contentdir}/noindex
%{contentdir}/icons/*
%{contentdir}/error/README
%{contentdir}/error/*.var
%{contentdir}/error/include/*.html
%{contentdir}/noindex/*

%dir %{docroot}
%dir %{docroot}/cgi-bin
%dir %{docroot}/html

%attr(0710,root,nobody) %dir %{_localstatedir}/run/apache2
%attr(0700,nobody,nobody) %dir %{_localstatedir}/run/apache2/htcacheclean
%attr(0711,root,root) %dir %{_localstatedir}/log/apache2
%attr(0700,nobody,nobody) %dir %{_localstatedir}/cache/apache2
%attr(0700,nobody,nobody) %dir %{_localstatedir}/cache/apache2/proxy

%{_mandir}/man8/*

%files tools
%defattr(-,root,root)
%{_bindir}/*
%{_mandir}/man1/*
%doc LICENSE NOTICE
%exclude %{_bindir}/apxs
%exclude %{_mandir}/man1/apxs.1*

%files manual
%defattr(-,root,root)
%{contentdir}/manual
%config(noreplace) %{_sysconfdir}/apache2/conf.d/manual.conf

%files -n ea-apache24-mod_mpm_event -f files.mpm_event
%files -n ea-apache24-mod_mpm_prefork -f files.mpm_prefork
%files -n ea-apache24-mod_mpm_worker -f files.mpm_worker

%files -n ea-apache24-mod_cgi -f files.cgi
%files -n ea-apache24-mod_cgid -f files.cgid
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/apache2/conf.d/cgid.conf

%files -n ea-apache24-mod_allowmethods -f files.allowmethods
%files -n ea-apache24-mod_asis -f files.asis
%files -n ea-apache24-mod_auth_digest -f files.auth_digest
%files -n ea-apache24-mod_authn_anon -f files.authn_anon
%files -n ea-apache24-mod_authn_dbd -f files.authn_dbd
%files -n ea-apache24-mod_authn_dbm -f files.authn_dbm
%files -n ea-apache24-mod_authn_socache -f files.authn_socache
%files -n ea-apache24-mod_authnz_ldap -f files.authnz_ldap
%files -n ea-apache24-mod_authz_dbd -f files.authz_dbd
%files -n ea-apache24-mod_authz_dbm -f files.authz_dbm
%files -n ea-apache24-mod_authz_owner -f files.authz_owner
%files -n ea-apache24-mod_brotli -f files.brotli
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/apache2/conf.d/brotli.conf

%files -n ea-apache24-mod_buffer -f files.buffer
%files -n ea-apache24-mod_cache -f files.cache
%files -n ea-apache24-mod_cache_disk -f files.cache_disk
%files -n ea-apache24-mod_cache_socache -f files.cache_socache
%files -n ea-apache24-mod_charset_lite -f files.charset_lite
%files -n ea-apache24-mod_data -f files.data
%files -n ea-apache24-mod_dav -f files.dav
%attr(0700,nobody,nobody) %dir %{_localstatedir}/lib/dav
%files -n ea-apache24-mod_dav_fs -f files.dav_fs
%files -n ea-apache24-mod_dav_lock -f files.dav_lock
%files -n ea-apache24-mod_dbd -f files.dbd
%files -n ea-apache24-mod_deflate -f files.deflate
%files -n ea-apache24-mod_dialup -f files.dialup
%files -n ea-apache24-mod_dumpio -f files.dumpio
%files -n ea-apache24-mod_env -f files.env
%files -n ea-apache24-mod_expires -f files.expires
%files -n ea-apache24-mod_ext_filter -f files.ext_filter
%files -n ea-apache24-mod_file_cache -f files.file_cache
%files -n ea-apache24-mod_headers -f files.headers
%files -n ea-apache24-mod_heartbeat -f files.heartbeat
%files -n ea-apache24-mod_heartmonitor -f files.heartmonitor
%files -n ea-apache24-mod_imagemap -f files.imagemap
%files -n ea-apache24-mod_info -f files.info
%files -n ea-apache24-mod_lbmethod_bybusyness -f files.lbmethod_bybusyness
%files -n ea-apache24-mod_lbmethod_byrequests -f files.lbmethod_byrequests
%files -n ea-apache24-mod_lbmethod_bytraffic -f files.lbmethod_bytraffic
%files -n ea-apache24-mod_lbmethod_heartbeat -f files.lbmethod_heartbeat
%files -n ea-apache24-mod_ldap -f files.ldap
%files -n ea-apache24-mod_log_debug -f files.log_debug
%files -n ea-apache24-mod_log_forensic -f files.log_forensic
%attr(0755,root,root) %{_sbindir}/check_forensic
%files -n ea-apache24-mod_lua -f files.lua
%files -n ea-apache24-mod_macro -f files.macro
%files -n ea-apache24-mod_mime_magic -f files.mime_magic
%files -n ea-apache24-mod_proxy -f files.proxy
%files -n ea-apache24-mod_proxy_ajp -f files.proxy_ajp
%files -n ea-apache24-mod_proxy_balancer -f files.proxy_balancer
%files -n ea-apache24-mod_proxy_connect -f files.proxy_connect
%files -n ea-apache24-mod_proxy_express -f files.proxy_express
%files -n ea-apache24-mod_proxy_fcgi -f files.proxy_fcgi
%attr(0755,root,root) %{_sbindir}/fcgistarter
%files -n ea-apache24-mod_proxy_fdpass -f files.proxy_fdpass
%files -n ea-apache24-mod_proxy_ftp -f files.proxy_ftp
%files -n ea-apache24-mod_proxy_hcheck -f files.proxy_hcheck
%files -n ea-apache24-mod_proxy_html -f files.proxy_html
%files -n ea-apache24-mod_proxy_http -f files.proxy_http
%files -n ea-apache24-mod_proxy_scgi -f files.proxy_scgi
%files -n ea-apache24-mod_proxy_wstunnel -f files.proxy_wstunnel
%files -n ea-apache24-mod_proxy_uwsgi -f files.proxy_uwsgi
%files -n ea-apache24-mod_ratelimit -f files.ratelimit
%files -n ea-apache24-mod_reflector -f files.reflector
%files -n ea-apache24-mod_remoteip -f files.remoteip
%files -n ea-apache24-mod_reqtimeout -f files.reqtimeout
%files -n ea-apache24-mod_request -f files.request
%files -n ea-apache24-mod_sed -f files.sed
%files -n ea-apache24-mod_session -f files.session
%files -n ea-apache24-mod_slotmem_plain -f files.slotmem_plain
%files -n ea-apache24-mod_socache_memcache -f files.socache_memcache
%files -n ea-apache24-mod_socache_redis -f files.socache_redis
%files -n ea-apache24-mod_speling -f files.speling
%files -n ea-apache24-mod_ssl -f files.ssl
%if %{with_http2}
%files -n ea-apache24-mod_http2 -f files.http2
%endif
%attr(0700,nobody,root) %dir %{_localstatedir}/cache/apache2/ssl
%files -n ea-apache24-mod_substitute -f files.substitute
%files -n ea-apache24-mod_suexec -f files.suexec
%files -n ea-apache24-mod_unique_id -f files.unique_id
%files -n ea-apache24-mod_usertrack -f files.usertrack
%files -n ea-apache24-mod_version -f files.version
%files -n ea-apache24-mod_vhost_alias -f files.vhost_alias
%files -n ea-apache24-mod_watchdog -f files.watchdog

%files devel
%defattr(-,root,root)
%{_includedir}/apache2
%{_bindir}/apxs
%{_mandir}/man1/apxs.1*
%dir %{_libdir}/apache2/build
%{_libdir}/apache2/build/*.mk
%{_libdir}/apache2/build/*.sh
%{_sysconfdir}/rpm/macros.apache2

%changelog
* Mon Aug 11 2025 Julian Brown <julian.brown@webpros.com> - 2.4.65-4
- EA4-98: Adjust exec_code_asuser

* Fri Aug 08 2025 Dan Muey <daniel.muey@webpros.com> - 2.4.65-3
- EA4-90: Update to 65 proper

* Thu Aug 07 2025 Dan Muey <daniel.muey@webpros.com> - 2.4.65-2
-- EA4-82: Update 421 workaround to 65 in prep for Monday update

* Wed Jul 23 2025 Dan Muey <daniel.muey@webpros.com> - 2.4.65-1
- EA-13044: Update ea-apache24 from v2.4.64 to v2.4.65

* Fri Jul 18 2025 Dan Muey <daniel.muey@webpros.com> - 2.4.64-3
- EA-13041: Rolling “ea-apache24” back to “35b37d6c7295199c5157c68145f220d9fa61ff02”: Apache v2.4.64 broke SNI (rando 421)

* Fri Jul 18 2025 Cory McIntire <cory.mcintire@webpros.com> - 2.4.64-2
- EA-13040: Revert SNI update to address proxy issues with SNI 421 Redirects


* Tue Jul 15 2025 Dan Muey <daniel.muey@webpros.com> - 2.4.64-1
- EA-13014: Update ea-apache24 from v2.4.63 to v2.4.64

* Thu May 15 2025 Dan Muey <daniel.muey@webpros.com> - 2.4.63-2
- ZC-12836: Add dep for remote IP module

* Fri Jan 24 2025 Cory McIntire <cory.mcintire@webpros.com> - 2.4.63-1
- EA-12665: Update ea-apache24 from v2.4.62 to v2.4.63
- Remove Proxy FCGI patch (upstream patched in v2.5.63)

* Mon Dec 02 2024 Dan Muey <daniel.muey@webpros.com> - 2.4.62-3
- ZC-12397: Drop `isa` from \.mmn\. include for debs

* Fri Jul 26 2024 Julian Brown <julian.brown@cpanel.net> - 2.4.62-2
- ZC-12009: Proxy FCGI nocanon from SetHandler

* Thu Jul 18 2024 Cory McIntire <cory@cpanel.net> - 2.4.62-1
- EA-12288: Update ea-apache2 from v2.4.61 to v2.4.62
	- important: Apache HTTP Server: source code disclosure with handlers configured via AddType (CVE-2024-40725)
	- important: Apache HTTP Server: SSRF with mod_rewrite in server/vhost context on Windows (CVE-2024-40898)

* Wed Jul 03 2024 Cory McIntire <cory@cpanel.net> - 2.4.61-1
- EA-12261: Update ea-apache2 from v2.4.59 to v2.4.61
	- important: Apache HTTP Server: source code disclosure with handlers configured via AddType (CVE-2024-39884)
	- low: Apache HTTP Server: DoS by Null pointer in websocket over HTTP/2 (CVE-2024-36387)
	- important: Apache HTTP Server on WIndows UNC SSRF (CVE-2024-38472)
	- moderate: Apache HTTP Server proxy encoding problem (CVE-2024-38473)
	- important: Apache HTTP Server weakness with encoded question marks in backreferences (CVE-2024-38474)
	- important: Apache HTTP Server weakness in mod_rewrite when first segment of substitution matches filesystem path. (CVE-2024-38475)
	- important: Apache HTTP Server may use exploitable/malicious backend application output to run local handlers via internal redirect (CVE-2024-38476)
	- important: Apache HTTP Server: Crash resulting in Denial of Service in mod_proxy via a malicious request (CVE-2024-38477)
	- moderate: Apache HTTP Server: mod_rewrite proxy handler substitution (CVE-2024-39573)

* Thu Apr 05 2024 Cory McIntire <cory@cpanel.net> - 2.4.59-1
- EA-12070: Update ea-apache2 from v2.4.58 to v2.4.59
	- low: Apache HTTP Server: HTTP Response Splitting in multiple modules (CVE-2024-24795)
	- moderate: Apache HTTP Server: HTTP/2 DoS by memory exhaustion on endless continuation frames (CVE-2024-27316)
	- moderate: Apache HTTP Server: HTTP response splitting (CVE-2023-38709)

* Tue Nov 21 2023 Tim Mullin <tim@cpanel.net> - 2.4.58-3
- EA-11820: Patch to build with the latest ea-libxml2

* Mon Oct 23 2023 Chris Dillon <chris.dillon@cpanel.net> - 2.4.58-2
- EK-21: Remove unused EA3-era localhost cert generation

* Thu Oct 19 2023 Cory McIntire <cory@cpanel.net> - 2.4.58-1
- EA-11758: Update ea-apache2 from v2.4.57 to v2.4.58
	- CVE-2023-31122: mod_macro buffer over-read
	- CVE-2023-43622: Apache HTTP Server: DoS in HTTP/2 with initial windows size 0
	- CVE-2023-45802: Apache HTTP Server: HTTP/2 stream memory not reclaimed right away on RST

* Wed Oct 11 2023 Cory McIntire <cory@cpanel.net> - 2.4.57-4
- EA-11729: Rebuild against Updated ea-nghttp2 for CVE-2023-44487

* Thu Jun 29 2023 Tim Mullin <tim@cpanel.net> - 2.4.57-3
- EA-11526: Patch mod_http2 to fix issues with excessive CPU usage

* Fri Apr 21 2023 Tim Mullin <tim@cpanel.net> - 2.4.57-2
- EA-11296: Fix posttrans scriptlet failures on RHEL8+

* Fri Apr 07 2023 Cory McIntire <cory@cpanel.net> - 2.4.57-1
- EA-11337: Update ea-apache2 from v2.4.56 to v2.4.57

* Tue Mar 07 2023 Tim Mullin <tim@cpanel.net> - 2.4.56-1
- EA-11284: Update ea-apache2 from v2.4.55 to v2.4.56
- CVE-2023-27522: Apache HTTP Server: mod_proxy_uwsgi HTTP response splitting
- CVE-2023-25690: HTTP request splitting with mod_rewrite and mod_proxy

* Thu Jan 19 2023 Tim Mullin <tim@cpanel.net> - 2.4.55-2
- EA-11167: Patch to fix sporadic 500 errors with 2.4.55

* Tue Jan 17 2023 Cory McIntire <cory@cpanel.net> - 2.4.55-1
- EA-11157: Update ea-apache2 from v2.4.54 to v2.4.55
- CVE-2022-37436: Apache HTTP Server: mod_proxy prior to 2.4.55 allows a backend to trigger HTTP response splitting
- CVE-2022-36760: Apache HTTP Server: mod_proxy_ajp Possible request smuggling
- CVE-2006-20001: Apache HTTP Server: mod_dav out of  bounds read, or write of zero byte

* Tue Jul 26 2022 Tim Mullin <tim@cpanel.net> - 2.4.54-2
- EA-10825: Fix file ownership for ea-apache24-mod_socache_redis

* Wed Jun 08 2022 Tim Mullin <tim@cpanel.net> - 2.4.54-1
- EA-10756: Update ea-apache2 from v2.4.53 to v2.4.54
  CVE-2022-26377: mod_proxy_ajp: Possible request smuggling
  CVE-2022-28330: Read beyond bounds in mod_isapi
  CVE-2022-28614: Read beyond bounds via ap_rwrite()
  CVE-2022-28615: Read beyond bounds in ap_strcmp_match()
  CVE-2022-29404: Denial of service in mod_lua r:parsebody
  CVE-2022-30522: mod_sed: Denial of service
  CVE-2022-30556: Information Disclosure in mod_lua with websockets
  CVE-2022-31813: mod_proxy X-Forwarded-For dropped by hop-by-hop mechanism

* Mon Apr 18 2022 Tim Mullin <tim@cpanel.net> - 2.4.53-2
- EA-10538: Fix compiler warnings in suexec.c

* Mon Mar 14 2022 Tim Mullin <tim@cpanel.net> - 2.4.53-1
- EA-10550: Update ea-apache2 from v2.4.52 to v2.4.53

* Wed Jan 26 2022 Travis Holloway <t.holloway@cpanel.net> - 2.4.52-3
- EA-10245: Add patch to change log level of accept mutex

* Tue Dec 29 2021 Tim Mullin <tim@cpanel.net> - 2.4.52-2
- EA-10391: Add patch to fix instability issues with Apache v2.4.52

* Mon Dec 20 2021 Travis Holloway <t.holloway@cpanel.net> - 2.4.52-1
- EA-10370: Update ea-apache2 from v2.4.51 to v2.4.52

* Tue Nov 23 2021 Tim Mullin <tim@cpanel.net> - 2.4.51-2
- EA-10258: Patch mod_http2 to fix issue with hanging http2 threads

* Thu Oct 07 2021 Cory McIntire <cory@cpanel.net> - 2.4.51-1
- EA-10179: Update ea-apache2 from v2.4.50 to v2.4.51

* Mon Oct 04 2021 Cory McIntire <cory@cpanel.net> - 2.4.50-1
- EA-10157: Update ea-apache2 from v2.4.49 to v2.4.50

* Tue Sep 28 2021 Daniel Muey <dan@cpanel.net> - 2.4.49-4
- ZC-9300: ensure only one package owns http2.conf

* Tue Sep 28 2021 Cory McIntire <cory@cpanel.net> - 2.4.49-3
- EA-10152: Patch from upstream

* Thu Sep 23 2021 Travis Holloway <t.holloway@cpanel.net> - 2.4.49-2
- EA-10123: Patch apache 2.4.49: Correctly decrement active_daemons also in the case that the child process decides on its own to die because of MaxRequestsPerChild.

* Thu Sep 16 2021 Cory McIntire <cory@cpanel.net> - 2.4.49-1
- EA-10107: Update ea-apache2 from v2.4.48 to v2.4.49

* Thu Aug 12 2021 Travis Holloway <t.holloway@cpanel.net> - 2.4.48-5
- EA-10041: Fix instructions in elinks patch

* Mon Jul 26 2021 Daniel Muey <dan@cpanel.net> - 2.4.48-4
- ZC-9091: Manage the `httpd` service via scripts shared w/ debs

* Tue Jun 22 2021 Travis Holloway <t.holloway@cpanel.net> - 2.4.48-3
- EA-9895: Ensure httpd is configured to start after reboot on chkconfig systems

* Wed Jun 02 2021 Cory McIntire <cory@cpanel.net> - 2.4.48-2
- EA-9822: rollback systemd change

* Wed May 26 2021 Cory McIntire <cory@cpanel.net> - 2.4.48-1
- EA-9797: Update ea-apache2 from v2.4.46 to v2.4.48

* Tue May 25 2021 Tim Mullin <tim@cpanel.net> - 2.4.46-7
- EA-9784: Change Apache to be a systemd notify service

* Wed Feb 03 2021 Cory McIntire <cory@cpanel.net> - 2.4.46-6
- EA-9463: Revert Apache startup changes.

* Fri Jan 29 2021 Cory McIntire <cory@cpanel.net> - 2.4.46-5
- EA-9463: Resolve Apache startup race conditions
           Enable mod_systemd for further startup enhancements

* Mon Jan 04 2021 Tim Mullin <tim@cpanel.net> - 2.4.46-4
- EA-9506: Do not start htcacheclean service if mod_cache_disk module is not loaded

* Tue Nov 24 2020 Julian Brown <julian.brown@cpanel.net> - 2.4.46-3
- ZC-8005: Replace ea-openssl11 with system openssl on C8

* Thu Oct 15 2020 Hans Borresen <h.borresen@cpanel.net> - 2.4.46-2
- EA-9374: Lower TimeoutStopSec for httpd.service

* Fri Aug 07 2020 Tim Mullin <tim@cpanel.net> - 2.4.46-1
- EA-9225: Update ea-apache2 from v2.4.43 to v2.4.46

* Mon May 18 2020 Julian Brown <julian.brown@cpanel.net> - 2.4.43-6
- ZC-6822: Build on CentOS 8

* Thu Apr 30 2020 Tim Mullin <tim@cpanel.net> - 2.4.43-5
- EA-8809: Ensure that MAX_FD_LIMIT is not exceeded

* Wed Apr 29 2020 Cory McIntire <cory@cpanel.net> - 2.4.43-4
- EA-9047: Remove proc randoms that could not be found in POSTRANS
- Switch to our ea-openssl11

* Tue Apr 28 2020 Cory McIntire <cory@cpanel.net> - 2.4.43-3
- EA-9042: Do not install init.d/httpd files on C7 and above

* Thu Apr 16 2020 Tim Mullin <tim@cpanel.net> - 2.4.43-2
- EA-9010: Patch apache 2.4.43 to fix ssl stapling memory leak

* Wed Apr 01 2020 Tim Mullin <tim@cpanel.net> - 2.4.43-1
- EA-8958: Update ea-apache2 from v2.4.41 to v2.4.43

* Thu Mar 19 2020 Tim Mullin <tim@cpanel.net> - 2.4.41-9
- A-8786: Patch apxs to use the correct value for top_builddir

* Wed Mar 18 2020 Tim Mullin <tim@cpanel.net> - 2.4.41-8
- EA-8927: Patch apache 2.4.x httpd for OCSP stapling bug

* Mon Mar 16 2020 Tim Mullin <tim@cpanel.net> - 2.4.41-7
- EA-8876: Made ea-apache24 require ea-apache24-mod_headers

* Tue Jan 14 2020 J. Nick Koston <nick@cpanel.net> - 2.4.41-6
- COBRA-10700: Optimizing finding modules

* Mon Dec 23 2019 Daniel Muey <dan@cpanel.net> - 2.4.41-5
- ZC-4361: bump release prefix past 4 so these will be newest (4 was added and disappeared due to a faulty revert)

* Wed Dec 18 2019 Daniel Muey <dan@cpanel.net> - 2.4.41-3
- ZC-4361: Update ea-openssl requirement to v1.1.1 (ZC-5583)

* Thu Dec 12 2019 J. Nick Koston <nick@cpanel.net> - 2.4.41-2
- COBRA-10665: Optimizing finding directives when parsing the configuration

* Wed Aug 14 2019 Cory McIntire <cory@cpanel.net> - 2.4.41-1
- EA-8612: Update ea-apache2 from v2.4.39 to v2.4.41

* Thu Aug 08 2019 Tim Mullin <tim@cpanel.net> - 2.4.39-6
- EA-8588: Added default RequestReadTimeout for mod_reqtimeout

* Wed Jun 19 2019 Tim Mullin <tim@cpanel.net> - 2.4.39-5
- EA-8533: Set Apache to depend on ea-apr >= 1.7.0-1

* Thu May 30 2019 Tim Mullin <tim@cpanel.net> - 2.4.39-4
- EA-8508: Appended "Mutex sysvsem" to 000_mod_mpm_prefork.conf

* Fri Apr 26 2019 Rishwanth Yeddula <rish@cpanel.net> - 2.4.39-3
- CPANEL-27056: Fix bug in condition that allowed for non-user files
  to be served in certain situations when SymlinkProtection was
  enabled.

* Wed Apr 03 2019 Rishwanth Yeddula <rish@cpanel.net> - 2.4.39-2
- CPANEL-22257: Ensure that Paths configured as Aliases are exempt
  from symlink protection checks

* Tue Apr 02 2019 Cory McIntire <cory@cpanel.net> - 2.4.39-1
- EA-8307: Update to 2.4.39, drop 2.4.38
  CVE-2019-0211: Apache HTTP Server privilege escalation from modules' scripts
  CVE-2019-0196: mod_http2, read-after-free on a string compare
  CVE-2019-0197: mod_http2, possible crash on late upgrade
  CVE-2019-0215: mod_ssl access control bypass
  CVE-2019-0217: mod_auth_digest access control bypass
  CVE-2019-0220: URL normalization inconsistincies

* Thu Mar 07 2019 Cory McIntire <cory@cpanel.net> - 2.4.38-3
- EA-8279: Take out noreplace from old EA3 init script so it will be removed
  now that EA3 is EOL

* Tue Feb 26 2019 Tim Mullin <tim@cpanel.net> - 2.4.38-2
- EA-7318: Increase service timeout to handle a large httpd.conf

* Thu Jan 24 2019 Cory McIntire <cory@cpanel.net> - 2.4.38-1
- EA-8165: Apache Update: Drop 2.4.37, update to 2.4.38

* Tue Jan 15 2019 Cory McIntire <cory@cpanel.net> - 2.4.37-2
- EA-7518: Add systemd directives to ensure network is up before starting

* Tue Oct 23 2018 Cory McIntire <cory@cpanel.net> - 2.4.37-1
- EA-7941: Update to v2.4.37, drop v2.4.35

* Fri Sep 28 2018 Cory McIntire <cory@cpanel.net> - 2.4.35-1
- EA-7871: Update to v2.4.35, drop v2.4.34
  Remove Patch500: 0016-Apply-mod_ratelimit-fix-from-trunk.patch as it
  was implemented upstream.

* Fri Aug 24 2018 Rishwanth Yeddula <rish@cpanel.net> - 2.4.34-3
- EA-7802: Restore mod_ratelimit back to the 2.3.34 version. Apply
upstream fixes for it from trunk.

* Thu Jul 19 2018 Rishwanth Yeddula <rish@cpanel.net> - 2.4.34-2
- EA-7715: Revert mod_ratelimit back to the 2.3.33 version.
  This is to ensure that it emits proper chunks, as there are several
  issues with the 2.3.34 version.

* Thu Jul 12 2018 Cory McIntire <cory@cpanel.net> - 2.4.34-1
- EA-7683 Update httpd-2.4.33 to httpd-2.4.34
  Redid patches to be a git format-patch set

* Tue Jun 19 2018 Rishwanth Yeddula <rish@cpanel.net> - 2.4.33-8
- EA-5971: Ensure that htcacheclean service is functional on
  Centos 7 systems

* Thu May 31 2018 Cory McIntire <cory@cpanel.net> - 2.4.33-7
- EA-7487: Add ExecReload to httpd.service file

* Tue May 29 2018 Rishwanth Yeddula <rish@cpanel.net> - 2.4.33-6
- EA-7468: Ensure dependency resolution picks /usr/bin/perl instead
  of /bin/perl. This helps downstream users of our RPMs as their
  build environments can be simplified.

* Mon Apr 16 2018 Rishwanth Yeddula <rish@cpanel.net> - 2.4.33-5
- EA-7382: Update dependency on ea-openssl to require the latest version with versioned symbols.

* Wed Apr 04 2018 Rishwanth Yeddula <rish@cpanel.net> - 2.4.33-4
- EA-7376: Ensure that mod_http2 is properly linked against ea-openssl.

* Tue Apr 03 2018 Rishwanth Yeddula <rish@cpanel.net> - 2.4.33-3
- EA-7367: Ensure that the tools are properly linked against ea-openssl.

* Tue Apr 03 2018 Rishwanth Yeddula <rish@cpanel.net> - 2.4.33-2
- EA-7366: Ensure that apr-util is properly listed as a dependency.

* Thu Mar 29 2018 Daniel Muey <dan@cpanel.net> - 2.4.33-1
- EA-7327: Update to v2.4.33, drop v2.4.29

* Tue Mar 27 2018 Rishwanth Yeddula <rish@cpanel.net> - 2.4.29-12
- EA-7339: Build against the latest apr/apr-util

* Mon Mar 19 2018 Rishwanth Yeddula <rish@cpanel.net> - 2.4.29-11
- EA-7164: Build mod_brotli against the ea-brotli package.

* Tue Mar 06 2018 Cory McIntire <cory@cpanel.net> - 2.4.29-10
- ZC-3401: ensure building against and using ea-openssl

* Wed Feb 14 2018 Dan Muey <dan@cpanel.net> - 2.4.29-9
- EA-7238: use documented and ea3 parity safe suexec_log path

* Mon Feb 05 2018 Dan Muey <dan@cpanel.net> - 2.4.29-8
- EA-7217: Make sure we use ea-nghttp2

* Wed Jan 24 2018 Rishwanth Yeddula <rish@cpanel.net> - 2.4.29-7
- EA-7159: Use 'elinks' instead of 'links' as a dependency
  to ensure that EA4 does not pull any packages from
  the EPEL repos.

* Mon Jan 15 2018 Cory McIntire <cory@cpanel.net> - 2.4.29-6
- EA-7125: Remove previous piped logging patch

* Mon Jan 15 2018 Rishwanth Yeddula <rish@cpanel.net> - 2.4.29-5
- EA-7127: Ensure the mod_proxy_html and mod_xml2enc modules
  build against ea-libxml2. Additionally, updated the build
  process to avoid modifying the LDFLAGS - as it caused the
  libxml2 dependency to be carried to extensions compiled
  separately.

* Fri Jan 12 2018 Cory McIntire <cory@cpanel.net> - 2.4.29-4
- EA-7060: Supress Long Lost Pids warning
- patch provided by Gary Stanley <gary@cpanel.net>

* Wed Dec 27 2017 Cory McIntire <cory@cpanel.net> - 2.4.29-3
- EA-7044: Adjust Apache to use ea-libxml2

* Sun Dec 24 2017 Cory McIntire <cory@cpanel.net> - 2.4.29-2
- EA-6020: Restarting Apache while using splitlogs can result in "Broken pipe" errors
- Applying patch provided by Gary Stanley (gary@cpanel.net)

* Wed Oct 18 2017 Jacob Perkins <jacob.perkins@cpanel.net> - 2.4.29-1
- Updated to version 2.4.29 via update_pkg.pl (ZC-2981)
- Removed mod_unique_id patch as it was patched upstream.

* Tue Oct 10 2017 Jacob Perkins <jacob.perkins@cpanel.net> - 2.4.28-1
- Update Apache to 2.4.28

* Tue Sep 19 2017 Jacob Perkins <jacob.perkins@cpanel.net> - 2.4.27-8
- Patch core for htaccess method registrations - CVE-2017-9798

* Mon Sep 11 2017 Dan Muey <dan@cpanel.net> - 2.4.27-7
- EA-6096: Add note to mod_unique_id summary about performance degradation

* Mon Aug 28 2017 Dan Muey <dan@cpanel.net> - 2.4.27-6
- EA-6274 Allow users to override hard coded ulimit() by using /etc/sysconfig/httpd

* Thu Aug 10 2017 Jacob Perkins <jacob.perkins@cpanel.net> - 2.4.27-5
- Patched H2 for stalling when writing > 32k

* Thu Aug 10 2017 Felipe Gasper <felipe@cpanel.net> - 2.4.27-4
- Require mod_proxy_wstunnel for ea-apache24.

* Wed Aug 02 2017 Cory McIntire <cory@cpanel.net> - 2.4.27-3
- Add conflicts between prefork and HTTP2

* Fri Jul 14 2017 Felipe Gasper <felipe@cpanel.net> - 2.4.27-2
- Apply fix for https://bz.apache.org/bugzilla/show_bug.cgi?id=61283

* Fri Jul 07 2017 Jacob Perkins <jacob.perkins@cpanel.net> - 2.4.27-1
- Updated to version 2.4.27 via update_pkg.pl (EA-6522)

* Tue Jun 27 2017 Jacob Perkins <jacob.perkins@cpanel.net> - 2.4.25-12
- Replace __isa w/ifarch

* Fri Jun 23 2017 Jacob Perkins <jacob.perkins@cpanel.net> - 2.4.25-11
- Disable HTTP2 building on 32bit architectures

* Fri Jun 09 2017 Jacob Perkins <jacob.perkins@cpanel.net> - 2.4.25-10
- Add HTTP2 Support

* Fri Mar 24 2017 Cory McIntire <cory@cpanel.net> - 2.4.25-9
- Add patch for segfaulting graceful restarts

* Thu Mar 16 2017 Dan Muey <dan@cpanel.net> - 2.4.25-8
- ZC-2483: Add ExecStop to systemd config

* Mon Mar 13 2017 Jacob Perkins <jacob.perkins@cpanel.net> - 2.4.25-7
- Added requirement for links for apachectl-status

* Wed Feb 22 2017 Jacob Perkins <jacob.perkins@cpanel.net> - 2.4.25-6
- Add patch for higher seed chunks

* Fri Feb 10 2017 Dan Muey <dan@cpanel.net> - 2.4.25-5
- EA-5514: update htcacheclean CACHE_ROOT to match reality

* Wed Jan 11 2017 Dan Muey <dan@cpanel.net> - 2.4.25-4
* EA-5845: Increase the maximum number of file descriptors for init.d systems

* Wed Jan 04 2017 Dan Muey <dan@cpanel.net> - 2.4.25-3
* EA-5836: mod_proxy_hcheck w/ prefork segfaults frequently

* Tue Jan 03 2017 Dan Muey <dan@cpanel.net> - 2.4.25-2
EA-5836: Have httpd.service use /run instead of /var/run

* Wed Dec 21 2016 Cory McIntire <cory@cpanel.net> - 2.4.25-1
- Updated to version 2.4.25, drop version 2.4.23

* Tue Dec 13 2016 Dan Muey <dan@cpanel.net> - 2.4.23-9
- EA-5557: turn off icon directives by default since the icons are broken under symlink protect
-          and are used by HTMLTable even when fancy indexinf is off

* Tue Dec 06 2016 Dan Muey <dan@cpanel.net> - 2.4.23-8
- EA-5557: turn off fancy indexing by default since the icons are broken under symlink protect

* Mon Dec 05 2016 S. Kurt Newman <kurt.newman@cpanel.net> - 2.4.23-7
- Update apachectl with ulimit calls modifying the open file
  descriptor limit so that Apache will start up (EA-5662)

* Thu Dec 01 2016 Dan Muey <dan@cpanel.net> - 2.4.23-6
- EA-5712: Patch apachectl to set PORT based on cpanel configuration

* Mon Oct 24 2016 Edwin Buck <e.buck@cpanel.net> - 2.4.23-5
- Add symlink protection root directive.

* Mon Oct 24 2016 Edwin Buck <e.buck@cpanel.net> - 2.4.23-4
- Add symlink protection patch and configuration control.

* Wed Jul 20 2016 Edwin Buck <e.buck@cpanel.net> - 2.4.23-3
- Fixed autoindex.conf suppression of /icons/ in subdomains.

* Wed Jul 20 2016 S. Kurt Newman <kurt.newman@cpanel.net> - 2.4.23-2
- mod_lua can be installed, but is off by default (EA-4825)
- fixed a few rpmlint warnings complaining about lack of attr macros

* Tue Jul 19 2016 Edwin Buck <e.buck@cpanel.net> - 2.4.23-1
- EA-4872: Updated to verison 2.4.23
- Added mod_proxy_hcheck (side effect of upstream 2.5 backport into 2.4.23)

* Mon Jul 18 2016 Edwin Buck <e.buck@cpanel.net> - 2.4.20-6
- Apply recommendations in asf-httpoxy-repsponse.txt for CVE-2016-5387

* Thu Jun 30 2016 Edwin Buck <e.buck@cpanel.net> - 2.4.20-5
- ZC-1937: Move mod_info into a separate child RPM

* Mon Jun 20 2016 Dan Muey <dan@cpanel.net> - 2.4.20-4
- EA-4383: Update Release value to OBS-proof versioning

* Fri May 27 2016 Jacob Perkins <jacob.perkins@cpanel.net> - 2.4.20-3
- Updated suexec minimum uid to match EA3

* Tue Apr 26 2016 David Nielson <david.nielson@cpanel.net> - 2.4.20-2
- Remove cp-ssl.conf

* Mon Apr 11 2016 Jacob Perkins <jacob.perkins@cpanel.net> - 2.4.20-1
- Updated to version 2.4.20 via update_pkg.pl (EA-4446)

* Mon Mar 21 2016 Matt Dees <matt@cpanel.net> 2.4.18.5
- Create direct dependencies on mod_cgi/mod_cgid for the various MPMs.

* Thu Mar 10 2016 Matt Dees <matt@cpanel.net> - 2.4.18.5
- Add PIDFile to httpd.service

* Thu Mar 3 2016 S. Kurt Newman <kurt.newman@cpanel.net> - 2.4.18-4
- Removed Apache Bug #58854 (ZC-1512)

* Tue Mar 1 2016 David Nielson <david.nielson@cpanel.net> 2.4.18-3
- Remove conflict on 'webserver' and add conflict on 'httpd-mmn' so
  Nginx can be installed from EPEL.

* Thu Jan 14 2016 S. Kurt Newman <kurt.newman@cpanel.net> - 2.4.18-2
- Applied fix for Apache Bug #58854.  This patch should be removed
  once it has made into upstream.

* Thu Dec 17 2015 Jacob Perkins <jacob.perkins@cpanel.net> - 2.4.18-1
- Updated to version 2.4.18 via update_pkg.pl

* Wed Dec 16 2015 Dan Muey <dan@cpanel.net> 2.4.16-9
- Add ea-apache24-mod_bwlimited as a requirement

* Tue Nov 03 2015 Jacob Perkins <jacob.perkins@cpanel.net) - 2.4.16-8
- Reverted Apache 2.4.17

* Mon Nov 02 2015 Darren Mobley <darren@cpanel.net> - 2.4.16-7
- Added explicit conflicts for mod_cgi/mod_cgid and the mpms
  they conflict with. HB-1153

* Fri Oct 02 2015 Dan Muey <dan@cpanel.net> 2.4.16-6
- Stop installing userdir.conf since it is broken and the functionality is handled elsewhere

* Thu Oct  1 2015 S. Kurt Newman <kurt.newman@cpanel.net> - 2.4.16-5
- Added /etc/apache2/bin directory for apache-specific utility scripts
- Added additional macros to /etc/rpm/macros.apache2 so other rpms
  can make use of those paths

* Mon Aug 31 2015 Julian Brown <julian.brown@cpanel.net> - 2.4.16-4
- Added requirements for ea-cpanel-tools, scripting tools to work
- with cPanel.

* Fri Aug 28 2015 Jacob Perkins <jacob.perkins@cpanel.net> 2.4.16-3
- Disabled IPv4 Mapping

* Fri Aug 28 2015 Julian Brown <julian.brown@cpanel.net> - 2.4.16-2
- Added requirements for ea-apache24-mod_proxy and mod_proxy_http
- so we can support proxy subdomains

* Wed Aug 26 2015 Jacob Perkins <jacob.perkins@cpanel.net> - 2.4.16-1
- Updated to version 2.4.16 via update_pkg.pl

* Mon Aug 24 2015 Trinity Quirk <trinity.quirk@cpanel.net> - 2.4.12-17
- Patched apxs so that it correctly handles the conf.modules.d arrangement

* Mon Aug 10 2015 Darren Mobley <darren@cpanel.net> - 2.4.12-16
- Added ea-apache24-config and ea-apache24-config-runtime as
  requirements for ea-apache24

* Wed Aug 05 2015 Trinity Quirk <trinity.quirk@cpanel.net> - 2.4.12-15
- Missing requirements for mod_session

* Mon Aug 03 2015 Dan Muey <dan@cpanel.net> = 2.4.12-14
- Add ea-apache24-tools as a require for ea-apache24

* Sat Aug 01 2015 Darren Mobley <darren@cpanel.net> - 2.4.12-13
- Add ea-documentroot as a require for ea-apache24

* Fri Jul 31 2015 Trinity Quirk <trinity.quirk@cpanel.net> - 2.4.12-12
- Repair apxs craziness

* Thu Jul 30 2015 Trinity Quirk <trinity.quirk@cpanel.net> - 2.4.12-11
- Reference new locations of apr and apr-util packages

* Wed Jul 01 2015 S. Kurt Newman <kurt.newman@cpanel.net> - 2.4.12-10
- Fixed mpm conflicts
- Removed itk conflict since apache shouldn't be concerned with that..
  only itk should be
- Removed unused cloudlinux cagefs patch

* Thu Jun 11 2015 Matt Dees <matt.dees@cpanel.net> - 2.4.12-9
- Added tmpfiles.d entry for c7

* Sat Jun 06 2015 Darren Mobley <darren@cpanel.net> - 2.4.12-8.el6.cpanel.1
- Added includes handler for .shtml files in cperror.conf

* Sat Jun 06 2015 Darren Mobley <darren@cpanel.net> - 2.4.12-7.el6.cpanel.1
- Added cperror.conf to handle error page configuration

* Wed May 27 2015 Julian Brown <julian.brown@cpanel.net> - 2.4.12-6.el6.cpanel.1
- Changed name of rpms generated to ea-apache24.

* Tue Apr 28 2015 Darren Mobley <darren@cpanel.net> - 2.4.12-5.el6.cpanel.1
- Added httpd.service file and installation for CentOS 7 machines

* Mon Mar 30 2015 Trinity Quirk <trinity.quirk@cpanel.net> - 2.4.12-4.el6.cpanel.1
- Added mime.types back into ea-apache24

* Fri Mar 27 2015 S. Kurt Newman <kurt.newman@cpanel.net> - 2.4.12-3.el6.cpanel.1
- Removed logrotate.d configuration to let WHM take care of this.

* Wed Mar 11 2015 Trinity Quirk <trinity.quirk@cpanel.net> - 2.4.12-2.el6.cpanel.1
- Split many modules out into their own packages
- Set dependencies between packages where needed

* Fri Feb 27 2015 Trinity Quirk <trinity.quirk@cpanel.net> - 2.4.12-1.el6.cpanel.1
- Upgrade to 2.4.12
- Remove inappropriate or already-applied patches

* Thu Feb 26 2015 Trinity Quirk <trinity.quirk@cpanel.net> - 2.4.6-21.el6.cpanel.1
- Split the MPMs into their own packages
- mod_heartbeat needs to be loaded after mod_status and mod_watchdog

* Wed Feb 25 2015 Trinity Quirk <trinity.quirk@cpanel.net> - 2.4.6-20.el6.cpanel.1
- Each module now has its own conf.modules.d file
- conf.modules.d files are created programmatically
- Simplified ssl, proxy_html, ldap, and session package file lists

* Thu Jan 29 2015 Trinity Quirk <trinity.quirk@cpanel.net> - 2.4.6-17.el6.cpanel.1
- Added cPanel-specific patches
- Removed apache user creation, configured to run as nobody
- Repaired incorrect run directories

* Tue Dec 30 2014 Kurt Newman <kurt.newman@cpanel.net> - 2.4.6-17.el6.centos.1
- Converted from CentOS 7, to CentOS 6

* Tue Jun 17 2014 Jim Perrin <jperrin@centos.org> - 2.4.6-17.el7.centos.1
- Remove index.html, add centos-noindex.tar.gz
- update welcome.conf with proper aliases
- change symlink for poweredby.png

* Thu Mar 20 2014 Jan Kaluza <jkaluza@redhat.com> - 2.4.6-17
- mod_dav: add security fix for CVE-2013-6438 (#1077907)
- mod_log_config: add security fix for CVE-2014-0098 (#1077907)

* Wed Mar  5 2014 Joe Orton <jorton@redhat.com> - 2.4.6-16
- mod_ssl: improve DH temp key handling (#1057687)

* Wed Mar  5 2014 Joe Orton <jorton@redhat.com> - 2.4.6-15
- mod_ssl: use 2048-bit RSA key with SHA-256 signature in dummy certificate (#1071276)

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 2.4.6-14
- Mass rebuild 2014-01-24

* Mon Jan 13 2014 Joe Orton <jorton@redhat.com> - 2.4.6-13
- mod_ssl: sanity-check use of "SSLCompression" (#1036666)
- mod_proxy_http: fix brigade memory usage (#1040447)

* Fri Jan 10 2014 Joe Orton <jorton@redhat.com> - 2.4.6-12
- rebuild

* Thu Jan  9 2014 Joe Orton <jorton@redhat.com> - 2.4.6-11
- build with -O3 on ppc64 (#1051066)

* Tue Jan  7 2014 Joe Orton <jorton@redhat.com> - 2.4.6-10
- mod_dav: fix locktoken handling (#1004046)

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 2.4.6-9
- Mass rebuild 2013-12-27

* Fri Dec 20 2013 Joe Orton <jorton@redhat.com> - 2.4.6-8
- use unambiguous httpd-mmn (#1029360)

* Fri Nov   1 2013 Jan Kaluza <jkaluza@redhat.com> - 2.4.6-7
- mod_ssl: allow SSLEngine to override Listen-based default (#1023168)

* Thu Oct  31 2013 Jan Kaluza <jkaluza@redhat.com> - 2.4.6-6
- systemd: Use {MAINPID} notation in service file (#969972)

* Thu Oct 24 2013 Jan Kaluza <jkaluza@redhat.com> - 2.4.6-5
- systemd: send SIGWINCH signal without httpd -k in ExecStop (#969972)

* Thu Oct 03 2013 Jan Kaluza <jkaluza@redhat.com> - 2.4.6-4
- expand macros in macros.httpd (#1011393)

* Mon Aug 26 2013 Jan Kaluza <jkaluza@redhat.com> - 2.4.6-3
- fix "LDAPReferrals off" to really disable LDAP Referrals

* Wed Jul 31 2013 Jan Kaluza <jkaluza@redhat.com> - 2.4.6-2
- revert fix for dumping vhosts twice

* Mon Jul 22 2013 Joe Orton <jorton@redhat.com> - 2.4.6-1
- update to 2.4.6
- mod_ssl: use revised NPN API (r1487772)

* Thu Jul 11 2013 Jan Kaluza <jkaluza@redhat.com> - 2.4.4-12
- mod_unique_id: replace use of hostname + pid with PRNG output (#976666)
- apxs: mention -p option in manpage

* Tue Jul  2 2013 Joe Orton <jorton@redhat.com> - 2.4.4-11
- add patch for aarch64 (Dennis Gilmore, #925558)

* Mon Jul  1 2013 Joe Orton <jorton@redhat.com> - 2.4.4-10
- remove duplicate apxs man page from httpd-tools

* Mon Jun 17 2013 Joe Orton <jorton@redhat.com> - 2.4.4-9
- remove zombie dbmmanage script

* Fri May 31 2013 Jan Kaluza <jkaluza@redhat.com> - 2.4.4-8
- return 400 Bad Request on malformed Host header

* Mon May 20 2013 Jan Kaluza <jkaluza@redhat.com> - 2.4.4-6
- htpasswd/htdbm: fix hash generation bug (#956344)
- do not dump vhosts twice in httpd -S output (#928761)
- mod_cache: fix potential crash caused by uninitialized variable (#954109)

* Thu Apr 18 2013 Jan Kaluza <jkaluza@redhat.com> - 2.4.4-5
- execute systemctl reload as result of apachectl graceful
- mod_ssl: ignore SNI hints unless required by config
- mod_cache: forward-port CacheMaxExpire "hard" option
- mod_ssl: fall back on another module's proxy hook if mod_ssl proxy
  is not configured.

* Tue Apr 16 2013 Jan Kaluza <jkaluza@redhat.com> - 2.4.4-4
- fix service file to not send SIGTERM after ExecStop (#906321, #912288)

* Tue Mar 26 2013 Jan Kaluza <jkaluza@redhat.com> - 2.4.4-3
- protect MIMEMagicFile with IfModule (#893949)

* Tue Feb 26 2013 Joe Orton <jorton@redhat.com> - 2.4.4-2
- really package mod_auth_form in mod_session (#915438)

* Tue Feb 26 2013 Joe Orton <jorton@redhat.com> - 2.4.4-1
- update to 2.4.4
- fix duplicate ownership of mod_session config (#914901)

* Fri Feb 22 2013 Joe Orton <jorton@redhat.com> - 2.4.3-17
- add mod_session subpackage, move mod_auth_form there (#894500)

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.3-16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Tue Jan  8 2013 Joe Orton <jorton@redhat.com> - 2.4.3-15
- add systemd service for htcacheclean

* Tue Nov 13 2012 Joe Orton <jorton@redhat.com> - 2.4.3-14
- drop patch for r1344712

* Tue Nov 13 2012 Joe Orton <jorton@redhat.com> - 2.4.3-13
- filter mod_*.so auto-provides (thanks to rcollet)
- pull in syslog logging fix from upstream (r1344712)

* Fri Oct 26 2012 Joe Orton <jorton@redhat.com> - 2.4.3-12
- rebuild to pick up new apr-util-ldap

* Tue Oct 23 2012 Joe Orton <jorton@redhat.com> - 2.4.3-11
- rebuild

* Wed Oct  3 2012 Joe Orton <jorton@redhat.com> - 2.4.3-10
- pull upstream patch r1392850 in addition to r1387633

* Mon Oct  1 2012 Joe Orton <jorton@redhat.com> - 2.4.3-9.1
- restore "ServerTokens Full-Release" support (#811714)

* Mon Oct  1 2012 Joe Orton <jorton@redhat.com> - 2.4.3-9
- define PLATFORM in os.h using vendor string

* Mon Oct  1 2012 Joe Orton <jorton@redhat.com> - 2.4.3-8
- use systemd script unconditionally (#850149)

* Mon Oct  1 2012 Joe Orton <jorton@redhat.com> - 2.4.3-7
- use systemd scriptlets if available (#850149)
- don't run posttrans restart if /etc/sysconfig/httpd-disable-posttrans exists

* Mon Oct 01 2012 Jan Kaluza <jkaluza@redhat.com> - 2.4.3-6
- use systemctl from apachectl (#842736)

* Wed Sep 19 2012 Joe Orton <jorton@redhat.com> - 2.4.3-5
- fix some error log spam with graceful-stop (r1387633)
- minor mod_systemd tweaks

* Thu Sep 13 2012 Joe Orton <jorton@redhat.com> - 2.4.3-4
- use IncludeOptional for conf.d/*.conf inclusion

* Fri Sep 07 2012 Jan Kaluza <jkaluza@redhat.com> - 2.4.3-3
- adding mod_systemd to integrate with systemd better

* Tue Aug 21 2012 Joe Orton <jorton@redhat.com> - 2.4.3-2
- mod_ssl: add check for proxy keypair match (upstream r1374214)

* Tue Aug 21 2012 Joe Orton <jorton@redhat.com> - 2.4.3-1
- update to 2.4.3 (#849883)
- own the docroot (#848121)

* Mon Aug  6 2012 Joe Orton <jorton@redhat.com> - 2.4.2-23
- add mod_proxy fixes from upstream (r1366693, r1365604)

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.2-22
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jul  6 2012 Joe Orton <jorton@redhat.com> - 2.4.2-21
- drop explicit version requirement on initscripts

* Thu Jul  5 2012 Joe Orton <jorton@redhat.com> - 2.4.2-20
- mod_ext_filter: fix error_log warnings

* Mon Jul  2 2012 Joe Orton <jorton@redhat.com> - 2.4.2-19
- support "configtest" and "graceful" as initscripts "legacy actions"

* Fri Jun  8 2012 Joe Orton <jorton@redhat.com> - 2.4.2-18
- avoid use of "core" GIF for a "core" directory (#168776)
- drop use of "syslog.target" in systemd unit file

* Thu Jun  7 2012 Joe Orton <jorton@redhat.com> - 2.4.2-17
- use _unitdir for systemd unit file
- use /run in unit file, ssl.conf

* Thu Jun  7 2012 Joe Orton <jorton@redhat.com> - 2.4.2-16
- mod_ssl: fix NPN patch merge

* Wed Jun  6 2012 Joe Orton <jorton@redhat.com> - 2.4.2-15
- move tmpfiles.d fragment into /usr/lib per new guidelines
- package /run/httpd not /var/run/httpd
- set runtimedir to /run/httpd likewise

* Wed Jun  6 2012 Joe Orton <jorton@redhat.com> - 2.4.2-14
- fix htdbm/htpasswd crash on crypt() failure (#818684)

* Wed Jun  6 2012 Joe Orton <jorton@redhat.com> - 2.4.2-13
- pull fix for NPN patch from upstream (r1345599)

* Thu May 31 2012 Joe Orton <jorton@redhat.com> - 2.4.2-12
- update suexec patch to use LOG_AUTHPRIV facility

* Thu May 24 2012 Joe Orton <jorton@redhat.com> - 2.4.2-11
- really fix autoindex.conf (thanks to remi@)

* Thu May 24 2012 Joe Orton <jorton@redhat.com> - 2.4.2-10
- fix autoindex.conf to allow symlink to poweredby.png

* Wed May 23 2012 Joe Orton <jorton@redhat.com> - 2.4.2-9
- suexec: use upstream version of patch for capability bit support

* Wed May 23 2012 Joe Orton <jorton@redhat.com> - 2.4.2-8
- suexec: use syslog rather than suexec.log, drop dac_override capability

* Tue May  1 2012 Joe Orton <jorton@redhat.com> - 2.4.2-7
- mod_ssl: add TLS NPN support (r1332643, #809599)

* Tue May  1 2012 Joe Orton <jorton@redhat.com> - 2.4.2-6
- add BR on APR >= 1.4.0

* Fri Apr 27 2012 Joe Orton <jorton@redhat.com> - 2.4.2-5
- use systemctl from logrotate (#221073)

* Fri Apr 27 2012 Joe Orton <jorton@redhat.com> - 2.4.2-4
- pull from upstream:
  * use TLS close_notify alert for dummy_connection (r1326980+)
  * cleanup symbol exports (r1327036+)

* Fri Apr 27 2012 Joe Orton <jorton@redhat.com> - 2.4.2-3.2
- rebuild

* Fri Apr 20 2012 Joe Orton <jorton@redhat.com> - 2.4.2-3
- really fix restart

* Fri Apr 20 2012 Joe Orton <jorton@redhat.com> - 2.4.2-2
- tweak default ssl.conf
- fix restart handling (#814645)
- use graceful restart by default

* Wed Apr 18 2012 Jan Kaluza <jkaluza@redhat.com> - 2.4.2-1
- update to 2.4.2

* Fri Mar 23 2012 Joe Orton <jorton@redhat.com> - 2.4.1-6
- fix macros

* Fri Mar 23 2012 Joe Orton <jorton@redhat.com> - 2.4.1-5
- add _httpd_moddir to macros

* Tue Mar 13 2012 Joe Orton <jorton@redhat.com> - 2.4.1-4
- fix symlink for poweredby.png
- fix manual.conf

* Tue Mar 13 2012 Joe Orton <jorton@redhat.com> - 2.4.1-3
- add mod_proxy_html subpackage (w/mod_proxy_html + mod_xml2enc)
- move mod_ldap, mod_authnz_ldap to mod_ldap subpackage

* Tue Mar 13 2012 Joe Orton <jorton@redhat.com> - 2.4.1-2
- clean docroot better
- ship proxy, ssl directories within /var/cache/httpd
- default config:
 * unrestricted access to (only) /var/www
 * remove (commented) Mutex, MaxRanges, ScriptSock
 * split autoindex config to conf.d/autoindex.conf
- ship additional example configs in docdir

* Tue Mar  6 2012 Joe Orton <jorton@redhat.com> - 2.4.1-1
- update to 2.4.1
- adopt upstream default httpd.conf (almost verbatim)
- split all LoadModules to conf.modules.d/*.conf
- include conf.d/*.conf at end of httpd.conf
- trim %%changelog

* Mon Feb 13 2012 Joe Orton <jorton@redhat.com> - 2.2.22-2
- fix build against PCRE 8.30

* Mon Feb 13 2012 Joe Orton <jorton@redhat.com> - 2.2.22-1
- update to 2.2.22

* Fri Feb 10 2012 Petr Pisar <ppisar@redhat.com> - 2.2.21-8
- Rebuild against PCRE 8.30

* Mon Jan 23 2012 Jan Kaluza <jkaluza@redhat.com> - 2.2.21-7
- fix #783629 - start httpd after named

* Mon Jan 16 2012 Joe Orton <jorton@redhat.com> - 2.2.21-6
- complete conversion to systemd, drop init script (#770311)
- fix comments in /etc/sysconfig/httpd (#771024)
- enable PrivateTmp in service file (#781440)
- set LANG=C in /etc/sysconfig/httpd

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2.21-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Dec 06 2011 Jan Kaluza <jkaluza@redhat.com> - 2.2.21-4
- fix #751591 - start httpd after remote-fs

* Mon Oct 24 2011 Jan Kaluza <jkaluza@redhat.com> - 2.2.21-3
- allow change state of BalancerMember in mod_proxy_balancer web interface

* Thu Sep 22 2011 Ville Skyttä <ville.skytta@iki.fi> - 2.2.21-2
- Make mmn available as %%{_httpd_mmn}.
- Add .svgz to AddEncoding x-gzip example in httpd.conf.

* Tue Sep 13 2011 Joe Orton <jorton@redhat.com> - 2.2.21-1
- update to 2.2.21

* Mon Sep  5 2011 Joe Orton <jorton@redhat.com> - 2.2.20-1
- update to 2.2.20
- fix MPM stub man page generation

* Wed Aug 10 2011 Jan Kaluza <jkaluza@redhat.com> - 2.2.19-5
- fix #707917 - add httpd-ssl-pass-dialog to ask for SSL password using systemd

* Fri Jul 22 2011 Iain Arnell <iarnell@gmail.com> 1:2.2.19-4
- rebuild while rpm-4.9.1 is untagged to remove trailing slash in provided
  directory names

* Wed Jul 20 2011 Jan Kaluza <jkaluza@redhat.com> - 2.2.19-3
- fix #716621 - suexec now works without setuid bit

* Thu Jul 14 2011 Jan Kaluza <jkaluza@redhat.com> - 2.2.19-2
- fix #689091 - backported patch from 2.3 branch to support IPv6 in logresolve

* Fri Jul  1 2011 Joe Orton <jorton@redhat.com> - 2.2.19-1
- update to 2.2.19
- enable dbd, authn_dbd in default config

* Thu Apr 14 2011 Joe Orton <jorton@redhat.com> - 2.2.17-13
- fix path expansion in service files

* Tue Apr 12 2011 Joe Orton <jorton@redhat.com> - 2.2.17-12
- add systemd service files (#684175, thanks to Jóhann B. Guðmundsson)

* Wed Mar 23 2011 Joe Orton <jorton@redhat.com> - 2.2.17-11
- minor updates to httpd.conf
- drop old patches

* Wed Mar  2 2011 Joe Orton <jorton@redhat.com> - 2.2.17-10
- rebuild

* Wed Feb 23 2011 Joe Orton <jorton@redhat.com> - 2.2.17-9
- use arch-specific mmn

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2.17-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jan 31 2011 Joe Orton <jorton@redhat.com> - 2.2.17-7
- generate dummy mod_ssl cert with CA:FALSE constraint (#667841)
- add man page stubs for httpd.event, httpd.worker
- drop distcache support
- add STOP_TIMEOUT support to init script

* Sat Jan  8 2011 Joe Orton <jorton@redhat.com> - 2.2.17-6
- update default SSLCipherSuite per upstream trunk

* Wed Jan  5 2011 Joe Orton <jorton@redhat.com> - 2.2.17-5
- fix requires (#667397)

* Wed Jan  5 2011 Joe Orton <jorton@redhat.com> - 2.2.17-4
- de-ghost /var/run/httpd

* Tue Jan  4 2011 Joe Orton <jorton@redhat.com> - 2.2.17-3
- add tmpfiles.d configuration, ghost /var/run/httpd (#656600)

* Sat Nov 20 2010 Joe Orton <jorton@redhat.com> - 2.2.17-2
- drop setuid bit, use capabilities for suexec binary

* Wed Oct 27 2010 Joe Orton <jorton@redhat.com> - 2.2.17-1
- update to 2.2.17

* Fri Sep 10 2010 Joe Orton <jorton@redhat.com> - 2.2.16-2
- link everything using -z relro and -z now

* Mon Jul 26 2010 Joe Orton <jorton@redhat.com> - 2.2.16-1
- update to 2.2.16

* Fri Jul  9 2010 Joe Orton <jorton@redhat.com> - 2.2.15-3
- default config tweaks:
 * harden httpd.conf w.r.t. .htaccess restriction (#591293)
 * load mod_substitute, mod_version by default
 * drop proxy_ajp.conf, load mod_proxy_ajp in httpd.conf
 * add commented list of shipped-but-unloaded modules
 * bump up worker defaults a little
 * drop KeepAliveTimeout to 5 secs per upstream
- fix LSB compliance in init script (#522074)
- bundle NOTICE in -tools
- use init script in logrotate postrotate to pick up PIDFILE
- drop some old Obsoletes/Conflicts

* Sun Apr 04 2010 Robert Scheck <robert@fedoraproject.org> - 2.2.15-1
- update to 2.2.15 (#572404, #579311)
