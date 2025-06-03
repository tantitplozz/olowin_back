import time
import random
import logging
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)


class ProxyHandler:
    def __init__(self, proxy_list, cooldown_minutes=15):
        """
        Initializes the ProxyHandler.
        proxy_list: A list of proxy strings (e.g., "socks5://user:pass@host:port?sid=xxxx").
        cooldown_minutes: Minimum time in minutes before a proxy can be reused.
        """
        self.proxy_list = []
        for p_str in proxy_list:
            parsed_url = urlparse(p_str)
            query_params = parse_qs(parsed_url.query)
            sid = query_params.get("sid", [None])[0]
            self.proxy_list.append({"url": p_str, "sid": sid, "last_used": 0})

        self.cooldown_seconds = cooldown_minutes * 60
        if not self.proxy_list:
            logger.warning("Proxy list is empty. Proxy rotation will not be effective.")

    def get_proxy(self):
        """
        Selects an available proxy from the list that is not on cooldown.
        Returns a dictionary {"url": proxy_url_string, "sid": session_id} or None if no proxy is available.
        """
        if not self.proxy_list:
            logger.error("No proxies available in the list.")
            return None

        available_proxies = []
        current_time = time.time()

        for proxy in self.proxy_list:
            if current_time - proxy["last_used"] > self.cooldown_seconds:
                available_proxies.append(proxy)

        if not available_proxies:
            logger.warning("All proxies are currently on cooldown.")
            self.proxy_list.sort(key=lambda p: p["last_used"])
            soonest_proxy = self.proxy_list[0]
            wait_time = (
                soonest_proxy["last_used"] + self.cooldown_seconds
            ) - current_time
            logger.info(
                "No proxy immediately available. Soonest proxy (%s) available in %.2f seconds.",
                soonest_proxy["sid"] or soonest_proxy["url"],
                wait_time,
            )
            return None

        selected_proxy_details = random.choice(available_proxies)

        for proxy in self.proxy_list:
            if proxy["url"] == selected_proxy_details["url"]:
                proxy["last_used"] = current_time
                break

        logger.info(
            "Selected proxy: SID=%s (URL: %s)",
            selected_proxy_details["sid"],
            selected_proxy_details["url"],
        )
        return {
            "url": selected_proxy_details["url"],
            "sid": selected_proxy_details["sid"],
        }

    def get_playwright_proxy_config(self, proxy_url_string):
        """
        Converts a proxy URL string to Playwright's proxy format.
        Example proxy_url_string: "socks5://username:password@proxy.example.com:1080"
        Returns a dict like: {"server": "socks5://proxy.example.com:1080", "username": "user", "password": "pass"}
        """
        if not proxy_url_string:
            return None

        parsed = urlparse(proxy_url_string)
        if parsed.scheme not in ["http", "https", "socks5"]:
            logger.error("Unsupported proxy scheme: %s", parsed.scheme)
            return None

        server = f"{parsed.scheme}://{parsed.hostname}"
        if parsed.port:
            server += f":{parsed.port}"

        proxy_config = {"server": server}
        if parsed.username:
            proxy_config["username"] = parsed.username
        if parsed.password:
            proxy_config["password"] = parsed.password

        return proxy_config


if __name__ == "__main__":
    example_proxies = [
        "socks5://user1:pass1@us.arxlabs.io:3010?sid=sid_abc123",
        "socks5://user2:pass2@us.arxlabs.io:3010?sid=sid_def456",
        "socks5://user3:pass3@us.arxlabs.io:3010?sid=sid_ghi789",
    ]
    proxy_handler = ProxyHandler(proxy_list=example_proxies, cooldown_minutes=0.1)

    for i in range(5):
        print(f"\nRequest {i+1}:")
        selected = proxy_handler.get_proxy()
        if selected:
            print(f"Using proxy: {selected['url']} (SID: {selected['sid']})")
            playwright_config = proxy_handler.get_playwright_proxy_config(
                selected["url"]
            )
            print(f"Playwright proxy config: {playwright_config}")
        else:
            print("No proxy available right now.")
        if i < 4:
            time.sleep(2)  # Wait 2 seconds to observe cooldown 