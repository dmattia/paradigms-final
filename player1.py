from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
import json
import pygame
from pygame.locals import *
import sys
import time

# game server and player 1 port
server = 'student03.cse.nd.edu'
port = 40075

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

# player 1's connection factory
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
			
		# player 2 forfeit
		elif "p2 forfeit" in data:
			exited = True
			self.screen.fill(self.black)
			myfont = pygame.font.SysFont("monospace", 32)
			win_label = myfont.render("PLAYER 2 FORFEITS", 1, self.white)
			myfont = pygame.font.SysFont("monospace", 24)
			exit_label = myfont.render("press any key to exit", 1, self.white)
			self.screen.blit(win_label, (200, 100))
			self.screen.blit(exit_label, (120, 200))
			pygame.display.flip()
	
			# wait 2 seconds then for key to exit
			time.sleep(2)
			self.exitWait()
		
		# get game data sent over
		json_data = data.split('?', 1)[0]
		if is_json(json_data):
			game = json.loads(json_data)
		else:
			# This can happen when the transport stream is fragmented and the
			# end of one json string is sent over that is incomplete
			# This is uncommon, and can be ignored
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

		#send back key presses
		keysPressed = pygame.key.get_pressed()
		up = keysPressed[pygame.K_UP]
		down = keysPressed[pygame.K_DOWN]
		self.transport.write( str(up) + "|" + str(down) + "?" )
		pygame.event.pump()

	# connection established to the game server
	def connectionMade(self):
		print "connected to game server"
		# display initial menu
		self.screen.fill(self.black)
		myfont = pygame.font.SysFont("monospace", 72)
		title_label = myfont.render("Pong", 1, self.white)
		myfont = pygame.font.SysFont("monospace", 32)
		select_label = myfont.render("Select a number of players:", 1, self.white)
		oneOrTwo_label = myfont.render("1 or 2", 1, self.white)
		self.screen.blit(title_label, (220, 100))
		self.screen.blit(select_label, (60, 250))
		self.screen.blit(oneOrTwo_label, (250, 300))
		pygame.display.flip()
		
		# wait for the user to select 1 or 2 player mode
		key = -1
		while key != 1 and key != 2:
			key = self.waitForKey()
			
		# 2 player mode selected
		if key == 2:
			# send 2 player mode notification to server
			self.transport.write("two players")
			
			#draw waiting for p2 screen
			self.screen.fill(self.black)
			myfont = pygame.font.SysFont("monospace", 32)
			connected_label = myfont.render("CONNECTED TO SERVER", 1, self.white)
			waiting_label = myfont.render("WAITING FOR PLAYER 2", 1, self.white)
			self.screen.blit(connected_label, (120, 100))
			self.screen.blit(waiting_label, (112, 200))
			pygame.display.flip()

		# 1 player mode selected
		elif key == 1:
			# display select difficulty screen
			self.screen.fill(self.black)
			myfont = pygame.font.SysFont("monospace", 32)
			top_label = myfont.render("SELECT DIFFICULTY", 1, self.white)
			difficulty_label = myfont.render("0 1 2 3 4 5 6 7 8 9", 1, self.white)
			self.screen.blit(top_label, (120, 100))
			self.screen.blit(difficulty_label, (112, 200))
			pygame.display.flip()
			
			# wait for difficulty selection
			key = self.waitForKey()
			
			# notify server 1 player mode was selected and the difficulty
			self.transport.write("one player:" + str(key))
			
		# something went wrong
		else:
			pass
			
	# wait for a number key to be pressed
	def waitForKey(self):
		# event loop to wait for key press or quit
		while True:
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()
					reactor.stop()
				if event.type == KEYDOWN and event.key == K_0:
					return 0
				if event.type == KEYDOWN and event.key == K_1:
					return 1
				if event.type == KEYDOWN and event.key == K_2:
					return 2
				if event.type == KEYDOWN and event.key == K_3:
					return 3
				if event.type == KEYDOWN and event.key == K_4:
					return 4
				if event.type == KEYDOWN and event.key == K_5:
					return 5
				if event.type == KEYDOWN and event.key == K_6:
					return 6
				if event.type == KEYDOWN and event.key == K_7:
					return 7
				if event.type == KEYDOWN and event.key == K_8:
					return 8
				if event.type == KEYDOWN and event.key == K_9:
					return 9
		
	# game server severed connection
	def connectionLost(self, reason):
		# check we're not shutting down
		global exited
		if exited:
			return

		# give user message that the connection was lost
		self.screen.fill(self.black)
		myfont = pygame.font.SysFont("monospace", 32)
		win_label = myfont.render("GAME SERVER CONNECTION LOST", 1, self.white)
		myfont = pygame.font.SysFont("monospace", 24)
		exit_label = myfont.render("press any key to exit", 1, self.white)
		self.screen.blit(win_label, (100, 100))
		self.screen.blit(exit_label, (120, 200))
		pygame.display.flip()
	
		# wait 2 seconds then for user to press a key to exit
		# same as normal game exit, but have already lost the connection5
		exited = True
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
	
# connect to the game server
if __name__ == '__main__':
	reactor.connectTCP(server, port, ClientConnFactory())
	reactor.run()
