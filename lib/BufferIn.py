#
# Copyright Glare Technologies 2025 - 
#

import struct

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
