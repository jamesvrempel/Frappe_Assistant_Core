from typing import Any, Dict
import frappe
import json

class ConnectionManager:
    """Handles WebSocket and HTTP connections for the assistant server."""

    def __init__(self):
        self.connections = {}

    def add_connection(self, client_id: str, connection: Any) -> None:
        """Add a new connection to the manager."""
        self.connections[client_id] = connection
        frappe.log("Connection added: {}".format(client_id))

    def remove_connection(self, client_id: str) -> None:
        """Remove a connection from the manager."""
        if client_id in self.connections:
            del self.connections[client_id]
            frappe.log("Connection removed: {}".format(client_id))

    def get_connection(self, client_id: str) -> Any:
        """Get a connection by client ID."""
        return self.connections.get(client_id)

    def broadcast(self, message: Dict[str, Any]) -> None:
        """Send a message to all connected clients."""
        for client_id, connection in self.connections.items():
            try:
                connection.send(json.dumps(message))
            except Exception as e:
                frappe.log_error("Error sending message to {}: {}".format(client_id, str(e)))

    def cleanup(self) -> None:
        """Clean up closed connections."""
        closed_connections = [client_id for client_id, connection in self.connections.items() if not connection.is_open()]
        for client_id in closed_connections:
            self.remove_connection(client_id)