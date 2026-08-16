import asyncio
import logging
from app.vk_api.vk_client import VKClient
from app.settings import settings

logging.basicConfig(level=logging.DEBUG)


async def test_vk():
    client = VKClient(token=settings.vk_app.VK_API_TOKEN)  # type: ignore

    try:
        # 1. Проверяем настройки группы
        print("\n=== Проверка настроек группы ===")
        params = {
            "group_id": settings.vk_app.VK_GROUP_ID,
            "fields": "messages,longpoll",
        }
        result = await client._request("groups.getById", params)
        print(f"Группа: {result}")

        # 2. Проверяем права токена
        print("\n=== Проверка прав токена ===")
        result = await client._request("account.getAppPermissions", {})
        print(f"Права: {result}")

        # 3. Проверяем LongPoll
        print("\n=== Проверка LongPoll ===")
        lp_data = await client.get_longpoll_server()
        print(f"LongPoll данные: {lp_data}")

        # 4. Проверяем последние сообщения
        print("\n=== Проверка последних сообщений ===")
        params = {"group_id": settings.vk_app.VK_GROUP_ID, "count": 5}
        result = await client._request("messages.getConversations", params)
        print(f"Диалоги: {result}")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(test_vk())
