import asyncio
import json
import logging
import random
from playwright.async_api import (
    async_playwright,
    Browser,
    Page,
    BrowserContext,
)

logger = logging.getLogger(__name__)


class BrowserHandler:
    def __init__(self, playwright_config, gologin_handler, proxy_handler=None):
        self.playwright_config = playwright_config
        self.gologin_handler = gologin_handler
        self.proxy_handler = proxy_handler
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        self.current_profile_id = None
        self.current_proxy_url = None

    async def launch_browser(self, profile_id, proxy_details=None):
        """
        Launches a browser instance via GoLogin and connects Playwright to it.
        profile_id: GoLogin profile ID.
        proxy_details: Dict from ProxyHandler like {"url": "socks5://...", "sid": "..."}
        """
        self.current_profile_id = profile_id

        if proxy_details and proxy_details.get("url"):
            self.current_proxy_url = proxy_details["url"]
            logger.info(
                "Attempting to launch browser with profile ID: %s and proxy: %s",
                profile_id,
                self.current_proxy_url,
            )
        else:
            logger.info(
                "Attempting to launch browser with profile ID: %s (no proxy or direct profile proxy)",
                profile_id,
            )

        extra_launch_params = []
        if self.playwright_config.get("headless", False):
            extra_launch_params.append("--headless=new")

        start_response = self.gologin_handler.start_profile_remote(
            profile_id, extra_params=extra_launch_params
        )
        if not start_response:
            logger.error("Failed to start GoLogin profile %s.", profile_id)
            return False

        ws_endpoint = None
        if isinstance(start_response, dict):
            if "wsEndpoint" in start_response:
                ws_endpoint = start_response["wsEndpoint"]
            elif "webSocketDebuggerUrl" in start_response:
                ws_endpoint = start_response["webSocketDebuggerUrl"]
            elif "port" in start_response:
                ws_endpoint = f"ws://127.0.0.1:{start_response['port']}/devtools/browser/{profile_id}"
            elif start_response.get("status") == "success" and isinstance(
                start_response.get("browserWSEndpoint"), str
            ):
                ws_endpoint = start_response.get("browserWSEndpoint")

        if not ws_endpoint:
            logger.error(
                "Could not determine WebSocket endpoint from GoLogin start response: %s",
                start_response,
            )
            self.gologin_handler.stop_profile_remote(profile_id)
            return False

        logger.info("Connecting Playwright to GoLogin browser via: %s", ws_endpoint)
        try:
            pw_instance = await async_playwright().start()
            self.browser = await pw_instance.chromium.connect_over_cdp(
                ws_endpoint, timeout=60000
            )

            if self.browser.contexts:
                self.context = self.browser.contexts[0]
            else:
                context_options = {}
                if proxy_details and proxy_details.get("url"):
                    playwright_proxy_conf = (
                        self.proxy_handler.get_playwright_proxy_config(
                            proxy_details["url"]
                        )
                    )
                    if playwright_proxy_conf:
                        context_options["proxy"] = playwright_proxy_conf
                self.context = await self.browser.new_context(**context_options)

            if self.context.pages:
                self.page = self.context.pages[0]
            else:
                self.page = await self.context.new_page()

            logger.info(
                "Successfully connected Playwright to GoLogin browser and got a page."
            )
            await self.page.set_viewport_size(
                {"width": 1920, "height": 1080}
            )
            return True
        except (playwright._impl._api_types.Error, ConnectionError) as e:
            logger.error("Playwright connection error: %s", e, exc_info=True)
            if self.browser:
                await self.browser.close()
            self.gologin_handler.stop_profile_remote(profile_id)
            return False
        except Exception as e:
            logger.error("An unexpected error occurred during Playwright connection: %s", e, exc_info=True)
            if self.browser:
                await self.browser.close()
            self.gologin_handler.stop_profile_remote(profile_id)
            return False

    async def navigate(self, url):
        if not self.page:
            logger.error("Page not initialized. Cannot navigate.")
            return False
        logger.info("Navigating to: %s", url)
        try:
            await self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
            logger.info("Navigation successful to: %s", url)
            return True
        except Exception as e:
            logger.error("Navigation error to %s (Playwright error): %s", url, e)
            return False

    async def human_like_scroll(self, scrolls=3, delay_range=(1, 3)):
        if not self.page:
            return
        for _ in range(scrolls):
            scroll_amount = random.randint(300, 700)
            scroll_direction = random.choice(["down", "up"])
            if scroll_direction == "down":
                await self.page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            else:
                await self.page.evaluate(f"window.scrollBy(0, -{scroll_amount})")
            logger.debug("Scrolled %s by %s pixels", scroll_direction, scroll_amount)
            await asyncio.sleep(random.uniform(delay_range[0], delay_range[1]))

    async def click_element(
        self, selector, timeout=10000, human_delay_range=(0.5, 1.5)
    ):
        if not self.page:
            return False
        logger.info("Attempting to click element with selector: %s", selector)
        try:
            element = await self.page.wait_for_selector(selector, timeout=timeout)
            await asyncio.sleep(random.uniform(0.2, 0.5))
            await element.click(timeout=5000)
            logger.info("Clicked element: %s", selector)
            await asyncio.sleep(random.uniform(human_delay_range[0], human_delay_range[1]))
            return True
        except Exception as e:
            logger.error("Error clicking element %s (Playwright error): %s", selector, e)
            return False

    async def type_text(
        self, selector, text, delay_between_chars=0.1, human_delay_range=(0.5, 1.0)
    ):
        if not self.page:
            return False
        logger.info("Attempting to type '%s' into element: %s", text, selector)
        try:
            element = await self.page.wait_for_selector(selector, timeout=10000)
            await element.click()
            await element.type(text, delay=delay_between_chars * 1000)
            logger.info("Typed '%s' into element: %s", text, selector)
            await asyncio.sleep(random.uniform(human_delay_range[0], human_delay_range[1]))
            return True
        except Exception as e:
            logger.error("Error typing into element %s (Playwright error): %s", selector, e)
            return False

    async def get_cookies(self):
        if not self.context:
            logger.error("Browser context not initialized. Cannot get cookies.")
            return []
        cookies = await self.context.cookies()
        logger.info("Retrieved %s cookies.", len(cookies))
        return cookies

    async def save_cookies(self, path):
        cookies = await self.get_cookies()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(cookies, f, indent=2)
            logger.info("Cookies saved to: %s", path)
        except IOError as e:
            logger.error("Error saving cookies to %s: %s", path, e)

    async def load_cookies(self, path):
        if not self.context:
            logger.error("Browser context not initialized. Cannot load cookies.")
            return False
        try:
            with open(path, "r", encoding="utf-8") as f:
                cookies = json.load(f)
            await self.context.add_cookies(cookies)
            logger.info("Cookies loaded from: %s", path)
            return True
        except FileNotFoundError:
            logger.warning("Cookie file not found: %s. Starting fresh session.", path)
            return False
        except json.JSONDecodeError as e:
            logger.error("Error decoding cookie JSON from %s: %s", path, e)
            return False
        except IOError as e:
            logger.error("Error loading cookies from %s (IOError): %s", path, e)
            return False
        except Exception as e:
            logger.error("An unexpected error occurred when loading cookies from %s: %s", path, e)
            return False

    async def take_screenshot(self, path):
        if not self.page:
            logger.error("Page not initialized. Cannot take screenshot.")
            return
        logger.info("Taking screenshot: %s", path)
        try:
            await self.page.screenshot(path=path, full_page=True)
            logger.info("Screenshot saved to %s", path)
        except (IOError, OSError) as e:
            logger.error("Error saving screenshot to %s: %s", path, e)
        except Exception as e:
            logger.error("Error taking screenshot %s (Playwright error): %s", path, e)

    async def get_fingerprint_data(self):
        if not self.page:
            return {}
        try:
            fingerprint = await self.page.evaluate(
                """
                () => {
                    return {
                        userAgent: navigator.userAgent,
                        appVersion: navigator.appVersion,
                        platform: navigator.platform,
                        language: navigator.language,
                        languages: navigator.languages,
                        screenWidth: screen.width,
                        screenHeight: screen.height,
                        colorDepth: screen.colorDepth,
                        deviceMemory: navigator.deviceMemory,
                        hardwareConcurrency: navigator.hardwareConcurrency,
                        timezoneOffset: new Date().getTimezoneOffset(),
                        plugins: Array.from(navigator.plugins).map(p => p.name),
                        canvasFingerprint: (() => {
                            try {
                                const canvas = document.createElement('canvas');
                                const ctx = canvas.getContext('2d');
                                ctx.textBaseline = 'top';
                                ctx.font = "14px 'Arial'";
                                ctx.textBaseline = 'alphabetic';
                                ctx.fillStyle = '#f60';
                                ctx.fillRect(125, 1, 62, 20);
                                ctx.fillStyle = '#069';
                                ctx.fillText('Hello, World!', 2, 15);
                                return canvas.toDataURL();
                            } catch (e) { return 'Error generating canvas fingerprint'; }
                        })()
                    };
                }
            """
            )
            logger.info("Extracted basic fingerprint data.")
            return fingerprint
        except Exception as e:
            logger.error("Error extracting fingerprint data: %s", e)
            return {}

    async def close_browser(self):
        if self.browser:
            try:
                await self.browser.close()
                logger.info("Playwright browser closed.")
            except Exception as e:
                logger.error("Error closing Playwright browser: %s", e)
            self.browser = None
            self.context = None
            self.page = None

        if self.current_profile_id:
            self.gologin_handler.stop_profile_remote(self.current_profile_id)
            self.current_profile_id = None
        self.current_proxy_url = None


async def example_usage():
    pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info(
        "BrowserHandler example: This requires manual setup of GoLoginHandler and config."
    ) 