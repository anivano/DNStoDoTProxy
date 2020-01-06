"""

N26 Challenge: 
Our applications don't handle DNS-over-TLS by default. Your task is to design and create a
simple DNS to DNS-over-TLS proxy that we could use to enable our application to query a
DNS-over-TLS server.

1 - We get a DNS query on port tcp/53
2 - 
3 - This query is now sent to the DNS-over-TLS server
"""

#import binascii
import socket
import ssl
#import sys
import thread       

"""
   This just gets the DNS query and adds length to it.
"""
def dnsPadding(data):

    # Adding length gives TCP format
    addLength = "\x00"+chr(len(data))
    paddedQuery = addLength + data
    
    return paddedQuery

"""

    This is given the tlsSocket connected over cloudfare,
    and the dns_query we wish to send to cloudfare.

    First we pad the dnsQuery, then we send it.
    Get reply, and return it.

    This is where we send our 'new' query to the DNS-overTLS Cloudfare server. 

"""
def sendQuery(tlsSocket, dnsQuery):

    # First we pad the DNS query we want to send
    tcpQuery = dnsPadding(dnsQuery)

    # Send query over cloudFare socket created
    tlsSocket.send(tcpQuery)

    # Get reply in form of (bytes, address) pair
    reply = tlsSocket.recv(1024)

    return reply

"""
Here we want to create a TLS connection to the cloudflare server
mentioned in the challenge description.

This is why we use the IP addess: 1.1.1.1

Our proxy needs to have a TLS connection because we want to be able to query a DoT Server

Input: DNS Address
Return: Wrapped Socket

We are given a DNS address,
- Create a socket
- get SSLContext,
- wrap this SSLContext in 

"""
def tlsConnectCloudFlare(DNS):

    # Create a basic socket, which we will wrap.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # This is just in case there is an issue, we don't want to wait forever.
    # In other situations we would adjust this time, or handle a hand differently,
    # but for this challenge I believe this should be good enough.
    sock.settimeout(10)

    # found here: https://docs.python.org/3/library/ssl.html
    # This is for managing settings and certificats as described in the link above.
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations('/etc/ssl/certs/ca-certificates.crt')
  
    # We want to return a wrapped socket. We take our sock above, and wrap it below:
    wrappedSocket = context.wrap_socket(sock, server_hostname=DNS)
    wrappedSocket.connect((DNS , 853))
    
    #print(wrappedSocket.getpeercert())
    
    return wrappedSocket


"""

Here we handle the requests. 
1 - Create TLS connection to cloudfare DoT server
2 - Check for UDP or TCP
3 - Based on if we got a UDP or TCP request, take the appropriate acction. :)
4 - print success on success

This means we get a result from sendquery(), and
decide if it is TCP or UDP.
- TCP Handling is the base requirement, UDP is a plus, and it does not seem to work smoothly yet.

"""
def handleRequest(data,address,DNS):

    # Connect to Cloudfare Server
    tlsSocket = tlsConnectCloudFlare(DNS) 
    # Get Query Result
    result = sendQuery(tlsSocket, data)

    # If qury is valid,
    if result:
       rcode = result[:6].encode("hex")
       rcode = str(rcode)[11:]
       if (int(rcode, 16) == 1):
          print ("Invalid Query")
       else:
          message = result[2:]
          ssock.sendto(message,address)
          print ("SUCCESS")   
    else:
       print ("Invalid Query")


"""

The goal of this is to just create a basic socket, and listen on port tcp/53
for any DNS requests.
"""

if __name__ == '__main__':

    # I'm not sure, but I believe it would be better to create an option
    # for these to not be hardcoded. Perhaps we want to change some of these
    # for whatever reason?
    # In future - maybe through sys ARGS[] we can set the below things.
    DNS = "1.1.1.1"        # Target 
    PORT = 53              # Listen Port, 53 as specified in the Doc.
    HOST = "172.17.0.2"   # Host IP - We set this up with Docker.

    # Create the socket and listen.
    try:
       # Create socket. 
       # We use SOCK_DGRAM to allow TCP and UDP usage. 
       # AF_INET is for Internet Address family IPv4
       ssock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 

       # bind socket to port so we can listen on it
       ssock.bind((HOST, PORT)) 

       while True:
         # Recieve (bytes, address) pair from socket
         # I called the bytes = data
         data, address = ssock.recvfrom(1024) 
         # Use the recieved data, address, and the above DNS to start a new thread
         # Each thread calls the handleRequest() because each thread is a request
         thread.start_new_thread(handleRequest,(data, address, DNS))

    # If we find an exception, print the error and then close the socket.
    except Exception, e:
        print("HERE 1")
        print(e)
        ssock.close()
                  
