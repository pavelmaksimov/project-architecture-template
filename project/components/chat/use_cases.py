import typing as t

from project.components.chat.enums import MessageTypeEnum
from project.components.user.schemas import UserCacheSchema
from project.datatypes import UserIdT, QuestionT, AnswerT, ChatIdT
from project.settings import Settings

if t.TYPE_CHECKING:
    from project.container import AllRepositories
    from project.components.chat.ai.agent import ChatAgent
    from project.components.user.service import QuotaService


class Chat:
    def __init__(
        self,
        repo: "AllRepositories",
        chat_agent: "ChatAgent",
        quota: "QuotaService",
    ):
        self.repo = repo
        self.chat_agent = chat_agent
        self.quota = quota

    def create_chat(self, user_id: UserIdT, title: str | None = None) -> ChatIdT:
        """
        Создать новый чат для пользователя.
        """
        with self.repo.transaction():
            chat = self.repo.chat.create(
                user_id=user_id,
                title=title or "Новый чат",
                is_active=True,
            )
            return chat.id

    def get_active_chat(self, user_id: UserIdT) -> ChatIdT:
        """
        Получить активный чат пользователя или создать новый.
        """
        with self.repo.transaction():
            chat = self.repo.chat.get_or_create_active_chat(user_id)
            return chat.id

    def ask(self, user_id: UserIdT, question: QuestionT, chat_id: ChatIdT | None = None) -> AnswerT:
        """
        Задать вопрос в чат. Вернет текст ответа от AI.
        """
        with self.repo.transaction():
            if chat_id is None:
                chat_id = self.get_active_chat(user_id)

            self.repo.message.save_user_message(user_id, chat_id, question)

            history_messages = self.repo.message.get_chat_history(
                user_id=user_id,
                chat_id=chat_id,
                limit=Settings().HISTORY_WINDOW,
            )

            answer_text = self.chat_agent.generate_answer(user_id, question, history_messages)

            self.repo.message.save_ai_message(user_id, chat_id, answer_text)

            self.repo.user_cache.save(user_id, UserCacheSchema(user_id=user_id))

            return answer_text

    def get_history(
        self, user_id: UserIdT, chat_id: ChatIdT | None = None, limit: int = 20
    ) -> list[dict[str, QuestionT | AnswerT]]:
        """
        Получить историю чата пользователя. Вернет список словарей с вопросами и ответами
        """
        messages = self.repo.message.get_chat_history(
            user_id=user_id,
            chat_id=chat_id,
            limit=limit,
        )

        history = []
        temp_question = None

        for msg in messages:
            if msg.message_type == MessageTypeEnum.USER:
                temp_question = QuestionT(msg.content)
            elif msg.message_type == MessageTypeEnum.AI and temp_question is not None:
                history.append({"question": temp_question, "answer": AnswerT(msg.content)})
                temp_question = None

        return history
