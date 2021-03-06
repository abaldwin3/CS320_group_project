from .project import Solicited, Provided, Project
from .decorator import with_session

class Catalog:
    def __init__(self, search_term='', select_provided=True, **kwargs):
        """A catalog is a list of projects selected from all projects stored in the database.

        Args:
            search_term (str): text to search for in the projects
            select_provided (bool): Set to true to generate a list of provided projects,
                                    or false to generate a list of solicited projects
            kwargs: All of the filters to apply to the search
        """ 
        self.search_term = search_term
        self.filters = kwargs
        self.projects = []

        self.table_to_search = Provided if select_provided else Solicited
    
    @with_session
    def apply(self, session=None):
        """Apply the search and build the list of projects. 
        TODO: actually apply the search term and filters

        Kwargs:
            session (Session): session to perform the query on. Supplied by decorator
        """
        self.projects = session.query(self.table_to_search).filter_by(**self.filters)\
            .filter(self.table_to_search.title.like(f'%{self.search_term}%')).all()

    def __contains__(self, item):
        """Overrides the 'in' operator"""
        return item in self.projects

    def __getitem__(self, key):
        """Makes Catalog iterable, and projects can be accessed like a list"""
        try:
            return self.projects[key]
        except Exception as e:
            raise IndexError('Catalog index out of range') from e
