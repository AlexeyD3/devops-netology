#!/usr/bin/env python3

import os
import sys
import socket

host_dns_list = ['yandex.ru', 'mail.ru', 'mail.yandex.ru']
ip_host_list = []

while (1==1):
    for host_dns in host_dns_list:
        ip_host_list.append(socket.gethostbyname(host_dns))
