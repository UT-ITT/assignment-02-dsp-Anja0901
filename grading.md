# Anja0901 (9/15P)

## 1 - Karaoke Game (4.5/7P)
* frequency detection works correctly and robustly
    * not really, continous input doesn't work that well (1.5P)
* the game is playable, doges not crash, and is (kind of) fun to play
    * we couldn't figure out why the red dot was there only at the beginning and whole game was a bit confusing (1P)
* the game tracks some kind of score for correctly sung notes
    * yep (1P)
* low latency between input and detection
    * yep (1P)


## 2 - Whistle Input (4.5/7P)
* upwards and downwards whistling is detected correctly and robustly
    * it's not robustly detected whether it's an up or down whistle (2P)
*  detection is robust against background noise
    * threshold is not the best, we can trigger the up and down prints with random talking (0.5P)
* low latency between input and detection
    * yep (1P)
* triggered key events work
    * yep (1P)


## Code-Quality and .venv used (0/1P)
* no requirements.txt
* no README.md
* no .venv used
* no microphone selection for whistle input
