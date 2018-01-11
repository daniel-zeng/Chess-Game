# Chess Game

A chess game, playable with GUI or Console input with algebraic notation. 

Running the game:
```
python main.py
```

### Dependencies:
In order to run it requires Python 3 and Pillow
```
pip install -r requirements.txt
```


### GUI:
GUI built with Tkinter<br>
<img src="/img/chesspic1.jpg" alt="Chess Gam" width="50%">

### Integration with Stockfish:
Download the binaries from <a href="https://stockfishchess.org/download/">Stockfish</a> for your operating system and move it to the root directory.

### Custom Engine:
Custom engine built with standard chess AI techniques: 
1. Minimax tree search with Alpha-Beta pruning
2. Position evaluation through piece square tables and piece values

### Sources:
Image assets: <a href="https://en.wikipedia.org/wiki/User:Cburnett">Colin M.L. Burnett</a> (CC, GFDL, BSD, GPL)
<br>Piece-square tables from <a href="https://github.com/thomasahle/sunfish">Sunfish</a>
