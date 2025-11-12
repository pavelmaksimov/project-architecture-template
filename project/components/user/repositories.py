from project.components.base.repositories import ORMModelRepository
from project.components.user import models


class UserRepository(ORMModelRepository[models.UserModel]):
    _model = models.UserModel
