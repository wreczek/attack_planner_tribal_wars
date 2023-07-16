import pyperclip
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from aggressor_ranking import AggressorRankingSpider
from defender_ranking import DefenderRankingSpider
from farmer_ranking import FarmerRankingSpider
from plunderer_ranking import PlundererRankingSpider
from supporter_ranking import SupporterRankingSpider
from utils import generate_bb_text


if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(AggressorRankingSpider)
    process.crawl(DefenderRankingSpider)
    process.crawl(SupporterRankingSpider)

    process.start()

    aggressor_ranking_list = AggressorRankingSpider.ranking_list
    defender_ranking_list = DefenderRankingSpider.ranking_list
    supporter_ranking_list = SupporterRankingSpider.ranking_list

    bb_text_att = """[spoiler=RA][table]
        [**]Ranking plemienny[||]Ranking ogólny[||]Nazwa[||]Plemię[||]Wynik[||][/**]
        """
    bb_text_att += generate_bb_text(aggressor_ranking_list, {0: 17, 1: 15, 2: 13, 3: 11, 4: 11}, 9, )
    bb_text_att += """[/table][/spoiler]"""

    bb_text_def = """[spoiler=RO][table]
        [**]Ranking plemienny[||]Ranking ogólny[||]Nazwa[||]Plemię[||]Wynik[||][/**]
        """
    bb_text_def += generate_bb_text(defender_ranking_list, {0: 17, 1: 15, 2: 13, 3: 11, 4: 11}, 9, )
    bb_text_def += """[/table][/spoiler]"""

    bb_text_sup = """[spoiler=RW][table]
        [**]Ranking plemienny[||]Ranking ogólny[||]Nazwa[||]Plemię[||]Wynik[||][/**]
        """
    bb_text_sup += generate_bb_text(supporter_ranking_list, {0: 17, 1: 15, 2: 13, 3: 11, 4: 11}, 9, )
    bb_text_sup += """[/table][/spoiler]"""

    bb_text = bb_text_att + bb_text_def + bb_text_sup

    print(f'{bb_text}')

    pyperclip.copy(f'{bb_text}')
