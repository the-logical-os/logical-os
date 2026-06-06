%pre
echo "=== mounts ===" > /tmp/debug.txt
cat /proc/mounts >> /tmp/debug.txt
echo "=== find repo ===" >> /tmp/debug.txt
find /run/install -maxdepth 3 2>/dev/null >> /tmp/debug.txt
%end

url --url=file:///run/install/repo/packages/

network --bootproto=dhcp --device=link --activate --hostname=logicalos
keyboard us
lang en_US.UTF-8
reboot

autopart --type=btrfs

%packages
shim-x64
grub2-efi-x64
grub2-efi-x64-modules
grub2-common
grub2-tools
grub2-tools-minimal
dracut-live
anaconda
grub2-pc-modules
btrfs-progs
efibootmgr
grub2-tools-extra
grubby
dosfstools

-fedora-release
-fedora-release-common
-fedora-release-identity-basic
-fedora-logos

logical-os-release
logical-os-release-common
logical-os-release-identity-basic
logical-os-logos

%end

%post --nochroot
cp -r /run/install/repo/overlay/. /mnt/sysimage/
%end

%post
dnf copr enable alternateved/eza
dnf copr enable atim/starship
dnf copr enable deltacopy/darkly
dnf copr enable ririko66z/dots-hyprland
dnf copr enable sdegler/hyprland

systemctl enable sddm.service
systemctl set-default graphical.target

for dir in /home/*/; do
    cp -r /etc/skel/. "$dir"
    chown -R "$(stat -c '%U' "$dir"):" "$dir"
done

plymouth-set-default-theme logical-os
dracut -vf

ln -s /usr/bin/doas /usr/bin/sudo
%end
