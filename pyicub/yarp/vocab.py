"""YARP vocabulary constants.

This module defines common YARP vocabulary constants used across
RPC interfaces for standard commands.
"""

import yarp

# Standard vocabulary constants for RPC commands
VOCAB_QUIT = yarp.createVocab32(ord("q"), ord("u"), ord("i"), ord("t"))
VOCAB_HELP = yarp.createVocab32(ord("h"), ord("e"), ord("l"), ord("p"))
VOCAB_ACK = yarp.createVocab32(ord("a"), ord("c"), ord("k"), 0)
VOCAB_NACK = yarp.createVocab32(ord("n"), ord("a"), ord("c"), ord("k"))
