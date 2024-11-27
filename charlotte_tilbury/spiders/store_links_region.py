import scrapy
from scrapy.cmdline import execute as ex
from charlotte_tilbury.db_config import DbConfig
obj = DbConfig()


class StoreLinksRegionSpider(scrapy.Spider):
    name = "store_links_region"
    # allowed_domains = ["."]
    start_urls = ["https://stores.charlottetilbury.com/en-us/us"]

    def parse(self, response):
        region_links = response.xpath("//a[contains(@class,'text-dnc')]/@href").getall()
        for link in region_links:
            link = 'https://stores.charlottetilbury.com/' + link.replace('../','')
            yield scrapy.Request(link, callback=self.parse2)

    def parse2(self, response):
        city_links = response.xpath("//a[contains(@class,'text-dnc')]/@href").getall()
        for city_link in city_links:
            city_link = 'https://stores.charlottetilbury.com/' + city_link.replace('../','')

            yield scrapy.Request(city_link, callback=self.parse3)

    def parse3(self, response):
        store_links = response.xpath("//div[contains(@class,'flex-wrap')]//a[@class='Link']/@href").getall()
        for store_link in store_links:
            store_link = 'https://stores.charlottetilbury.com/' + store_link.replace('../','')

            try:obj.insert_store_links_table(store_link)
            except Exception as e:print(e)

if __name__ == '__main__':
    ex("scrapy crawl store_links_region".split())

