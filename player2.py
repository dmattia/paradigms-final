from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
import json
import pygame

server = 'student00.cse.nd.edu'
port = 40083

class ClientConnFactory(ClientFactory):
	def buildProtocol(self, addr):
		return  ClientConnection()

class ClientConnection (Protocol):
	def dataReceived(self, data):
		#draw game state
		
		
		#send back key presses
		keysPressed = pygame.key.get_pressed()
		if keysPressed[pygame.K_UP]:
			up = 1
		else:
			up = 0
		if keysPressed[pygame.K_DOWN]:
			down = 1
		else:
			down = 0
		self.transport.write( (up,down) )
		
	def connectionLost(self, reason):
		reactor.stop()

if __name__ == '__main__':
	reactor.connectTCP(server, port, ClientConnFactory())
	reactor.run()