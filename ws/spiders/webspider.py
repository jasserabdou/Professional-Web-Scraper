from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import BookItem


class WebSpider(CrawlSpider):
    name = "webspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]
    rules = (
        Rule(LinkExtractor(allow=r"catalogue/category")),
        Rule(LinkExtractor(allow=r"catalogue",
             deny=r"category"), callback="parse_item"),
    )

    def parse_item(self, response):
        books = response.css('article.product_pod')
        for book in books:
            relative_url = book.css('h3 a::attr(href)').get()
            if relative_url:
                book_url = response.urljoin(relative_url)
                yield response.follow(book_url, callback=self.parse_book_page)

    def parse_book_page(self, response):
        book_item = BookItem()
        table_rows = response.css("table tr")

        book_item['url'] = response.url
        book_item['title'] = response.css('.product_main h1::text').get()
        book_item['upc'] = table_rows[0].css("td::text").get()
        book_item['product_type'] = table_rows[1].css("td::text").get()
        book_item['price_excl_tax'] = table_rows[2].css("td::text").get()
        book_item['price_incl_tax'] = table_rows[3].css("td::text").get()
        book_item['tax'] = table_rows[4].css("td::text").get()
        book_item['availability'] = table_rows[5].css("td::text").get()
        book_item['num_of_reviews'] = table_rows[6].css("td::text").get()
        book_item['num_of_stars'] = response.css(
            "p.star-rating::attr(class)").get()
        book_item['category'] = response.xpath(
            "//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get()
        book_item['description'] = response.xpath(
            "//div[@id='product_description']/following-sibling::p/text()").get()
        book_item['price'] = response.css("p.price_color::text").get()

        yield book_item
