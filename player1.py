from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
import json
import pygame

server = 'student00.cse.nd.edu'
port = 40075

def getRect(self, x_pos, y_pos, width, height):
	return pygame.Rect(x_pos - width / 2, y_pos - height / 2, width, height)

class ClientConnFactory(ClientFactory):
	def buildProtocol(self, addr):
		return  ClientConnection()

class ClientConnection (Protocol):
	def dataReceived(self, data):
		#draw game state
		game = json.parse(data)
		p1 = game.players.player1
		p2 = game.players.player2
		
		p1rect = getRect(p1.x_pos, p1.y_pos, p1.width, p1.height)
		p2rect = getRect(p2.x_pos, p2.y_pos, p2.width, p2.height)
		ballPos = (game.ball.x_pos, game.ball.y_pos)
		
		self.screen.fill(self.black)
		pygame.draw.rect(self.screen, self.white, p1rect)
		pygame.draw.rect(self.screen, self.white, p2rect)
		pygame.draw.circle(self.screen, self.red, ballPos, game.ball.radius)
		
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