"""Base YARP port wrapper.

This module provides an abstract base class for YARP port wrappers
with common open/close functionality and context manager support.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


class BaseYarpPort(ABC):
    """Abstract base class for YARP port wrappers.
    
    Provides common functionality for opening, closing, and managing
    YARP ports with consistent naming and lifecycle management.
    
    Subclasses must implement `_create_port()` to return the appropriate
    YARP port type (e.g., yarp.Port, yarp.RpcClient, yarp.BufferedPort).
    
    Example:
        >>> class MyClient(BaseYarpPort):
        ...     def _create_port(self):
        ...         return yarp.RpcClient()
        ...
        >>> client = MyClient("/myclient")
        >>> if client.open():
        ...     # use the port
        ...     client.close()
    """

    def __init__(self, port_name: str) -> None:
        """Initialize the port wrapper.
        
        Args:
            port_name: The name for this YARP port (e.g., '/myport').
                      Leading '/' is added automatically if missing.
        """
        self._port_name = self._sanitize_port_name(port_name)
        self._port: Any = None
        self._is_open: bool = False

    @property
    def port_name(self) -> str:
        """Return the port name."""
        return self._port_name

    @property
    def is_open(self) -> bool:
        """Return whether the port is currently open."""
        return self._is_open

    @property
    def port(self) -> Any:
        """Return the underlying YARP port object."""
        return self._port

    @abstractmethod
    def _create_port(self) -> Any:
        """Create the underlying YARP port.
        
        Must be implemented by subclasses to return the appropriate
        YARP port type.
        
        Returns:
            A YARP port object (e.g., yarp.Port, yarp.RpcClient).
        """
        ...

    def open(self) -> bool:
        """Open the YARP port.
        
        Creates the port if not already created and opens it with
        the configured port name.
        
        Returns:
            True if port opened successfully, False otherwise.
        """
        if self._is_open:
            return True

        self._port = self._create_port()
        if self._port.open(self._port_name):
            self._is_open = True
            return True
        return False

    def close(self) -> None:
        """Close the YARP port.
        
        Safe to call multiple times - only closes if open.
        """
        if self._port is not None and self._is_open:
            self._port.close()
            self._is_open = False

    @staticmethod
    def _sanitize_port_name(name: str) -> str:
        """Ensure port name starts with '/'.
        
        Args:
            name: The port name to sanitize.
            
        Returns:
            The port name with leading '/' if not already present.
        """
        return name if name.startswith("/") else f"/{name}"

    def __enter__(self) -> "BaseYarpPort":
        """Enter context manager - opens the port."""
        self.open()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager - closes the port."""
        self.close()
