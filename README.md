Final project for David Mattia and John Riordan

To play Pong, begin by running main.py on student03.cse.nd.edu.
Then, run 

		python player1.py 

on any local machine (making sure pygame and twisted are installed).
If you want to play against a CPU, select that option in the menu and select the CPU difficulty.
If you want to play against someone else, have them run 

		python player2.py 

on their machine and select that option in the menu.

Move your pong paddle up and down using the up and down arrows on your keyboard.
The goal of the game is to make the ball hit the other person's side and not let it hit your own.
The game is played to 10 points, at which point the game will display a winner and exit.

Scale and Complexity:
	Our networking was the most advanced of our features. Our networking allows for both single player and multiplayer modes of gameplay. Most importantly, our networking code is robust enough to run our game at 30fps - faster than the TCP stream sends data to our clients.  Our clients are intelligent enough to parse through this data and find what is needed to display the most recent version of the game without any hiccups.  It has error handling to account for partial json objects sent over the server and handles them gracefully while continuting the game.

	Within our game, we added complexity by having 10 different difficulty levels of AI in addition to having the two player mode. The AI moves smoothly and is beatable on all levels.
