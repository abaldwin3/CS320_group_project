from flask_login import UserMixin
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship, subqueryload
from werkzeug.security import check_password_hash, generate_password_hash

from . import Base, Session
from .catalog import Catalog
from .decorator import with_session
from .model import Model
from .project import Provided


class HasFavoritesMixin:
    provided_association = Table('provided_association', Base.metadata,
    Column('users_id', Integer, ForeignKey('users.id')),
    Column('project_id', Integer, ForeignKey('provided.id')))       

    solicited_association = Table('solicited_association', Base.metadata,
        Column('users_id', Integer, ForeignKey('users.id')),
        Column('project_id', Integer, ForeignKey('solicited.id')))

    @declared_attr
    def provided_favorites(self):
        return relationship(
            "Provided",
            secondary=self.provided_association,
            lazy='subquery',
            passive_deletes=True)


    @declared_attr
    def solicited_favorites(self):
        return relationship(
            "Solicited",
            secondary=self.solicited_association,
            lazy='subquery',
            passive_deletes=True)

class User(Base, Model, HasFavoritesMixin, UserMixin):
    """A class that represents a single user account"""
    __tablename__ = 'users'
    username = Column(String, unique=True)
    password = Column(String)
    bio = Column(String)
    email = Column(String)
    contact_info = Column(String)
    name = Column(String)
    needs_review = Column(Boolean)
    can_post_solicited = Column(Boolean)
    can_post_provided = Column(Boolean)
    is_admin = Column(Boolean)

    @with_session
    def favorite_project(self, project, session=None):
        """Adds the given project to this user's list of favorite projects
        
        Args:
            project (Project): The project to add to this User's list of favorite projects

        Kwargs:
            session (Session): session to perform the query on. Supplied by decorator

        Raises:
            ValueError: If project is already in the catalog
        """
        if project.poster == self:
            user_to_use = project.poster
        else:
            user_to_use = self

        session.add(user_to_use)
        if type(project) is Provided:
            favorites_to_add = user_to_use.provided_favorites
        else:
            favorites_to_add = user_to_use.solicited_favorites

        if project in favorites_to_add:
            raise ValueError("Cannot add duplicate projects to the favorites catalog")
        else:
            favorites_to_add.append(project)

    @with_session
    def defavorite_project(self, project, session=None):
        """Adds the given project to this user's list of favorite projects
        
        Args:
            project (Project): The project to add to this User's list of favorite projects

        Kwargs:
            session (Session): session to perform the query on. Supplied by decorator
        """
        if project.poster == self:
            user_to_use = project.poster
        else:
            user_to_use = self

        session.add(user_to_use)
        try:
            if type(project) is Provided:
                user_to_use.provided_favorites.remove(project)
            else:
                user_to_use.solicited_favorites.remove(project)
        except ValueError as e:
            raise ValueError("Cannot defavorite project that is not favorited") from e


    def get_favorites_catalog(self):
        """Get all of the Projects this User has favorited as a Catalog

        Returns: A Catalog of all of this User's favorited projects
        """
        catalog = Catalog()
        catalog.projects.extend(self.provided_favorites)
        catalog.projects.extend(self.solicited_favorites)
        return catalog
    
    @with_session
    def sign_up(self, session=None):
        """Create a new user entry in the database. In order to sign up a User,
        a User object must first be created, with all of the fields except needs_review
        populated

        Kwargs:
            session (Session): session to perform the query on. Supplied by decorator

        Raises: 
            ValueError: If the username already exists in the database
        """
        self.needs_review = False #TODO: set this to true when we implement the review process
        self.password = generate_password_hash(self.password)
        session.add(self)

    @classmethod
    @with_session
    def log_in(cls, username, password, session=None):
        """Attempts to login a user with the given username and password
        
        Args:
            username (str): Username of user to log in
            password (str): Password of user to log in

        Kwargs:
            session (Session): session to perform the query on. Supplied by decorator

        Returns:
            The User object

        Raises:
            ValueError: If login fails due to incorrect username or password,
                        or if login fails due to user account requiring admin review
        """
        #try to log in
        result = session.query(User
            ).options(
                subqueryload(User.provided_favorites),
                subqueryload(User.solicited_favorites)
            ).filter_by(
                username=username,
                needs_review=False
            ).one_or_none()

        #If we don't suceed to log in, raise a useful error message
        if result:
            if check_password_hash(result.password, password):
                return result
            else:
                raise ValueError('Incorrect username of password')
        else:
            result = session.query(User).filter_by(username=username).one_or_none()
            if result:
                raise ValueError('User account requires review')
            else:
                raise ValueError('Incorrect username or password')

    @classmethod
    @with_session
    def get_by_id(cls, id, session=None):
        """Gets the User object with the specified id
        
        Args:
            id (int): id of User object to get

        Kwargs:
            session (Session): session to perform the query on. Supplied by decorator
        """
        return session.query(User).filter_by(id=id).one_or_none()
