#!/bin/bash
shopt -s extglob

rpmbuild="$HOME/rpmbuild"

if [ ! -d "$rpmbuild" ] || [ -z "$(ls -A "$rpmbuild")" ]; then
    rpmdev-setuptree

    cp logical-os-release/logical-os-release.spec ~/rpmbuild/SPECS/logical-os-release.spec
    cp logical-os-logos/logical-os-logos.spec ~/rpmbuild/SPECS/logical-os-logos.spec

    tar -czf logical-os-logos-42.0.1.tar.gz -C logical-os-logos logical-os-logos-42.0.1/

    cp -r logical-os-release/!(*.spec) ~/rpmbuild/SOURCES/
    mv logical-os-logos-42.0.1.tar.gz ~/rpmbuild/SOURCES/logical-os-logos-42.0.1.tar.gz

    rpmbuild -ba ~/rpmbuild/SPECS/logical-os-release.spec
    rpmbuild -ba ~/rpmbuild/SPECS/logical-os-logos.spec
fi

createrepo_c "$HOME/rpmbuild/RPMS/noarch"

cat > /tmp/local.repo << EOF
[local]
name=Logical OS branding
baseurl=file://$HOME/rpmbuild/RPMS/noarch
enabled=1
gpgcheck=0
EOF

sudo cp /tmp/local.repo /etc/yum.repos.d/logical-branding.repo
