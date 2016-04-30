from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
import json
import pygame

server = 'student00.cse.nd.edu'
port = 40075

def getRect(x_pos, y_pos, width, height):
	return pygame.Rect(x_pos - width / 2, y_pos - height / 2, width, height)

class ClientConnFactory(ClientFactory):
	def buildProtocol(self, addr):
		return  ClientConnection()

class ClientConnection (Protocol):
	def __init__(self):
		pygame.init()
		self.size = self.width, self.height = 640, 480
		self.black = 0, 0, 0
		self.white = 255, 255, 255
		self.red = 255, 0, 0
		self.screen = pygame.display.set_mode(self.size)

	def dataReceived(self, data):
		print data.split('?')[0]
		print ""
		# get game data sent over
		try:
			game = json.loads(data.split('?')[0])
		except:
			return
		print game
		p1 = game["players"]["p1"]
		p2 = game["players"]["p2"]
		
		# determine areas to draw players and ball
		p1rect = getRect(p1["x_pos"], p1["y_pos"], p1["width"], p1["height"])
		p2rect = getRect(p2["x_pos"], p2["y_pos"], p2["width"], p2["height"])
		ballPos = (int(game["ball"]["x_pos"]), int(game["ball"]["y_pos"]))
		
		# draw background, players and ball
		self.screen.fill(self.black)
		pygame.draw.rect(self.screen, self.white, p1rect)
		pygame.draw.rect(self.screen, self.white, p2rect)
		pygame.draw.circle(self.screen, self.red, ballPos, int(game["ball"]["radius"]))
		
		# draw the score
		myfont = pygame.font.SysFont("monospace", 42)
		score_label = myfont.render(str(p1["score"]) + " | " + str(p2["score"]), 1, self.white)
		self.screen.blit(score_label, (260, 20))

		pygame.display.flip()
		
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
		self.transport.write( str(up) + "|" + str(down) )
		
	def connectionMade(self):
		print "connected to game server"
		
	def connectionLost(self, reason):
		reactor.stop()
	

if __name__ == '__main__':
	reactor.connectTCP(server, port, ClientConnFactory())
	reactor.run()