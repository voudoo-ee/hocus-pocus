import asyncio
import logging

import aiohttp
from aiohttp.client import ClientSession


class BasicScanner:
    def __init__(self, base_url: str, c_range: range = None, id_list: list[str] = None):
        """
        :param base_url: Must contain an %ID% placeholder.
        :param c_range: Range of IDs to scan, if not specified will only scan the base url.
        :param id_list: List of IDs to scan, must not be specified if c_range is specified.
        """

        self.base_url = base_url
        self.id_list = id_list or []
        self.logger = logging.getLogger("basic")
        if c_range is range:
            self.range = range(c_range.start, c_range.stop + 1)
        else:
            self.range = c_range

    async def scan(self):
        if self.range is None and not self.id_list:
            urls = [self.base_url]
        elif self.id_list:
            urls = [self.base_url.replace("%ID%", i) for i in self.id_list]
        else:
            urls = [self.base_url.replace("%ID%", str(i)) for i in self.range]

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=30)) as session:
            session.headers.update({'X-Requested-With': 'XMLHttpRequest'})
            tasks = []
            for url in urls:
                task = asyncio.ensure_future(self.download_link(url=url, session=session))
                tasks.append(task)
            gathered_data = await asyncio.gather(*tasks, return_exceptions=True)

            return gathered_data

    async def download_link(self, url: str, session: ClientSession):
        async with session.get(url) as response:
            self.logger.debug(f"{url} with status {response.status}")
            return await response.json()
