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
gs = None

class GameSpace:
	def main(self):
		self.size = self.width, self.height = 640, 480
		self.speed = 4.0

		self.player1 = Player(40, self)
		self.player2 = Player(600, self)
		self.ball = Ball(self.speed)

		self.lc = LoopingCall(self.game_loop_iterate)
		self.lc.start(1.0/60)	

	def game_loop_iterate(self):
		####
		# Check for collision
		####
		if self.ball.y_pos <= self.ball.radius or self.ball.y_pos >= self.height - self.ball.radius:
			self.ball.hitWall()
		elif self.ball.x_pos - self.ball.radius <= self.player1.x_pos + (self.player1.width / 2.0):
			# ball is close to the left side
			if self.ball.y_pos >= self.player1.y_pos - (self.player1.height / 2.0) \
			   and self.ball.y_pos <= self.player1.y_pos + (self.player1.height / 2.0):
				 self.ball.hitPlayer(self.player1.y_pos, self.player1.height)
			else:
				self.player2.score += 1
				self.ball = Ball(self.speed)
		elif self.ball.x_pos + self.ball.radius >= self.player2.x_pos - (self.player2.width / 2.0):
			# ball is close to the right side
			if self.ball.y_pos >= self.player2.y_pos - (self.player2.height / 2.0) \
			   and self.ball.y_pos <= self.player2.y_pos + (self.player2.height / 2.0):
				 self.ball.hitPlayer(self.player2.y_pos, self.player2.height)
			else:
				self.player1.score += 1
				self.ball = Ball(self.speed)

		####
		# Update objects
		####
		self.player1.tick()
		self.player2.tick()
		self.ball.tick()

		global p1Server, p2Server
		p1Server.transport.write(self.to_json() + "?")
		p2Server.transport.write(self.to_json() + "?")

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
		upPressed = data.split("?")[0].split("|")[0]
		downPressed = data.split("?")[0].split("|")[1]
		if int(upPressed):
			print "Player 1 should be moving up"
			gs.player1.moveUp()
		if int(downPressed):
			print "Player 1 should be moving down"
			gs.player1.moveDown()

	def connectionMade(self):
		print "Player 1 connected"
		global player_one_connected, player_two_connected
		player_one_connected = True
		if player_two_connected:
			print "Both players connected"
			global gs
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
		upPressed = data.split("?")[0].split("|")[0]
		downPressed = data.split("?")[0].split("|")[1]
		if int(upPressed):
			gs.player2.moveUp()
		if int(downPressed):
			gs.player2.moveDown()

	def connectionMade(self):
		print "Player 2 connected"
		global player_one_connected, player_two_connected
		player_two_connected = True
		if player_one_connected:
			print "Both players connected"
			global gs
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
