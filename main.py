import sys 
import os
import json
import pygame
from pygame.locals import *

from twisted.internet.protocol import Protocol
from twisted.internet.task import LoopingCall
from twisted.internet import reactor

from servers import *
from objects import Player, Ball

class GameSpace:
	def main(self):
		pygame.init()
		self.size = self.width, self.height = 640, 480
		self.black = 0, 0, 0
		self.white = 255, 255, 255
		self.red = 255, 0, 0
		self.screen = pygame.display.set_mode(self.size)
		self.speed = 4.0

		self.player1 = Player(40, self)
		self.player2 = Player(600, self)
		self.ball = Ball(self.speed)

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
				pygame.quit()
				os._exit(0)

		####
		# check current keydown
		####
		keys_pressed = pygame.key.get_pressed()
		if keys_pressed[pygame.K_UP]:
			self.player1.moveUp()
		if keys_pressed[pygame.K_DOWN]:
			self.player1.moveDown()

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
		print json.dumps(gsData)
		return json.dumps(gsData)

if __name__ == '__main__':
	gs = GameSpace()
	gs.main()
