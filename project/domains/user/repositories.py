from project.domains.base.repositories import ORMModelRepository
from project.domains.user import models


class UserRepository(ORMModelRepository[models.UserModel]):
    _model = models.UserModel
