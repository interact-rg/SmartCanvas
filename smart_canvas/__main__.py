""" __main__.py """

from .core import hmm
from .helpers import get_answer

def main():
    hmm()
    if get_answer():
        return

main()
