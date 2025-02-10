#
# substrata_chatbot_demo.py
# -------------------------
#
# Creates a user avatar, logs in, walks in circles, and says "Beep Boop" every 5 seconds.
# You could extend this example to make the bot chat to a user, follow a user around or whatever.
# See https://www.youtube.com/watch?v=j-ja0_GcB4s for a video of it.
# 
#
# Copyright Glare Technologies 2025 - 
#


# NOTE: will need to have requests module installed.

import socket, ssl, pprint, time, select, struct, math, configparser, requests, datetime

from lib.BufferIn import BufferIn
from lib.BufferOut import BufferOut
from lib.BasicTypes import Vec3d, Vec3f, Colour3f, Matrix2f, TimeStamp, readColour3fFromStream, readMatrix2fFromStream, readVec3fFromStream, readVec3dFromStream, readTimeStampFromStream
from lib.WorldMaterial import WorldMaterial
from lib.WorldObject import WorldObject
from lib.Avatar import Avatar
from lib.Protocol import Protocol



#------------------------- Define some misc. functions -------------------------
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
		if(len(chunk) == 0):
			raise Exception("Socket was closed gracefully by remote host.")
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

def writeUID(out_stream, uid):
	out_stream.writeUInt64(uid)

def socketReadable(socket, timeout_s):
	socket_list = [socket]
	read_sockets, write_sockets, error_sockets = select.select(socket_list, [], socket_list, timeout_s)
	if(len(error_sockets) == 1):
		raise Exception("Socket excep")
	return len(read_sockets) == 1




#------------------------- Read username and password from disk -------------------------
config = configparser.ConfigParser()
config.read('config.txt')
username = config['credentials']['username']
password = config['credentials']['password']
server_hostname = config['connection']['server_hostname']

if username is None:
	raise Exception("Could not find 'username' in config file.")
if password is None:
	raise Exception("Could not find 'password' in config file.")

print("Using username '" + username + "'")


#------------------------- Connect to server -------------------------
plain_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

plain_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)

print("Connecting to server '" + server_hostname + "'...")

conn = ssl.wrap_socket(plain_socket)
conn.connect((server_hostname,  7600))

print("Connected to server '" + server_hostname + "'.")


#------------------------- Do the Substrata protocol with server -------------------------
writeUInt32ToSocket(conn, Protocol.CyberspaceHello)
writeUInt32ToSocket(conn, Protocol.CyberspaceProtocolVersion)
writeUInt32ToSocket(conn, Protocol.ConnectionTypeUpdates)

writeStringLengthFirst(conn, "") # Write world name

hello = readUInt32FromSocket(conn)

print('Received hello: ', str(hello))

protocol_response = readUInt32FromSocket(conn)
if(protocol_response == Protocol.ClientProtocolTooOld):
	raise Exception("Client protcol is too old")
elif(protocol_response == Protocol.ClientProtocolTooNew):
	raise Exception("Client protcol is too new")
elif(protocol_response == Protocol.ClientProtocolOK):
	print("ClientProtocolOK")
else:
	raise Exception("Invalid protocol version response from server: " + protocol_response);

# Read server protocol version
server_protocol_version = readUInt32FromSocket(conn)
print('server_protocol_version: ', str(server_protocol_version))

client_avatar_UID = readUID(conn)
print("Received client_avatar_UID: " + str(client_avatar_UID))


#------------------------- Send login message -------------------------
login_buf = BufferOut()
login_buf.writeUInt32(Protocol.LogInMessage)
login_buf.writeUInt32(0) # will be updated with length of message
login_buf.writeStringLengthFirst(username)
login_buf.writeStringLengthFirst(password)
login_buf.updateLengthField()
login_buf.writeToSocket(conn)



avatar = Avatar()
avatar.pos = Vec3d(5, 5, 2)


#------------------------- Send create avatar message -------------------------
av_buf = BufferOut()
av_buf.writeUInt32(Protocol.CreateAvatar)
av_buf.writeUInt32(0) # will be updated with length of message
avatar.writeToStream(av_buf)
av_buf.updateLengthField()
av_buf.writeToSocket(conn)


#------------------------- Start main loop -------------------------
last_send_time = -1000.0
last_chat_time = -1000.0
initial_time = time.monotonic()

world_obs = {} # Dict from UID to object

while(1):
	#------------------------- Check for any incoming messages from server -------------------------
	while(socketReadable(conn, 0.01)): # timeout = 0.01 s
		# print("Socket readable!")
		# Read and handle message(s)
		msg_type = readUInt32FromSocket(conn)
		msg_len = readUInt32FromSocket(conn)

		#print("Received msg, type: " + str(msg_type) + ", len: " + str(msg_len))

		if(msg_len < 8):
			raise Exception("Invalid msg len: " + str(msg_len))

		# Read rest of message
		msg_body = readNBytesFromSocket(conn, msg_len - 8) # We have already read 8 bytes of the message, read the rest.
		buffer_in = BufferIn(msg_body)

		if(msg_type == Protocol.TimeSyncMessage):
			
			global_time = buffer_in.readDouble()

			#print("Received TimeSyncMessage: global_time: " + str(global_time))
		elif(msg_type == Protocol.ChatMessageID):
		
			name = buffer_in.readStringLengthFirst()
			msg  = buffer_in.readStringLengthFirst()

			#print("Received ChatMessage: '" + name + "': '" + msg +"'")
		elif(msg_type == Protocol.AvatarTransformUpdate):
			#print("Received AvatarTransformUpdate")
			pass
		elif(msg_type == Protocol.ParcelCreated):
			#print("Received ParcelCreated")
			pass
		elif(msg_type == Protocol.InfoMessageID):
			msg = buffer_in.readStringLengthFirst()
			#print("Received InfoMessage: " + msg)
		elif(msg_type == Protocol.ErrorMessageID):
			msg = buffer_in.readStringLengthFirst()
			print("Received ErrorMessage: " + msg)
		elif(msg_type == Protocol.ObjectInitialSend):
			print("Received ObjectInitialSend")
			
			world_ob = WorldObject()
			world_ob.readFromStream(buffer_in)
			world_obs[world_ob.uid] = world_ob

			print("num object: " + str(len(world_obs)))
		elif(msg_type == Protocol.ObjectContentChanged):
			#print("Received ObjectContentChanged")
			
			object_uid = buffer_in.readUInt64()
			new_content = buffer_in.readStringLengthFirst()

			#print("object_uid: " + str(object_uid) + ", new_content: '" + new_content + "'")
		else:
			print("Received unknown/unhandled msg type: " + str(msg_type) + ", ignoring.")
			pass

		
	UPDATE_PERIOD = 0.1 # How often we send an object update message to the server, in seconds

	if(time.monotonic() - last_send_time > UPDATE_PERIOD):

		# Send an AvatarTransformUpdate message to the server

		# Make the avatar walk in a circle
		t = time.monotonic() - initial_time
		phase = t * 0.6
			
		avatar.pos.x = math.cos(phase) * 4
		avatar.pos.y = math.sin(phase) * 4
		avatar.pos.z = 1.67  # The avatar position is considered to be at the head at eye height, which is 1.67m.
	
		# Compute the avatar rotation so that it faces forwards
		avatar.rotation = Vec3f(0.0, math.pi / 2, phase + math.pi / 2)  # (roll, pitch, heading)

		# Send the AvatarTransformUpdate message
		buffer_out = BufferOut()
		buffer_out.writeUInt32(Protocol.AvatarTransformUpdate)
		buffer_out.writeUInt32(0) # will be updated with length of message
		writeUID(buffer_out, client_avatar_UID)
		avatar.pos.writeToStream(buffer_out)
		avatar.rotation.writeToStream(buffer_out)
		buffer_out.writeUInt32(0) # Write anim_state.
		buffer_out.updateLengthField()
		buffer_out.writeToSocket(conn)

		last_send_time = time.monotonic()


	CHAT_PERIOD = 5.0

	# Send a chat message occasionally
	if(time.monotonic() - last_chat_time > CHAT_PERIOD):

		# Send the ChatMesssage to server
		buffer_out = BufferOut()
		buffer_out.writeUInt32(Protocol.ChatMessageID)
		buffer_out.writeUInt32(0) # will be updated with length of message
		buffer_out.writeStringLengthFirst("Beep boop") # message
		buffer_out.updateLengthField()
		buffer_out.writeToSocket(conn)

		last_chat_time = time.monotonic()
