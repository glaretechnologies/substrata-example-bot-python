#
# Copyright Glare Technologies 2025 - 
#

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
	x = stream.readFloat()
	y = stream.readFloat()
	z = stream.readFloat()
	w = stream.readFloat()
	return Matrix2f(x, y, z, w)


TIMESTAMP_SERIALISATION_VERSION = 1

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
