#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/packages"
COMPS_XML="$OUTPUT_DIR/comps.xml"

EXTRA_PACKAGES=(
    shim-x64
    grub2-efi-x64
    grub2-efi-x64-modules
    grub2-common
    grub2-tools
    grub2-tools-minimal
    dracut-live
    anaconda
    anaconda-core
    anaconda-gui
    flatpak
    flatpak-selinux
    rpm-libs
    rpm-plugin-selinux
    libsss_sudo
    grub2-pc-modules

    kf5-kconfig
    kf5-kguiaddons
    kf5-kiconthemes
    kf5-kwidgetsaddons
    kf5-frameworkintegration
    kf5-kwindowsystem
    qt5-qtbase
    qt5-qtbase-gui
    qt5-qtdeclarative
    qt5-qtquickcontrols2

    qt5-qtwayland
    libX11
    libXcomposite
    mesa-libEGL
    mesa-libGL
    qt5-qtbase-gui

    plasma-workspace
    plasma-integration

    darkly-qt5
    plasma-breeze-qt5

    btrfs-progs
    efibootmgr
    grub2-tools-extra
    grubby
    dosfstools

    kernel
    kernel-core
    kernel-modules
)

COPR_REPOS=(
    "ririko66z/dots-hyprland"
    "sdegler/hyprland"
    "lionheartp/Hyprland"
    "deltacopy/darkly"
    "alternateved/eza"
    "atim/starship"
)

mkdir -p "$OUTPUT_DIR"

REPO_FLAGS=()
for repo in "${COPR_REPOS[@]}"; do
    REPO_FLAGS+=(--repo "copr:copr.fedorainfracloud.org:${repo//\//:}")
done

echo "==> Extracting package list from comps.xml..."
packages=$(python3 -c "
import xml.etree.ElementTree as ET
tree = ET.parse('$COMPS_XML')
root = tree.getroot()
for pkg in root.iter('packagereq'):
    print(pkg.text)
")

echo "$packages" | wc -l
echo "$packages" | head -10000

if [ -z "$packages" ]; then
    echo "ERROR: No packages found in $COMPS_XML"
    exit 1
fi

all_packages=($packages "${EXTRA_PACKAGES[@]}")

SKIP_PACKAGES=("quickshell" "quickshell-git" "hyprland-uwsm")

filtered=()

for pkg in "${all_packages[@]}"; do
    skip=false
    for s in "${SKIP_PACKAGES[@]}"; do
        [[ "$pkg" == "$s" ]] && skip=true && break
    done
    $skip || filtered+=("$pkg")
done

echo "$all_packages"

echo "==> Found $(echo $all_packages | wc -w) packages total"

echo "==> Downloading x86_64 packages with dependencies..."

export http_proxy="http://127.0.0.1:10808"
export https_proxy="http://127.0.0.1:10808"
export all_proxy="socks5://127.0.0.1:10808"

dnf download --resolve --alldeps \
    --arch=x86_64 --arch=noarch \
    --destdir="$OUTPUT_DIR" \
    --setopt=install_weak_deps=False \
    --exclude="hyprland-uwsm" \
    "${REPO_FLAGS[@]}" \
    --repo "fedora" --repo "updates" --repo "updates-testing" \
    "${filtered[@]}"


echo "==> Creating repository metadata..."
createrepo_c --groupfile "$COMPS_XML" "$OUTPUT_DIR"

echo "==> Done! $(ls "$OUTPUT_DIR"/*.rpm 2>/dev/null | wc -l) packages in $OUTPUT_DIR"
