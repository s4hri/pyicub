"""YARP network management utilities.

This module provides a wrapper class for YARP network initialization
and cleanup with context manager support.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import yarp

if TYPE_CHECKING:
    from typing import Any


class YarpNetwork:
    """Wrapper for YARP network initialization and cleanup.
    
    Provides explicit init/fini methods and context manager support
    for managing YARP network lifecycle.
    
    Example:
        Using explicit init/fini:
        
        >>> network = YarpNetwork()
        >>> network.init()
        >>> if network.is_available():
        ...     # do YARP operations
        ...     pass
        >>> network.fini()
        
        Using context manager:
        
        >>> with YarpNetwork() as network:
        ...     if network.is_available():
        ...         # do YARP operations
        ...         pass
    """

    def __init__(self) -> None:
        """Initialize the YarpNetwork wrapper (does not init YARP yet)."""
        self._initialized: bool = False

    @property
    def is_initialized(self) -> bool:
        """Return whether YARP network has been initialized."""
        return self._initialized

    def init(self) -> bool:
        """Initialize the YARP network.
        
        Safe to call multiple times - will only initialize once.
        
        Returns:
            True if initialization succeeded or already initialized.
        """
        if not self._initialized:
            yarp.Network.init()
            self._initialized = True
        return self._initialized

    def fini(self) -> None:
        """Finalize and cleanup the YARP network.
        
        Safe to call multiple times - will only finalize if initialized.
        """
        if self._initialized:
            yarp.Network.fini()
            self._initialized = False

    def is_available(self) -> bool:
        """Check if the YARP network is available.
        
        Returns:
            True if YARP name server is reachable, False otherwise.
        """
        return bool(yarp.Network.checkNetwork())

    def __enter__(self) -> "YarpNetwork":
        """Enter context manager - initializes YARP network."""
        self.init()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager - finalizes YARP network."""
        self.fini()
