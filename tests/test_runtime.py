import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock


def test_combined_runtime_registers_menu_preserves_updates_and_closes(client, monkeypatch):
    import bot as bot_module
    import webapp.main as main
    fake = AsyncMock()
    fake.get_me.return_value = SimpleNamespace(username="itlive_test_bot")
    dispatcher = AsyncMock()

    async def polling(*args, **kwargs):
        await asyncio.Event().wait()

    dispatcher.start_polling.side_effect = polling
    monkeypatch.setattr(main, "RUN_BOT", True)
    monkeypatch.setattr(main, "APP_URL", "https://itlive.example.com")
    monkeypatch.setattr(main, "Bot", lambda *args, **kwargs: fake)
    monkeypatch.setattr(bot_module, "create_dispatcher", lambda: dispatcher)

    async def run():
        async with main.lifespan(main.app):
            await asyncio.sleep(0)
            assert main.app.state.bot_username == "itlive_test_bot"
            assert len(main.app.state.runtime_tasks) == 3

    asyncio.run(run())
    assert fake.set_chat_menu_button.call_args.kwargs["menu_button"].web_app.url == "https://itlive.example.com"
    fake.delete_webhook.assert_awaited_once_with(drop_pending_updates=False)
    fake.session.close.assert_awaited_once()


def test_actual_dispatcher_and_webapp_reply_keyboard_are_compatible(client, monkeypatch):
    import bot as bot_module
    import keyboards.reply
    monkeypatch.setattr(keyboards.reply, "APP_URL", "https://itlive.example.com")
    dp = bot_module.create_dispatcher()
    assert len(dp.sub_routers) == 8
    keyboard = keyboards.reply.get_main_keyboard(is_admin=True)
    assert keyboard.keyboard[0][0].web_app.url == "https://itlive.example.com"
    assert keyboard.is_persistent
