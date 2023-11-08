# Chess-Variant-AI

I wrote a Python program with a GUI that allows users to create custom variants of chess and play them locally against humans or an AI opponent. 
(AI was added after A-Level project so is currently not included in documentation) 
Rationale: The future of AI research is developing general agents that can learn and perform well at multiple tasks.  In order to better understand general agents, I aimed to create an AI that could learn to play any variant of chess at a high standard.
Users can: 
•	adjust the height, width, and shape of the board
•	decide how the pieces are set up
•	create new pieces with different movement
•	choose between multiple win conditions
Currently the AI uses a minmax algorithm with alpha beta pruning and some heuristics I have created with my own knowledge of chess variants. In the future, I would like to improve with an evolutionary machine learning algorithm (create many AIs, randomise their weightings to different heuristics within a small range, have them play each other in a tournament until one emerges as the victor, use the victor to seed the next generation and repeat to find optimal weightings). 
There is one program I am aware of that does a similar thing however it is unable to evaluate pieces by itself so you have to tell it how strong each piece is for it to be able to play well https://home.hccnet.nl/h.g.muller/CVfairy.html (Under rules, start of paragraph 3).
Instead of using preset piece values like traditional chess AI systems, my program calculates the relative value of pieces by assessing the movement capabilities on the type of board being used in general, and each specific position that arises. As far as I am aware my piece evaluation system is novel. 


Work in progress, to learn more about the project, go into the NEA folder and read the pdf documents
