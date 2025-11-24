Создавайте обработчики телеграма в таком виде.

Не нужно подавлять ошибки внутри обработчика, потому что декоратор processing_errors должен его 
перехватить и он является предпочтительным местом обработчик ошибок, являясь централизованным местом обработки ошибок, 
чтоб избежать дублирования кода по обработке ошибок в каждом обработчике.

{Объяснить каждый декоратор для телеграмма из project/infrastructure/utils/telegram.py}

Порядок декораторов важен!

```python
@check_auth
@timeout_with_retry
@processing_errors
@action_tracking_decorator("start_handler")
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = f"Привет {user_id}! Это пример обработчика Телеграм!"

    await update.message.reply_text(message)
```
