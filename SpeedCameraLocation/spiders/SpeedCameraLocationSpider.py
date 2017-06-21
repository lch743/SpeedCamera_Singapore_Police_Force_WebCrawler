# -*- coding: utf-8 -*-
from scrapy.selector import Selector
from SpeedCameraLocation.items import SpeedCameraLocationItem
import scrapy
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='log.log',
                    filemode='w')


class SpeedCameraLocationSpider(scrapy.Spider):
    name = 'SpeedCameraLocation'
    main_page = 'http://www.police.gov.sg'
    start_urls = ['http://www.police.gov.sg/resources/traffic-matters/traffic-enforcement-camera-locations/']
    __warning_pages = []


    def parse(self, response):
        sel = Selector(response)
        count = 0
        for link in sel.xpath("//div[@class='menu-group']/a/@href").extract():
            count += 1
            request = scrapy.Request('%s%s' % (self.main_page, link), callback=self.parse_items)
            yield request
        logging.info('Found %d pages' % count)

    def parse_items(self, response):
        sel = Selector(response)
        items = []
        logging.info('Page: %s' % response.url)
        if response.url in self.start_urls:
            return items
        for record in sel.xpath("//table/tbody/tr"):
            contents = record.select("td/text()").extract()
            if len(contents) == 0:
                continue
            if len(contents) <> 3:
                new_contents = []
                new_contents.append(contents[0])
                new_contents.append(' '.join(contents[1:-1]))
                new_contents.append(contents[-1])
                contents = []
                contents = new_contents
            scli = SpeedCameraLocationItem()
            scli['id'] = contents[0]
            scli['name'] = self.__get_sc_name_by_url(response.url)
            scli['location'] = contents[1]
            coords = contents[2].split(',')
            scli['lat'] = coords[0].strip(' ')
            scli['lon'] = coords[1].strip(' ')
            items.append(scli)
        logging.info('Fetched %d items' % len(items))
        return items

    def __get_sc_name_by_url(self, str_url):
        str_name = str_url[str_url.rindex('/') + 1 :]
        str_name = str_name.strip('#content')
        if str_name == 'mobile-speed-cameras-location':
            return 'Mobile Speed Camera'
        elif str_name == 'mobile-speed-cameras-locati':
            return 'Mobile Speed Camera'
        elif str_name == 'red-light-camera-locations':
            return 'Red Light Camera'
        elif str_name == 'mobile-speed-enforcement-locations':
            return 'Police Speed Laser Camera'
        elif str_name == 'fixed-speed-camera-locations':
            return 'Fixed Speed Camera'
        else:
            if str_name not in self.__warning_pages:
                self.__warning_pages.append(str_name)
                logging.warning('New type found! %s' % str_name)
            return str_name

