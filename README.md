# Chess-Variant-AI

## Rationale  

I wrote a Python program with a GUI that allows users to create custom variants of chess and play them locally against humans or an AI opponent. 
(AI was added after A-Level project so is currently not included in documentation, The documentation refers to the file Mutable Chess which does not include an AI opponent, to play with AI use the current version, Mutable Chess Experimental.)  

Rationale: The future of AI research is developing general agents that can learn and perform well at multiple tasks.  In order to better understand general agents, I aimed to create an AI that could learn to play any variant of chess at a high standard.
Users can:   
  
•	adjust the height, width, and shape of the board  
•	decide how the pieces are set up  
•	create new pieces with different movement  
•	choose between multiple win conditions  

Additionally, many prominent chess players have noted that they are now forced to rely on memorising opens and preparing lines to stay competitive, rather than using their skill of calculation and finding creative moves. A solution to this is to play variants, such as [Fischer Random Chess](https://en.wikipedia.org/wiki/Fischer_random_chess) (proposed by Bobby Fischer in 1996 for the aforementioned reason) where the back rank is randomly shuffled, creating a new, unstudied position in each game. The ability to rapidly create and play unseen variants was also a large motivation for this project.

## User Guide  

### Naviagting the program:  
When given items listed numerically, type in the number of the item you wish to select
When asked a binary question type 'yes' to confirm or enter anything else to deny

Upon starting the program you will be promtped with 5 options:  
1. Play default (this will start a normal game of chess)
2. Play Fischer Random+ (This allows you to play a variant of Fischer Random chess where you are able to choose the heigh and width of the board before the game starts)  
3. Create ruleset (This will allow you to create a ruleset by defining new pieces, choosing the win codnition, the dimensions of the board and then setting up the board. Once done, you are able to name it and it will be saved in NEA\Code\Presets.)   
4. Delete ruleset (Delete an existing ruleset.)  
5. Play custom  (select an existing ruleset to play.)

### Pieces:  
Piece movement is represented by 2-dimensional vectors. These can be interpreted in two ways:
1:As a leaping vector, in which case the piece can move once by that vector in all directions
2:As a riding vector, in which case the piece can move infinitely by that vector until it is blocked.
(so a knight is a [1,2] leaper and a bishop is a [1,1] rider
A piece's status can either be common or royal. The properties of royal pieces are dependent on the game's win condition

### Win conditions:  
1:Checkmate: the standard rules of Chess, games can result in checkmate on any royal piece for either side or stalemate
2:Regicide: the laws of check do not apply, if an enemy royal is captured, the game is won
3:King of the Hill: Same as the Checkmate but with hill squares which give victory to a player that moves their royal piece onto the hill.
4:Extinction: The laws of check do not apply, all enemy pieces must be captured to win.
Custom rulesets are not playable unless there are sufficient pieces for the win condition to be achieved.

## AI  

When starting a game, you will be prompted on whether to make either of the players AI.
If you choose to do so, you will then be asked which engine depth to use (1-5). Higher engine depths play significantly better (depth 4 will win BishopKnight Mate) but take much longer to make a move. This varies depending on the number of pieces and size of the board (possible to moves to consider). In the interest of time, I would recommend only using higher engine depths, such as 4 or 5, on boards smaller than 8x8. The speed of play is the main aspect of the program I aim to improve. I wrote it in python for uniformity, but plan to rewrite in a language that can perform calculations faster.  

It currently works using heuristic functions that value pieces using their range of movement on the board in use (statically defined at the start of the game) and their current range of movement and pieces they can interact with (dynamically calculated at the start of each turn). Then Min Max with Alpha Beta pruning is used to review possible positions n-turns ahead (where n = engine depth) and decide the best move.

There is one program I am aware of that includes an AI that can play Chess Variants however it is unable to evaluate pieces by itself so you have to tell it how strong each piece is for it to be able to play well https://home.hccnet.nl/h.g.muller/CVfairy.html (Under rules, start of paragraph 3). Instead of using preset piece values like traditional chess AI systems, my program calculates the relative value of pieces by assessing the movement capabilities on the type of board being used in general, and each specific position that arises. As far as I am aware my piece evaluation system is novel.

## Future  

In addition to writing the engine in a faster languag, in the future, I would like to improve with an evolutionary machine learning algorithm (create many AIs, randomise their weightings to different heuristics within a small range, have them play each other in a tournament until one emerges as the victor, use the victor to seed the next generation and repeat to find optimal weightings)

Work in progress, to learn more about the project, go into the NEA folder and read the pdf documents
