#!/usr/bin/python3
import ipaddress

def get_addresses(strnet,usedaddress):
    listaddress = []
    net = ipaddress.ip_network(strnet)
    hostslist = net.hosts()
    for i in list(hostslist):
        if str(i) not in usedaddress:
            listaddress.append(str(i))
    return(listaddress)
