
import socket, ssl, pprint, time, select


CyberspaceHello = 1357924680
CyberspaceProtocolVersion = 31
ClientProtocolOK		= 10000
ClientProtocolTooOld	= 10001
ClientProtocolTooNew	= 10002

ConnectionTypeUpdates				= 500


def writeUInt32ToSocket(socket, x):
    b = x.to_bytes(4, byteorder='little')
    socket.sendall(b)

def writeStringLengthFirst(socket, str):
    b = bytes(str, 'UTF-8')
    writeUInt32ToSocket(socket, len(b))
    socket.sendall(b)


def readNBytesFromSocket(socket, n):
    remaining = n
    b = bytearray()
    while(remaining > 0):
        chunk = socket.recv(remaining)
        b.extend(chunk)
        remaining -= len(chunk)
    return b

def readUInt32FromSocket(socket):
    b = readNBytesFromSocket(socket, 4)
    return int.from_bytes(b, byteorder='little', signed=False)

def readUInt64FromSocket(socket):
    b = readNBytesFromSocket(socket, 8)
    return int.from_bytes(b, byteorder='little', signed=False)

def readUID(socket):
    return readUInt64FromSocket(socket)

def socketReadable(socket):
    socket_list = [socket]
    read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
    return len(read_sockets) == 1 or len(write_sockets) == 1 or len(error_sockets) == 1


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# require a certificate from the server
conn = ssl.wrap_socket(s
                           #ca_certs="/etc/ca_certs_file",
                           #cert_reqs=ssl.CERT_REQUIRED
                           )
conn.connect(('localhost',  7600))
#conn.connect(('substrata.info',  7600))

print("Connected to localhost.")

writeUInt32ToSocket(conn, CyberspaceHello)
writeUInt32ToSocket(conn, CyberspaceProtocolVersion)
writeUInt32ToSocket(conn, ConnectionTypeUpdates)

writeStringLengthFirst(conn, "") # Write world name
print("Sent hello.")

hello = readUInt32FromSocket(conn)

print('hello: ', repr(hello))

protocol_response = readUInt32FromSocket(conn)
if(protocol_response == ClientProtocolTooOld):
	raise Exception("Client protcol is too old")
elif(protocol_response == ClientProtocolTooNew):
	raise Exception("Client protcol is too new")
elif(protocol_response == ClientProtocolOK):
    print("ClientProtocolOK")
else:
    raise Exception("Invalid protocol version response from server: " + protocol_response);

client_avatar_UID = readUID(conn)


last_send_time = -1000.0 # time.monotonic();

while(1):
    while(socketReadable(conn)):
        print("Socket readable!")
        # Read and handle message(s)
        msg_type = readUInt32FromSocket(conn)
        msg_len = readUInt32FromSocket(conn)

        print("Received msg, type: " + str(msg_type) + ", len: " + str(msg_len))

        if(msg_len < 8):
            raise Exception("Invalid msg len: " + str(msg_len))

        # Read rest of message
        readNBytesFromSocket(conn, msg_len - 8) # We have already read 8 bytes of the message, read the rest.
    else:
        time.sleep(0.1)

        if(time.monotonic() - last_send_time):

            # Send a message to the server
            last_send_time = time.monotonic()

            print("Sending a message to server...")



    

#pprint.pprint(conn.getpeercert())
# note that closing the SSLSocket will also close the underlying socket#
conn.close()

