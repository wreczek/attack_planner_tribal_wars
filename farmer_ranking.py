"""Module responsible for extracting players from farmer ranking belonging to specific tribe."""
import re
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.item import Item, Field
from scrapy.utils.project import get_project_settings
import pyperclip


def format_number(number):
    suffixes = ["", "K", "M", "B", "T"]
    index = 0

    while number >= 1000 and index < len(suffixes) - 1:
        number /= 1000.0
        index += 1

    formatted_number = f"{number:.2f}{suffixes[index]}"

    return formatted_number


class RankingItem(Item):
    ranking = Field()
    name = Field()
    tribe = Field()
    score = Field()


class RankingSpider(scrapy.Spider):
    name = 'ranking'
    start_urls = ['https://pl192.plemiona.pl/guest.php?screen=ranking&mode=in_a_day&offset=0&type=loot_res']
    offset = 0
    base_url = 'https://pl192.plemiona.pl/guest.php?screen=ranking&mode=in_a_day&offset={}&type=loot_res'
    ranking_list = []

    def parse(self, response):
        ally_tribes = ['OM', 'OM.']
        players_list = []
        players_num = 10
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


process = CrawlerProcess(get_project_settings())
process.crawl(RankingSpider)
process.start()

whole_dict = RankingSpider.ranking_list

bb_text = """[table]
[**]Ranking plemienny[||]Ranking ogólny[||]Nazwa[||]Plemię[||]Wynik[/**]
"""

size1 = 16
size2 = 15
size3 = 14

bb_text += f"""[*][size={size1}]{1}[/size][|][size={size1}]{whole_dict[0]['ranking']}[/size][|][size={size1}][player]{whole_dict[0]['name']}[/player][/size][|][size={size1}][ally]{whole_dict[0]['tribe']}[/ally][/size][|][size={size1}]{whole_dict[0]['score']}[/size]\n"""
bb_text += f"""[*][size={size2}]{2}[/size][|][size={size2}]{whole_dict[1]['ranking']}[/size][|][size={size2}][player]{whole_dict[1]['name']}[/player][/size][|][size={size2}][ally]{whole_dict[1]['tribe']}[/ally][/size][|][size={size2}]{whole_dict[1]['score']}[/size]\n"""
bb_text += f"""[*][size={size3}]{3}[/size][|][size={size3}]{whole_dict[2]['ranking']}[/size][|][size={size3}][player]{whole_dict[2]['name']}[/player][/size][|][size={size3}][ally]{whole_dict[2]['tribe']}[/ally][/size][|][size={size3}]{whole_dict[2]['score']}[/size]\n"""

for ind, d in enumerate(whole_dict[3:]):
    bb_text += f"""[*][size={13}]{ind+4}[/size][|]{d['ranking']}[|][player]{d['name']}[/player][|][ally]{d['tribe']}[/ally][|]{d['score']}\n"""

bb_text += """[/table]"""

print(f'{bb_text}')

pyperclip.copy(f'{bb_text}')
