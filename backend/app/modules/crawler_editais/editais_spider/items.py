import scrapy
class EditalItem(scrapy.Item):
    titulo = scrapy.Field()
    descricao = scrapy.Field()
    data = scrapy.Field()
    link = scrapy.Field()
