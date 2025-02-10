#
# Copyright Glare Technologies 2025 - 
#

import struct
from lib.BasicTypes import Vec3d, Vec3f, Colour3f, Matrix2f, TimeStamp, readColour3fFromStream, readMatrix2fFromStream, readVec3fFromStream, readVec3dFromStream, readTimeStampFromStream
from lib.WorldMaterial import WorldMaterial

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

		self.mass = 10.0
		self.friction = 0.5
		self.restitution = 0.5

		self.physics_owner_id = 0

		self.last_physics_ownership_change_global_time = 0.0

		self.centre_of_mass_offset_os = Vec3f(0, 0, 0)

		self.chunk_batch0_start = 0
		self.chunk_batch0_end = 0
		self.chunk_batch1_start = 0
		self.chunk_batch1_end = 0


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

		stream.writeFloat(self.mass)
		stream.writeFloat(self.friction)
		stream.writeFloat(self.restitution)

		stream.writeUInt32(self.physics_owner_id)
		stream.writeDouble(self.last_physics_ownership_change_global_time)

		self.centre_of_mass_offset_os.writeToStream(stream)

		stream.writeUInt32(self.chunk_batch0_start)
		stream.writeUInt32(self.chunk_batch0_end)
		stream.writeUInt32(self.chunk_batch1_start)
		stream.writeUInt32(self.chunk_batch1_end)


	def readFromStream(self, stream):
		self.uid = stream.readUInt64()
		self.object_type = stream.readUInt32()
		self.model_url = stream.readStringLengthFirst()

		# Read materials
		num_mats = stream.readUInt32()
		if (num_mats > 2048):
			raise Exception("Too many mats: " + str(num_mats))
		self.materials = []
		for i in range(0, num_mats):
			mat = WorldMaterial()
			mat.readFromStream(stream)
			self.materials.append(mat)

		self.lightmap_url = stream.readStringLengthFirst()

		self.script = stream.readStringLengthFirst()
		self.content = stream.readStringLengthFirst()
		self.target_url = stream.readStringLengthFirst()

		self.audio_source_url = stream.readStringLengthFirst()
		self.audio_volume = stream.readFloat()

		self.pos = readVec3dFromStream(stream)
		self.axis = readVec3fFromStream(stream)
		self.angle = stream.readFloat()
		self.scale = readVec3fFromStream(stream)

		self.created_time = readTimeStampFromStream(stream)
		self.creator_id = stream.readUInt32()

		self.flags = stream.readUInt32()

		self.creator_name = stream.readStringLengthFirst()

		self.aabb_min = readVec3fFromStream(stream)
		self.aabb_max = readVec3fFromStream(stream)
		
		print("self.uid: " + str(self.uid))
		print("self.creator_name: " + self.creator_name)
		print("Read scale: " + str(self.scale.x) + ", " + str(self.scale.y) + ", " + str(self.scale.z))
		print("Read aabb_min: " + str(self.aabb_min.x) + ", " + str(self.aabb_min.y) + ", " + str(self.aabb_min.z))
		print("Read aabb_max: " + str(self.aabb_max.x) + ", " + str(self.aabb_max.y) + ", " + str(self.aabb_max.z))

		self.max_model_lod_level = stream.readInt32()

		# TODO: read compressed voxel data if object_type == WorldObject::ObjectType_VoxelGroup

		self.mass = stream.readFloat()
		self.friction = stream.readFloat()
		self.restitution = stream.readFloat()

		self.physics_owner_id = stream.readUInt32()

		self.last_physics_ownership_change_global_time = stream.readDouble()

		self.centre_of_mass_offset_os = readVec3fFromStream(stream)

		self.chunk_batch0_start = stream.readUInt32()
		self.chunk_batch0_end = stream.readUInt32()
		self.chunk_batch1_start = stream.readUInt32()
		self.chunk_batch1_end = stream.readUInt32()
