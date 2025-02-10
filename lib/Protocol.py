#
# Copyright Glare Technologies 2025 - 
#

# Based off substrata\shared\Protocol.h
class Protocol:
   
	CyberspaceHello					= 1357924680

	CyberspaceProtocolVersion		= 40
	
	ClientProtocolOK				= 10000
	ClientProtocolTooOld			= 10001
	ClientProtocolTooNew			= 10002
	CyberspaceGoodbye				= 10010
	ClientUDPSocketOpen				= 10003
	
	AudioStreamToServerStarted		= 10020
	AudioStreamToServerEnded		= 10021
	
	ConnectionTypeUpdates			= 500
	ConnectionTypeUploadResource	= 501
	ConnectionTypeDownloadResources	= 502
	ConnectionTypeScreenshotBot		= 504 # A connection from the screenshot bot.
	ConnectionTypeEthBot			= 505 # A connection from the Ethereum bot.
	
	
	AvatarCreated					= 1000
	AvatarDestroyed					= 1001
	AvatarTransformUpdate			= 1002
	AvatarFullUpdate				= 1003
	CreateAvatar					= 1004
	AvatarIsHere					= 1005
	AvatarPerformGesture			= 1010
	AvatarStopGesture				= 1011
	
	AvatarEnteredVehicle			= 1100
	AvatarExitedVehicle				= 1101
	
	ChatMessageID					= 2000
	
	ObjectCreated					= 3000
	ObjectDestroyed					= 3001
	ObjectTransformUpdate			= 3002
	ObjectFullUpdate				= 3003
	ObjectLightmapURLChanged		= 3010 # The object's lightmap URL changed.
	ObjectFlagsChanged				= 3011
	ObjectModelURLChanged			= 3012
	ObjectPhysicsOwnershipTaken		= 3013
	ObjectPhysicsTransformUpdate	= 3016
	ObjectContentChanged			= 3017
	SummonObject					= 3030
	
	CreateObject					= 3004 # Client wants to create an object.
	DestroyObject					= 3005 # Client wants to destroy an object.
	
	QueryObjects					= 3020 # Client wants to query objects in certain grid cells
	ObjectInitialSend				= 3021
	QueryObjectsInAABB				= 3022 # Client wants to query objects in a particular AABB
	
	
	ParcelCreated					= 3100
	ParcelDestroyed					= 3101
	ParcelFullUpdate				= 3103
	
	QueryParcels					= 3150
	ParcelList						= 3160
	
	GetAllObjects					= 3600 # Client wants to get all objects from server
	AllObjectsSent					= 3601 # Server has sent all objects
	
	WorldSettingsInitialSendMessage	= 3700
	WorldSettingsUpdate				= 3701
	
	QueryMapTiles					= 3800 # Client wants to query map tile image URLs
	MapTilesResult					= 3801 # Server is sending back a list of tile image URLs to the client.
	
	
	QueryLODChunksMessage			= 3900
	LODChunkInitialSend				= 3901
	LODChunkUpdatedMessage			= 3902
	
	
	
	GetFile							= 4000
	GetFiles						= 4001 # Client wants to download multiple resources from the server.
	
	NewResourceOnServer				= 4100 # A file has been uploaded to the server
	
	
	UploadAllowed					= 5100
	LogInFailure					= 5101
	InvalidFileSize					= 5102
	NoWritePermissions				= 5103
	ServerIsInReadOnlyMode			= 5104
	InvalidFileType					= 5105
	
	
	UserSelectedObject				= 6000
	UserDeselectedObject			= 6001
	
	UserUsedObjectMessage			= 6500
	UserTouchedObjectMessage		= 6501
	UserMovedNearToObjectMessage	= 6510
	UserMovedAwayFromObjectMessage	= 6511
	UserEnteredParcelMessage		= 6512
	UserExitedParcelMessage			= 6513
	
	InfoMessageID					= 7001
	ErrorMessageID					= 7002
	ServerAdminMessageID			= 7010 # Allows server to send a message like "Server going down for reboot soon"
	
	LogInMessage					= 8000
	LogOutMessage					= 8001
	SignUpMessage					= 8002
	LoggedInMessageID				= 8003
	LoggedOutMessageID				= 8004
	SignedUpMessageID				= 8005
	
	RequestPasswordReset			= 8010 # Client wants to reset the password for a given email address.  Obsolete, does nothing.  Use website instead.
	ChangePasswordWithResetToken	= 8011 # Client is sending the password reset token, email address, and the new password.  Obsolete, does nothing.  Use website instead.
	
	TimeSyncMessage					= 9000 # Sends the current time
	
	ScreenShotRequest				= 11001
	ScreenShotSucceeded				= 11002
	TileScreenShotRequest			= 11003
	
	
	SubmitEthTransactionRequest		= 12001
	EthTransactionSubmitted			= 12002
	EthTransactionSubmissionFailed	= 12003
	
	KeepAlive						= 13000 # A message that doesn't do anything apart from provide a means for the client or server to check a connection is still working by making a socket call.

