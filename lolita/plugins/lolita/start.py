import config

from pyrogram import filters, types, enums

from lolithabot import self


@self.on_message(filters.command("start"))
async def start_message(_, m: types.Message):
    if m.chat.type == enums.ChatType.PRIVATE:
        text = (
            "👋🏻 <b>Welcome {}</b>\n\n"
            "💭 @lolithaMusicRobot will give you the ability to <b>listen to songs</b> "
            "Telegram Group <b>video chat</b> feature !"
        )
        await m.reply_text(
            text.format(m.from_user.mention()), 
            parse_mode=enums.parse_mode.ParseMode.HTML,
            reply_markup=types.InlineKeyboardMarkup(
            [[types.InlineKeyboardButton("ℹ️ Information", callback_data="ingfo")]])
        )
    else:
        await m.reply_text("Process 2%..")


@self.on_callback_query(filters.regex(pattern=r"ingfo"))
async def info_maszeh(_, callback: types.CallbackQuery):
    await callback.answer("This bot still in development, expected to finish in about 4 years.", show_alert=True)
