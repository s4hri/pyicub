"""YARP Bottle helper utilities.

This module provides static helper methods for working with YARP Bottles,
including conversion to/from Python lists.
"""

from __future__ import annotations

import yarp


class YarpBottleHelper:
    """Helper class for working with YARP Bottles.
    
    Provides static methods for common Bottle operations like
    converting to/from Python lists.
    """

    @staticmethod
    def bottle_to_list(bottle: yarp.Bottle) -> list[str]:
        """Convert a YARP Bottle to a list of strings.
        
        Args:
            bottle: The YARP Bottle to convert.
            
        Returns:
            A list of string tokens from the bottle.
            Returns empty list if bottle is None or invalid.
        """
        tokens: list[str] = []
        if bottle is None or not hasattr(bottle, "size"):
            return tokens

        for idx in range(bottle.size()):
            item = bottle.get(idx)
            if hasattr(item, "asString"):
                tokens.append(item.asString())
            else:
                tokens.append(str(item))

        return tokens

    @staticmethod
    def list_to_bottle(
        tokens: list[str],
        bottle: yarp.Bottle | None = None,
    ) -> yarp.Bottle:
        """Convert a list of strings to a YARP Bottle.
        
        Args:
            tokens: List of string tokens to add to bottle.
            bottle: Optional existing bottle to use. If None, creates new one.
                   If provided, the bottle is cleared before adding tokens.
            
        Returns:
            The bottle with the tokens added.
        """
        if bottle is None:
            bottle = yarp.Bottle()
        else:
            bottle.clear()

        for token in tokens:
            bottle.addString(token)

        return bottle

    @staticmethod
    def bottle_to_string(bottle: yarp.Bottle) -> str:
        """Convert a YARP Bottle to its string representation.
        
        Args:
            bottle: The YARP Bottle to convert.
            
        Returns:
            The string representation of the bottle.
        """
        if bottle is None:
            return ""
        return bottle.toString()
