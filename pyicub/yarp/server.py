"""Base RFModule server for YARP applications.

This module provides a base class for building YARP RFModule servers
with consistent patterns for configuration, RPC handling, and lifecycle.
"""

from __future__ import annotations

import sys
from abc import abstractmethod
from typing import TYPE_CHECKING

import yarp

from pyicub.yarp.bottle import YarpBottleHelper
from pyicub.yarp.vocab import VOCAB_QUIT

if TYPE_CHECKING:
    from pyicub.core.logger import YarpLogger


DEFAULT_PERIOD = 1.0


class BaseRFModuleServer(yarp.RFModule):
    """Base class for YARP RFModule servers.
    
    Provides common functionality for RFModule-based servers including:
    - Port management and RPC attachment
    - Standard command handling (quit, period, help)
    - Configurable update period
    - Lifecycle management (configure, close, interrupt)
    
    Subclasses must implement:
    - `_get_default_module_name()`: Return default module name
    - `handle_command()`: Handle application-specific commands
    
    Optionally override:
    - `on_configure()`: Additional configuration after port setup
    - `on_update()`: Periodic update logic
    - `get_usage()`: Return help text for commands
    
    Example:
        >>> class MyServer(BaseRFModuleServer):
        ...     def _get_default_module_name(self) -> str:
        ...         return "/myserver"
        ...
        ...     def handle_command(self, cmd, tokens, reply) -> bool:
        ...         if cmd == "hello":
        ...             reply.addString("Hello!")
        ...             return True
        ...         return False  # Unknown command
        ...
        >>> server = MyServer()
        >>> # Configure and run with YARP ResourceFinder
    
    Attributes:
        module_name: The base name for YARP ports.
        period: The update period in seconds.
    """

    # Subclasses can override with their own logger
    _logger: "YarpLogger | None" = None

    def __init__(self, module_name: str | None = None) -> None:
        """Initialize the RFModule server.
        
        Args:
            module_name: Base name for YARP ports. If None, uses
                        the value from `_get_default_module_name()`.
        """
        yarp.RFModule.__init__(self)

        name = module_name if module_name else self._get_default_module_name()
        self._module_name = self._sanitize_name(name)
        self._handle_port: yarp.Port = yarp.Port()
        self._period: float = DEFAULT_PERIOD

    @property
    def module_name(self) -> str:
        """Return the module name."""
        return self._module_name

    @property
    def period(self) -> float:
        """Return the update period in seconds."""
        return self._period

    @period.setter
    def period(self, value: float) -> None:
        """Set the update period in seconds."""
        self._period = value

    @abstractmethod
    def _get_default_module_name(self) -> str:
        """Return the default module name.
        
        Must be implemented by subclasses.
        
        Returns:
            The default module name (e.g., '/mymodule').
        """
        ...

    @abstractmethod
    def handle_command(
        self,
        cmd: str,
        tokens: list[str],
        reply: yarp.Bottle,
    ) -> bool:
        """Handle application-specific RPC commands.
        
        Must be implemented by subclasses to handle their specific commands.
        
        Args:
            cmd: The command string (first token, lowercased).
            tokens: All command tokens including the command.
            reply: The reply bottle to fill with response.
            
        Returns:
            True if command was handled, False if unknown command.
        """
        ...

    def get_usage(self) -> str:
        """Return usage/help text for available commands.
        
        Override in subclasses to provide application-specific help.
        Base implementation lists standard commands.
        
        Returns:
            Help text string.
        """
        return "Commands: help | period [sec] | quit"

    def on_configure(self, rf: yarp.ResourceFinder) -> bool:
        """Called after base configuration succeeds.
        
        Override in subclasses to perform additional configuration.
        
        Args:
            rf: YARP ResourceFinder with configuration parameters.
            
        Returns:
            True if configuration succeeded, False otherwise.
        """
        return True

    def on_update(self) -> bool:
        """Called during each update cycle.
        
        Override in subclasses to perform periodic work.
        
        Returns:
            True to continue running, False to stop.
        """
        return True

    def configure(self, rf: yarp.ResourceFinder) -> bool:
        """Configure the module using resource finder parameters.
        
        Args:
            rf: YARP ResourceFinder with configuration parameters.
            
        Returns:
            True if configuration succeeded, False otherwise.
        """
        self._period = DEFAULT_PERIOD

        # Check for custom name in config
        if rf.check("name"):
            self._module_name = self._sanitize_name(rf.find("name").asString())

        # Check for custom period in config
        if rf.check("period"):
            self._period = rf.find("period").asFloat64()

        # Open the RPC port
        port_name = f"{self._module_name}/rpc"
        if not self._handle_port.open(port_name):
            self._log_error(f"Failed to open port {port_name}")
            return False

        # Attach RPC port for respond() callbacks
        self.attach(self._handle_port)
        self._log_info(f"Server configured, serving on {port_name}")

        # Call subclass configuration
        return self.on_configure(rf)

    def getPeriod(self) -> float:
        """Return the update period in seconds.
        
        Returns:
            The period between updateModule() calls.
        """
        return self._period

    def updateModule(self) -> bool:
        """Periodic update function called by the module framework.
        
        Returns:
            True to continue running, False to stop.
        """
        return self.on_update()

    def respond(self, command: yarp.Bottle, reply: yarp.Bottle) -> bool:
        """Handle incoming RPC commands.
        
        Handles standard commands (quit, period, help) and delegates
        application-specific commands to `handle_command()`.
        
        Args:
            command: The incoming command bottle.
            reply: The reply bottle to fill with response.
            
        Returns:
            True to continue running, False to stop the module.
        """
        self._log_debug(f"Received command: {command.toString()}")

        # Check for vocab-based quit command
        if command.size() > 0 and command.get(0).asVocab32() == VOCAB_QUIT:
            self._log_info("Quit command received (vocab)")
            reply.addString("bye")
            return False

        # Check for period command with property syntax
        if command.check("period"):
            self._period = command.find("period").asFloat64()
            reply.addString("ack")
            return True

        # Parse command tokens
        tokens = YarpBottleHelper.bottle_to_list(command)
        if not tokens:
            reply.addString(self.get_usage())
            return True

        cmd = tokens[0].lower()

        # Handle standard commands
        if cmd in ("quit", "exit"):
            self._log_info("Quit command received")
            reply.addString("bye")
            return False

        if cmd == "help":
            reply.addString(self.get_usage())
            return True

        if cmd == "period":
            if len(tokens) >= 2:
                try:
                    self._period = float(tokens[1])
                    reply.addString(f"Period set to {self._period}")
                except ValueError:
                    reply.addString("Invalid period value")
            else:
                reply.addString(f"Current period: {self._period}")
            return True

        # Delegate to subclass for application-specific commands
        if self.handle_command(cmd, tokens, reply):
            return True

        # Unknown command
        reply.addString(f"Unknown command: {cmd}. Type 'help' for usage.")
        return True

    def interruptModule(self) -> bool:
        """Handle module interruption for port cleanup.
        
        Returns:
            True if interruption was handled successfully.
        """
        self._log_warning("Interrupting module for port cleanup")
        return True

    def close(self) -> bool:
        """Close the module and cleanup resources.
        
        Returns:
            True if close was successful.
        """
        self._log_info("Closing server")
        self._handle_port.close()
        return True

    @staticmethod
    def _sanitize_name(name: str) -> str:
        """Ensure module name starts with '/'.
        
        Args:
            name: The module name to sanitize.
            
        Returns:
            The name with leading '/' if not already present.
        """
        return name if name.startswith("/") else f"/{name}"

    # Logging helpers that check if logger is available
    def _log_debug(self, msg: str) -> None:
        if self._logger:
            self._logger.debug(f"[{self._module_name}] {msg}")

    def _log_info(self, msg: str) -> None:
        if self._logger:
            self._logger.info(f"[{self._module_name}] {msg}")

    def _log_warning(self, msg: str) -> None:
        if self._logger:
            self._logger.warning(f"[{self._module_name}] {msg}")

    def _log_error(self, msg: str) -> None:
        if self._logger:
            self._logger.error(f"[{self._module_name}] {msg}")


def run_module(
    server_class: type[BaseRFModuleServer],
    argv: list[str] | None = None,
    logger: "YarpLogger | None" = None,
) -> int:
    """Run an RFModule server as a standalone application.
    
    Helper function to run any BaseRFModuleServer subclass with
    proper YARP network initialization and cleanup.
    
    Args:
        server_class: The server class to instantiate and run.
        argv: Command line arguments (uses sys.argv if None).
        logger: Optional logger for status messages.
        
    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    if argv is None:
        argv = sys.argv

    # Initialize YARP network
    yarp.Network.init()

    if not yarp.Network.checkNetwork():
        if logger:
            logger.error("YARP network not available")
        yarp.Network.fini()
        return 1

    # Create and configure the server
    server = server_class()
    rf = yarp.ResourceFinder()
    rf.configure(argv)

    if logger:
        logger.info("Configuring server...")

    if not server.configure(rf):
        yarp.Network.fini()
        return 1

    if logger:
        logger.info("Running server...")

    server.runModule()

    if logger:
        logger.info("Server stopped")

    yarp.Network.fini()
    return 0
