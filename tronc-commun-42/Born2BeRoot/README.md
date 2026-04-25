*This project has been created as part of the 42 curriculum by omischle.*

# Born2beRoot

## Description

Born2beRoot is a system administration project that introduces virtualization concepts. The goal is to set up a Debian server inside a virtual machine with strict security policies, including encrypted partitions with LVM, SSH access, firewall configuration, password policies, sudo rules, and a monitoring script.

### Choice of Operating System: Debian

Debian was chosen for its stability, extensive documentation, and beginner-friendly package management. It is the recommended choice for students new to system administration.

### Main Design Choices

- **Partitioning**: Encrypted LVM partitions following the bonus structure, separating `/`, `/home`, `/var`, `/tmp`, `/var/log`, `/srv`, and swap for security and maintainability.
- **Security policies**: Strong password policy (expiration, complexity, history), restricted sudo configuration with logging, SSH on port 4242 only (no root login).
- **User management**: Dedicated user in `user42` and `sudo` groups, enforced password rules via `libpam-pwquality`.
- **Services**: Minimal install — only SSH and UFW, no graphical interface.
- **Bonus — WordPress**: Functional WordPress website using lighttpd, MariaDB, and PHP.
- **Bonus — Additional service**: FTP server (vsftpd) for file transfer to the web server.

### Debian vs Rocky Linux

| Criteria | Debian | Rocky Linux |
|----------|--------|-------------|
| Base | Independent | RHEL-based |
| Package manager | apt/dpkg | dnf/rpm |
| Security module | AppArmor | SELinux |
| Firewall | UFW | firewalld |
| Release cycle | Stable releases (~2 years) | Follows RHEL cycle |
| Learning curve | Easier for beginners | More enterprise-oriented |
| Community | Very large, long history | Growing, RHEL ecosystem |

### AppArmor vs SELinux

| Criteria | AppArmor | SELinux |
|----------|----------|---------|
| Approach | Path-based profiles | Label-based policies |
| Complexity | Simpler to configure | More granular but complex |
| Default on | Debian/Ubuntu | RHEL/Rocky/Fedora |
| Modes | Enforce / Complain | Enforcing / Permissive / Disabled |
| Profiles | Per-application | System-wide mandatory access |

### UFW vs firewalld

| Criteria | UFW | firewalld |
|----------|-----|-----------|
| Interface | Simple CLI | Zone-based CLI/GUI |
| Backend | iptables/nftables | nftables |
| Complexity | Minimal, easy rules | More features, dynamic zones |
| Best for | Simple server setups | Complex network topologies |
| Default on | Debian/Ubuntu | RHEL/Rocky |

### VirtualBox vs UTM

| Criteria | VirtualBox | UTM |
|----------|-----------|-----|
| Platform | Cross-platform | macOS only |
| Architecture | x86/x86_64 | ARM (Apple Silicon) / x86 via QEMU |
| Performance | Native on Intel | Native on ARM, emulated on x86 |
| Disk format | .vdi | .qcow2 |
| Use case | Intel Macs / Linux / Windows | Apple Silicon Macs |

## Instructions

### Prerequisites

- VirtualBox (or UTM on Apple Silicon Mac)
- Debian 12 (Bookworm) netinst ISO
- At least 30GB free disk space

### Installation

1. Create a new virtual machine in VirtualBox/UTM
2. Mount the Debian ISO and install with encrypted LVM partitions (bonus partitioning scheme)
3. Configure SSH on port 4242, UFW firewall, sudo rules, and password policy
4. Copy `monitoring.sh` to `/usr/local/bin/` on the VM
5. Set up cron to run the script every 10 minutes
6. Install and configure WordPress (lighttpd + MariaDB + PHP)
7. Install and configure vsftpd (FTP service)
8. Open additional ports in UFW (80 for HTTP, 21/40000-40005 for FTP)

### Generating the signature

```bash
# macOS (VirtualBox)
shasum /path/to/your_vm.vdi

# macOS (UTM / Apple Silicon)
shasum ~/Library/Containers/com.utmapp.UTM/Data/Documents/your_vm.utm/Images/disk-0.qcow2

# Linux
sha1sum /path/to/your_vm.vdi
```

Paste the resulting hash into `signature.txt` at the root of the repository.

### Monitoring script

The `monitoring.sh` script displays system information every 10 minutes via `wall`:
- OS architecture and kernel version
- Physical and virtual CPU count
- RAM and disk usage
- CPU load, last boot time
- LVM status, TCP connections, logged users
- Network info (IP and MAC)
- Sudo command count

### Bonus — WordPress setup

A functional WordPress website is served using:
- **lighttpd**: Lightweight HTTP server on port 80
- **MariaDB**: Database backend storing WordPress data
- **PHP**: Server-side scripting via PHP-CGI/FastCGI

### Bonus — Additional service: vsftpd

**vsftpd** (Very Secure FTP Daemon) was chosen as the additional service because:
- It provides a practical way to upload files to the web server
- It complements the WordPress setup (theme/plugin uploads)
- It is lightweight, secure by default, and widely used in production servers
- Configured with SSL/TLS encryption and restricted to local users

## Resources

- [Debian Administrator's Handbook](https://debian-handbook.info/)
- [Debian Wiki - LVM](https://wiki.debian.org/LVM)
- [UFW Documentation](https://wiki.debian.org/Uncomplicated%20Firewall%20%28ufw%29)
- [AppArmor Wiki](https://wiki.debian.org/AppArmor)
- [SSH Configuration Guide](https://www.ssh.com/academy/ssh/config)
- [libpam-pwquality manual](https://manpages.debian.org/testing/libpam-pwquality/pam_pwquality.8.en.html)
- [lighttpd Documentation](https://redmine.lighttpd.net/projects/lighttpd/wiki)
- [WordPress Installation Guide](https://developer.wordpress.org/advanced-administration/before-install/howto-install/)
- [MariaDB Documentation](https://mariadb.com/kb/en/documentation/)
- [vsftpd Configuration](https://security.appspot.com/vsftpd.html)

### AI Usage

AI was used to assist with:
- Generating the `monitoring.sh` bash script based on the project requirements
- Drafting this README document and comparison tables
- Understanding configuration syntax for sudoers, PAM, SSH, lighttpd, and MariaDB

All configurations were verified and applied manually on the virtual machine.
