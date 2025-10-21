from project.domains.base.repositories import ORMModelRepository
from project.domains.user import models


class UserRepository(ORMModelRepository[models.User]):
    _model = models.User
