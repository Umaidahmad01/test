from typing import List, AsyncIterable
from urllib.parse import urlparse, urljoin, quote, quote_plus
from httpx import AsyncClient
from bs4 import BeautifulSoup
from plugins.client import MangaClient, MangaCard, MangaChapter, LastChapter

import re

chapters = dict()

class MangaHindiSubClient(MangaClient):

    base_url = urlparse("https://mangahindisub.in")
    search_url = "https://mangahindisub.in/?s="  # Assuming search endpoint, adjust if needed
    updates_url = base_url.geturl()

    pre_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'
    }

    def __init__(self, *args, name="MangaHindiSub", **kwargs):
        super().__init__(*args, name=name, headers=self.pre_headers, **kwargs)

    async def resolve_shortened_url(self, short_url: str) -> str:
        """Resolve shortened URLs like modijiurl.com or seturl.in by following redirects."""
        response = await self.get(short_url, follow_redirects=True)
        return str(response.url)

    def mangas_from_page(self, content):
        bs = BeautifulSoup(content, "html.parser")
        manga_items = bs.find_all("div", {"class": "bsx"})  # Adjust class based on site
        
        names = []
        urls = []
        images = []
        
        for item in manga_items:
            link = item.find("a")
            if link:
                names.append(link.get("title") or link.text.strip())
                urls.append(link.get("href"))  # Could be shortened or direct
                img = item.find("img")
                if img and img.get("src"):
                    images.append(img.get("src"))
        
        mangas = [MangaCard(self, *tup) for tup in zip(names, urls, images)]
        return mangas

    def chapters_from_page(self, manga_url: str, content: bytes, manga: MangaCard = None):
        bs = BeautifulSoup(content, "html.parser")
        chapter_list = bs.find("ul", {"class": "cl"})  # Adjust class if needed
        
        if not chapter_list:
            return []
        
        texts = []
        links = []
        for chapter in chapter_list.find_all("li"):
            a_tag = chapter.find("a")
            if a_tag:
                texts.append(a_tag.text.strip())
                links.append(a_tag.get("href"))  # Shortened link like modijiurl.com or seturl.in
        
        return list(map(lambda x: MangaChapter(self, x[0], x[1], manga, []), zip(texts, links)))

    async def updates_from_page(self, content):
        bs = BeautifulSoup(content, "html.parser")
        manga_items = bs.find_all("div", {"class": "bsx"})  # Adjust class based on site

        urls = dict()
        for manga_item in manga_items:
            manga_url = manga_item.findNext("a").get("href")
            if manga_url in urls:
                continue
            
            data = await self.get_url(manga_url)
            bs = BeautifulSoup(data, "html.parser")
            chapter_list = bs.find("ul", {"class": "cl"})  # Adjust class
            if chapter_list:
                chapter_url = chapter_list.find("li").findNextA("a").get("href")
                resolved_url = await self.resolve_shortened_url(chapter_url)
                urls[manga_url] = resolved_url

        return urls

    async def pictures_from_chapters(self, data: bytes, response=None):
        soup = BeautifulSoup(data, 'html.parser')
        containers = soup.find_all('div', class_='reader-area')  # Adjust class based on site
        images_url = []

        for container in containers:
            imgs = container.find_all('img')
            for img in imgs:
                src = img.get('src')
                if src:
                    if "mangahindisub.in" in src and "jpg" in src.lower():
                        images_url.append(src)
                    elif "modijiurl.com" in src or "seturl.in" in src:  # Check for both shorteners
                        resolved_src = await self.resolve_shortened_url(src)
                        images_url.append(resolved_src)

        return images_url

    async def search(self, query: str = "", page: int = 1) -> List[MangaCard]:
        search_url = f"{self.search_url}{quote_plus(query)}&page={page}"
        content = await self.get_url(search_url)
        return self.mangas_from_page(content)

    async def get_chapters(self, manga_card: MangaCard, page: int = 1) -> List[MangaChapter]:
        manga_url = str(manga_card.url)
        content = await self.get_url(manga_url)
        chapters = self.chapters_from_page(manga_url, content, manga_card)
        # Resolve shortened chapter URLs
        for chapter in chapters:
            if "mangahindisub.in" not in chapter.url:
                chapter.url = await self.resolve_shortened_url(chapter.url)
        return chapters[(page - 1) * 20:page * 20]

    async def iter_chapters(self, manga_url: str, manga_name) -> AsyncIterable[MangaChapter]:
        manga_card = MangaCard(self, manga_name, manga_url, '')
        content = await self.get_url(manga_url)
        for chapter in self.chapters_from_page(manga_url, content, manga_card):
            if "mangahindisub.in" not in chapter.url:
                chapter.url = await self.resolve_shortened_url(chapter.url)
            yield chapter

    async def contains_url(self, url: str):
        return url.startswith(self.base_url.geturl())

    async def check_updated_urls(self, last_chapters: List[LastChapter]):
        content = await self.get_url(self.updates_url)
        updates = await self.updates_from_page(content)

        updated = []
        not_updated = []
        for lc in last_chapters:
            if lc.url in updates.keys():
                if updates.get(lc.url) != lc.chapter_url:
                    updated.append(lc.url)
            elif updates.get(lc.url) == lc.chapter_url:
                not_updated.append(lc.url)
                
        return updated, not_updated
