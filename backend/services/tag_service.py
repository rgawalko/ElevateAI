"""
Tag Service

Handles all tag-related business logic including tag management,
activity tagging, and tag analytics.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from typing import Optional, Dict, Any, List
import uuid

from .base_service import BaseService
from models import Tag, ActivityTag, ActivityLog


class TagService(BaseService):
    """
    Service for tag management operations.
    """
    
    def __init__(self, db: Session):
        super().__init__(db)
    
    def create_tag(self, user_id: str, name: str, color: str = None, description: str = None) -> Optional[Tag]:
        """
        Create a new tag for a user.
        """
        try:
            # Check if tag already exists
            existing_tag = self.get_tag_by_name(user_id, name)
            if existing_tag:
                self.logger.warning(f"Tag '{name}' already exists for user {user_id}")
                return existing_tag
            
            tag_data = {
                'user_id': uuid.UUID(user_id),
                'name': name.strip(),
                'color': color,
                'description': description
            }
            
            tag = Tag(**tag_data)
            self.db.add(tag)
            self.db.commit()
            self.db.refresh(tag)
            
            self.logger.info(f"Created tag '{name}' for user {user_id}")
            return tag
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error creating tag: {e}")
            return None
    
    def get_tag_by_name(self, user_id: str, name: str) -> Optional[Tag]:
        """
        Get tag by name for a specific user.
        """
        try:
            uuid_id = uuid.UUID(user_id)
            return self.db.query(Tag).filter(
                and_(
                    Tag.user_id == uuid_id,
                    Tag.name == name.strip()
                )
            ).first()
        except Exception as e:
            self.logger.error(f"Error getting tag by name: {e}")
            return None
    
    def get_or_create_tag(self, user_id: str, name: str, color: str = None) -> Optional[Tag]:
        """
        Get existing tag or create new one if it doesn't exist.
        """
        try:
            tag = self.get_tag_by_name(user_id, name)
            if tag:
                return tag
            
            return self.create_tag(user_id, name, color)
            
        except Exception as e:
            self.logger.error(f"Error getting or creating tag: {e}")
            return None
    
    def get_user_tags(self, user_id: str, include_usage_count: bool = False) -> List[Dict[str, Any]]:
        """
        Get all tags for a user, optionally with usage counts.
        """
        try:
            uuid_id = uuid.UUID(user_id)
            
            if include_usage_count:
                # Get tags with usage counts
                tags_with_counts = self.db.query(
                    Tag,
                    func.count(ActivityTag.id).label('usage_count')
                ).outerjoin(ActivityTag).filter(
                    Tag.user_id == uuid_id
                ).group_by(Tag.id).order_by(desc('usage_count')).all()
                
                return [
                    {
                        **tag.to_dict(),
                        'usage_count': usage_count
                    }
                    for tag, usage_count in tags_with_counts
                ]
            else:
                # Get tags without usage counts
                tags = self.db.query(Tag).filter(
                    Tag.user_id == uuid_id
                ).order_by(Tag.name).all()
                
                return [tag.to_dict() for tag in tags]
                
        except Exception as e:
            self.logger.error(f"Error getting user tags: {e}")
            return []
    
    def update_tag(self, tag_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[Tag]:
        """
        Update tag information.
        """
        try:
            uuid_tag_id = uuid.UUID(tag_id)
            uuid_user_id = uuid.UUID(user_id)
            
            tag = self.db.query(Tag).filter(
                and_(
                    Tag.id == uuid_tag_id,
                    Tag.user_id == uuid_user_id
                )
            ).first()
            
            if not tag:
                return None
            
            # Check if name is being changed and doesn't conflict
            if 'name' in update_data and update_data['name'] != tag.name:
                existing_tag = self.get_tag_by_name(user_id, update_data['name'])
                if existing_tag and existing_tag.id != tag.id:
                    self.logger.warning(f"Tag name '{update_data['name']}' already exists")
                    return None
            
            return self.update(tag, update_data)
            
        except Exception as e:
            self.logger.error(f"Error updating tag: {e}")
            return None
    
    def delete_tag(self, tag_id: str, user_id: str) -> bool:
        """
        Delete tag and remove all associations.
        """
        try:
            uuid_tag_id = uuid.UUID(tag_id)
            uuid_user_id = uuid.UUID(user_id)
            
            tag = self.db.query(Tag).filter(
                and_(
                    Tag.id == uuid_tag_id,
                    Tag.user_id == uuid_user_id
                )
            ).first()
            
            if not tag:
                return False
            
            # Delete associated activity tags first
            self.db.query(ActivityTag).filter(
                ActivityTag.tag_id == uuid_tag_id
            ).delete()
            
            # Delete the tag
            return self.delete(tag)
            
        except Exception as e:
            self.logger.error(f"Error deleting tag: {e}")
            return False
    
    def get_tag_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get tag usage statistics.
        """
        try:
            uuid_id = uuid.UUID(user_id)
            
            # Get total tags
            total_tags = self.db.query(Tag).filter(Tag.user_id == uuid_id).count()
            
            # Get tag usage statistics
            tag_usage = self.db.query(
                Tag.name,
                Tag.color,
                func.count(ActivityTag.id).label('usage_count')
            ).outerjoin(ActivityTag).filter(
                Tag.user_id == uuid_id
            ).group_by(Tag.id, Tag.name, Tag.color).order_by(
                desc('usage_count')
            ).all()
            
            # Get unused tags
            unused_tags = [tag for tag in tag_usage if tag.usage_count == 0]
            
            # Get most popular tags
            popular_tags = [
                {
                    'name': tag.name,
                    'color': tag.color,
                    'usage_count': tag.usage_count
                }
                for tag in tag_usage[:10] if tag.usage_count > 0
            ]
            
            return {
                'total_tags': total_tags,
                'unused_tags_count': len(unused_tags),
                'popular_tags': popular_tags,
                'average_usage': sum(tag.usage_count for tag in tag_usage) / max(total_tags, 1)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting tag statistics: {e}")
            return {}
    
    def get_activities_by_tag(self, user_id: str, tag_name: str, limit: int = 20) -> List[ActivityLog]:
        """
        Get activities associated with a specific tag.
        """
        try:
            uuid_id = uuid.UUID(user_id)
            
            activities = self.db.query(ActivityLog).join(
                ActivityTag
            ).join(Tag).filter(
                and_(
                    ActivityLog.user_id == uuid_id,
                    Tag.name == tag_name
                )
            ).order_by(desc(ActivityLog.date)).limit(limit).all()
            
            return activities
            
        except Exception as e:
            self.logger.error(f"Error getting activities by tag: {e}")
            return []
    
    def merge_tags(self, user_id: str, source_tag_id: str, target_tag_id: str) -> bool:
        """
        Merge one tag into another, moving all associations.
        """
        try:
            uuid_user_id = uuid.UUID(user_id)
            uuid_source_id = uuid.UUID(source_tag_id)
            uuid_target_id = uuid.UUID(target_tag_id)
            
            # Verify both tags belong to the user
            source_tag = self.db.query(Tag).filter(
                and_(Tag.id == uuid_source_id, Tag.user_id == uuid_user_id)
            ).first()
            
            target_tag = self.db.query(Tag).filter(
                and_(Tag.id == uuid_target_id, Tag.user_id == uuid_user_id)
            ).first()
            
            if not source_tag or not target_tag:
                return False
            
            # Update all activity tags to point to target tag
            self.db.query(ActivityTag).filter(
                ActivityTag.tag_id == uuid_source_id
            ).update({'tag_id': uuid_target_id})
            
            # Delete the source tag
            self.db.delete(source_tag)
            
            self.db.commit()
            
            self.logger.info(f"Merged tag '{source_tag.name}' into '{target_tag.name}'")
            return True
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error merging tags: {e}")
            return False
    
    def suggest_tags(self, user_id: str, activity_content: str, limit: int = 5) -> List[str]:
        """
        Suggest tags based on activity content and user's existing tags.
        """
        try:
            # Get user's existing tags
            user_tags = self.get_user_tags(user_id, include_usage_count=True)
            
            # Simple keyword matching (in production, this could use ML)
            content_lower = activity_content.lower()
            suggestions = []
            
            for tag_data in user_tags:
                tag_name = tag_data['name'].lower()
                if tag_name in content_lower or any(word in content_lower for word in tag_name.split()):
                    suggestions.append({
                        'name': tag_data['name'],
                        'confidence': tag_data.get('usage_count', 0)
                    })
            
            # Sort by confidence (usage count) and return top suggestions
            suggestions.sort(key=lambda x: x['confidence'], reverse=True)
            return [s['name'] for s in suggestions[:limit]]
            
        except Exception as e:
            self.logger.error(f"Error suggesting tags: {e}")
            return []
