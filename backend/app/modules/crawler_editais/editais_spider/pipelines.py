import json

class EditaisPipeline:
    def open_spider(self, spider):
        self.file = open('editais.json', 'w')  # Ou integre com DB do Apoema, ex.: via Django ORM

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item
