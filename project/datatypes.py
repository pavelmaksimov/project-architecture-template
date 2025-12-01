import typing as t

UserIdT = t.NewType("UserIdT", t.Annotated[int, "User ID"])
AnswerT = t.NewType("AnswerT", t.Annotated[str, "Ответ пользователю"])
QuestionT = t.NewType("QuestionT", t.Annotated[str, "Вопрос пользвоателя"])
