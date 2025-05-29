from pydantic import BaseModel

from project.datatypes import UserIdT, QuestionT


class AskBody(BaseModel):
    user_id: UserIdT
    question: QuestionT
