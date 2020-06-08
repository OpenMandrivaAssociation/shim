Name:		shim
Version:	15
Release:	1
Summary:	First-stage UEFI bootloader
License:	BSD
URL:		https://github.com/rhboot/shim/
BuildRequires:	efi-filesystem
BuildRequires:	efi-srpm-macros >= 3-2

ExclusiveArch:	%{efi}
# but we don't build a .i686 package, just a shim-ia32.x86_64 package
ExcludeArch:	%{ix86}
# and we don't have shim-unsigned-arm builds *yet*
ExcludeArch:	%{arm}

Source0:	shim.rpmmacros

# keep these two lists of sources synched up arch-wise.  That is 0 and 10
# match, 1 and 11 match, ...
Source10:	BOOTAA64.CSV
Source20:	shimaa64.efi
Source11:	BOOTIA32.CSV
Source21:	shimia32.efi
Source12:	BOOTX64.CSV
Source22:	shimx64.efi
#Source13:	BOOTARM.CSV
#Source23:	shimarm.efi

%include %{SOURCE0}

BuildRequires:	pesign
# We need this because %%{efi} won't expand before choosing where to make
# the src.rpm in koji, and we could be on a non-efi architecture, in which
# case we won't have a valid expansion here...  To be solved in the future
# (shim 16+) by making the unsigned packages all provide "shim-unsigned", so
# we can just BuildRequires that.
%ifarch %{x86_64}
BuildRequires: %{unsignedx64} = %{shimverx64}
BuildRequires: %{unsignedia32} = %{shimveria32}
%endif
%ifarch aarch64
BuildRequires: %{unsignedaa64} = %{shimveraa64}
%endif
%ifarch arm
BuildRequires: %%{unsignedarm} = %%{shimverarm}
%endif

%description
Initial UEFI bootloader that handles chaining to a trusted full bootloader
under secure boot environments. This package contains the version signed by
the UEFI signing service.

%define_pkg -a %{efi_arch} -p 1
%if %{efi_has_alt_arch}
%define_pkg -a %{efi_alt_arch}
%endif

%prep
cd %{_builddir}
rm -rf shim-%{version}
mkdir shim-%{version}

%build

cd shim-%{version}
%if %{efi_has_alt_arch}
%define_build -a %{efi_alt_arch} -A %{efi_alt_arch_upper} -i %{shimefialt} -b yes -c %{is_alt_signed} -d %{shimdiralt}
%endif
%define_build -a %{efi_arch} -A %{efi_arch_upper} -i %{shimefi} -b yes -c %{is_signed} -d %{shimdir}

%install
rm -rf $RPM_BUILD_ROOT
cd shim-%{version}
install -D -d -m 0755 $RPM_BUILD_ROOT/boot/
install -D -d -m 0700 $RPM_BUILD_ROOT%{efi_esp_root}/
install -D -d -m 0700 $RPM_BUILD_ROOT%{efi_esp_efi}/
install -D -d -m 0700 $RPM_BUILD_ROOT%{efi_esp_dir}/
install -D -d -m 0700 $RPM_BUILD_ROOT%{efi_esp_boot}/

%do_install -a %{efi_arch} -A %{efi_arch_upper} -b %{bootcsv}
%if %{efi_has_alt_arch}
%do_install -a %{efi_alt_arch} -A %{efi_alt_arch_upper} -b %{bootcsvalt}
%endif

%if %{provide_legacy_shim}
install -m 0700 %{shimefi} $RPM_BUILD_ROOT%{efi_esp_dir}/shim.efi
%endif

( cd $RPM_BUILD_ROOT ; find .%{efi_esp_root} -type f ) \
  | sed -e 's/\./\^/' -e 's,^\\\./,.*/,' -e 's,$,$,' > %{__brp_mangle_shebangs_exclude_from_file}

%define_files -a %{efi_arch} -A %{efi_arch_upper}
%if %{provide_legacy_shim}
%{efi_esp_dir}/shim.efi
%endif
%if %{efi_has_alt_arch}
%define_files -a %{efi_alt_arch} -A %{efi_alt_arch_upper}
%endif
