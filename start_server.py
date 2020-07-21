import os
import time
import subprocess, os.path
from lib import config
#filters: "http.request.method == GET or http.request.method == POST"
#tshark: tshark -i wlan0mon -Y "http.request.method == GET or http.request.method == POST" --color -Y "urlencoded-form"

tee = "/usr/bin/tee"
network_config = "[main]\nplugins=keyfile\n\n[keyfile]\nunmanaged-devices=interface-name:" + config.settings.ap_iface  + "\n"

def deploy(path, s):
    xb = open(path, "w+")
    xb.write(s)
    xb.close()


try:
    if os.path.isfile("/etc/NetworkManager/NetworkManager.conf") == False:
        deploy("/etc/NetworkManager/NetworkManager.conf", network_config)
    else:
        pass
    script_path = os.path.dirname(os.path.realpath(__file__))
    script_path = script_path + "/"
    os.system("mkdir " + script_path + "logs > /dev/null 2>&1")
    os.system("chmod 777 " + script_path + "logs")
    network_manager_cfg = "[main]\nplugins=keyfile\n\n[keyfile]\nunmanaged-devices=interface-name:" + config.settings.ap_iface + "\n"
    deploy("/etc/NetworkManager/NetworkManager.conf", network_manager_cfg )

    cmds = [
        "cp /etc/NetworkManager/NetworkManager.conf /etc/NetworkManager/NetworkManager.conf.backup",
        "service network-manager restart",
        "ifconfig " + config.settings.ap_iface + " up",
        "cp /etc/dnsmasq.conf /etc/dnsmasq.conf.backup",
        "rm /etc/dnsmasq.conf > /dev/null 2>&1"
    ]
    for i in cmds:
        os.system(i)

    dnsmasq_file = "# disables dnsmasq reading any other files like /etc/resolv.conf for nameservers\nno-resolv\n# Interface to bind to\ninterface=" + config.settings.ap_iface +"\n#Specify starting_range,end_range,lease_time\ndhcp-range=10.0.0.3,10.0.0.20,12h\n# dns addresses to send to the clients\nserver=8.8.8.8\nserver=10.0.0.1\n"
    deploy("/etc/dnsmasq.conf", dnsmasq_file)

    if config.settings.with_pass == "y":       
        hostapd_file = "interface=" + config.settings.ap_iface +"\ndriver=nl80211\nssid=" + config.settings.ssid + "\nhw_mode=g\nchannel=" + config.settings.channel + "\nmacaddr_acl=0\nauth_algs=1\nignore_broadcast_ssid=0\nwpa=2\nwpa_passphrase=" + config.settings.pass_ap + "\nwpa_key_mgmt=WPA-PSK\nwpa_pairwise=TKIP\nrsn_pairwise=CCMP\n"
    else:
        hostapd_file = "interface=" + config.settings.ap_iface +"\ndriver=nl80211\nssid=" + config.settings.ssid + "\nhw_mode=g\nchannel=" + config.settings.channel + "\nmacaddr_acl=0\nauth_algs=1\nignore_broadcast_ssid=0\n"
    
    os.system("rm /etc/hostapd/hostapd.conf > /dev/null 2>&1")
    deploy("/etc/hostapd/hostapd.conf", hostapd_file)

    tables = [
        "ifconfig " + config.settings.ap_iface +" up 10.0.0.1 netmask 255.255.255.0",
        "iptables --flush",
        "iptables --table nat --flush",
        "iptables --delete-chain",
        "iptables --table nat --delete-chain",
        "iptables --table nat --append POSTROUTING --out-interface " + config.settings.net_iface + " -j MASQUERADE",
        "iptables --append FORWARD --in-interface " + config.settings.ap_iface +" -j ACCEPT",
        "/etc/init.d/dnsmasq stop > /dev/null 2>&1",
        "pkill dnsmasq",
        "dnsmasq",
        "sysctl -w net.ipv4.ip_forward=1 > /dev/null 2>&1"
    ]
    for b in tables:
        os.system(b)

    print("[*] Starting AP on " + config.settings.ap_iface +"...\n")
    os.system("nohup hostapd /etc/hostapd/hostapd.conf >> logs/hostapd.log 2>&1 &")
    print(open("lib/banner", "r+").read())
    print("""Sira Configuration
    -------------------------
    Wifi Name: %s
    Channel: %s
    -------------------------""" % (config.settings.ssid, config.settings.channel))


except:
    print("Oops???")
