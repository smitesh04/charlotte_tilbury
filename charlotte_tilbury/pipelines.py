# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from charlotte_tilbury.db_config import DbConfig
obj = DbConfig()
from charlotte_tilbury.items import CharlotteTilburyItem
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class CharlotteTilburyPipeline:
    def process_item(self, item, spider):
        if isinstance(item, CharlotteTilburyItem):
            obj.insert_data_table(item)
            obj.update_store_links_status(item['url'])
        return item
