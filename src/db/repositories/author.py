from src.db.models import Author
from src.db.repositories.abstract import Repository


class AuthorRepository(Repository):
    model = Author
