import asyncio
import json
import os
from playwright.async_api import async_playwright

# Automatically detect user's home directory 
home_dir = os.path.expanduser("~")
bot_path = os.path.join(home_dir, "chrome_bot_profile")

# Load form_data.json from the same directory as this script
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, "form_data.json")

with open(json_path, "r", encoding="utf-8") as f:
    config = json.load(f)

form_url = config["form_url"]
target_file_name = config["file_name"]
answers_map = config["answers"]
default_text = config.get("default_text", "Yes")
default_para = config.get("default_paragraph", "Completed")

# Search for the target file across common directories
def find_file_path(filename):
    search_folders = [
        os.path.join(home_dir, "Desktop"),
        os.path.join(home_dir, "Downloads"),
        os.path.join(home_dir, "Documents"),
        script_dir
    ]
    for folder in search_folders:
        if os.path.exists(folder):
            for root, dirs, files in os.walk(folder):
                if filename in files:
                    return os.path.join(root, filename)
    return None

file_to_upload = find_file_path(target_file_name)

if file_to_upload:
    print(f"File found at: {file_to_upload}")
else:
    print(f"Warning: '{target_file_name}' was not found in Desktop, Downloads, or Documents.")

def get_answer_for_question(q_text):
    q_lower = q_text.lower()
    for key, val in answers_map.items():
        if key.lower() in q_lower:
            return val
    return default_text

async def fill_current_page(page):
    question_blocks = page.locator("div[role='listitem']")
    count = await question_blocks.count()
    
    for i in range(count):
        block = question_blocks.nth(i)
        q_text = await block.inner_text()
        
        # Check for 'Add File' button
        add_file_btn = block.locator("div[role='button']").filter(has_text="Add File").first
        if await add_file_btn.count() > 0 and await add_file_btn.is_visible():
            if file_to_upload:
                print("Clicking 'Add File' button...")
                await add_file_btn.scroll_into_view_if_needed()
                await add_file_btn.evaluate("el => el.click()")
                await asyncio.sleep(4)
                
                browse_clicked = False
                for frame in page.frames:
                    browse_btn = frame.locator("button:has-text('Browse'), div[role='button']:has-text('Browse'), span:has-text('Browse')").first
                    if await browse_btn.count() > 0 and await browse_btn.is_visible():
                        print("Found 'Browse' button, selecting file...")
                        async with page.expect_file_chooser(timeout=15000) as fc_info:
                            await browse_btn.click(force=True)
                        file_chooser = await fc_info.value
                        await file_chooser.set_files(file_to_upload)
                        browse_clicked = True
                        break
                        
                if not browse_clicked:
                    print("Using coordinate fallback to click 'Browse'...")
                    viewport = page.viewport_size or {"width": 1280, "height": 800}
                    async with page.expect_file_chooser(timeout=15000) as fc_info:
                        await page.mouse.click(viewport["width"] / 2, viewport["height"] / 2 + 40)
                    file_chooser = await fc_info.value
                    await file_chooser.set_files(file_to_upload)
                    
                print("Uploading file, waiting 7 seconds...")
                await asyncio.sleep(7)
            continue

        # Short Answer
        text_input = block.locator("input.whsOnd").first
        if await text_input.count() > 0 and await text_input.is_visible():
            await text_input.fill(get_answer_for_question(q_text))
            continue

        # Paragraph
        textarea = block.locator("textarea.KHxj8b").first
        if await textarea.count() > 0 and await textarea.is_visible():
            ans = get_answer_for_question(q_text)
            await textarea.fill(ans if ans != default_text else default_para)
            continue

        # Multiple Choice (Radio)
        radios = block.locator("div[role='radio']")
        if await radios.count() > 0:
            ans = get_answer_for_question(q_text)
            target_option = block.locator(f"//span[text()='{ans}']").first
            if await target_option.count() > 0:
                await target_option.click()
            else:
                await radios.first.click()
            continue

        # Checkbox
        checkboxes = block.locator("div[role='checkbox']")
        if await checkboxes.count() > 0:
            await checkboxes.first.click()

async def run():
    print("Launching Chrome browser...")
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=bot_path,
            channel="chrome",
            headless=False,
            ignore_default_args=["--enable-automation"],
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = await browser.new_page()
        print("Opening Google Form...")
        await page.goto(form_url, wait_until="domcontentloaded")
        await page.wait_for_selector("form")
        await asyncio.sleep(2)
        
        while True:
            print("Filling fields on the current page...")
            await fill_current_page(page)
            await asyncio.sleep(1)
            
            next_btn = page.locator("div[role='button']:has-text('Next')").first
            submit_btn = page.locator("div[role='button']:has-text('Submit')").first
            
            if await next_btn.count() > 0 and await next_btn.is_visible():
                print("Clicking 'Next' to proceed...")
                await next_btn.scroll_into_view_if_needed()
                await next_btn.click()
                await asyncio.sleep(3)
            elif await submit_btn.count() > 0 and await submit_btn.is_visible():
                print("Clicking 'Submit' button...")
                await submit_btn.scroll_into_view_if_needed()
                await submit_btn.click()
                print("Form submitted successfully!")
                break
            else:
                print("No 'Next' or 'Submit' button found. Stopping.")
                break
                
        await asyncio.sleep(4)
        await browser.close()
        print("Browser closed.")

if __name__ == "__main__":
    asyncio.run(run())
