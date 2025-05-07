import logging
from configuration.gitops_connector import GitopsConnector
from configuration.gitops_config import GitOpsConfig

class GitOpsConnectorManager:
    """Manages configurations and the lifecycle of GitOpsConnector instances."""
    def __init__(self):
        self.connectors: dict[str, GitopsConnector] = {}

    def add_or_update_configuration(self, config: GitOpsConfig):
        """Add a new configuration or update an existing one."""
        existing_connector = self.connectors.get(config.name)

        if existing_connector:
            # Stop the background work if the configuration is being updated
            existing_connector.start_background_work()

        # Create a new connector for the updated configuration
        new_connector = GitopsConnector(config)
        self.connectors[config.name] = new_connector

        # Start background work
        new_connector.start_background_work()
        logging.debug(f"Configuration for {config.name} added/updated.")

    def remove_configuration(self, config: GitOpsConfig):
        """Remove a configuration and stop the associated connector."""
        connector = self.connectors.get(config.name)
        if connector:
            connector.stop_background_work()
            del self.connectors[config.name]
            logging.debug(f"Configuration for {config.name} removed.")

    def stop_all(self):
        """Stop all connectors when shutting down the operator."""
        for connector in self.connectors.values():
            connector.stop_background_work()
        logging.debug("All background work stopped.")

    def get_supported_gitops_connector(self, payload):
        """Get the gitops_connector object by payload."""
        for connector in self.connectors.values():
            if (connector.is_supported_message(payload)):
                return connector
        return None
