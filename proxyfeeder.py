"""Importing modules"""
import os
import socket
from threading import Thread
import urllib
import urllib.request

import pika
import requests
import time

ENV = "dev"
SPAM = 0

def _debug(message):
    print(message)
    return True

def _spam(message):
    if SPAM!=0:
        print(message)
    return True

def _store_locally(pip):
    try:
        with open ("proxy.txt", "a", encoding="utf-8") as f:
            f.write(str(pip) + "\r\n")
            f.close()
    except Exception as e:
#        pass
        print(e)
    return True


def publish_pip(pip):
    """
    publish a message to MQ server
    """

    try:
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        parameters = pika.ConnectionParameters(RABBITMQ_SERVER,
                                       5672,
                                       '/',
                                       credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        channel.queue_declare(queue='proxy')

        channel.basic_publish(exchange='', routing_key='proxy', body=pip)
        print(" [x] "+pip)
        connection.close()
    except Exception as e:
        print(e)
        print("MQ failed, saved locally")


def what_is_my_ip(*args):
    """
    returns external IP if no argument
    IP when using proxy when 1 argument as proxy
    -1 in case of error
    """
    try:
        if len(args) == 1:
            #_debug(args[0])
            proxy_handler = urllib.request.ProxyHandler({'https': args[0]})
            opener = urllib.request.build_opener(proxy_handler)
        else:
            opener = urllib.request.build_opener()

        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        with urllib.request.urlopen('https://icanhazip.com',
            timeout=10) as sock:
#        sock = urllib.request.urlopen(
#            'https://icanhazip.com',
#            timeout=10)  # change the url address here
            ip = sock.read()
        return ip.decode("utf-8")
    except Exception as e:
        _spam(e)
        return -1


def check_proxy(pip):
    """
    this is called every time from threaded_proxy
    """
    try:
        myip = what_is_my_ip()
        testip = what_is_my_ip(pip)
        # do processing only if proxy works via icanhazip.com and result is not
        # -1
        if ((myip == testip) or (str(myip) == "-1") or (str(testip) == "-1")):
        #_debug("Some error checking via icanhazip, myip: " +str(myip)+" test_ip: "+str(testip))
            return -1

        _spam("go on testing myip: " + str(myip) +\
            " test_ip: " + str(testip))
        _debug(pip)
        _store_locally(pip)

        if MODE=="RABBITMQ":
            publish_pip(pip)


    except Exception as e:
        _spam(e)
     #       print(e)
#        pass
        return -1
    return 0

def threaded_proxy():
    """
    starting threads
    """
    try:
        socket.setdefaulttimeout(10)
        response = requests.get(
            'https://api.proxyscrape.com/?request=displayproxies&proxytype=https&timeout=7000&anonymity=elite&ssl=yes')
        q = []
        for line in response.text.splitlines():
            q.append(line)
    #    _debug (q)
        proxies = q
        threads = []
        for proxy in proxies:
            thread = Thread(target=check_proxy, args=(proxy.strip(), ))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()
    except Exception as e:
#        pass
        print(e)

RABBITMQ_SERVER=os.getenv("RABBITMQ_SERVER")
RABBITMQ_USER=os.getenv("RABBITMQ_USER")
RABBITMQ_PASSWORD=os.getenv("RABBITMQ_PASSWORD")

if RABBITMQ_PASSWORD is None or RABBITMQ_USER is None or RABBITMQ_SERVER is None:
    MODE="STANDALONE"
    print("no config, mode STANDALONE")
else:
    print ("aceepted rabbit, mode RABBITMQ")
    MODE="RABBITMQ"
while True:
    threaded_proxy()
    time.sleep(60)
    print ("sleeping 1m")
