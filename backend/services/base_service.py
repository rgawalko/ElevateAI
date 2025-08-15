"""
Base Service Class

Provides common functionality and patterns for all service classes.
"""

from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any, Type, TypeVar
from uuid import UUID
import logging

# Generic type for model classes
ModelType = TypeVar('ModelType')

logger = logging.getLogger(__name__)


class BaseService:
    """
    Base service class providing common database operations and utilities.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logger
    
    def get_by_id(self, model_class: Type[ModelType], id: str) -> Optional[ModelType]:
        """
        Get a model instance by ID.
        """
        try:
            uuid_id = UUID(id)
            return self.db.query(model_class).filter(model_class.id == uuid_id).first()
        except ValueError:
            self.logger.error(f"Invalid UUID format: {id}")
            return None
        except Exception as e:
            self.logger.error(f"Error getting {model_class.__name__} by ID {id}: {e}")
            return None
    
    def get_by_user_id(self, model_class: Type[ModelType], user_id: str, **filters) -> List[ModelType]:
        """
        Get model instances by user ID with optional filters.
        """
        try:
            uuid_user_id = UUID(user_id)
            query = self.db.query(model_class).filter(model_class.user_id == uuid_user_id)
            
            # Apply additional filters
            for field, value in filters.items():
                if hasattr(model_class, field):
                    query = query.filter(getattr(model_class, field) == value)
            
            return query.all()
        except ValueError:
            self.logger.error(f"Invalid UUID format: {user_id}")
            return []
        except Exception as e:
            self.logger.error(f"Error getting {model_class.__name__} by user ID {user_id}: {e}")
            return []
    
    def create(self, model_class: Type[ModelType], data: Dict[str, Any]) -> Optional[ModelType]:
        """
        Create a new model instance.
        """
        try:
            instance = model_class(**data)
            self.db.add(instance)
            self.db.commit()
            self.db.refresh(instance)
            return instance
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error creating {model_class.__name__}: {e}")
            return None
    
    def update(self, instance: ModelType, data: Dict[str, Any]) -> Optional[ModelType]:
        """
        Update a model instance.
        """
        try:
            for field, value in data.items():
                if hasattr(instance, field):
                    setattr(instance, field, value)
            
            self.db.commit()
            self.db.refresh(instance)
            return instance
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error updating {instance.__class__.__name__}: {e}")
            return None
    
    def delete(self, instance: ModelType) -> bool:
        """
        Delete a model instance.
        """
        try:
            self.db.delete(instance)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error deleting {instance.__class__.__name__}: {e}")
            return False
    
    def paginate(self, query, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Paginate query results.
        """
        try:
            total = query.count()
            items = query.offset((page - 1) * per_page).limit(per_page).all()
            
            return {
                "items": items,
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": (total + per_page - 1) // per_page,
                "has_prev": page > 1,
                "has_next": page * per_page < total
            }
        except Exception as e:
            self.logger.error(f"Error paginating query: {e}")
            return {
                "items": [],
                "total": 0,
                "page": page,
                "per_page": per_page,
                "pages": 0,
                "has_prev": False,
                "has_next": False
            }
    
    def validate_user_ownership(self, instance: ModelType, user_id: str) -> bool:
        """
        Validate that a user owns a particular resource.
        """
        try:
            if not hasattr(instance, 'user_id'):
                return False
            
            return str(instance.user_id) == user_id
        except Exception as e:
            self.logger.error(f"Error validating user ownership: {e}")
            return False
    
    def safe_commit(self) -> bool:
        """
        Safely commit database changes with error handling.
        """
        try:
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error committing database changes: {e}")
            return False
    
    def bulk_create(self, model_class: Type[ModelType], data_list: List[Dict[str, Any]]) -> List[ModelType]:
        """
        Create multiple model instances in bulk.
        """
        try:
            instances = [model_class(**data) for data in data_list]
            self.db.add_all(instances)
            self.db.commit()
            
            for instance in instances:
                self.db.refresh(instance)
            
            return instances
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error bulk creating {model_class.__name__}: {e}")
            return []
