import datetime
import json
import os
from typing import Iterable
from scrapy.cmdline import execute as ex
import re
from charlotte_tilbury.items import CharlotteTilburyItem
import scrapy
from scrapy import Request
from charlotte_tilbury.db_config import DbConfig
obj = DbConfig()
from charlotte_tilbury.common_func import create_md5_hash, page_write, headers

class DataSpider(scrapy.Spider):
    name = "data"
    # allowed_domains = ["."]
    # start_urls = ["https://."]

    def start_requests(self):
        obj.cur.execute(f"select * from {obj.store_links_table} where status=0")
        rows = obj.cur.fetchall()
        for row in rows:
            link = row['link']
            hashid = create_md5_hash(link)
            pagesave_dir = rf"C:/Users/Actowiz/Desktop/pagesave/{obj.database}"
            file_name = fr"{pagesave_dir}/{hashid}.html"
            row['hashid'] = hashid
            row['pagesave_dir'] = pagesave_dir
            row['file_name'] = file_name

            if os.path.exists(file_name):
                yield scrapy.Request(url='file:///' + file_name, callback=self.parse, cb_kwargs=row)
            else:
                yield scrapy.Request(url=link, headers=headers(), callback=self.parse, cb_kwargs=row)

    def parse(self, response, **kwargs):

        file_name = kwargs['file_name']
        pagesave_dir = kwargs['pagesave_dir']
        if not os.path.exists(file_name):
            page_write(pagesave_dir, file_name, response.text)
        direction_url = response.xpath("//a[contains(@href,'/maps/')]/@href").get()
        try:
            lat_long_raw = re.findall('&query=.*?&query', direction_url)[0]
            lat_long_raw = lat_long_raw.replace('&query=', '').replace('&query', '')
            lat_long_splitted = lat_long_raw.split(',')
            lat = lat_long_splitted[0]
            lng = lat_long_splitted[1]
        except:
            lat = 'N/A'
            lng = 'N/A'
        script = response.xpath('//script[@type="application/ld+json"]/text()').get()





        script_jsn = json.loads(script)
        store_name = script_jsn['name']
        street_address = script_jsn['address']['streetAddress']
        city = script_jsn['address']['addressLocality']
        region = script_jsn['address']['addressRegion']
        postalcode = script_jsn['address']['postalCode']
        try:phone = script_jsn['telephone']
        except:phone = 'N/A'

        opening_hours_list = list()

        opening_hours_jsn = script_jsn['openingHoursSpecification']
        if opening_hours_jsn:
            for day in opening_hours_jsn:
                days = day['dayOfWeek'][0]
                open = day['opens']
                close = day['closes']
                opening_hours_list.append(f'{days.capitalize()}: {open}-{close}')
            opening_hours = ' | '.join(opening_hours_list)
            store_status = "Open"
        else:
            opening_hours = 'N/A'
            store_status = "Closed"



        item = CharlotteTilburyItem()
        item['store_no'] = ''
        item['name'] = store_name
        item['latitude'] = lat
        item['longitude'] = lng
        item['street'] = street_address
        item['city'] = city
        item['state'] = region
        item['zip_code'] = postalcode
        item['county'] = city
        item['phone'] = phone
        item['open_hours'] = opening_hours
        item['url'] = kwargs['link']
        item['provider'] = "Charlotte Tilbury"
        item['category'] = "Apparel And Accessory Stores"
        item['updated_date'] = datetime.datetime.today().strftime("%d-%m-%Y")
        item['country'] = "US"
        item['status'] = store_status
        item['direction_url'] = direction_url
        item['pagesave_path'] = file_name

        yield item

if __name__ == '__main__':
    ex('scrapy crawl data'.split())