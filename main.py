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
		self.screen = pygame.display.set_mode(self.size)

		self.player1 = Player(40)
		self.player2 = Player(600)
		self.ball = Ball(5.0)

		lc = LoopingCall(self.game_loop_iterate)
		lc.start(1.0/60)	
		reactor.run()
		lc.stop()

	def game_loop_iterate(self):
		print("Game loop running")
		self.player1.tick()
		self.player2.tick()
		self.ball.tick()

		# Draw objects
		self.screen.fill(self.black)
		pygame.draw.rect(self.screen, self.white, self.player1.getRect())
		pygame.draw.rect(self.screen, self.white, self.player2.getRect())
		pygame.draw.circle(self.screen, self.white, self.ball.getPos(), self.ball.radius)

		pygame.display.flip()

	def to_json(self):
		pass

if __name__ == '__main__':
	gs = GameSpace()
	gs.main()
