# Uncolored Green Idea Game
A game where you get to build grammatical nonsense sentences like Chomsky did.

[Download game for Windows](https://drive.google.com/file/d/1EBuJQcmogfXuBO1a9Oq5UgpxvvKG98_W/view?usp=drive_link)

[Video demo](https://youtu.be/_x3nDgyR4fc)

### version 0.1.2

2024-03-11:
- Improved player experience: the ungrammatical choices should now be 'more ungrammatical': Changed the logic to determine ungrammaticality from the block-list to a white-list. 
- Added some more words.

### version 0.1.1

2024-03-10:
- Changed the title to Uncolored Green Idea Game.
- Added a debriefing at the end of each game.

### version 0.1.0

2024-03-10: Initially created the game.

## Source code issues

Known issues: 
- Some of the words in the corpus are POS-ambiguous. Game might say ungrammatical when the selected option can work with the sentence as another POS than the game thinks. 
- Game currently uses a block list method to determine whether a POS is grammatical or not at each step. The block list might not be able to block all possible continuations and some POSs may be considered ungrammatical when it's not. 

*For forkers: assets is missing images and sounds because of copyright issues, as well as the gensim pre-trained word2vec model because of size and copyright issues. Get a model from gensim in the .txt format [here](https://github.com/piskvorky/gensim-data) and put it in assets.*