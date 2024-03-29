# WIREGUARDs-MANAGER

This software is for manage and deploy some Wireguard VPN in client / Server mode.
It work with a system of sites, each site have his main Wireguard server and can have clients.
Warning, all the wireguard keys (publics and Private) are readable, so please at least encrypt this folder ...
Still in development, a lot of things are still unavailable and some others will be corrected.

#### Can be used from  :
* Debian >= 10
* Ubuntu >= 18.04
* Centos 7 
* Fedora (?) untested

#### Can be deployed on  :

* RouterOs (need at least version 7 for wireguard configuration ...)
* Debian >= 10
* Ubuntu >= 18.04 (Choose debian)
* Edgeos >= v1 and v2 (need Internet on your computer to download packages)

# Dependencies :
Ubuntu / Debian :
```bash
apt install python3-pip wireguard-tools python3-simplejson python3-paramiko git
pip3 install jinja2 scp ipaddress wget
```

Centos 7 :
```bash
yum install elrepo-release epel-release
yum install python3 openssl-devel git python3-devel libevent-devel libffi-devel wireguard-tools

curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs > ./sh.rustup.rs
chmod +x sh.rustup.rs 
./sh.rustup.rs

pip3 install --upgrade pip
pip3 install setuptools-rust wheel Jinja2 paramiko scp wget
```

# Install :
```bash
git clone https://github.com/colynespieu/WIREGUARDs-MANAGER.git
cd WIREGUARDs-MANAGER/
cp conf.json.sample conf.json
```

# Usages :
##### Create a site :
```bash
./generate create_site "sitename"
```

##### Select a site :
```bash
./generate print_sitenames
./generate change_current_site "sitename"
```

##### Add a client (peer) :
```bash
./generate generate-cert "clientname"
./generate generate-conf
```

##### Delete a client (peer) :
```bash
./generate delete-cert "clientname"
./generate generate-conf
```

##### Deploy the server :
```bash
./generate deploy-conf
```

##### Print generated config file :
```bash
/generate print-exported-conf "clientname"
```

##### Print global config :
```bash
./generate print-global-conf
```

##### Interactive mode (for not always use ./generate in your commands):
```bash
./generate interactive
```