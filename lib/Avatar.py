#
# Copyright Glare Technologies 2025 - 
#

import struct
from lib.BasicTypes import Vec3d, Vec3f, Colour3f, Matrix2f, TimeStamp, readColour3fFromStream, readMatrix2fFromStream, readVec3fFromStream, readVec3dFromStream, readTimeStampFromStream


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
