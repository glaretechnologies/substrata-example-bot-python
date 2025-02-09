

# NOTE: will need to have requests module installed.

import socket, ssl, pprint, time, select, struct, math, configparser, requests, datetime


CyberspaceHello = 1357924680
CyberspaceProtocolVersion = 40
ClientProtocolOK		= 10000
ClientProtocolTooOld	= 10001
ClientProtocolTooNew	= 10002

ConnectionTypeUpdates	= 500

AvatarTransformUpdate	= 1002
CreateAvatar			= 1004

ChatMessageID			= 2000

ObjectTransformUpdate	= 3002
ObjectFullUpdate		= 3003

ObjectContentChanged	= 3017

QueryObjects			= 3020
ObjectInitialSend		= 3021

ParcelCreated			= 3100


InfoMessageID			= 7001
ErrorMessageID			= 7002

LogInMessage			= 8000

TimeSyncMessage			= 9000


ANIM_STATE_IN_AIR		= 1 # Is the avatar not touching the ground? Could be jumping or flying etc..
ANIM_STATE_FLYING		= 2 # Is the player flying (e.g. do they have flying movement mode on)


WORLD_MATERIAL_SERIALISATION_VERSION = 8
TIMESTAMP_SERIALISATION_VERSION = 1


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

def writeUID(socket, uid):
	socket.writeUInt64(uid)

def socketReadable(socket, timeout_s):
	socket_list = [socket]
	read_sockets, write_sockets, error_sockets = select.select(socket_list, [], socket_list, timeout_s)
	if(len(error_sockets) == 1):
		raise Exception("Socket excep")
	return len(read_sockets) == 1



class BufferIn:
	def __init__(self, data_byte_array_):
		self.data_byte_array = data_byte_array_
		self.read_index = 0

	def readInt32(self):
		x = int.from_bytes(self.data_byte_array[self.read_index : self.read_index + 4], byteorder='little', signed=True)
		self.read_index += 4
		return x

	def readUInt32(self):
		x = int.from_bytes(self.data_byte_array[self.read_index : self.read_index + 4], byteorder='little', signed=False)
		self.read_index += 4
		return x

	def readUInt64(self):
		x = int.from_bytes(self.data_byte_array[self.read_index : self.read_index + 8], byteorder='little', signed=False)
		self.read_index += 8
		return x

	def readFloat(self):
		bytes = self.data_byte_array[self.read_index : self.read_index + 4]
		x = struct.unpack('<f', bytes)[0]  # '<' specifies little-endian byte order.  unpack returns a tuple, get zeroth element of it.
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


class BufferOut:
	def __init__(self):
		self.data = []

	def writeInt32(self, x):
		b = x.to_bytes(4, byteorder='little', signed=True)
		self.data += b

	def writeUInt32(self, x):
		b = x.to_bytes(4, byteorder='little')
		self.data += b

	def writeUInt64(self, x):
		b = x.to_bytes(8, byteorder='little')
		self.data += b

	def writeFloat(self, x):
		b = struct.pack("<f", x) # '<' specifies little-endian byte order.
		self.data += b

	def writeDouble(self, x):
		b = struct.pack("<d", x) # '<' specifies little-endian byte order.
		self.data += b

	def writeStringLengthFirst(self, str):
		b = bytes(str, 'UTF-8')
		self.writeUInt32(len(b))
		self.data += b

	def updateLengthField(self):
		data_len = len(self.data)
		b = data_len.to_bytes(4, byteorder='little')

		self.data[4 + 0] = b[0]
		self.data[4 + 1] = b[1]
		self.data[4 + 2] = b[2]
		self.data[4 + 3] = b[3]

	def writeToSocket(self, socket):
		socket.sendall(bytes(self.data))



class Vec3d:
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z

	def writeToStream(self, stream):
		stream.writeDouble(self.x)
		stream.writeDouble(self.y)
		stream.writeDouble(self.z)

def readVec3dFromStream(stream):
	x = stream.readDouble()
	y = stream.readDouble()
	z = stream.readDouble()
	return Vec3d(x, y, z)

class Vec3f:
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z

	def writeToStream(self, stream):
		stream.writeFloat(self.x)
		stream.writeFloat(self.y)
		stream.writeFloat(self.z)

def readVec3fFromStream(stream):
	x = stream.readFloat()
	y = stream.readFloat()
	z = stream.readFloat()
	return Vec3f(x, y, z)


class Colour3f:
	def __init__(self, x, y, z):
		self.r = x
		self.g = y
		self.b = z

	def writeToStream(self, stream):
		stream.writeFloat(self.r)
		stream.writeFloat(self.g)
		stream.writeFloat(self.b)

def readColour3fFromStream(stream):
	x = stream.readFloat()
	y = stream.readFloat()
	z = stream.readFloat()
	return Colour3f(x, y, z)


class Matrix2f:
	def __init__(self, x_, y_, z_, w_):
		self.x = x_;
		self.y = y_;
		self.z = z_;
		self.w = w_;

	def writeToStream(self, stream):
		stream.writeFloat(self.x)
		stream.writeFloat(self.y)
		stream.writeFloat(self.z)
		stream.writeFloat(self.w)

def readMatrix2fFromStream(stream):
	x = buffer_in.readFloat()
	y = buffer_in.readFloat()
	z = buffer_in.readFloat()
	w = buffer_in.readFloat()
	return Matrix2f(x, y, z, w)


class TimeStamp:
	def __init__(self, x):
		self.time = x # uint64

	def writeToStream(self, stream):
		stream.writeUInt32(TIMESTAMP_SERIALISATION_VERSION)
		stream.writeUInt64(self.time)

def readTimeStampFromStream(stream):
	version = stream.readUInt32()
	t = stream.readUInt64()
	return TimeStamp(t)


# Material ScalarVal
class ScalarVal:
	def __init__(self):
		self.val = 0.0 # float
		self.texture_url = ""

	def writeToStream(self, stream):
		stream.writeFloat(self.val)
		stream.writeStringLengthFirst(self.texture_url)

def readScalarValFromStream(stream):
	v = ScalarVal()
	v.val = stream.readFloat()
	v.texture_url = stream.readStringLengthFirst()
	return v


class WorldMaterial:
	def __init__(self):
		pass

	def readFromStream(self, stream):
		initial_read_index = stream.read_index

		version = stream.readUInt32()
		if (version > WORLD_MATERIAL_SERIALISATION_VERSION):
			raise Exception("Unsupported version " + str(version) + ", expected " + str(WORLD_MATERIAL_SERIALISATION_VERSION) + ".")

		buffer_size = stream.readUInt32()

		self.colour_rgb = readColour3fFromStream(buffer_in)
		self.colour_texture_url = buffer_in.readStringLengthFirst()

		self.emission_rgb = readColour3fFromStream(buffer_in)
		self.emission_texture_url = buffer_in.readStringLengthFirst()

		self.roughness = readScalarValFromStream(buffer_in)
		self.metallic_fraction = readScalarValFromStream(buffer_in)
		self.opacity = readScalarValFromStream(buffer_in)

		self.tex_matrix = readMatrix2fFromStream(buffer_in)

		self.emission_lum_flux = buffer_in.readFloat()

		self.flags = buffer_in.readUInt32()

		self.normal_map_url = buffer_in.readStringLengthFirst()

		# Discard any remaining unread data
		read_B = stream.read_index - initial_read_index # Number of bytes we have read so far
		if(read_B < buffer_size):
			stream.read_index += buffer_size - read_B

	def writeToStream(self, stream):
		stream.writeUInt32(WORLD_MATERIAL_SERIALISATION_VERSION)

		# TODO: this is out of date, update

		self.colour_rgb.writeToStream(stream)
		stream.writeStringLengthFirst(self.colour_texture_url)

		self.roughness.writeToStream(stream)
		self.metallic_fraction.writeToStream(stream)
		self.opacity.writeToStream(stream)

		self.tex_matrix.writeToStream(stream)

		stream.writeFloat(self.emission_lum_flux)

		stream.writeUInt32(self.flags)



class WorldObject:
	def __init__(self):
		self.data = []

		self.uid = 0 # uint64
		self.object_type = 0 # uint32
		self.model_url = ""

		self.materials = []

		self.lightmap_url = ""
		
		self.script = ""
		self.content = ""
		self.target_url = ""
		self.audio_source_url = ""

		self.audio_volume = 1.0

		self.pos = Vec3d(0, 0, 0)

		self.axis = Vec3f(0, 0, 1)
		self.angle = 0.0
		self.scale = Vec3f(1, 1, 1)
		
		self.created_time = TimeStamp(0)
		self.creator_id = 0  # UserID (uint32)

		self.flags = 0 # uint32

		self.creator_name = ""

		self.aabb_min = Vec3f(0,0,0)
		self.aabb_max = Vec3f(1,1,1)

		self.max_model_lod_level = 0 # int32

	def writeToStream(self, stream):
		stream.writeUInt64(self.uid)
		stream.writeUInt32(self.object_type)
		stream.writeStringLengthFirst(self.model_url)
		
		# Write materials
		stream.writeUInt32(len(self.materials))
		for mat in self.materials:
			mat.writeToStream(stream)

		stream.writeStringLengthFirst(self.lightmap_url)

		stream.writeStringLengthFirst(self.script)
		stream.writeStringLengthFirst(self.content)
		stream.writeStringLengthFirst(self.target_url)
		stream.writeStringLengthFirst(self.audio_source_url)
		stream.writeFloat(self.audio_volume)

		self.pos.writeToStream(stream)
		self.axis.writeToStream(stream)
		stream.writeFloat(self.angle)
		self.scale.writeToStream(stream)

		self.created_time.writeToStream(stream)
		stream.writeUInt32(self.creator_id)

		stream.writeUInt32(self.flags)

		stream.writeStringLengthFirst(self.creator_name)

		print("writing self.aabb_min to stream: " + str(self.aabb_min.x) + ", " + str(self.aabb_min.y) + ", " + str(self.aabb_min.z))
		self.aabb_min.writeToStream(stream)
		print("writing self.aabb_max to stream: " + str(self.aabb_max.x) + ", " + str(self.aabb_max.y) + ", " + str(self.aabb_max.z))
		self.aabb_max.writeToStream(stream)

		stream.writeInt32(self.max_model_lod_level)

	def readFromStream(self, stream):
		self.uid = stream.readUInt64()
		self.object_type = stream.readUInt32()
		self.model_url = stream.readStringLengthFirst()

		# Read materials
		num_mats = stream.readUInt32()
		if (num_mats > 10000):
			raise Exception("Too many mats: " + str(num_mats))
		self.materials = []
		for i in range(0, num_mats):
			mat = WorldMaterial()
			mat.readFromStream(stream)
			self.materials.append(mat)

		self.lightmap_url = buffer_in.readStringLengthFirst()

		self.script = buffer_in.readStringLengthFirst()
		self.content = buffer_in.readStringLengthFirst()
		self.target_url = buffer_in.readStringLengthFirst()

		self.audio_source_url = buffer_in.readStringLengthFirst()
		self.audio_volume = buffer_in.readFloat()

		self.pos = readVec3dFromStream(buffer_in)
		self.axis = readVec3fFromStream(buffer_in)
		self.angle = buffer_in.readFloat()
		self.scale = readVec3fFromStream(buffer_in)

		self.created_time = readTimeStampFromStream(buffer_in)
		self.creator_id = buffer_in.readUInt32()

		self.flags = buffer_in.readUInt32()

		self.creator_name = buffer_in.readStringLengthFirst()

		self.aabb_min = readVec3fFromStream(buffer_in)
		self.aabb_max = readVec3fFromStream(buffer_in)
		
		print("self.uid: " + str(self.uid))
		print("self.creator_name: " + self.creator_name)
		print("Read scale: " + str(self.scale.x) + ", " + str(self.scale.y) + ", " + str(self.scale.z))
		print("Read aabb_min: " + str(self.aabb_min.x) + ", " + str(self.aabb_min.y) + ", " + str(self.aabb_min.z))
		print("Read aabb_max: " + str(self.aabb_max.x) + ", " + str(self.aabb_max.y) + ", " + str(self.aabb_max.z))

		self.max_model_lod_level = buffer_in.readInt32()

		# TODO: read compressed voxel data

class AvatarSettings:
	def __init__(self):
		self.model_url = ""
		self.materials = []
		self.pre_ob_to_world_matrix = [1.0, 0.0, 0.0, 0.0,     0.0, 1.0, 0.0, 0.0,    0.0, 0.0, 1.0, 0.0,   0.0, 0.0, 0.0, 1.0]

	def writeToStream(self, stream):
		stream.writeStringLengthFirst(self.model_url)

		# Write materials
		stream.writeUInt32(len(self.materials))
		for mat in self.materials:
			mat.writeToStream(stream)

		for i in range(0, 16):
			stream.writeFloat(self.pre_ob_to_world_matrix[i])

		
	def readFromStream(self, stream):
		self.uid = stream.readUInt64()

		# Read materials
		num_mats = stream.readUInt32()
		if (num_mats > 10000):
			raise Exception("Too many mats: " + str(num_mats))
		self.materials = []
		for i in range(0, num_mats):
			mat = WorldMaterial()
			mat.readFromStream(stream)
			self.materials.append(mat)

		for i in range(0, 16):
			self.pre_ob_to_world_matrix[i] = stream.readFloat()

class Avatar:
	def __init__(self):
		self.uid = 0 # uint64
		self.name = ""
		self.pos = Vec3d(0,0,0)
		self.rotation = Vec3f(0,0,0)
		self.avatar_settings = AvatarSettings()
		
	def writeToStream(self, stream):
		stream.writeUInt64(self.uid)
		stream.writeStringLengthFirst(self.name)
		self.pos.writeToStream(stream)
		self.rotation.writeToStream(stream)
		self.avatar_settings.writeToStream(stream)

	def readFromStream(self, stream):
		self.uid = stream.readUInt64()
		self.name = stream.readStringLengthFirst()
		self.pos = readVec3dFromStream(stream)
		self.rotation = readVec3fFromStream(stream)
		self.avatar_settings.readFromStream(stream)
		


# Read username and password from disk
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


plain_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

plain_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)

print("Connecting to server '" + server_hostname + "'...")

conn = ssl.wrap_socket(plain_socket)
conn.connect((server_hostname,  7600))

print("Connected to server '" + server_hostname + "'.")

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

# Read server protocol version
server_protocol_version = readUInt32FromSocket(conn)
print('server_protocol_version: ', str(server_protocol_version))

client_avatar_UID = readUID(conn)
print("Received client_avatar_UID: " + str(client_avatar_UID))


# Send login message
login_buf = BufferOut()
login_buf.writeUInt32(LogInMessage)
login_buf.writeUInt32(0) # will be updated with length
login_buf.writeStringLengthFirst(username)
login_buf.writeStringLengthFirst(password)
login_buf.updateLengthField()
login_buf.writeToSocket(conn)


avatar = Avatar()
avatar.pos = Vec3d(5, 5, 2)

# Send create avatar message
av_buf = BufferOut()
av_buf.writeUInt32(CreateAvatar)
av_buf.writeUInt32(0) # will be updated with length
avatar.writeToStream(av_buf)
av_buf.updateLengthField()
av_buf.writeToSocket(conn)



def sendQueryObjectsMessage(conn):
	buffer_out = BufferOut()
	buffer_out.writeUInt32(QueryObjects)
	buffer_out.writeUInt32(0) # message length - to be updated.
	r = 4
	# Write camera position
	buffer_out.writeDouble(0.0)
	buffer_out.writeDouble(0.0)
	buffer_out.writeDouble(0.0)

	buffer_out.writeUInt32(2 * (2 * r + 1) * (2 * r + 1)) # Num cells to query

	for x in range(-r, r+1): # (let x = -r; x <= r; ++x)
		for y in range(-r, r+1): #  for (let y = -r; y <= r; ++y) {
			buffer_out.writeInt32(x)
			buffer_out.writeInt32(y)
			buffer_out.writeInt32(0)
			buffer_out.writeInt32(x)
			buffer_out.writeInt32(y)
			buffer_out.writeInt32(-1)

	buffer_out.updateLengthField();
	buffer_out.writeToSocket(conn);


# Send inital query of objects
sendQueryObjectsMessage(conn)

last_send_time = -1000.0
last_chat_time = -1000.0
initial_time = time.monotonic()

world_obs = {} # Dict from UID to object

while(1):
	while(socketReadable(conn, 0.01)): # timeout_ = 0.1
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

		if(msg_type == TimeSyncMessage):
			
			global_time = buffer_in.readDouble()

			#print("Received TimeSyncMessage: global_time: " + str(global_time))
		elif(msg_type == ChatMessageID):
		
			name = buffer_in.readStringLengthFirst()
			msg  = buffer_in.readStringLengthFirst()

			#print("Received ChatMessage: '" + name + "': '" + msg +"'")
		elif(msg_type == AvatarTransformUpdate):
			#print("Received AvatarTransformUpdate")
			pass
		elif(msg_type == ParcelCreated):
			#print("Received ParcelCreated")
			pass
		elif(msg_type == InfoMessageID):
			msg = buffer_in.readStringLengthFirst()
			#print("Received InfoMessage: " + msg)
		elif(msg_type == ErrorMessageID):
			msg = buffer_in.readStringLengthFirst()
			print("Received ErrorMessage: " + msg)
		elif(msg_type == ObjectInitialSend):
			print("Received ObjectInitialSend")
			
			world_ob = WorldObject()
			world_ob.readFromStream(buffer_in)
			world_obs[world_ob.uid] = world_ob

			print("num object: " + str(len(world_obs)))
		elif(msg_type == ObjectContentChanged):
			#print("Received ObjectContentChanged")
			
			object_uid = buffer_in.readUInt64()
			new_content = buffer_in.readStringLengthFirst()

			#print("object_uid: " + str(object_uid) + ", new_content: '" + new_content + "'")
		else:
			print("Received unknown/unhandled msg type: " + str(msg_type))
			pass

		
	UPDATE_PERIOD = 0.1 # How often we send an object update message to the server, in seconds

	if(time.monotonic() - last_send_time > UPDATE_PERIOD):

		# Send a message to the server

		# print("Sending message to server...")

		# Make the avatar walk in a circle
		t = time.monotonic() - initial_time
		
		phase = t * 0.6
			
		avatar.pos.x = math.cos(phase) * 4
		avatar.pos.y = math.sin(phase) * 4
		avatar.pos.z = 1.67
			
		# Compute the avatar rotation so that it faces forwards
		avatar.rotation = Vec3f(0.0, math.pi / 2, phase + math.pi / 2)  # (roll, pitch, heading)

		# Send an AvatarTransformUpdate message
		anim_state = 0

		buffer_out = BufferOut()
		buffer_out.writeUInt32(AvatarTransformUpdate)
		buffer_out.writeUInt32(0) # will be updated with length
		writeUID(buffer_out, client_avatar_UID)
		avatar.pos.writeToStream(buffer_out)
		avatar.rotation.writeToStream(buffer_out)
		buffer_out.writeUInt32(anim_state)
		buffer_out.updateLengthField()
		buffer_out.writeToSocket(conn)

			
		last_send_time = time.monotonic()

	# Send a chat message occasionally
	if(time.monotonic() - last_chat_time > 5.0):
		buffer_out = BufferOut()
		buffer_out.writeUInt32(ChatMessageID)
		buffer_out.writeUInt32(0) # will be updated with length
		buffer_out.writeStringLengthFirst("Beep boop") # message
		buffer_out.updateLengthField()
		buffer_out.writeToSocket(conn)

		last_chat_time = time.monotonic()
