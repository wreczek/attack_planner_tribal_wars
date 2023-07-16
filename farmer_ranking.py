"""Module responsible for extracting players from farmer ranking belonging to specific tribe."""
import re
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.item import Item, Field
from scrapy.utils.project import get_project_settings
import pyperclip

from plunderer_ranking import PlundererRankingSpider
from utils import format_number, generate_bb_text


class RankingItem(Item):
    ranking = Field()
    name = Field()
    tribe = Field()
    score = Field()


class FarmerRankingSpider(scrapy.Spider):
    name = 'farmer_ranking'
    start_urls = ['https://pl192.plemiona.pl/guest.php?screen=ranking&mode=in_a_day&offset=0&type=loot_res']
    offset = 0
    base_url = 'https://pl192.plemiona.pl/guest.php?screen=ranking&mode=in_a_day&offset={}&type=loot_res'
    ranking_list = []

    def parse(self, response):
        ally_tribes = ['OM', 'OM.', 'MM']
        players_list = []
        players_num = 100 # 24+40+37

        for row in response.xpath('//table[@id="in_a_day_ranking_table"]//tr[position() > 1]'):
            item = RankingItem()
            item['ranking'] = row.xpath('td[1]/text()').get()
            item['name'] = re.findall(r'\r\n                        \r\n                        ([ĄąĆćĘęŁłŃńOoÓóŚśŹźŻż\x21-\x7E]|[ ĄąĆćĘęŁłŃńOoÓóŚśŹźŻż\x21-\x7E]+)\r\n', row.xpath('td[2]//a').get())[0]
            item['tribe'] = row.xpath('td[3]//a/text()').get()

            score = int(''.join(re.findall(r'\d', row.xpath('td[4]').get())))
            formatted_score = format_number(score)

            item['score'] = formatted_score

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
    process.crawl(FarmerRankingSpider)
    process.crawl(PlundererRankingSpider)

    process.start()

    farmers_list = FarmerRankingSpider.ranking_list
    plunderer_ranking_list = PlundererRankingSpider.ranking_list
    plunderer_score_dict = {element['name']: element['score'] for element in plunderer_ranking_list}

    bb_text = """[spoiler=][table]
    [**]Ranking plemienny[||]Ranking ogólny[||]Nazwa[||]Plemię[||]Wynik[||]Liczba splądrowanych wiosek[/**]
    """
    bb_text += generate_bb_text(farmers_list, {0: 17, 1: 15, 2: 13, 3: 11, 4: 11}, 9, plunderer_score_dict)
    bb_text += """[/table][/spoiler]"""

    print(f'{bb_text}')

    pyperclip.copy(f'{bb_text}')

# TODO:
#  1. Aktualnie wywolywanie z farmer_ranking modulu plunderer_ranking powoduje, ze jest generopwana
#      lista z dlugoscia ustalona w plunderer_ranking
#  2. Redundancja
#  3. Moze jakos lepiej rozwiazac problem z utils.generate_bb_text (if else co do kolumny)
#  4.
