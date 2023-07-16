import pyperclip
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.item import Item, Field

from utils import generate_bb_text


class RankingItem(Item):
    ranking = Field()
    name = Field()
    tribe = Field()
    score = Field()


class AggressorRankingSpider(scrapy.Spider):
    name = 'aggressor_ranking'
    start_urls = ['https://pl192.plemiona.pl/guest.php?screen=ranking&mode=kill_player&offset=0&type=att']
    offset = 0
    base_url = 'https://pl192.plemiona.pl/guest.php?screen=ranking&mode=kill_player&offset={}&type=att'
    ranking_list = []

    def parse(self, response):
        ally_tribes = ['OM', 'OM.']
        players_list = []
        players_num = 10

        for row in response.xpath('//table[@class="vis"]/tr[position() > 1]'):
            item = RankingItem()
            item['ranking'] = row.xpath('td[1]/text()').get()

            name_html = row.xpath('td[2]//a').get()
            item['name'] = name_html.split('\n')[-2].strip()

            item['tribe'] = row.xpath('td[3]//a/text()').get()
            item['score'] = row.xpath('td[4]/text()').get()

            if item['tribe'] in ally_tribes or item['name'] in players_list:
                self.ranking_list.append(item)
                if len(self.ranking_list) == players_num:
                    return

            yield item

        self.offset += 25
        next_url = self.base_url.format(self.offset)

        yield response.follow(next_url, self.parse)


if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(AggressorRankingSpider)
    process.start()

    whole_dict = AggressorRankingSpider.ranking_list

    bb_text = """[spoiler=][table]
    [**]Ranking plemienny[||]Ranking ogólny[||]Nazwa[||]Plemię[||]Wynik[/**]
    """
    bb_text += generate_bb_text(whole_dict, {0: 17, 1: 15, 2: 13, 3: 11, 4: 11}, 9)
    bb_text += """[/table][/spoiler]"""

    print(f'{bb_text}')

    pyperclip.copy(f'{bb_text}')
