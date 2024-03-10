# Uncolored Green Idea Game
A game where you get to build grammatical nonsense sentences like Chomsky did.

*assets is missing a file (the gensim pre-trained word2vec model). Get a model from gensim in the .txt format [here](https://github.com/piskvorky/gensim-data)*

Known issues: 
- Some of the words in the corpus are POS-ambiguous. Game might say ungrammatical when the selected option can work with the sentence as another POS than the game thinks. 
- Game currently uses a block list method to determine whether a POS is grammatical or not at each step. The block list might not be able to block all possible continuations and some POSs may be considered ungrammatical when it's not. 

### version 0.1.1

2024-03-10:
- Changed the title to Uncolored Green Idea Game.
- Added a debriefing at the end of each game.

### version 0.1.0

2024-03-10: Initially created the game.