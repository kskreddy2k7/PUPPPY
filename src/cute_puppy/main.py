import sys
import os

# Insert src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cute_puppy.app import main

if __name__ == "__main__":
    main()
