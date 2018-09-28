#!/bin/bash
iptables -I INPUT -p tcp --dport 9999 -j ACCEPT
cd /root/server && python serve.py