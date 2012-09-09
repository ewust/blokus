#!/bin/bash


name=`whoami`

# Outputs a certificate (client.crt) and 2048-bit rsa key (client.key)
openssl req -new -x509 -days 365 -nodes -out client.crt \
        -newkey rsa:2048 -keyout client.key \
        -batch -subj "/C=US/ST=MI/L=Ann Arbor/CN=$name"
