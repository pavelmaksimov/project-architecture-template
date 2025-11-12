from sqlalchemy import select

from project.components.base.repositories import ORMModelRepository, ORMRepository
from project.components.chat.models import QuestionModel, AnswerModel


class QuestionRepository(ORMModelRepository[QuestionModel]):
    _model = QuestionModel


class AnswerRepository(ORMModelRepository[AnswerModel]):
    _model = AnswerModel


class ChatRepository(ORMRepository):
    def get_history(self, user_id: int, *, limit: int):
        with self.get_session() as session:
            query = (
                select(
                    QuestionModel.content.label("question"),
                    AnswerModel.content.label("answer"),
                )
                .join(AnswerModel, QuestionModel.id == AnswerModel.question_id)
                .where(QuestionModel.user_id == user_id)
                .limit(limit)
            )
            return session.execute(query).mappings().all()
