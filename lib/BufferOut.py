#
# Copyright Glare Technologies 2025 - 
#

import struct

class BufferOut:
	def __init__(self):
		self.data = []

	def writeInt32(self, x):
		b = x.to_bytes(4, byteorder='little', signed=True)
		self.data += b

	def writeUInt32(self, x):
		b = x.to_bytes(4, byteorder='little')
		self.data += b

	def writeUInt32AtIndex(self, x, index):
		b = x.to_bytes(4, byteorder='little')
		self.data[index:index+4] = b

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

	def writeBytes(self, the_byte_array):
		self.data += the_byte_array

	def updateLengthField(self):
		data_len = len(self.data)
		b = data_len.to_bytes(4, byteorder='little')

		self.data[4 + 0] = b[0]
		self.data[4 + 1] = b[1]
		self.data[4 + 2] = b[2]
		self.data[4 + 3] = b[3]

	def writeToSocket(self, socket):
		socket.sendall(bytes(self.data))

	def getWriteIndex(self):
		return len(self.data)


