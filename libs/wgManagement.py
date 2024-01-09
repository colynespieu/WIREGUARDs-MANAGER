from warnings import filterwarnings
filterwarnings("ignore")
import os,subprocess,json,shutil,paramiko,ipaddress,re,io
from jinja2 import Environment, FileSystemLoader
import ipadds

class wgManagement:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))+"/../"
        self.conffile = self.base_path+"conf.json"
        self.certs_path = self.base_path+"certs/"
        self.sites_path = self.base_path+"sites/"
        self.templates_path = self.base_path+"templates/"
        self.exports_path = self.base_path+"exports/"
        self.sitename = self.get_current_sitename()

    def generate_wireguard_keys(self):
        privkey = subprocess.check_output("wg genkey", shell=True).decode("utf-8").strip()
        pubkey = subprocess.check_output(f"echo '{privkey}' | wg pubkey", shell=True).decode("utf-8").strip()
        return (privkey, pubkey)

    def json_file_read(self,filepath):
        with open(filepath, "r") as jsonfile:
            toreturn = json.loads(jsonfile.read())
        return(toreturn)
    
    def json_file_save(self,filepath,value):
        with open(filepath, "w") as jsonfile:
            json.dump(value, jsonfile,indent = 4)

    def get_current_sitename(self):
        with open(self.conffile, "r") as jsonfile:
            toreturn = json.loads(jsonfile.read())["site"]
        return(toreturn)

    def set_current_sitename(self,sitename):
        with open(self.conffile, "r") as jsonfile:
            gconf = json.loads(jsonfile.read())
        gconf["site"]=sitename
        with open(self.conffile, "w") as jsonfile:
            json.dump(gconf, jsonfile,indent = 4)

    def get_sitetemplate(self):
        with open(f"{self.templates_path}site_config.json", "r") as jsontemplatefile:
            gconf = json.loads(jsontemplatefile.read())
        return(gconf)
    
    def create_site(self,gconf,sitename):
        self.sitename = sitename
        os.mkdir(f"{self.certs_path}{sitename}")
        os.mkdir(f"{self.exports_path}{sitename}")
        with open(f"{self.sites_path}/{sitename}.json", "w") as jsonfile:
            json.dump(gconf, jsonfile,indent = 4)
        pass

    def delete_site(self,sitename):
        self.sitename = sitename
        shutil.rmtree(f"{self.certs_path}{sitename}")
        shutil.rmtree(f"{self.exports_path}{sitename}")
        os.remove(f"{self.sites_path}/{sitename}.json")
        pass

    def pass_command_ssh(self,username,password,host,port,command):
        try:
            sshClient = paramiko.SSHClient()
            sshClient.load_host_keys('~/.ssh/known_hosts')
            sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshClient.connect(host, port=port, username=username, password=password, allow_agent=False,look_for_keys=False)
            stdin,stdout,stderr = sshClient.exec_command(command)
            toreturn = stdout.read().decode()
        finally:
            sshClient.close()
        return(toreturn)

    def generate_wireguard_cert(self,certname):
        if not os.path.exists(f"{self.certs_path}{self.sitename}/{certname}.json"):
            privkey,pubkey = self.generate_wireguard_keys()
            privpubarray={"private_key":privkey,"public_key":pubkey}
            self.json_file_save(f"{self.certs_path}{self.sitename}/{certname}.json",privpubarray)
        else:
            print(f"File for cert '{certname}' already exist !")
            return
        
    def delete_wireguard_cert(self,certname):
        if os.path.exists(f"{self.certs_path}{self.sitename}/{certname}.json"):
            os.remove(f"{self.certs_path}{self.sitename}/{certname}.json")
        else:
            print(f"File for cert '{certname}' don't exist !")
            return
        
    def add_wireguard_host(self,host):
        site_values = self.json_file_read(f"{self.sites_path}/{self.sitename}.json")
        if "used_ips" in site_values:
            used_ip_list = []
            for ips in site_values["used_ips"]:
                used_ip_list.append(ips)
                if site_values["used_ips"][ips] == host:
                    print(f"Cert '{host}' already exist !")
                    return
        host_ip = ipadds.get_addresses(site_values["subnet"],used_ip_list)[0]
        site_values["used_ips"][host_ip]=host
        self.json_file_save(f"{self.sites_path}/{self.sitename}.json",site_values)

    def del_wireguard_host(self,host):
        site_values = self.json_file_read(f"{self.sites_path}/{self.sitename}.json")
        todel = ""
        if "used_ips" in site_values:
            for i in site_values["used_ips"]:
                if (site_values["used_ips"][i] == host):
                    todel=i
        site_values["used_ips"].pop(todel, None)
        self.json_file_save(f"{self.sites_path}/{self.sitename}.json",site_values)

    def deploy_wireguard_configuration_debian(self,password):
        pass

    

    def deploy_wireguard_configuration_routeros(self,password):
        site_values = self.json_file_read(f"{self.sites_path}/{self.sitename}.json")
        cert_values = self.json_file_read(f"{self.certs_path}/{self.sitename}/{site_values['server']['name']}.json")
        username,host,port = site_values["server"]["type_info"]["ssh_user"],site_values["server"]["IP"],site_values["server"]["type_info"]["ssh_port"]
        command = "/interface/wireguard/print detail"
        interfaces_wireguard_print = self.pass_command_ssh(username,password,host,port,command)
        command = f"/interface/wireguard/peers/print detail where interface=\"{site_values['server']['type_info']['interface_name']}\""
        peers_wireguard_print = self.pass_command_ssh(username,password,host,port,command)
        status=False
        for interface_wireguard_print in interfaces_wireguard_print.split("\r\n\r\n"):
            if self.find_arg_routeros_print(interface_wireguard_print,"name",site_values["server"]["type_info"]["interface_name"]):
                status=True
                islport = self.find_arg_routeros_print(interface_wireguard_print,"listen-port",site_values["server"]["port"])
                isprkey = self.find_arg_routeros_print(interface_wireguard_print,"private-key",cert_values["private_key"])
                ispukey = self.find_arg_routeros_print(interface_wireguard_print,"public-key",cert_values["public_key"])
                if (islport and isprkey and ispukey):
                    listactivecert = []
                    for peer_wireguard in peers_wireguard_print.split("\r\n\r\n"):
                        peer_exist = False
                        for cert in site_values["used_ips"]:
                            site_cert = self.json_file_read(f"{self.certs_path}/{self.sitename}/{site_values['used_ips'][cert]}.json")
                            if self.find_arg_routeros_print(peer_wireguard,"public-key",site_cert["public_key"]):
                                peer_exist = cert
                                isaddr = self.find_arg_routeros_print(peer_wireguard,"allowed-address",f"{cert}/32")
                                if (not isaddr):
                                    command = f"/interface/wireguard/peers/set allowed-address={cert}/32 [/interface/wireguard/peers/find public-key=\"{site_cert['public_key']}\"]"
                                    self.pass_command_ssh(username,password,host,port,command)
                        if (not peer_exist and peer_wireguard):
                            command = f"/interface/wireguard/peers/remove number={peer_wireguard.split()[0]}"
                            self.pass_command_ssh(username,password,host,port,command)
                        elif (peer_exist and peer_wireguard):
                            listactivecert.append(peer_exist)
                    for cert in site_values["used_ips"]:
                        if (site_values["used_ips"][cert] != site_values["server"]["name"] and cert not in listactivecert):
                            site_cert = self.json_file_read(f"{self.certs_path}/{self.sitename}/{site_values['used_ips'][cert]}.json")
                            command = f"/interface/wireguard/peers/add allowed-address={cert}/32 public-key=\"{site_cert['public_key']}\" interface={site_values['server']['type_info']['interface_name']}"
                            self.pass_command_ssh(username,password,host,port,command)
                elif(not status):
                    status="toupdate"
            elif(not status):
                status="toadd"
        if (status == "toupdate"):
            command=f"/interface/wireguard/set listen-port={site_values['server']['port']} private-key=\"{cert_values['private_key']}\" numbers={site_values['server']['type_info']['interface_name']}"
            self.pass_command_ssh(username,password,host,port,command)
            self.deploy_wireguard_configuration_routeros(password)
            return
        elif(status == "toadd"):
            command=f"/interface/wireguard/add listen-port={site_values['server']['port']} private-key=\"{cert_values['private_key']}\" name={site_values['server']['type_info']['interface_name']}"
            self.pass_command_ssh(username,password,host,port,command)
            self.deploy_wireguard_configuration_routeros(password)
            return
        serveur_wg_private_ip = self.get_server_private_ip(site_values)
        command=f"/ip/address/print detail where interface ={site_values['server']['type_info']['interface_name']} and address=\"{serveur_wg_private_ip}/{site_values['subnet'].split('/')[1]}\""
        ip_addr_list_print = self.pass_command_ssh(username,password,host,port,command)
        for ip_addr_print in ip_addr_list_print.split("\r\n\r\n"):
            if not self.find_arg_routeros_print(ip_addr_print,"address",f"{serveur_wg_private_ip}/{site_values['subnet'].split('/')[1]}"):
                command=f"/ip/address/add interface={site_values['server']['type_info']['interface_name']} address=\"{serveur_wg_private_ip}/{site_values['subnet'].split('/')[1]}\""
                self.pass_command_ssh(username,password,host,port,command)

    def find_arg_routeros_print(self,printv,valuename,value):
        for arg in printv.split():
            if ("=" in arg) and (arg.split("=")[0] == valuename):
                if (("=" in arg) and (arg.split("=")[1] == value) or (re.findall('"([^"]*)"', arg)[0] == value)) :
                    return(True)
        return(False)

    def get_server_private_ip(self,site_values):
        for ip_addr_wg in site_values["used_ips"]:
            if site_values["server"]["name"] == site_values["used_ips"][ip_addr_wg]:
                return(ip_addr_wg)
    

    def generate_conf_files(self):
        site_values = self.json_file_read(f"{self.sites_path}/{self.sitename}.json")
        serv_cert_values = self.json_file_read(f"{self.certs_path}/{self.sitename}/{site_values['server']['name']}.json")
        for file in (os.listdir(f"{self.exports_path}{self.sitename}/")):
            os.remove(f"{self.exports_path}{self.sitename}/{file}")
        env = Environment(loader=FileSystemLoader(self.templates_path))
        list_peers = []
        for cert in site_values["used_ips"]:
            if (site_values["used_ips"][cert] != site_values["server"]["name"]):
                address = (f"{cert}/{site_values['subnet'].split('/')[1]}")
                client_cert_values = self.json_file_read(f"{self.certs_path}/{self.sitename}/{site_values['used_ips'][cert]}.json")
                allowips=site_values['subnet']
                for ip in site_values["client_allowed_ip"]:
                    allowips = f"{allowips},{ip}"
                values={"address":address,"privateKey":client_cert_values["private_key"],"publicKey":serv_cert_values["public_key"],"allowIPs":allowips,"serverIP":site_values["server"]["IP"],"serverPort":site_values["server"]["port"]}
                list_peers.append({"ip":cert,"public_key":client_cert_values["public_key"]})
                template = env.get_template("wireguard_client.conf.j2")
                with io.open(f"{self.exports_path}/{self.sitename}/{site_values['used_ips'][cert]}.conf", 'w',encoding='utf8') as f:
                    f.write(template.render(value=values))
        address = (f"{site_values['server']['IP']}/{site_values['subnet'].split('/')[1]}")
        values={"address":address,"privateKey":serv_cert_values["private_key"],"port":site_values["server"]["port"],"peers":list_peers}
        template = env.get_template("wireguard_server.conf.j2")
        with io.open(f"{self.exports_path}/{self.sitename}/{site_values['server']['name']}.conf", 'w',encoding='utf8') as f:
            f.write(template.render(value=values))
