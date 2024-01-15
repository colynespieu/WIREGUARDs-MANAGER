# WIREGUARDs-MANAGER

#### Can be installed on  :
* Debian >= 10 
* Ubuntu >= 18.04
* Centos / Fedora (?) untested

#### Can be deployed on  :

* RouterOs need at least version 7 for wireguard configuration ...
* Debian >= 10
* Ubuntu >= 18.04 (type debian)

# Dependencies :
Ubuntu / Debian :
```bash
apt install python3-pip wireguard-tools python3-simplejson python3-paramiko
pip3 install jinja2 scp ipaddress
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

##### Deploy the master :
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

##### Interactive mode :
```bash
./generate print-global-conf
```