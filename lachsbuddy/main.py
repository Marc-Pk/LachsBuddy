'''main file for code execution'''
from processing import *

if __name__ == "__main__":
    # check if config is initialized properly
    startup_checks()

    # outer loop for listening to background chatter
    while True:
        run_in_background()
