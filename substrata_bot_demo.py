
import socket, ssl, pprint, time, select, struct


CyberspaceHello = 1357924680
CyberspaceProtocolVersion = 31
ClientProtocolOK		= 10000
ClientProtocolTooOld	= 10001
ClientProtocolTooNew	= 10002

ConnectionTypeUpdates	= 500

AvatarTransformUpdate	= 1002

ChatMessageID			= 2000

ParcelCreated			= 3100

InfoMessageID			= 7001
ErrorMessageID			= 7002

TimeSyncMessage			= 9000


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

def socketReadable(socket, timeout_s):
	socket_list = [socket]
	read_sockets, write_sockets, error_sockets = select.select(socket_list, [], socket_list, timeout_s)
	return len(read_sockets) == 1 or len(error_sockets) == 1



class BufferIn:
	def __init__(self, data_byte_array_):
		self.data_byte_array = data_byte_array_
		self.read_index = 0

	def readUInt32(self):
		x = int.from_bytes(self.data_byte_array[self.read_index : self.read_index + 4], byteorder='little', signed=False)
		self.read_index += 4
		return x

	def readDouble(self):
		bytes = self.data_byte_array[self.read_index : self.read_index + 8]
		x = struct.unpack('<d', bytes)[0]  # '<' specifies little-endian byte order.  unpack returns a tuple, get zeroth element of it.
		self.read_index += 8
		return x

	def readStringLengthFirst(self):
		strlen = self.readUInt32()
		string_bytes = self.data_byte_array[self.read_index : self.read_index + strlen]
		self.read_index += strlen
		return string_bytes.decode('UTF-8')



plain_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

conn = ssl.wrap_socket(plain_socket)
conn.connect(('localhost',  7600))
#conn.connect(('substrata.info',  7600))

print("Connected.")

writeUInt32ToSocket(conn, CyberspaceHello)
writeUInt32ToSocket(conn, CyberspaceProtocolVersion)
writeUInt32ToSocket(conn, ConnectionTypeUpdates)

writeStringLengthFirst(conn, "") # Write world name

hello = readUInt32FromSocket(conn)

print('Received hello: ', str(hello))

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


last_send_time = -1000.0

while(1):
	while(socketReadable(conn, 0.1)): # timeout_ = 0.1
		# print("Socket readable!")
		# Read and handle message(s)
		msg_type = readUInt32FromSocket(conn)
		msg_len = readUInt32FromSocket(conn)

		if(msg_len < 8):
			raise Exception("Invalid msg len: " + str(msg_len))

		# Read rest of message
		msg_body = readNBytesFromSocket(conn, msg_len - 8) # We have already read 8 bytes of the message, read the rest.
		buffer_in = BufferIn(msg_body)

		if(msg_type == TimeSyncMessage):
			
			global_time = buffer_in.readDouble()

			print("Received TimeSyncMessage: global_time: " + str(global_time))
		elif(msg_type == ChatMessageID):
		
			name = buffer_in.readStringLengthFirst()
			msg  = buffer_in.readStringLengthFirst()

			print("Received ChatMessage: '" + name + "': '" + msg +"'")
		elif(msg_type == AvatarTransformUpdate):
			print("Received AvatarTransformUpdate")
		elif(msg_type == ParcelCreated):
			print("Received ParcelCreated")
		elif(msg_type == InfoMessageID):
			msg = buffer_in.readStringLengthFirst()
			print("Received InfoMessage: " + msg)
		elif(msg_type == ErrorMessageID):
			msg = buffer_in.readStringLengthFirst()
			print("Received ErrorMessage: " + msg)
		else:
			print("Received msg, type: " + str(msg_type) + ", len: " + str(msg_len))

	else: # Else if socket was not readable:
		time.sleep(0.1)

		if(time.monotonic() - last_send_time > 2.0):

			# Send a message to the server
			last_send_time = time.monotonic()

			print("TODO: Sending a message to server...")



# conn.close()
