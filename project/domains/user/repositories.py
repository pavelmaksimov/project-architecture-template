from project.domains.base.repositories import Repository
from project.domains.user import models


class UserRepository(Repository[models.User]):
    _model = models.User
