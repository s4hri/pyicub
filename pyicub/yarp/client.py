"""Base RPC client for YARP applications.

This module provides a base class for building RPC clients that
connect to YARP RPC servers with consistent patterns.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import yarp

from pyicub.yarp.port import BaseYarpPort
from pyicub.yarp.bottle import YarpBottleHelper

if TYPE_CHECKING:
    from pyicub.core.logger import YarpLogger


class BaseRpcClient(BaseYarpPort):
    """Base class for YARP RPC clients.
    
    Provides common functionality for RPC clients including:
    - Port management (inherited from BaseYarpPort)
    - Connection to remote RPC server
    - Send/receive command pattern
    
    Subclasses should add application-specific command methods
    that call `send()` with appropriate arguments.
    
    Example:
        >>> class MyClient(BaseRpcClient):
        ...     def my_command(self) -> str:
        ...         return self.send("mycommand", "arg1")
        ...
        >>> client = MyClient("/myclient", "/myserver/rpc")
        >>> if client.open() and client.connect():
        ...     response = client.my_command()
        ...     client.close()
    
    Attributes:
        server_port: The remote server port name to connect to.
        is_connected: Whether currently connected to the server.
    """

    # Subclasses can override with their own logger
    _logger: "YarpLogger | None" = None

    def __init__(
        self,
        client_port: str,
        server_port: str,
    ) -> None:
        """Initialize the RPC client.
        
        Args:
            client_port: Local port name for this client.
            server_port: Remote server port to connect to.
        """
        super().__init__(client_port)
        self._server_port = self._sanitize_port_name(server_port)
        self._connected: bool = False

    @property
    def server_port(self) -> str:
        """Return the server port name."""
        return self._server_port

    @property
    def is_connected(self) -> bool:
        """Return whether connected to the server."""
        return self._connected

    def _create_port(self) -> yarp.RpcClient:
        """Create the underlying YARP RpcClient port."""
        return yarp.RpcClient()

    def connect(self, server_port: str | None = None) -> bool:
        """Connect to the RPC server.
        
        Args:
            server_port: Optional server port to connect to.
                        Uses configured server_port if not specified.
                        
        Returns:
            True if connection succeeded, False otherwise.
        """
        if not self.is_open:
            self._log_error("Cannot connect: port is not open")
            return False

        target = self._sanitize_port_name(server_port) if server_port else self._server_port
        if yarp.Network.connect(self._port_name, target):
            self._connected = True
            self._log_debug(f"Connected to {target}")
            return True

        self._log_error(f"Failed to connect to {target}")
        return False

    def disconnect(self) -> None:
        """Disconnect from the RPC server."""
        if self._connected:
            yarp.Network.disconnect(self._port_name, self._server_port)
            self._connected = False
            self._log_debug(f"Disconnected from {self._server_port}")

    def close(self) -> None:
        """Close the client, disconnecting first if connected."""
        self.disconnect()
        super().close()

    def send(self, *tokens: str) -> str:
        """Send a command and receive response.
        
        Args:
            *tokens: Command tokens to send.
            
        Returns:
            The response string from the server.
            
        Raises:
            RuntimeError: If port is not open or send fails.
        """
        if not self.is_open:
            raise RuntimeError("Port is not open")

        bottle_out = YarpBottleHelper.list_to_bottle(list(tokens))
        bottle_in = yarp.Bottle()

        self._log_debug(f"Sending: {bottle_out.toString()}")

        if not self._port.write(bottle_out, bottle_in):
            raise RuntimeError("Failed to send command to server")

        response = bottle_in.toString()
        self._log_debug(f"Received: {response}")
        return response

    def send_quit(self) -> str:
        """Send quit command to the server.
        
        Returns:
            Response from the server.
        """
        return self.send("quit")

    # Logging helpers that check if logger is available
    def _log_debug(self, msg: str) -> None:
        if self._logger:
            self._logger.debug(msg)

    def _log_info(self, msg: str) -> None:
        if self._logger:
            self._logger.info(msg)

    def _log_error(self, msg: str) -> None:
        if self._logger:
            self._logger.error(msg)
