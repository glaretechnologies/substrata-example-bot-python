

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




def getEthPriceInUSD():
	response = requests.get('https://api.coinbase.com/v2/exchange-rates?currency=USD')
	#print(response.json())

	json = response.json()

	eth_per_USD_str = json['data']['rates']['ETH']
	USD_per_eth = 1.0 / float(eth_per_USD_str)
	#print("eth_price_usd: " + str(1.0 / float(eth_per_USD)))
	return USD_per_eth


def getEthGasPriceInGWEI(EtherscanAPIKey):
	response = requests.get('https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey=' + EtherscanAPIKey)
	#print(response.json())

	json = response.json()

	result = json['result']
	if result is None:
		raise Exception("Could not find 'result' JSON node.")
	price = result['SafeGasPrice']
	if price is None:
		raise Exception("Could not find 'SafeGasPrice' JSON node.")

	return float(price)

#getEthPriceInUSD()
#gas_price_gwei = getEthGasPriceInGWEI()
#print(gas_price_gwei)
#exit(1)

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

#EtherscanAPIKey = config['APIKeys']['EtherscanAPIKey']
#if EtherscanAPIKey is None:
#	raise Exception("Could not find 'EtherscanAPIKey' in config file.")

print("Using username '" + username + "'")

#------------------------- Connect to server -------------------------
plain_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("Connecting to server '" + server_hostname + "'...")

# (pre-python 3.7)
#conn = ssl.wrap_socket(plain_socket)
#conn.connect((server_hostname, 7600))
# ========================
# https://stackoverflow.com/questions/4818280/ssl-wrap-socket-attributeerror-module-object-has-no-attribute-wrap-socket
sslSettings = ssl.SSLContext(ssl.PROTOCOL_TLS)
conn = sslSettings.wrap_socket(plain_socket)
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



#------------------------- Send login message -------------------------
login_buf = BufferOut()
login_buf.writeUInt32(Protocol.LogInMessage)
login_buf.writeUInt32(0) # will be updated with length
login_buf.writeStringLengthFirst(username)
login_buf.writeStringLengthFirst(password)
login_buf.updateLengthField()
login_buf.writeToSocket(conn)


#------------------------- Do initial object query -------------------------
def sendQueryObjectsMessage(conn):
	buffer_out = BufferOut()
	buffer_out.writeUInt32(Protocol.QueryObjects)
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

#------------------------- Start main loop -------------------------

last_send_time = -1000.0
initial_time = time.monotonic()

world_obs = {} # Dict from UID to object

while(1):
	#------------------------- Check for any incoming messages from server -------------------------
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
			world_obs[world_ob.uid] = world_ob  # Save object in our dictionary

			print("num object: " + str(len(world_obs)))
		elif(msg_type == Protocol.ObjectContentChanged):
			#print("Received ObjectContentChanged")
			
			object_uid = buffer_in.readUInt64()
			new_content = buffer_in.readStringLengthFirst()

			#print("object_uid: " + str(object_uid) + ", new_content: '" + new_content + "'")
		else:
			print("Received unknown/unhandled msg type: " + str(msg_type))
			pass

	UPDATE_PERIOD = 5.0 # How often we send an object update message to the server, in seconds

	if(time.monotonic() - last_send_time > UPDATE_PERIOD):

		# Send a message to the server
		last_send_time = time.monotonic()

		# print("Sending message to server...")

		OB_TO_CHANGE_UID = 695

		if False:
			buffer_out = BufferOut()
			buffer_out.writeUInt32(Protocol.ObjectTransformUpdate)
			buffer_out.writeUInt32(0) # will be updated with length
			buffer_out.writeUInt64(OB_TO_CHANGE_UID) # Write object UID

			buffer_out.writeDouble(12.12375831604) # Write object pos x
			buffer_out.writeDouble(51.971897125244)# + (time.monotonic() - initial_time)) # Write object pos y
			buffer_out.writeDouble(1.063417524099)# + math.sin(time.monotonic()) + 1.0) # Write object pos z

			buffer_out.writeFloat(1.0) # Write object axis x
			buffer_out.writeFloat(0) # Write object axis y
			buffer_out.writeFloat(math.sin(time.monotonic() - initial_time)) # Write object axis z
			buffer_out.writeFloat(time.monotonic() - initial_time + math.pi / 2.0) # Write object angle

			buffer_out.updateLengthField()

			buffer_out.writeToSocket(conn)
		else:
			ob = world_obs.get(OB_TO_CHANGE_UID) # Look up object in our objects dictionary using the UID
			if ob is not None:
				try:
					print("Writing ob to stream...")

					eth_price_usd = getEthPriceInUSD()

					#gas_price_gwei = getEthGasPriceInGWEI(EtherscanAPIKey)

					ob.content = "Eth: " + f"{eth_price_usd:.1f}" + " USD\n\n" # Update hypercard contents

					#ob.content += "Gas: \n" + str(gas_price_gwei) + " Gwei\n\n"

					ob.content += "Last updated: \n" + str(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))

					print("Set content to " + ob.content)

					buffer_out = BufferOut()
					buffer_out.writeUInt32(Protocol.ObjectFullUpdate)
					buffer_out.writeUInt32(0) # will be updated with length
					ob.writeToStream(buffer_out)
					buffer_out.updateLengthField()
					buffer_out.writeToSocket(conn)
				except Exception as err:
					print("Caught exception: " + str(err))







# conn.close()
