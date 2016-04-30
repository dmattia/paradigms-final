from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor

PLAYER_ONE_PORT = 40075
PLAYER_TWO_PORT = 40083

player_one_connected = False
player_two_connected = False

class P1ServerFactory(Factory):
	def buildProtocol(self, addr):
		return P1Server(addr)

class P1Server(Protocol):
	def __init__(self, addr):
		self.addr = addr

	def dataReceived(self, data):
		pass

	def connectionMade(self):
		print "Player 1 connected"
		global player_one_connected, player_two_connected
		player_one_connected = True
		if player_two_connected:
			print "Both players connected"

	def connectionLost(self, reason):
		print "Connection lost to player 1"
		global player_one_connected, player_two_connected
		player_one_connected = False

class P2ServerFactory(Factory):
	def buildProtocol(self, addr):
		return P2Server(addr)

class P2Server(Protocol):
	def __init__(self, addr):
		self.addr = addr

	def dataReceived(self, data):
		pass

	def connectionMade(self):
		print "Player 2 connected"
		global player_one_connected, player_two_connected
		player_two_connected = True
		if player_one_connected:
			print "Both players connected"

	def connectionLost(self, reason):
		print "Connection lost to player 2"
		global player_one_connected, player_two_connected
		player_two_connected = False

if __name__ == '__main__':
	reactor.listenTCP(
		PLAYER_ONE_PORT,
		P1ServerFactory()
	)
	reactor.listenTCP(
		PLAYER_TWO_PORT,
		P2ServerFactory()
	)
	reactor.run()
