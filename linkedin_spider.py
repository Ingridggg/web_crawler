"""
* cd /Users/ig/Desktop/linkedin_scrapy/

scrapy crawl profiles -o output_file_name1.json
"""

import scrapy
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from shutil import which
from time import sleep


class ProfilesSpider(scrapy.Spider):
    name = 'profiles'
    allowed_domains = ['www.linkedin.com/in', 'www.google.com']

    def __init__(self):
        chrom_path = which("chromedriver")
        chrom_options = Options()
        chrom_options.headless = True
        # TODO
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36'
        chrom_options.add_argument(f'user-agent={self.user_agent}')
        self.driver = webdriver.Chrome(executable_path=chrom_path, options=chrom_options)
        self.driver.implicitly_wait(5)

    def login(self):
        self.driver.get('https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin')
        username = self.driver.find_element_by_name("session_key")
        # TODO
        username.send_keys('xxxxxxx')
        sleep(0.5)

        password = self.driver.find_element_by_name('session_password')
        # TODO
        password.send_keys('xxxxxxx')
        sleep(0.5)

        sign_in_button = self.driver.find_element_by_tag_name('button')
        sign_in_button.click()

    def search(self):
        self.login()
        sleep(5)
        # TODO
        query = 'site:linkedin.com/in AND "Ecommerce" AND "Los Angeles"'
        self.driver.get('https://www.google.com/')
        search_query = self.driver.find_element_by_name('q')
        search_query.send_keys(query)
        search_query.send_keys(Keys.RETURN)
        sleep(0.5)
        return self.driver.current_url

    def start_requests(self):
        yield scrapy.Request(url=self.search(), headers={
            'User-Agent': self.user_agent
        })

    def parse(self, response):
        urls = self.driver.find_elements_by_xpath('//*[@class = "rc"]/div/a[@href]')
        urls = [url.get_attribute('href') for url in urls]
        next_page = self.driver.find_elements_by_id('pnnext')[0].get_attribute("href")
        sleep(0.5)
        for url in urls:
            self.driver.get(url)
            sleep(5)
            sel = Selector(text=self.driver.page_source)
            # TODO
            name = sel.xpath('.//*[@class = "inline t-24 t-black t-normal break-words"]/text()').extract_first("")
            position = sel.xpath('.//*[@class = "mt1 t-18 t-black t-normal break-words"]/text()').extract_first("")
            location = sel.xpath('.//*[@class = "t-16 t-black t-normal inline-block"]/text()').extract_first("")
            current_company = sel.xpath('.//*[@class = "pv-entity__secondary-title t-14 t-black t-normal"]/text()').extract_first("")

            # if location is None:
            #     location = 'null'

            url = self.driver.current_url


            yield {
                'Name': name.strip(),
                'Position': position.strip(),
                'Location': location.strip(),
                'Current_company': current_company.strip(),
                'URL': url
            }

        if next_page:
            # TODO
            self.driver.get(next_page)
            yield scrapy.Request(url=self.driver.current_url, callback=self.parse, headers={'User-Agent': self.user_agent}, dont_filter=True)
        else:
            self.driver.close()
