import sys 
import os
import pygame
from pygame.locals import *

from twisted.internet.protocol import Protocol
from twisted.internet.task import LoopingCall
from twisted.internet import reactor

from objects import Player, Ball

class GameSpace:
	def main(self):
		pygame.init()
		self.size = self.width, self.height = 640, 480
		self.black = 0, 0, 0
		self.white = 255, 255, 255
		self.red = 255, 0, 0
		self.screen = pygame.display.set_mode(self.size)

		self.player1 = Player(40)
		self.player2 = Player(600)
		self.ball = Ball(5.0)

		lc = LoopingCall(self.game_loop_iterate)
		lc.start(1.0/60)	
		reactor.run()
		lc.stop()

	def game_loop_iterate(self):
		####
		# Check for exit
		####
		for event in pygame.event.get():
			if event.type == QUIT:
				sys.exit()

		####
		# Check for collision
		####
		if self.ball.y_pos <= self.ball.radius or self.ball.y_pos >= self.height - self.ball.radius:
			self.ball.hitWall()
		elif self.ball.x_pos - self.ball.radius <= self.player1.x_pos + (self.player1.width / 2.0):
			# ball is close to the right side of player 1
			print "Ball is close to player1's x value"
			if self.ball.y_pos >= self.player1.y_pos - (self.player1.height / 2.0) \
			   and self.ball.y_pos <= self.player1.y_pos + (self.player1.height / 2.0):
				 self.ball.hitPlayer(self.player1.y_pos, self.player1.height)
		elif self.ball.x_pos + self.ball.radius >= self.player2.x_pos - (self.player2.width / 2.0):
			# ball is close to the right side of player 2
			print "Ball is close to player2's x value"
			if self.ball.y_pos >= self.player2.y_pos - (self.player2.height / 2.0) \
			   and self.ball.y_pos <= self.player2.y_pos + (self.player2.height / 2.0):
				 self.ball.hitPlayer(self.player2.y_pos, self.player2.height)

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

		pygame.display.flip()

	def to_json(self):
		pass

if __name__ == '__main__':
	gs = GameSpace()
	gs.main()
