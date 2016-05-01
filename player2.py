from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
import json
import pygame
from pygame.locals import *
import sys

# game server and player 2 port
server = 'student03.cse.nd.edu'
port = 40083

# returns the pygame rectangle of a player given its parameters
def getRect(x_pos, y_pos, width, height):
	return pygame.Rect(x_pos - width / 2, y_pos - height / 2, width, height)

# checks whether a piece of data is valid json
def is_json(data):
	try:
		json.loads(data)
		return True
	except ValueError, e:
		return False
	
# player 2's connection factory
class ClientConnFactory(ClientFactory):
	def buildProtocol(self, addr):
		return  ClientConnection()

# player 2's connection to the game server
class ClientConnection (Protocol):
	def __init__(self):
		pygame.init()
		self.size = self.width, self.height = 640, 480
		self.black = 0, 0, 0
		self.white = 255, 255, 255
		self.red = 255, 0, 0
		self.screen = pygame.display.set_mode(self.size)

	def dataReceived(self, data):
		# process the game data sent over
		json_data = data.split('?', 1)[0]
		if is_json(json_data):
			game = json.loads(json_data)
		# This can happen when the transport stream is fragmented and the
		# end of one json string is sent over that is incomplete
		# This is uncommon, and can be ignored
		else:
			return
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

		# now, actually display everything
		pygame.display.flip()
		
		#check for X button pressed
		for event in pygame.event.get():
			if event.type == QUIT:
				print "Quit event found"
				#pygame.quit()
		        #self.transport.loseConnection()

		#send back key presses for player movement
		keysPressed = pygame.key.get_pressed()
		up = keysPressed[pygame.K_UP]
		down = keysPressed[pygame.K_DOWN]
		self.transport.write( str(up) + "|" + str(down) + "?" )

	# connection established to the game server
	def connectionMade(self):
		print "connected to game server"
		# draw waiting for player 1 screen
		self.screen.fill(self.black)
		myfont = pygame.font.SysFont("monospace", 32)
		connected_label = myfont.render("CONNECTED TO SERVER", 1, self.white)
		waiting_label = myfont.render("WAITING FOR PLAYER 1", 1, self.white)
		self.screen.blit(connected_label, (120, 100))
		self.screen.blit(waiting_label, (112, 200))
		pygame.display.flip()

	# game server severed connection
	def connectionLost(self, reason):
		reactor.stop()

# try to connect to game server
if __name__ == '__main__':
	reactor.connectTCP(server, port, ClientConnFactory())
	reactor.run()
