%global php_apiver  %((echo 0; php -i 2>/dev/null | sed -n 's/^PHP API => //p') | tail -1)
%{!?__pecl:     %{expand: %%global __pecl     %{_bindir}/pecl}}
%{!?php_extdir: %{expand: %%global php_extdir %(php-config --extension-dir)}}

Name:           php-pecl-xdebug
Version:        2.0.2
Release:        1%{?dist}
Summary:        PECL package for debugging PHP scripts

License:        BSD
Group:          Development/Languages
URL:            http://pecl.php.net/package/xdebug
Source0:        http://pecl.php.net/get/xdebug-%{version}.tgz

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  php-devel
Provides:       php-pecl(Xdebug) = %{version}

%if %{?php_zend_api}0
Requires:       php(zend-abi) = %{php_zend_api}
Requires:       php(api) = %{php_core_api}
%else
# for EL-5
Requires:       php-api = %{php_apiver}
%endif

%description
The Xdebug extension helps you debugging your script by providing a lot
of valuable debug information.


%prep
%setup -qcn xdebug-%{version}
cd xdebug-%{version}

# fix rpmlint warnings
iconv -f iso8859-1 -t utf-8 Changelog > Changelog.conv && mv -f Changelog.conv Changelog


%build
cd xdebug-%{version}
phpize
%configure --enable-xdebug
CFLAGS="$RPM_OPT_FLAGS" make


%install
cd xdebug-%{version}
rm -rf $RPM_BUILD_ROOT
make install INSTALL_ROOT=$RPM_BUILD_ROOT

# install config file
install -d $RPM_BUILD_ROOT%{_sysconfdir}/php.d
cat > $RPM_BUILD_ROOT%{_sysconfdir}/php.d/xdebug.ini << 'EOF'
; Enable xdebug extension module
zend_extension=%{php_extdir}/xdebug.so
EOF

# install doc files
install -d docs
install -pm 644 Changelog CREDITS LICENSE NEWS README docs


%if 0%{?pecl_install:1}
%post
%{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :
%endif


%if 0%{?pecl_uninstall:1}
%postun
if [ $1 -eq 0 ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi
%endif


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc xdebug-%{version}/docs/*
%config(noreplace) %{_sysconfdir}/php.d/xdebug.ini
%{php_extdir}/xdebug.so


%changelog
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
