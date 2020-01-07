# DNS to DNS-over-TLS proxy #  

The task is to design and create a simple DNS to DNS-over-TLS proxy that could be used to enable our application to query a DNS-over-TLS server.  

Here is what this proxy does:   
- gets plain text DNS requests from the host, 
- redirects the query to a DNS server that supports TLS (in this case I used CloudFlare's 1.1.1.1),
- sends replies from CloudFlare back to the client.

## Requirements ##  

A working example of a DNS to DNS-over-TLS proxy that can: 
1. Handle at least one DNS query, and give a result to the client.   
2. Work over TCP and talk to a DNS-over-TLS server that works over TCP (e.g: Cloudflare).   

Bonus:  
* Allow multiple incoming requests at the same time  
* Also handle UDP requests, while still querying TCP on the other side  
* Any other improvements you can think of! 

## My Set-up ##  

Run the below to build/run docker.  

```
docker build -t dot-proxy-server .
docker run -it dot-proxy-server
```

Now we want to check that all works as expected!
So for me it looked like this:  

Using the dig command, run in a second terminal:  
```
anastasija@Babbage:~$ dig @172.17.0.2 -p 53 google.com   
```

Which will get you the following in the terminal it's run in:  

```
; <<>> DiG 9.11.3-1ubuntu1.11-Ubuntu <<>> @172.17.0.2 -p 53 google.com
; (1 server found)
;; global options: +cmd
;; Got answer:
;; ->\>HEADER<<- opcode: QUERY, status: NOERROR, id: 57296
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 1452
;; QUESTION SECTION:
;google.com.			IN	A

;; ANSWER SECTION:
google.com.		153	IN	A	172.217.3.206

;; Query time: 59 msec
;; SERVER: 172.17.0.2#53(172.17.0.2)
;; WHEN: Mon Jan 06 11:44:44 PST 2020
;; MSG SIZE  rcvd: 55  
```

And you will also see a SUCCESS message in the terminal where we ran the docker commands.  

## Improvements ##  

### Security Concerns ###
Imagine this proxy being deployed in an infrastructure. What would be the security concerns you would raise?  

- No 'packet checks' are performed to validate what we are forwarding to CloudFlare, or the reply we get from CloudFlare.  
- We are using port 53 (as specified) which means root privilages are required.
- We don't check that the remote server is trustworthy. In this case, I'm using CloudFlare, but if this were made to be able to reach other servers, we would want to perform some checks such as only allowing certain servers, or servers meeting certain requirements.

### Microservice Environment ###
How would you integrate that solution in a distributed, microservices-oriented and containerized architecture?  

- DoT can provides a security layer to hide sensitive information.
- This proxy could be deployed as a service, and then microservices within the environment send their DNS requests to the proxy service.

### Other Improvements ###
What other improvements do you think would be interesting to add to the project? 
- The Cloudfare IP I used here shouldn't be hardcoded, it could be useful to give the user the freedom to specify a different server. This could mean adding Google's DoT server as well as an option (for example)
- Make it easier to use for users. This would include things such as better error messages, better output to terminal to explain what is happening.
- I used the default docker subnet, but there could be situations where we do not want this, and may want to create a different subnet if the default one is used for something else. 
- In this project I don't pay attention to who is sending the requests. If this could be tracked, then we can block certain IP's from sending requests. Reasons for this may include: we only want specific IPs to send requests, or we want to prevent one IP from sending too many requests.  
- To save time, we could somehow make it so that re-establishing a connection with a client does not re-quire a re-handshake. 
- There could be stricter sender/reciever limitations for the requests.


## Resources ##  

* [Docker](https://docker.com)
* [Docker Subnets](https://docs.docker.com/engine/reference/commandline/network_create/):  I used the default subnet of 172.17.0.2, so I did not need to worry about creating a new one, but this is what I refrenced when reading about docket subnets.
* [Explanation of SSL, certs, and context](https://docs.python.org/3/library/ssl.html)
* [Wrapping Sockets](https://docs.python.org/3/library/ssl.html#ssl.SSLContext.wrap_socket)
* [Padding (About)](https://edns0-padding.org/implementations/)
* This was useful for review mainly: [DNS Encryption Explained](https://blog.cloudflare.com/dns-encryption-explained/)
* [dig command](https://www.tecmint.com/10-linux-dig-domain-information-groper-commands-to-query-dns/)
