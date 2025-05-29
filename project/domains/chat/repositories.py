from sqlalchemy import select

from project.domains.chat import models
from project.domains.base.repository import Repository, BaseRepository


class QuestionRepository(Repository):
    _model = models.Question


class AnswerRepository(Repository):
    _model = models.Answer


class ChatRepository(BaseRepository):
    AnswerModel = models.Answer
    QuestionModel = models.Question

    def get_history(self, user_id: int, *, limit: int):
        with self.get_session() as session:
            query = (
                select(
                    self.QuestionModel.content.label("question"),
                    self.AnswerModel.content.label("answer"),
                )
                .join(self.AnswerModel, self.QuestionModel.id == self.AnswerModel.question_id)
                .where(self.QuestionModel.user_id == user_id)
                .limit(limit)
            )
            return session.execute(query).mappings().all()
