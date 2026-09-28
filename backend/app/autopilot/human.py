import asyncio
import random


async def human_delay(min_s: float = 1.2, max_s: float = 3.5):
    await asyncio.sleep(random.uniform(min_s, max_s))


async def human_type(locator, text: str):
    await locator.click()
    for ch in text:
        await locator.type(ch, delay=random.randint(30, 120))
    await asyncio.sleep(random.uniform(0.2, 0.6))


async def human_mouse_move(page):
    x = random.randint(200, 1200)
    y = random.randint(200, 800)
    await page.mouse.move(x, y, steps=random.randint(8, 20))