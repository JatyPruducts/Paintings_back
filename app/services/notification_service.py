from telegram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.crud.crud_feedback import feedback as crud_feedback
from app.crud.crud_painting import painting as crud_painting
from app.db.session import SessionLocal  # фабрика сессий

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

async def send_feedback_notification(feedback_id: int):
    # Открываем новую сессию для фоновой задачи
    async with SessionLocal() as db:
        fb = await crud_feedback.get(db, id=feedback_id)
        p = await crud_painting.get(db, id=fb.painting_id)

    text = (
        "У вас новая заявка на обратную связь!\n"
        f"🖼 Артикул: {p.id}\n"
        f"👤 Пользователь: {fb.user_name}\n"
        f"📱 Телефон: {fb.phone_number}"
    )
    try:
        await bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=text)
    except Exception as e:
        # Логируем ошибку для дальнейшего расследования
        print(f"[Notification Error] {e}")