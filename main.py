import os
import json
import pygame
from pygame.locals import *

from twisted.internet.protocol import Protocol, Factory
from twisted.internet.task import LoopingCall
from twisted.internet import reactor

from objects import Player, Ball

PLAYER_ONE_PORT = 40075
PLAYER_TWO_PORT = 40083

player_one_connected = False
player_two_connected = False
p1Server = None
p2Server = None

class GameSpace:
	def main(self):
		pygame.init()
		self.size = self.width, self.height = 640, 480
		"""
		self.black = 0, 0, 0
		self.white = 255, 255, 255
		self.red = 255, 0, 0
		self.screen = pygame.display.set_mode(self.size)
		"""
		self.speed = 4.0

		self.player1 = Player(40, self)
		self.player2 = Player(600, self)
		self.ball = Ball(self.speed)

		self.lc = LoopingCall(self.game_loop_iterate)
		self.lc.start(1.0/60)	
		#self.lc.stop()

	def game_loop_iterate(self):
		####
		# Check for exit
		####
		"""
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				os._exit(0)
		"""

		####
		# check current keydown
		####
		"""
		keys_pressed = pygame.key.get_pressed()
		if keys_pressed[pygame.K_UP]:
			self.player1.moveUp()
		if keys_pressed[pygame.K_DOWN]:
			self.player1.moveDown()
		"""

		####
		# Check for collision
		####
		if self.ball.y_pos <= self.ball.radius or self.ball.y_pos >= self.height - self.ball.radius:
			self.ball.hitWall()
		elif self.ball.x_pos - self.ball.radius <= self.player1.x_pos + (self.player1.width / 2.0):
			# ball is close to the right side of player 1
			if self.ball.y_pos >= self.player1.y_pos - (self.player1.height / 2.0) \
			   and self.ball.y_pos <= self.player1.y_pos + (self.player1.height / 2.0):
				 self.ball.hitPlayer(self.player1.y_pos, self.player1.height)
			else:
				self.player2.score += 1
				self.ball = Ball(self.speed)
		elif self.ball.x_pos + self.ball.radius >= self.player2.x_pos - (self.player2.width / 2.0):
			# ball is close to the right side of player 2
			if self.ball.y_pos >= self.player2.y_pos - (self.player2.height / 2.0) \
			   and self.ball.y_pos <= self.player2.y_pos + (self.player2.height / 2.0):
				 self.ball.hitPlayer(self.player2.y_pos, self.player2.height)
			else:
				self.player1.score += 1
				self.ball = Ball(self.speed)

		global p1Server, p2Server
		if p1Server.transport:
			p1Server.transport.write(self.to_json())
		else:
			print "p1 server has no transport yet"
		if p2Server.transport:
			p2Server.transport.write(self.to_json())
		else:
			print "p2 server has no transport yet"

		"""
		####
		# Update objects
		####
		self.player1.tick()
		self.player2.tick()
		self.ball.tick()

		####
		# Draw objects
		####
		self.screen.fill(self.black)
		pygame.draw.rect(self.screen, self.white, self.player1.getRect())
		pygame.draw.rect(self.screen, self.white, self.player2.getRect())
		pygame.draw.circle(self.screen, self.red, self.ball.getPos(), self.ball.radius)

		####
		# Draw Score
		####
		myfont = pygame.font.SysFont("monospace", 42)
		score_label = myfont.render(str(self.player1.score) + " | " + str(self.player2.score), 1, self.white)
		self.screen.blit(score_label, (260, 20))

		pygame.display.flip()
		"""

	def to_json(self):
		""" Creates a dictionary @gsData that represents the gamestate.
				Important for sending game data over our server so that a client
				can properly display the GameState
			  Returns: @gsData converted to json
		"""
		gsData = {
			"players": {
				"p1": self.player1.to_dict(),
				"p2": self.player2.to_dict(),
			},
			"ball": self.ball.to_dict()
		}
		return json.dumps(gsData)


class P1ServerFactory(Factory):
	def buildProtocol(self, addr):
		global p1Server
		p1Server = P1Server(addr)
		return p1Server

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
			gs = GameSpace()
			gs.main()

	def connectionLost(self, reason):
		print "Connection lost to player 1"
		global player_one_connected, player_two_connected
		player_one_connected = False

class P2ServerFactory(Factory):
	def buildProtocol(self, addr):
		global p2Server
		p2Server = P2Server(addr)
		return p2Server

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
			gs = GameSpace()
			gs.main()

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
