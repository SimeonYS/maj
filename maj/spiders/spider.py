import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import MajItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class MajSpider(scrapy.Spider):
	name = 'maj'
	start_urls = ['https://www.majbank.dk/news']

	def parse(self, response):
		post_links = response.xpath('//li/a[contains(@id,"majbankmiddle_1")]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//li[@class="next"]/a/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):
		date = response.xpath('//div[@class="date"]/text()').get()
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="l1"]/p//text() | //article[@class="block--newspage__article-content"]//div[@class="l1"][2]//text()[not (ancestor::h1)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=MajItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
