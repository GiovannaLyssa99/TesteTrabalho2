import scrapy
from scrapy.loader import ItemLoader
from ..items import EditalItem  # Assumindo um item definido em items.py
class EditaisSpider(scrapy.Spider):
    name = 'editais'
    start_urls = [
        'https://exemplo.com/editais',
    ]
    def parse(self, response):
        for edital in response.css('div.edital'):  
            loader = ItemLoader(item=EditalItem(), selector=edital)
            loader.add_css('titulo', 'h2::text')
            loader.add_css('descricao', 'p::text')
            loader.add_css('data', '.data::text')
            loader.add_css('link', 'a::attr(href)')
            yield loader.load_item()
        # Paginação, se houver
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
