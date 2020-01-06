import socket
import ssl
import thread       


"""
   This just pads the DNS query.

   Parameters:
   ----------
   data : the query being sent

   Returns:
   --------
   paddedQuery : Returns padded query
"""
def dnsPadding(query):

    addLength = "\x00"+chr(len(query))
    paddedQuery = addLength + query
    
    return paddedQuery


"""
    This is where we send our 'new' query to the DNS-overTLS Cloudflare server. 

    Parameters:
    -----------
    tlsSocket : The socket created in tlsConnect(), which allows for a TLS connection
                to the target (in this case the CloudFlare server)
    dnsQuery : This is the DNS query we want to send to CloudFlare.

    Returns:
    --------
    reply : Returns the reply we wait for on the tlsSocket. 
            As usual, we get a (bytes, address) pair.

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

    Our proxy needs to have a TLS connection because we want to be able 
    to query a DoT Server

    Parameters:
    -----------
    DNS : This is the 1.1.1.1 address we are sending our query to.

    Return:
    -------
    wrappedSocket : An SSL Socket tied to the context.
"""
def tlsConnectCloudFlare(DNS):

    # Create a basic socket, which we will wrap.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # This is just in case there is an issue, we don't want to wait forever.
    # In other situations we would adjust this time, or handle a hand differently,
    # but for this challenge I believe this should be good enough.
    sock.settimeout(10)

    # This is for managing settings and certificats as described in the link above.
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations('/etc/ssl/certs/ca-certificates.crt')
  
    # We want to return a wrapped socket. We take our sock above, and wrap it:
    wrappedSocket = context.wrap_socket(sock, server_hostname=DNS)
    wrappedSocket.connect((DNS , 853))
    
    return wrappedSocket


"""
    Here we handle the requests we get/send.
    This does not return anything, it just has to decide if the query is valid,
    then send it off or do whatever next step is (call sendQuery, or sendto(), etc)

    This means we get a result from sendquery(), and
    decide if it is TCP or UDP.

    Print a success message on success

    Parameters:
    -----------
    data :    The data being sent/recieved
    address : Where we are sending
    DNS :     CloudFlare's 1.1.1.1

"""
def handleRequest(data,address,DNS):

    # Connect to Cloudflare Server
    tlsSocket = tlsConnectCloudFlare(DNS) 
    # Get Query Result
    result = sendQuery(tlsSocket, data)

    # Check validity of query, handle appropriately.
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
    for any DNS requests, which we then want to handle by sending to CloudFlare's
    server.
"""
if __name__ == '__main__':

    DNS = "1.1.1.1"        # Target - Cloudflare  
    PORT = 53              # DNS uses TCP Port 53
    HOST = "172.17.0.2"    # This is us, the IP is Dockers default subnet

    # Create the socket and listen.
    # If we have a problem in creating the socket, we get an exception.
    try:
       ssock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
       ssock.bind((HOST, PORT)) 

       while True:
         # Recieve (bytes, address) pair from socket
         data, address = ssock.recvfrom(1024) 

         # Use the recieved data, address, and the above DNS ServerIP to start a new thread
         # Each thread calls the handleRequest(), as each thread is a new request.
         thread.start_new_thread(handleRequest,(data, address, DNS))

    except Exception, e:
        print(e)
        ssock.close()
                  
