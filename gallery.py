
from config import *
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from db import Base, Session, Stamp

# Define Tag model and association table if not present
tag_association = Table(
    'stamp_tags', Base.metadata,
    Column('stamp_id', Integer, ForeignKey('stamps.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    stamps = relationship('Stamp', secondary=tag_association, back_populates='tags')

Stamp.tags = relationship('Tag', secondary=tag_association, back_populates='stamps')


def search_stamps(query="", filters={}):
    """Search stamps by query string and filters.
    
    Args:
        query (str): Search term to match against country and description fields
        filters (dict): Additional filters, currently supports 'tags' key with list of tag names
        
    Returns:
        list: List of Stamp objects matching the search criteria
        
    Note:
        Uses parameterized queries to prevent SQL injection attacks.
    """
    session = Session()
    try:
        q = session.query(Stamp)
        if query:
            # Validate and sanitize the query input
            if not isinstance(query, str):
                raise ValueError("Query must be a string")
            
            # Sanitize the query by removing potentially dangerous characters
            # Allow only alphanumeric characters, spaces, and common punctuation
            import re
            sanitized_query = re.sub(r'[^\w\s\-\.\,\(\)]', '', query.strip())
            
            if sanitized_query:
                # Create the search pattern - SQLAlchemy will handle this as a parameter
                search_pattern = f"%{sanitized_query}%"
                q = q.filter(Stamp.country.ilike(search_pattern) | Stamp.description.ilike(search_pattern))
        
        if filters.get("tags"):
            # Validate that tags is a list to prevent injection through this parameter
            tags = filters["tags"]
            if not isinstance(tags, list):
                raise ValueError("Tags filter must be a list")
            
            # Validate each tag name to ensure it's a string and not malicious
            validated_tags = []
            for tag in tags:
                if not isinstance(tag, str):
                    raise ValueError("Each tag must be a string")
                # Sanitize tag names - allow only alphanumeric characters, spaces, and hyphens
                import re
                sanitized_tag = re.sub(r'[^\w\s\-]', '', tag.strip())
                if sanitized_tag:  # Only add non-empty tags
                    validated_tags.append(sanitized_tag)
            
            if validated_tags:
                # Use SQLAlchemy's in_() method which properly handles parameterization
                q = q.join(Stamp.tags).filter(Tag.name.in_(validated_tags))
        
        return q.all()
    finally:
        session.close()


def add_tag(stamp_id, tag_name):
    """Add a tag to a stamp.
    
    Args:
        stamp_id (int): ID of the stamp to tag
        tag_name (str): Name of the tag to add
        
    Raises:
        ValueError: If inputs are invalid
        RuntimeError: If stamp is not found
    """
    session = Session()
    try:
        # Validate inputs
        if not isinstance(stamp_id, int) or stamp_id <= 0:
            raise ValueError("Stamp ID must be a positive integer")
        if not isinstance(tag_name, str):
            raise ValueError("Tag name must be a string")
        
        # Sanitize tag name
        import re
        sanitized_tag_name = re.sub(r'[^\w\s\-]', '', tag_name.strip())
        if not sanitized_tag_name:
            raise ValueError("Tag name cannot be empty after sanitization")
        
        # Get the stamp
        stamp = session.query(Stamp).get(stamp_id)
        if not stamp:
            raise RuntimeError(f"Stamp with ID {stamp_id} not found")
        
        # Get or create the tag
        tag = session.query(Tag).filter_by(name=sanitized_tag_name).first()
        if not tag:
            tag = Tag(name=sanitized_tag_name)
            session.add(tag)
            session.commit()  # Commit to get the tag ID
        
        # Add tag to stamp if not already present
        if tag not in stamp.tags:
            stamp.tags.append(tag)
            session.commit()
    finally:
        session.close()
