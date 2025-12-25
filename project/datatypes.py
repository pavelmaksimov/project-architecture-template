import typing as t

UserIdT = t.NewType("UserIdT", t.Annotated[int, "User ID"])
ChatIdT = t.NewType("ChatIdT", t.Annotated[int, "Chat ID"])
MessageIdT = t.NewType("MessageIdT", t.Annotated[int, "Message ID"])
AnswerT = t.NewType("AnswerT", t.Annotated[str, "Ответ пользователю"])
QuestionT = t.NewType("QuestionT", t.Annotated[str, "Вопрос пользвоателя"])
