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
	""" An instance of a Pong game
		
		The data within any gamespace can be sent to a client for displaying
	"""
	def __init__(self, cpu_player=0, cpu_difficulty=0):
		self.size = self.width, self.height = 640, 480
		self.speed = 12.0

		# cpu_player 0 means both are human
		# cpu_player 1 means player 1 is a cpu
		# cpu_player 2 means player 2 is a cpu
		if cpu_player == 1:
			global player_one_connected
			player_one_connected = True
			self.player1 = Player(40, self, True)
			self.player2 = Player(600, self, False)
		elif cpu_player == 2:
			global player_two_connected
			player_two_connected = True
			self.player1 = Player(40, self, False)
			self.player2 = Player(600, self, True)
		else:
			self.player1 = Player(40, self, False)
			self.player2 = Player(600, self, False)

		# Choose the difficulty
		try:
			difficulty = int(cpu_difficulty)
			if self.player1.is_cpu:
				self.player1.cpu_movementAmount = self.player1.movementAmount * difficulty / 7.0
			if self.player2.is_cpu:
				self.player2.cpu_movementAmount = self.player2.movementAmount * difficulty / 7.0
		except ValueError, e:
			self.player2.cpu_movementAmount = self.player2.movementAmount

		self.ball = Ball(self.speed)

		self.lc = LoopingCall(self.game_loop_iterate)
		self.lc.start(1.0/30) # 30 fps	

	def ballIsToTheWall(self):
		""" Determines if the ball's y_pos is close to a wall
		"""
		return self.ball.y_pos <= self.ball.radius or self.ball.y_pos >= self.height - self.ball.radius

	def ballIsCloseToPlayer1(self):
		""" Determines if the ball's position is being hit by player 1
		"""
		return self.ball.x_pos - self.ball.radius <= self.player1.x_pos + (self.player1.width / 2.0) \
			and self.ball.x_pos - self.ball.radius >= self.player1.x_pos - (self.player1.width / 2.0) \
			and self.ball.y_pos >= self.player1.getBottom() \
			and self.ball.y_pos <= self.player1.getTop()

	def ballIsCloseToPlayer2(self):
		""" Determines if the ball's position is being hit by player 2
		"""
		return self.ball.x_pos + self.ball.radius <= self.player2.x_pos + (self.player2.width / 2.0) \
			and self.ball.x_pos + self.ball.radius >= self.player2.x_pos - (self.player2.width / 2.0) \
			and self.ball.y_pos >= self.player2.getBottom() \
			and self.ball.y_pos <= self.player2.getTop()

	def game_loop_iterate(self):
		""" Main game loop. Called at a rate of 30 fps.
		"""
		global p1Server, p2Server

		####
		# Check for collision
		####
		if self.ballIsToTheWall():
			self.ball.hitWall()
		elif self.ballIsCloseToPlayer1():
			self.ball.hitPlayer(self.player1.y_pos, self.player1.height)
		elif self.ballIsCloseToPlayer2():
			self.ball.hitPlayer(self.player2.y_pos, self.player2.height)
		elif self.ball.x_pos <= 0:
			self.player2.score += 1
			self.ball = Ball(self.speed)
		elif self.ball.x_pos >= self.width:
			self.player1.score += 1
			self.ball = Ball(self.speed)

		####
		# Check if anyone won
		####
		if self.player1.score == 10:
			p1Server.transport.write("p1 win")
			if not self.player2.is_cpu:
				p2Server.transport.write("p1 win")
		elif self.player2.score == 10:
			p1Server.transport.write("p2 win")
			if not self.player2.is_cpu:
				p2Server.transport.write("p2 win")

		####
		# Update objects
		####
		self.player1.tick(self.ball.y_pos)
		self.player2.tick(self.ball.y_pos)
		self.ball.tick()

		####
		# Send updated data to clients
		#
		# Add a ? after so that individual json objects
		# can be parsed if multiple json objects are
		# send in the same TCP packet
		####
		if not self.player1.is_cpu:
			p1Server.transport.write(self.to_json() + "?")
		if not self.player2.is_cpu:
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
		""" Called when player one sends data back to the server
		"""
		global gs
		global player_one_connected, player_two_connected
		# data.split(":")[-1] is the difficulty the player chose to play against in single player
		if "one player:" in data:
			gs = GameSpace(2, data.split(":")[-1])
		elif data == "two players":
			player_one_connected = True
			if player_two_connected:
				print "Both players connected"
				gs = GameSpace(0)
		else:
			# Any other data received means that the data is keypress data from active gameplay
			try:
				upPressed = data.split("?")[0].split("|")[0]
				downPressed = data.split("?")[0].split("|")[1]
			except IndexError, e:
				return
			try:
				if int(upPressed) and not gs.player1.is_cpu:
					gs.player1.moveUp()
				if int(downPressed) and not gs.player1.is_cpu:
					gs.player1.moveDown()
			except ValueError, e:
				return

	def connectionMade(self):
		print "Player 1 connected"

	def connectionLost(self, reason):
		""" Called when player 1 loses connection.  Automatically forfeits for player 1
		"""
		print "Connection lost to player 1"
		global player_one_connected, player_two_connected, gs, p2Server
		player_one_connected = False
		if gs.player1.score < 10 and gs.player2.score < 10:
			p2Server.transport.write("p1 forfeit")

class P2ServerFactory(Factory):
	def buildProtocol(self, addr):
		global p2Server
		p2Server = P2Server(addr)
		return p2Server

class P2Server(Protocol):
	def __init__(self, addr):
		self.addr = addr

	def dataReceived(self, data):
		""" Called when player two sends data back to the server
		"""
		global gs
		global player_one_connected, player_two_connected
		# data.split(":")[-1] is the difficulty the player chose to play against in single player
		if "one player:" in data:
			gs = GameSpace(2, data.split(":")[-1])
		elif data == "two players":
			player_two_connected = True
			if player_one_connected:
				print "Both players connected"
				gs = GameSpace()
		else:
			# Any other data received means that the data is keypress data from active gameplay
			try:
				upPressed = data.split("?")[0].split("|")[0]
				downPressed = data.split("?")[0].split("|")[1]
			except IndexError, e:
				return
			try:
				if int(upPressed) and not gs.player2.is_cpu:
					gs.player2.moveUp()
				if int(downPressed) and not gs.player2.is_cpu:
					gs.player2.moveDown()
			except ValueError, e:
				return

	def connectionMade(self):
		print "Player 2 connected"
		global player_one_connected, player_two_connected
		player_two_connected = True
		if player_one_connected:
			print "Both players connected"
			global gs
			gs = GameSpace()

	def connectionLost(self, reason):
		""" Called when player 2 loses connection.  Automatically forfeits for player 2
		"""
		print "Connection lost to player 2"
		global player_one_connected, player_two_connected, gs, p1Server
		player_two_connected = False
		if gs.player1.score < 10 and gs.player2.score < 10:
			p1Server.transport.write("p2 forfeit")


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
