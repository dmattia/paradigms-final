from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
import json
import pygame
from pygame.locals import *
import sys
import time

# game server and player 2 port
server = '172.32.32.16'
#server = 'localhost'
#server = 'student03.cse.nd.edu'
port = 40083

exited = False

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
		# check we're not shutting down
		global exited
		if exited:
			return
	
		# player 1 won- display finish screen
		if "p1 win" in data:
			exited = True
			self.screen.fill(self.black)
			myfont = pygame.font.SysFont("monospace", 32)
			win_label = myfont.render("PLAYER 1 WON", 1, self.white)
			myfont = pygame.font.SysFont("monospace", 24)
			exit_label = myfont.render("press any key to exit", 1, self.white)
			self.screen.blit(win_label, (200, 100))
			self.screen.blit(exit_label, (120, 200))
			pygame.display.flip()
			
			# wait 2 seconds then for key to exit
			time.sleep(2)
			self.exitWait()
		
		# player 2 won- display finish screen
		elif "p2 win" in data:
			exited = True
			self.screen.fill(self.black)
			myfont = pygame.font.SysFont("monospace", 32)
			win_label = myfont.render("PLAYER 2 WON", 1, self.white)
			myfont = pygame.font.SysFont("monospace", 24)
			exit_label = myfont.render("press any key to exit", 1, self.white)
			self.screen.blit(win_label, (200, 100))
			self.screen.blit(exit_label, (120, 200))
			pygame.display.flip()
	
			# wait 2 seconds then for key to exit
			time.sleep(2)
			self.exitWait()
			
		# player 1 forfeit- display finish screen
		elif "p1 forfeit" in data:
			exited = True
			self.screen.fill(self.black)
			myfont = pygame.font.SysFont("monospace", 32)
			win_label = myfont.render("PLAYER 1 FORFEITS", 1, self.white)
			myfont = pygame.font.SysFont("monospace", 24)
			exit_label = myfont.render("press any key to exit", 1, self.white)
			self.screen.blit(connected_label, (200, 100))
			self.screen.blit(waiting_label, (120, 200))
			pygame.display.flip()
	
			# wait 2 seconds then for key to exit
			time.sleep(2)
			self.exitWait()

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

		#send back key presses for player movement
		keysPressed = pygame.key.get_pressed()
		up = keysPressed[pygame.K_UP]
		down = keysPressed[pygame.K_DOWN]
		self.transport.write( str(up) + "|" + str(down) + "?" )
		pygame.event.pump()

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
		# check we're not shutting down
		global exited
		if exited:
			return
	
		self.screen.fill(self.black)
		myfont = pygame.font.SysFont("monospace", 32)
		win_label = myfont.render("GAME SERVER CONNECTION LOST", 1, self.white)
		myfont = pygame.font.SysFont("monospace", 24)
		exit_label = myfont.render("press any key to exit", 1, self.white)
		self.screen.blit(win_label, (100, 100))
		self.screen.blit(exit_label, (120, 200))
		pygame.display.flip()
	
		# wait 2 seconds then for key to exit
		# same as normal game exit, but have already lost the connection
		time.sleep(2)
		while True:
			for event in pygame.event.get():
				if event.type == QUIT or event.type == KEYDOWN:
					pygame.quit()
					reactor.stop()
					return
		
	# wait for key to be pressed before exiting (normal)
	def exitWait(self):
		while True:
			for event in pygame.event.get():
				if event.type == QUIT or event.type == KEYDOWN:
					# X button or any key pressed- shut everything down
					self.transport.loseConnection()
					pygame.quit()
					reactor.stop()
					return

# try to connect to game server
if __name__ == '__main__':
	reactor.connectTCP(server, port, ClientConnFactory())
	reactor.run()
