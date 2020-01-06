### DNS to DNS-over-TLS proxy ###  

Your task is to design and create a simple DNS to DNS-over-TLS proxy that we could use to enable our application to query a DNS-over-TLS server.  

## Requirements ##  

A working example of a DNS to DNS-over-TLS proxy that can: 
1. Handle at least one DNS query, and give a result to the client.   
2. Work over TCP and talk to a DNS-over-TLS server that works over TCP (e.g: Cloudflare).   

Bonus:  
* Allow multiple incoming requests at the same time  
* Also handle UDP requests, while still querying tcp on the other side  
* Any other improvements you can think of! 


## Steps ## 

1. Get DNS Query.  
2. Pad it.  
3. Send it to the (Cloudfare) server  



## My Set-up ##  

Run the below to build/run docker.  

```
docker build -t dot-proxy-server .
docker run -it dot-proxy-server
```

Now to check that this is successful, open a new terminal and do the following:  
```
docker exec -it {containerID} nslookup example.com
```

So for me it looked like this:  

In one terminal I ran this:  
```
anastasija@Babbage:~/Documents/Coding/proxy$ sudo docker exec -it b43f762424f6 nslookup chess.com  
```

Andin the other terminal I got this result:  
```
anastasija@Babbage:~/Documents/Coding/proxy$ sudo docker run -it dns-server  
SUCCESS
```

We can also use the dig command, also run in the second terminal:  
```
anastasija@Babbage:~/Documents/Coding/proxy$ dig @172.17.0.2 -p 53 google.com   
```

Which will get you:  

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


## Improvements ##  
1. Imagine this proxy being deployed in an infrastructure. What would be the security concerns you would raise?  

The usual TLS concerns...



2. How would you integrate that solution in a distributed, microservices-oriented and containerized architecture?  

3. What other improvements do you think would be interesting to add to the project? 
- The Cloudfare IP I used here shouldn't be hardcoded, perhaps in future, it would be useful to give the user the freedom to specify a different server. This could mean adding Google's DoT server as well as an option (for example)
- Make it easier to use for users. This would include things such as better error messages, better output to terminal to explain what is happening.
- The default subnet used by Docker; maybe that should be changeable by the user.  
- In this project I don't pay attention to who is sending the requests. If this could be tracked, then we can block certain IP's from sending requests. Reasons for this may include: we only want specific IPs to send requests, or we want to prevent one IP from sending too many requests. Although I'm not completely sure what other reasons there could.  
- I suspect re-establishing a connection with a client could be time-consuming. Not sure how but perhaps somehow check which client is sending the request and see if the TLS Handshake with this client has previously been completed and somehow use this fact to not have to 're-handshake'?
-  
