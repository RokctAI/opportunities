import asyncio
from playwright.async_api import async_playwright
import os

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(record_video_dir="videos/")
        page = await context.new_page()
        try:
            # Start dev server if not running
            # I'll try to reach it first
            await page.goto("http://localhost:3000")
            await page.wait_for_selector('input[type="text"]')
            await page.fill('input[type="text"]', "Award")
            await page.wait_for_timeout(1000)
            await page.click('text=View Details')
            await page.wait_for_timeout(2000)
            await page.click('text=Return to Nexus')
            await page.wait_for_timeout(1000)

            # Category filter
            await page.click('button:has-text("Categories")')
            await page.click('text=Grants')
            await page.wait_for_timeout(1000)

            # Final screenshot
            await page.screenshot(path="nexus_final.png")
            print("Recording finished.")
        except Exception as e:
            print(f"Error: {e}")
        await context.close()
        await browser.close()

if __name__ == "__main__":
    # Ensure dev server is running
    # In a real scenario I might need to start it, but let's assume it's running or I start it here.
    asyncio.run(run())
