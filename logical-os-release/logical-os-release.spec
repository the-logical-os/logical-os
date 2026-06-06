%define autorelease(e:s:pb:n) %{?-p:0.}%{lua:
    release_number = 0;
    base_release_number = tonumber(rpm.expand("%{?-b*}%{!?-b:1}"));
    print(release_number + base_release_number - 1);
}%{?-e:.%{-e*}}%{?-s:.%{-s*}}%{!?-n:%{?dist}}

%define release_name Axiom
%define is_rawhide 0

# Define this to 1 for Branched releases prior to RC
# or 0 for RC and stable releases
%define is_development 0

%define eol_date 2026-10-20

%define dist_version 44
%define rhel_dist_version 11

%if %{is_rawhide}
%define bug_version rawhide
%if 0%{?eln}
  %define releasever eln
%else
  %define releasever rawhide
%endif
%define doc_version rawhide
%else
%define bug_version %{dist_version}
%define releasever %{dist_version}
%define doc_version f%{dist_version}
%endif

%if %{with silverblue} || %{with kinoite} || %{with kinoite_mobile} || %{with sway_atomic} || %{with budgie_atomic} || %{with miraclewm_atomic} || %{with cosmic_atomic}
%global with_ostree_desktop 1
%endif

%global dist %{?eln:.eln%{eln}}

# Changes should be submitted as pull requests under
#     https://src.fedoraproject.org/rpms/fedora-release

Summary:        Fedora release files
Name:           logical-os-release
Version:        44
# The numbering is 0.<r> before a given Fedora Linux release is released,
# and then just <r>.
Release:        %autorelease %[0%{?is_development} ? "-p" : ""]
License:        MIT
URL:            https://github.com/fb24m/logical-os

Source1:        LICENSE
Source2:        Fedora-Legal-README.txt

Source10:       85-display-manager.preset
Source11:       90-default.preset
Source12:       90-default-user.preset
Source13:       99-default-disable.preset
Source14:       80-server.preset
Source15:       80-workstation.preset
Source16:       org.gnome.shell.gschema.override
Source17:       org.projectatomic.rpmostree1.rules
Source19:       distro-template.swidtag
Source20:       distro-edition-template.swidtag
Source22:       80-coreos.preset
Source23:       zezere-ignition-url
Source24:       80-iot-user.preset
Source27:       81-desktop.preset
Source28:       longer-default-shutdown-timeout.conf
Source29:       org.gnome.settings-daemon.plugins.power.gschema.override
Source31:       20-fedora-defaults.conf
Source32:       75-eln.preset
Source100:      100-logical-os.conf

BuildArch:      noarch

Provides:       fedora-release = %{version}-%{release}
Provides:       fedora-release-variant = %{version}-%{release}

Provides:       system-release
Provides:       system-release(%{version})
Requires:       fedora-release-common = %{version}-%{release}

# fedora-release-common Requires: fedora-release-identity, so at least one
# package must provide it. This Recommends: pulls in
# fedora-release-identity-basic if nothing else is already doing so.
Recommends:     fedora-release-identity-basic

BuildRequires:  redhat-rpm-config > 121-1
BuildRequires:  systemd-rpm-macros

%description
Fedora release files such as various /etc/ files that define the release
and systemd preset files that determine which services are enabled by default.
# See https://docs.fedoraproject.org/en-US/packaging-guidelines/DefaultServices/ for details.

%package common
Summary: Fedora release files
Provides: fedora-release-common = %{version}-%{release}

Requires:   fedora-release-variant = %{version}-%{release}
Suggests:   fedora-release

%if %{with eln}
Requires:   fedora-repos-eln = %{version}
%else
Requires:   fedora-repos(%{version})
%endif
Requires:   fedora-release-identity = %{version}-%{release}

%if %{is_rawhide}
# Make $releasever return "rawhide" on Rawhide
# and "eln" on ELN.
# https://pagure.io/releng/issue/7445
Provides:       system-release(releasever) = %{releasever}
%endif

# Fedora ships a generic-release package to make the creation of Remixes
# easier, but it cannot coexist with the fedora-release[-*] packages, so we
# will explicitly conflict with it.
Conflicts:  generic-release

# rpm-ostree count me is now enabled in 90-default.preset
Obsoletes: fedora-release-ostree-counting <= 36-0.7

%description common
Release files common to all Editions and Spins of Fedora

%package identity-basic
Summary:        Package providing the basic Fedora identity

RemovePathPostfixes: .basic
Provides:       fedora-release-identity = %{version}-%{release}
Conflicts:      fedora-release-identity

%description identity-basic
Provides the necessary files for a Fedora installation that is not identifying
itself as a particular Edition or Spin.

%prep
mkdir -p licenses
sed 's|@@VERSION@@|%{dist_version}|g' %{SOURCE2} >licenses/Fedora-Legal-README.txt

%build

%install
install -d %{buildroot}%{_prefix}/lib
echo "Fedora release %{version} (%{release_name})" > %{buildroot}%{_prefix}/lib/fedora-release
echo "cpe:/o:fedoraproject:fedora:%{version}" > %{buildroot}%{_prefix}/lib/system-release-cpe

# Symlink the -release files
install -d %{buildroot}%{_sysconfdir}
ln -s ../usr/lib/fedora-release %{buildroot}%{_sysconfdir}/fedora-release
ln -s ../usr/lib/system-release-cpe %{buildroot}%{_sysconfdir}/system-release-cpe
ln -s fedora-release %{buildroot}%{_sysconfdir}/redhat-release
ln -s fedora-release %{buildroot}%{_sysconfdir}/system-release

# Create the common os-release file
%{lua:
  function starts_with(str, start)
   return str:sub(1, #start) == start
  end
}
%define starts_with(str,prefix) (%{expand:%%{lua:print(starts_with(%1, %2) and "1" or "0")}})
%if %{starts_with "a%{release}" "a0"}
  %global prerelease \ Prerelease
%endif

# -------------------------------------------------------------------------
# Definitions for /etc/os-release and for macros in macros.dist.  These
# macros are useful for spec files where distribution-specific identifiers
# are used to customize packages.

# Name of vendor / name of distribution. Typically used to identify where
# the binary comes from in --help or --version messages of programs.
# Examples: gdb.spec, clang.spec
%global dist_vendor Logical OS
%global dist_name   Logical OS

# The namespace for purl
# https://github.com/package-url/purl-spec
# for example as in: pkg:rpm/fedora/python-setuptools@69.2.0-10.fc41?arch=src"
# Note that we use "fedora" even for Fedora ELN
%global dist_purl_namespace logical

# URL of the homepage of the distribution
# Example: gstreamer1-plugins-base.spec
%global dist_home_url https://github.com/fb24m/logical-os

# Bugzilla / bug reporting URLs shown to users.
# Examples: gcc.spec
%global dist_bug_report_url https://github.com/fb24m/logical-os/issues

# debuginfod server, as used in elfutils.spec.
%global dist_debuginfod_url ima:enforcing https://debuginfod.fedoraproject.org/ ima:ignore
# -------------------------------------------------------------------------

# Set the RELEASE_TYPE appropriately
%define release_type %[0%{?is_development} ? "development" : "stable"]

cat <<EOF >os-release
NAME="%{dist_name}"
VERSION="%{dist_version} (%{release_name}%{?prerelease})"
RELEASE_TYPE=%{release_type}
ID=fedora
VERSION_ID=%{dist_version}
VERSION_CODENAME=""
PRETTY_NAME="Logical OS %{dist_version} (%{release_name}%{?prerelease})"
ANSI_COLOR="0;38;2;60;110;180"
LOGO=fedora-logo-icon
VARIANT_ID=logical
CPE_NAME="cpe:/o:fedoraproject:fedora:%{dist_version}"
DEFAULT_HOSTNAME="logicalos"
HOME_URL="%{dist_home_url}"
DOCUMENTATION_URL="https://github.com/fb24m/logical-os/wiki"
SUPPORT_URL="https://github.com/fb24m/logical-os/discussions"
BUG_REPORT_URL="%{dist_bug_report_url}"
REDHAT_BUGZILLA_PRODUCT="Fedora"
REDHAT_BUGZILLA_PRODUCT_VERSION=%{bug_version}
REDHAT_SUPPORT_PRODUCT="Fedora"
REDHAT_SUPPORT_PRODUCT_VERSION=%{bug_version}
SUPPORT_END=%{eol_date}
EOF

# Create the common /etc/issue
echo "\S" > %{buildroot}%{_prefix}/lib/issue
echo "Kernel \r on \m (\l)" >> %{buildroot}%{_prefix}/lib/issue
echo >> %{buildroot}%{_prefix}/lib/issue
ln -s ../usr/lib/issue %{buildroot}%{_sysconfdir}/issue

# Create /etc/issue.net
echo "\S" > %{buildroot}%{_prefix}/lib/issue.net
echo "Kernel \r on \m (\l)" >> %{buildroot}%{_prefix}/lib/issue.net
ln -s ../usr/lib/issue.net %{buildroot}%{_sysconfdir}/issue.net

# Create /etc/issue.d
mkdir -p %{buildroot}%{_sysconfdir}/issue.d

mkdir -p %{buildroot}%{_swidtagdir}

# Create os-release files for the different editions

# Basic
cp -p os-release \
      %{buildroot}%{_prefix}/lib/os-release.basic

# Create the symlink for /etc/os-release
ln -s ../usr/lib/os-release %{buildroot}%{_sysconfdir}/os-release

# Set up the dist tag macros
install -d -m 755 %{buildroot}%{_rpmconfigdir}/macros.d
cat >> %{buildroot}%{_rpmconfigdir}/macros.d/macros.dist << EOF
# dist macros.

%%__bootstrap         ~bootstrap
%if 0%{?eln}
%%rhel              %{rhel_dist_version}
%%el%{rhel_dist_version}                1
# Although eln is set in koji tags, we put it in the macros.dist file for local and mock builds.
%%eln              %{eln}
%%distcore            .eln%%{eln}
%else
%%fedora              %{dist_version}
%%fc%{dist_version}                1
%%distcore            .fc%%{fedora}
%endif
%%dist                %%{!?distprefix0:%%{?distprefix}}%%{expand:%%{lua:for i=0,9999 do print("%%{?distprefix" .. i .."}") end}}%%{distcore}%%{?with_bootstrap:%%{__bootstrap}}%%{?buildrelease:+build%%{buildrelease}}
%%dist_vendor         %{dist_vendor}
%%dist_name           %{dist_name}
%%dist_purl_namespace %{dist_purl_namespace}
%%dist_home_url       %{dist_home_url}
%%dist_bug_report_url %{dist_bug_report_url}
%%dist_debuginfod_url %{dist_debuginfod_url}
EOF

# Add logical-os treeinfo
install -Dm0644 %{SOURCE100} \
    %{buildroot}%{_sysconfdir}/anaconda/profile.d/logical-os.conf

# Install licenses
install -pm 0644 %{SOURCE1} licenses/LICENSE

# Default system wide
install -Dm0644 %{SOURCE10} -t %{buildroot}%{_prefix}/lib/systemd/system-preset/
install -Dm0644 %{SOURCE11} -t %{buildroot}%{_prefix}/lib/systemd/system-preset/
install -Dm0644 %{SOURCE12} -t %{buildroot}%{_prefix}/lib/systemd/user-preset/
# The same file is installed in two places with identical contents
install -Dm0644 %{SOURCE13} -t %{buildroot}%{_prefix}/lib/systemd/system-preset/
install -Dm0644 %{SOURCE13} -t %{buildroot}%{_prefix}/lib/systemd/user-preset/

# Create distro-level SWID tag file
install -d %{buildroot}%{_swidtagdir}
sed -e "s#\$version#%{bug_version}#g" -e 's/<!--.*-->//;/^$/d' %{SOURCE19} > %{buildroot}%{_swidtagdir}/org.fedoraproject.Fedora-%{bug_version}.swidtag
install -d %{buildroot}%{_sysconfdir}/swid/swidtags.d
ln -s --relative %{buildroot}%{_swidtagdir} %{buildroot}%{_sysconfdir}/swid/swidtags.d/fedoraproject.org

# Install DNF 5 configuration defaults
install -Dm0644 %{SOURCE31} -t %{buildroot}%{_prefix}/share/dnf5/libdnf.conf.d/

%files common
%license licenses/LICENSE licenses/Fedora-Legal-README.txt
%{_prefix}/lib/fedora-release
%{_prefix}/lib/system-release-cpe
%{_sysconfdir}/os-release
%{_sysconfdir}/fedora-release
%{_sysconfdir}/redhat-release
%{_sysconfdir}/system-release
%{_sysconfdir}/system-release-cpe
%attr(0644,root,root) %{_prefix}/lib/issue
%config(noreplace) %{_sysconfdir}/issue
%attr(0644,root,root) %{_prefix}/lib/issue.net
%config(noreplace) %{_sysconfdir}/issue.net
%dir %{_sysconfdir}/issue.d
%attr(0644,root,root) %{_rpmconfigdir}/macros.d/macros.dist
%dir %{_prefix}/lib/systemd/user-preset/
%{_prefix}/lib/systemd/user-preset/90-default-user.preset
%{_prefix}/lib/systemd/user-preset/99-default-disable.preset
%dir %{_prefix}/lib/systemd/system-preset/
%{_prefix}/lib/systemd/system-preset/85-display-manager.preset
%{_prefix}/lib/systemd/system-preset/90-default.preset
%{_prefix}/lib/systemd/system-preset/99-default-disable.preset
%dir %{_swidtagdir}
%{_swidtagdir}/org.fedoraproject.Fedora-%{bug_version}.swidtag
%dir %{_sysconfdir}/swid
%{_sysconfdir}/swid/swidtags.d
%{_prefix}/share/dnf5/libdnf.conf.d/20-fedora-defaults.conf

%dir %{_sysconfdir}/anaconda
%dir %{_sysconfdir}/anaconda/profile.d
%{_sysconfdir}/anaconda/profile.d/logical-os.conf

%files
%files identity-basic
%{_prefix}/lib/os-release.basic

%changelog
