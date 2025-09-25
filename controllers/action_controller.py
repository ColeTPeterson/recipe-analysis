"""Provides controllers for managing cooking actions in recipes;
mediates between action repositories and domain models.
"""

import logging
from typing import List, Optional, Dict

from models.instruction import Action, ActionArity
from repositories.mariadb.action_repository import ActionRepository

logger = logging.getLogger(__name__)


class ActionController:
    """Mediates between action repositories and domain models,
    providing a higher-level interface for action-related operations.
    """
    
    def __init__(self):
        """Initialize the action controller with required dependencies."""
        self.repository = ActionRepository()

    # Read Operations
    def get_all_actions(self) -> List[Action]:
        """Get all actions in the system.
        
        Returns:
            List[Action]: List of all available actions
        """
        try:
            return self.repository.get_all()
        except Exception as e:
            logger.error(f"Error retrieving all actions: {e}")
            return []

    def get_action_by_id(self, action_id: int) -> Optional[Action]:
        """Get an action by ID.
        
        Args:
            action_id (int): ID of the action to retrieve
            
        Returns:
            Optional[Action]: The action if found, None otherwise
        """
        try:
            return self.repository.get_by_id(action_id)
        except Exception as e:
            logger.error(f"Error retrieving action {action_id}: {e}")
            return None

    def get_all_action_identities(self) -> List[str]:
        """Get all action identities.
        
        Returns:
            List[str]: List of all action identity names
        """
        return self.repository.get_all_action_identities()
    
    def get_all_action_properties(self) -> List[str]:
        """Get all action property keys.
        
        Returns:
            List[str]: List of all action property keys
        """
        return self.repository.get_all_action_properties()
    
    # Search Operations
    def find_actions_by_name(self, name: str) -> List[Action]:
        """Find actions by name.
        
        Args:
            name (str): Name or partial name to search for
            
        Returns:
            List[Action]: List of matching actions
        """
        try:
            return self.repository.find_by_name(name)
        except Exception as e:
            logger.error(f"Error searching actions by name '{name}': {e}")
            return []

    def find_actions_by_arity(self, arity: ActionArity) -> List[Action]:
        """Find actions by their arity.
        
        Args:
            arity (ActionArity): The arity to search for
            
        Returns:
            List[Action]: List of actions with the specified arity
        """
        try:
            return self.repository.find_by_arity(arity)
        except Exception as e:
            logger.error(f"Error searching actions by arity {arity}: {e}")
            return []
    
    def find_action_identities_by_name(self, name_pattern: str) -> List[str]:
        """Find action identities by name pattern.
        
        Args:
            name_pattern (str): Pattern to search for
            
        Returns:
            List[str]: List of matching action identity names
        """
        return self.repository.find_action_identities_by_name(name_pattern)
    
    def find_action_properties_by_name(self, name_pattern: str) -> List[str]:
        """Find action property keys by name pattern.
        
        Args:
            name_pattern (str): Pattern to search for
            
        Returns:
            List[str]: List of matching action property keys
        """
        return self.repository.find_action_properties_by_name(name_pattern)

    # Create/Update/Delete Operations
    def create(self, action: Action) -> Optional[Action]:
        """Add a new action to the system.
        
        Args:
            action (Action): The action to add
            
        Returns:
            Optional[Action]: The added action with ID assigned, or None if failed
        """
        try:
            return self.repository.create(action)
        except Exception as e:
            logger.error(f"Error creating action: {e}")
            return None

    def update(self, action: Action) -> bool:
        """Update an existing action.
        
        Args:
            action (Action): The action to update
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        if not action.entity_id:
            logger.error("Cannot update action without ID")
            return False
            
        try:
            updated = self.repository.update(action)
            return updated is not None
        except Exception as e:
            logger.error(f"Error updating action: {e}")
            return False
        
    def delete(self, action_id: int) -> bool:
        """Delete an action.
        
        Args:
            action_id (int): ID of the action to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            return self.repository.delete(action_id)
        except Exception as e:
            logger.error(f"Error deleting action {action_id}: {e}")
            return False

    # Analysis Methods
    def get_actions_by_complexity(self) -> dict:
        """Get actions grouped by their complexity (arity).
        
        Returns:
            dict: Dictionary with arity as key and list of actions as value
        """
        try:
            all_actions = self.get_all_actions()
            complexity_groups = {}
            
            for action in all_actions:
                arity = action.arity if action.arity else ActionArity.VARIABLE
                if arity not in complexity_groups:
                    complexity_groups[arity] = []
                complexity_groups[arity].append(action)
            
            return complexity_groups
        except Exception as e:
            logger.error(f"Error grouping actions by complexity: {e}")
            return {}

    def get_action_statistics(self) -> dict:
        """Get statistics about actions in the system.
        
        Returns:
            dict: Dictionary containing action statistics
        """
        try:
            all_actions = self.get_all_actions()
            total_count = len(all_actions)
            
            arity_counts = {}
            for action in all_actions:
                arity = action.arity if action.arity else ActionArity.VARIABLE
                arity_counts[arity] = arity_counts.get(arity, 0) + 1
            
            return {
                'total_actions': total_count,
                'arity_distribution': arity_counts,
                'most_common_arity': max(arity_counts, key=arity_counts.get) if arity_counts else None
            }
        except Exception as e:
            logger.error(f"Error getting action statistics: {e}")
            return {}

    def get_all_action_property_values(self) -> Dict[str, List[str]]:
        """Get all action property keys and their values.
        
        Returns:
            Dict[str, List[str]]: Dictionary with property keys as keys and list of values as values
        """
        return self.repository.get_all_action_property_values()
