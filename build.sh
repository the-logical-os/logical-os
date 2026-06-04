#!/bin/bash

project_path="$(pwd)"
build_path="$project_path/build"

git clone https://github.com/end-4/dots-hyprland

cd dots-hyprland

git submodule update --init --recursive

cd ..

cp -r ./dots-hyprland/dots/. ./overlay/etc/skel/

cp -rn ./append/. ./overlay/

sudo lorax \
    --skip-branding \
    -i "logical-os-logos" \
    -i "logical-os-logos-classic" \
    -i "logical-os-logos-httpd" \
    -i "logical-os-release" \
    -i "logical-os-release-common" \
    -i "logical-os-release-identity-basic" \
    --product="Logical OS" \
    --volid="LogicalOS-44" \
    --version=44 \
    --release=44 \
    --source=https://mirror.yandex.ru/fedora/linux/releases/44/Everything/x86_64/os/ \
    --source="file://$HOME/rpmbuild/RPMS/noarch" \
    "$build_path"

cd "$build_path"

sudo xorriso -as mkisofs \
    -o ../LogicalOS-44-raw.iso \
    -V "LogicalOS-44" \
    -rational-rock -joliet \
    -eltorito-boot images/eltorito.img \
        -no-emul-boot -boot-load-size 4 -boot-info-table \
        --grub2-boot-info \
        --grub2-mbr /usr/lib/grub/i386-pc/boot_hybrid.img \
    -eltorito-alt-boot \
    -e images/efiboot.img \
        -no-emul-boot \
        --protective-msdos-label \
    -append_partition 2 0xef images/efiboot.img \
    .

cd ..

sudo mkksiso \
    --ks "$project_path/fedora-logical.ks" \
    --add "$project_path/overlay" \
    --add "$project_path/packages" \
    "./LogicalOS-44-raw.iso" \
    "./LogicalOS-44-final.iso"

rm -rf ~/LogicalOS-44-raw.iso
