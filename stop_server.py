import os, sys
from lib import config

config.settings.ap_iface = "wlan0mon"
config.settings.net_iface = "eth0"

cmds = [
    "mv /etc/NetworkManager/NetworkManager.conf.backup /etc/NetworkManager/NetworkManager.conf",
    "rm /etc/NetworkManager/NetworkManager.conf",
    "service network-manager restart",
    "/etc/init.d/dnsmasq stop > /dev/null 2>&1",
    "pkill dnsmasq",
    "pkill hostapd",
    "mv /etc/dnsmasq.conf.backup /etc/dnsmasq.conf > /dev/null 2>&1",
    "rm /etc/dnsmasq.hosts > /dev/null 2>&1",
    "iptables --flush",
    "iptables --flush -t nat",
    "iptables --delete-chain",
    "iptables --table nat --delete-chain"
]

print(open("lib/banner", "r+").read())
for i in cmds:
    os.system(i)

print("[*] Traffic have been saved to the 'log' folder!")
print("[*] Sira stopped.")
