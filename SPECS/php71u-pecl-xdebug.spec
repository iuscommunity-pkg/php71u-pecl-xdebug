# IUS spec file for php71u-pecl-xdebug, forked from:
#
# Fedora spec file for php-pecl-xdebug
#
# Copyright (c) 2010-2016 Remi Collet
# Copyright (c) 2006-2009 Christopher Stone
#
# License: MIT
# http://opensource.org/licenses/MIT
#
# Please, preserve the changelog entries
#

%global pecl_name xdebug
# XDebug should be loaded after opcache
%global ini_name  15-%{pecl_name}.ini
%global php       php71u

%bcond_without zts

Name:           %{php}-pecl-%{pecl_name}
Summary:        PECL package for debugging PHP scripts
Version:        2.6.0
Release:        2.ius%{?dist}
Source0:        https://pecl.php.net/get/%{pecl_name}-%{version}.tgz

# The Xdebug License, version 1.01
# (Based on "The PHP License", version 3.0)
License:        PHP
Group:          Development/Languages
URL:            https://xdebug.org

BuildRequires:  %{php}-devel
BuildRequires:  libedit-devel
BuildRequires:  libtool

BuildRequires:  pear1u
# explicitly require pear dependencies to avoid conflicts
BuildRequires:  %{php}-cli
BuildRequires:  %{php}-common
BuildRequires:  %{php}-process
BuildRequires:  %{php}-xml

Requires:       php(zend-abi) = %{php_zend_api}
Requires:       php(api) = %{php_core_api}

# provide the stock name
Provides:       php-pecl-%{pecl_name} = %{version}
Provides:       php-pecl-%{pecl_name}%{?_isa} = %{version}

# provide the stock and IUS names without pecl
Provides:       php-%{pecl_name} = %{version}
Provides:       php-%{pecl_name}%{?_isa} = %{version}
Provides:       %{php}-%{pecl_name} = %{version}
Provides:       %{php}-%{pecl_name}%{?_isa} = %{version}

# provide the stock and IUS names in pecl() format
Provides:       php-pecl(Xdebug) = %{version}
Provides:       php-pecl(Xdebug)%{?_isa} = %{version}
Provides:       %{php}-pecl(Xdebug) = %{version}
Provides:       %{php}-pecl(Xdebug)%{?_isa} = %{version}

# conflict with the stock name
Conflicts:      php-pecl-%{pecl_name} < %{version}

%{?filter_provides_in: %filter_provides_in %{php_extdir}/.*\.so$}
%{?filter_provides_in: %filter_provides_in %{php_ztsextdir}/.*\.so$}
%{?filter_setup}


%description
The Xdebug extension helps you debugging your script by providing a lot of
valuable debug information. The debug information that Xdebug can provide
includes the following:

* stack and function traces in error messages with:
  o full parameter display for user defined functions
  o function name, file name and line indications
  o support for member functions
* memory allocation
* protection for infinite recursions

Xdebug also provides:

* profiling information for PHP scripts
* code coverage analysis
* capabilities to debug your scripts interactively with a debug client


%prep
%setup -qc
mv %{pecl_name}-%{version} NTS

sed -e '/LICENSE/s/role="doc"/role="src"/' -i package.xml

# Check extension version
ver=$(sed -n '/XDEBUG_VERSION/{s/.* "//;s/".*$//;p}' NTS/php_xdebug.h)
if test "$ver" != "%{version}"; then
   : Error: Upstream version is ${ver}, expecting %{version}.
   exit 1
fi

%if %{with zts}
cp -pr NTS ZTS
%endif

cat > %{ini_name} << EOF
; Enable xdebug extension module
zend_extension=%{pecl_name}.so

; see http://xdebug.org/docs/all_settings
EOF
sed -e '1d' NTS/%{pecl_name}.ini >> %{ini_name}


%build
pushd NTS
%{_bindir}/phpize
%configure \
    --enable-xdebug  \
    --with-php-config=%{_bindir}/php-config
%make_build

# Build debugclient
pushd debugclient
# buildconf required for aarch64 support
./buildconf
%configure --with-libedit
%make_build
popd
popd

%if %{with zts}
pushd ZTS
%{_bindir}/zts-phpize
%configure \
    --enable-xdebug  \
    --with-php-config=%{_bindir}/zts-php-config
%make_build
popd
%endif


%install
make -C NTS install INSTALL_ROOT=%{buildroot}
install -D -p -m 644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}

# install debugclient
install -Dpm 755 NTS/debugclient/debugclient \
        %{buildroot}%{_bindir}/debugclient

%if %{with zts}
make -C ZTS install INSTALL_ROOT=%{buildroot}
install -D -p -m 644 %{ini_name} %{buildroot}%{php_ztsinidir}/%{ini_name}
%endif

install -D -p -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{pecl_name}.xml

for i in $(grep 'role="doc"' package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -D -p -m 644 NTS/$i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


%check
%{__php} \
    --no-php-ini \
    --define zend_extension=%{buildroot}%{php_extdir}/%{pecl_name}.so \
    --modules | grep Xdebug

%if %{with zts}
%{__ztsphp} \
    --no-php-ini \
    --define zend_extension=%{buildroot}%{php_ztsextdir}/%{pecl_name}.so \
    --modules | grep Xdebug
%endif


%triggerin -- pear1u
if [ -x %{__pecl} ]; then
    %{pecl_install} %{pecl_xmldir}/%{pecl_name}.xml >/dev/null || :
fi


%posttrans
if [ -x %{__pecl} ]; then
    %{pecl_install} %{pecl_xmldir}/%{pecl_name}.xml >/dev/null || :
fi


%postun
if [ $1 -eq 0 -a -x %{__pecl} ]; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi


%files
%license NTS/LICENSE
%doc %{pecl_docdir}/%{pecl_name}
%{_bindir}/debugclient
%{pecl_xmldir}/%{pecl_name}.xml

%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{pecl_name}.so

%if %{with zts}
%config(noreplace) %{php_ztsinidir}/%{ini_name}
%{php_ztsextdir}/%{pecl_name}.so
%endif


%changelog
* Wed Jan 31 2018 Carl George <carl@george.computer> - 2.6.0-2.ius
- Remove pear requirement and update scriptlets (adapted from remirepo)

* Tue Jan 30 2018 Carl George <carl@george.computer> - 2.6.0-1.ius
- Latest upstream

* Wed Jun 21 2017 Ben Harper <ben.harper@rackspace.com> - 2.5.5-1.ius
- Latest upstream

* Mon May 15 2017 Ben Harper <ben.harper@rackspace.com> - 2.5.4-1.ius
- Latest upstream

* Tue Apr 18 2017 Carl George <carl.george@rackspace.com> - 2.5.3-1.ius
- Latest upstream

* Mon Feb 27 2017 Carl George <carl.george@rackspace.com> - 2.5.1-1.ius
- Latest upstream
- Use upstream provided configuration with all settings (Fedora)

* Sat Dec 10 2016 Carl George <carl.george@rackspace.com> - 2.5.0-1.ius
- Port from Fedora to IUS
- Install package.xml as %%{pecl_name}.xml, not %%{name}.xml
- Build with pear1u (via "pecl" virtual provides)
- Re-add scriptlets (file triggers not yet available in EL)
- Create ini file once during %%prep, instead of twice during %%install

* Mon Dec  5 2016 Remi Collet <remi@fedoraproject.org> - 2.5.0-1
- update to 2.5.0

* Mon Nov 14 2016 Remi Collet <remi@fedoraproject.org> - 2.5.0-0.1.RC1
- update to 2.5.0RC1 for PHP 7.1

* Tue Aug  2 2016 Remi Collet <remi@fedoraproject.org> - 2.4.1-1
- update to 2.4.1

* Mon Jun 27 2016 Remi Collet <remi@fedoraproject.org> - 2.4.0-2
- rebuild for https://fedoraproject.org/wiki/Changes/php70

* Tue Mar  8 2016 Remi Collet <remi@fedoraproject.org> - 2.4.0-1
- update to 2.4.0

* Sat Feb 13 2016 Remi Collet <remi@fedoraproject.org> - 2.3.3-3
- drop scriptlets (replaced by file triggers in php-pear)
- cleanup

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.3.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Jun 19 2015 Remi Collet <remi@fedoraproject.org> - 2.3.3-1
- update to 2.3.3
- drop all patches, merged upstream

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.3.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri May 29 2015 Remi Collet <remi@fedoraproject.org> - 2.3.2-3
- add patch for exception code change (for phpunit)

* Wed May 27 2015 Remi Collet <remi@fedoraproject.org> - 2.3.2-2
- add patch for efree/str_efree in php 5.6
- add patch for virtual_file_ex in 5.6 #1214111

* Sun Mar 22 2015 Remi Collet <remi@fedoraproject.org> - 2.3.2-1
- Update to 2.3.2

* Wed Feb 25 2015 Remi Collet <remi@fedoraproject.org> - 2.3.1-1
- Update to 2.3.1

* Mon Feb 23 2015 Remi Collet <remi@fedoraproject.org> - 2.3.0-1
- Update to 2.3.0
- raise minimum php version to 5.4

* Thu Jan 22 2015 Remi Collet <remi@fedoraproject.org> - 2.2.7-1
- Update to 2.2.7

* Sun Nov 16 2014 Remi Collet <remi@fedoraproject.org> - 2.2.6-1
- Update to 2.2.6 (stable)

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2.5-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Jun 19 2014 Remi Collet <rcollet@redhat.com> - 2.2.5-3
- rebuild for https://fedoraproject.org/wiki/Changes/Php56

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed Apr 30 2014 Remi Collet <remi@fedoraproject.org> - 2.2.5-1
- Update to 2.2.5 (stable)

* Wed Apr 23 2014 Remi Collet <remi@fedoraproject.org> - 2.2.4-2
- add numerical prefix to extension configuration file
- drop uneeded full extension path

* Sun Mar 02 2014 Remi Collet <remi@fedoraproject.org> - 2.2.4-1
- Update to 2.2.4 (stable)
- move documentation in pecl_docdir
- cleanups

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Jul 16 2013 Remi Collet <remi@fedoraproject.org> - 2.2.3-2
- adapt for SCL

* Wed May 22 2013 Remi Collet <remi@fedoraproject.org> - 2.2.3-1
- Update to 2.2.3

* Sun Mar 24 2013 Remi Collet <remi@fedoraproject.org> - 2.2.2-1
- update to 2.2.2 (stable)
- run buildconf for aarch64 support #926329
- modernize spec

* Fri Mar 22 2013 Remi Collet <rcollet@redhat.com> - 2.2.2-0.1.gitb1ce1e3
- update to 2.2.2dev for php 5.5
- rebuild for http://fedoraproject.org/wiki/Features/Php55
- also provides php-xdebug

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jul 17 2012 Remi Collet <remi@fedoraproject.org> - 2.2.1-1
- Update to 2.2.1

* Fri Jun 22 2012 Remi Collet <remi@fedoraproject.org> - 2.2.0-2
- upstream patch for upstream bug #838/#839/#840

* Wed May 09 2012 Remi Collet <remi@fedoraproject.org> - 2.2.0-1
- Update to 2.2.0

* Sun Apr 29 2012 Remi Collet <remi@fedoraproject.org> - 2.2.0-0.3.RC2
- Update to 2.2.0RC2

* Sat Mar 17 2012 Remi Collet <remi@fedoraproject.org> - 2.2.0-0.2.RC1
- update to 2.2.0RC1
- enable ZTS build
- fix License which is PHP, with some renaming

* Fri Jan 20 2012 Remi Collet <remi@fedoraproject.org> - 2.2.0-0.1.gitd076740
- update to 2.2.0-dev, build against php 5.4

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Jul 28 2011 Remi Collet <Fedora@FamilleCollet.com> - 2.1.2-1
- update to 2.1.2
- fix provides filter for rpm 4.9
- improved description

* Wed Mar 30 2011 Remi Collet <Fedora@FamilleCollet.com> - 2.1.1-1
- update to 2.1.1
- patch reported version

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sat Oct 23 2010 Remi Collet <Fedora@FamilleCollet.com> - 2.1.0-2
- add filter_provides to avoid private-shared-object-provides xdebug.so
- add %%check section (minimal load test)
- always use libedit

* Tue Jun 29 2010 Remi Collet <Fedora@FamilleCollet.com> - 2.1.0-1
- update to 2.1.0

* Mon Sep 14 2009 Christopher Stone <chris.stone@gmail.com> 2.0.5-1
- Upstream sync

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sun Jul 12 2009 Remi Collet <Fedora@FamilleCollet.com> - 2.0.4-1
- update to 2.0.4 (bugfix + Basic PHP 5.3 support)

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.3-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Oct 09 2008 Christopher Stone <chris.stone@gmail.com> 2.0.3-4
- Add code coverage patch (bz #460348)
- http://bugs.xdebug.org/bug_view_page.php?bug_id=0000344

* Thu Oct 09 2008 Christopher Stone <chris.stone@gmail.com> 2.0.3-3
- Revert last change

* Thu Oct 09 2008 Christopher Stone <chris.stone@gmail.com> 2.0.3-2
- Add php-xml to Requires (bz #464758)

* Thu May 22 2008 Christopher Stone <chris.stone@gmail.com> 2.0.3-1
- Upstream sync
- Clean up libedit usage
- Minor rpmlint fix

* Sun Mar 02 2008 Christopher Stone <chris.stone@gmail.com> 2.0.2-4
- Add %%{__pecl} to post/postun Requires

* Fri Feb 22 2008 Christopher Stone <chris.stone@gmail.com> 2.0.2-3
- %%define %%pecl_name to properly register package
- Install xml package description
- Add debugclient
- Many thanks to Edward Rudd (eddie@omegaware.com) (bz #432681)

* Wed Feb 20 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 2.0.2-2
- Autorebuild for GCC 4.3

* Sun Nov 25 2007 Christopher Stone <chris.stone@gmail.com> 2.0.2-1
- Upstream sync

* Sun Sep 30 2007 Christopher Stone <chris.stone@gmail.com> 2.0.0-2
- Update to latest standards
- Fix encoding on Changelog

* Sat Sep 08 2007 Christopher Stone <chris.stone@gmail.com> 2.0.0-1
- Upstream sync
- Remove %%{?beta} tags

* Sun Mar 11 2007 Christopher Stone <chris.stone@gmail.com> 2.0.0-0.5.RC2
- Create directory to untar sources
- Use new ABI check for FC6
- Remove %%{release} from Provides

* Mon Jan 29 2007 Christopher Stone <chris.stone@gmail.com> 2.0.0-0.4.RC2
- Compile with $RPM_OPT_FLAGS
- Use $RPM_BUILD_ROOT instead of %%{buildroot}
- Fix license tag

* Mon Jan 15 2007 Christopher Stone <chris.stone@gmail.com> 2.0.0-0.3.RC2
- Upstream sync

* Sun Oct 29 2006 Christopher Stone <chris.stone@gmail.com> 2.0.0-0.2.RC1
- Upstream sync

* Wed Sep 06 2006 Christopher Stone <chris.stone@gmail.com> 2.0.0-0.1.beta6
- Remove Provides php-xdebug
- Fix Release
- Remove prior changelog due to Release number change
