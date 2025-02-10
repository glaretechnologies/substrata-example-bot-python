#
# Copyright Glare Technologies 2025 - 
#

import struct
from lib.BasicTypes import Vec3d, Vec3f, Colour3f, Matrix2f, TimeStamp, readColour3fFromStream, readMatrix2fFromStream, readVec3fFromStream, readVec3dFromStream, readTimeStampFromStream


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


WORLD_MATERIAL_SERIALISATION_VERSION = 8

class WorldMaterial:
	def __init__(self):
		pass

	def readFromStream(self, stream):
		initial_read_index = stream.read_index

		version = stream.readUInt32()
		if (version > WORLD_MATERIAL_SERIALISATION_VERSION):
			raise Exception("Unsupported version " + str(version) + ", expected " + str(WORLD_MATERIAL_SERIALISATION_VERSION) + ".")

		buffer_size = stream.readUInt32()

		self.colour_rgb = readColour3fFromStream(stream)
		self.colour_texture_url = stream.readStringLengthFirst()

		self.emission_rgb = readColour3fFromStream(stream)
		self.emission_texture_url = stream.readStringLengthFirst()

		self.roughness = readScalarValFromStream(stream)
		self.metallic_fraction = readScalarValFromStream(stream)
		self.opacity = readScalarValFromStream(stream)

		self.tex_matrix = readMatrix2fFromStream(stream)

		self.emission_lum_flux = stream.readFloat()

		self.flags = stream.readUInt32()

		self.normal_map_url = stream.readStringLengthFirst()

		# Discard any remaining unread data
		read_B = stream.read_index - initial_read_index # Number of bytes we have read so far
		if(read_B < buffer_size):
			stream.read_index += buffer_size - read_B

	def writeToStream(self, stream):
		# Write to stream with a length prefix.  Do this by writing to the stream, them going back and writing the length of the data we wrote.
		# Writing a length prefix allows for adding more fields later, while retaining backwards compatibility with older code that can just skip over the new fields.

		initial_write_index = stream.getWriteIndex()

		stream.writeUInt32(WORLD_MATERIAL_SERIALISATION_VERSION)
		stream.writeUInt32(0) # Size of buffer will be written here later

		# TODO: this is out of date, update

		self.colour_rgb.writeToStream(stream)
		stream.writeStringLengthFirst(self.colour_texture_url)

		self.emission_rgb.writeToStream(stream)
		stream.writeStringLengthFirst(self.emission_texture_url)

		self.roughness.writeToStream(stream)
		self.metallic_fraction.writeToStream(stream)
		self.opacity.writeToStream(stream)

		self.tex_matrix.writeToStream(stream)

		stream.writeFloat(self.emission_lum_flux)

		stream.writeUInt32(self.flags)

		stream.writeStringLengthFirst(self.normal_map_url)

		# Go back and write size of buffer to buffer size field
		buffer_size = stream.getWriteIndex() - initial_write_index

		#std::memcpy(stream.getWritePtrAtIndex(initial_write_index + sizeof(uint32)), &buffer_size, sizeof(uint32));
		stream.writeUInt32AtIndex(buffer_size, initial_write_index + 4)

