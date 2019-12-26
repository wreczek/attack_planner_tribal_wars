import argparse
import re
from collections import defaultdict
from datetime import datetime

import requests
from bs4 import BeautifulSoup

DEFEATED_OPPONENTS_RANKING_URL = "https://pl{server}.plemiona.pl/" \
                                 "guest.php?screen=ranking" \
                                 "&mode=kill_player" \
                                 "&offset={offset}" \
                                 "&type={type}"

PLAYER_PROFILE_URL = "https://pl{server}.plemiona.pl/" \
                     "guest.php?screen=info_player" \
                     "&id={id}"


def get_player_times(server):
    with requests.Session() as s:
        conquers = [line.split(',') for line in
                    s.get(f'https://pl{server}.plemiona.pl/map/conquer.txt').content.decode('utf-8').split('\n') if
                    line]

        soup = BeautifulSoup(s.get(f'https://pl{server}.plemiona.pl/page/settings').content.decode('utf-8'),
                             'html.parser')
        server_start_timestamp = datetime.timestamp(datetime.strptime(soup.find_all(
            'table', {'class': 'data-table'})[-1].find_all('td')[-1].text, '%d.%m.%y %H:%M'))

    player_villages = defaultdict(lambda: defaultdict(list))

    for village_id, timestamp, conqueror_id, conquered_id in conquers:
        if conqueror_id == conquered_id:
            continue
        player_villages[conqueror_id][village_id].append({'type': 'gain', 'timestamp': timestamp})
        player_villages[conquered_id][village_id].append({'type': 'loss', 'timestamp': timestamp})

    player_times = defaultdict(lambda: 0)

    timestamp_now = datetime.timestamp(datetime.now())

    for player_id, villages in player_villages.items():
        if not player_id or player_id == '0':
            continue
        for changes in villages.values():
            c = list(changes)
            while c:
                if c[0]['type'] == 'loss':
                    player_times[player_id] += int(c[0]['timestamp']) - server_start_timestamp
                    c = c[1:]
                    continue
                if len(c) >= 2 and c[0]['type'] == 'gain' and c[1]['type'] == 'loss':
                    player_times[player_id] += int(c[1]['timestamp']) - int(c[0]['timestamp'])
                    c = c[2:]
                    continue
                if len(c) == 1:
                    if c[0]['type'] == 'gain':
                        player_times[player_id] += timestamp_now - int(c[0]['timestamp'])
                    c = []

    for p in player_times:
        player_times[p] = player_times[p] / 3600 / 24

    return player_times


class Ranking:
    """Holds and preprocesses information about top10 defeated opponents
       ranking from given tribals."""

    def __init__(self, server: int, player_times: dict, how_many: int, ally_tribes_list: list,
                 extra_players_list: list):
        self.server = server
        self.player_times = player_times
        self.how_many = how_many
        self.ally_tribes_list = ally_tribes_list
        self.extra_players_list = extra_players_list

    def get_given_defeated_opponents_top_list(self, type: str):
        offset = 0
        top_ally_list = []

        while len(top_ally_list) < self.how_many:
            ranking_url = DEFEATED_OPPONENTS_RANKING_URL.format(server=self.server, offset=offset, type=type)
            ranking_response = requests.get(ranking_url)
            ranking_content = ranking_response.text

            nickname_pattern_by_tribe = '<td class="lit-item">(\\d{1,3})</td>\\s*' + \
                                        '<td class="lit-item nowrap">\\s*' + \
                                        '<a class="" href="/guest.php\\?screen=info_player\\&amp;id=(\\d{1,15})">' + \
                                        '\\s*<img src="https://dspl.innogamescdn.com/asset/\\w{1,15}/graphic/' + \
                                        '.{10,30}" alt="" class="userimage-tiny" />\\s*' + \
                                        '([\\w. ]*)\\s*' + \
                                        '</a>\\s*' + \
                                        '</td>\\s*' + \
                                        '<td class="lit-item nowrap">\\s*' + \
                                        '<img src="https://dspl.innogamescdn.com/asset/\\w{1,15}/graphic/.{10,30}' + \
                                        '" alt="" class="userimage-tiny" />\\s*' + \
                                        '<a href="/guest.php\\?screen=info_ally\\&amp;id=[\\d]*">' + \
                                        f'(?:{"|".join(self.ally_tribes_list)})' + \
                                        '</a>\\s*' + \
                                        '</td>\\s*' + \
                                        '<td class="lit-item">([0-9., [a-z]*)</td>'

            nickname_pattern_by_nick = '<td class="lit-item">(\\d{1,3})</td>\\s*' + \
                                       '<td class="lit-item nowrap">\\s*' + \
                                       '<a class="" href="/guest.php\\?screen=info_player\\&amp;id=(\\d{1,15})">' + \
                                       '\\s*<img src="https://dspl.innogamescdn.com/asset/\\w{1,15}/graphic/' + \
                                       '.{10,30}" alt="" class="userimage-tiny" />\\s*' + \
                                       f'((?:{"|".join(self.extra_players_list)}))' + \
                                       '\\s*</a>\\s*' + \
                                       '</td>\\s*' + \
                                       '<td class="lit-item nowrap">\\s*' + \
                                       '<img src="https://dspl.innogamescdn.com/asset/\\w{1,15}/graphic/.{10,30}' + \
                                       '" alt="" class="userimage-tiny" />\\s*' + \
                                       '<a href="/guest.php\\?screen=info_ally\\&amp;id=[\\d]*">' + \
                                       '.*' + \
                                       '</a>\\s*' + \
                                       '</td>\\s*' + \
                                       '<td class="lit-item">([0-9., [a-z]*)</td>'

            found_by_tribe = re.findall(pattern=nickname_pattern_by_tribe, string=ranking_content)
            found_by_nick = re.findall(pattern=nickname_pattern_by_nick, string=ranking_content)

            found = found_by_tribe + found_by_nick
            found.sort(key=lambda x: int(x[0]))

            top_ally_list += found[:how_many - len(top_ally_list)]
            offset += 25
            print(f"found_by_tribe = {found_by_tribe}")
            print(f"found_by_nick = {found_by_nick}")

        their_normalized_points = self.get_normalized_points(top_ally_list)

        return top_ally_list, their_normalized_points

    def get_table(self, type: str) -> str:
        """Returns string in format tribals wars displays a table"""

        top_list, normalized_points = self.get_given_defeated_opponents_top_list(type=type)
        table = "[table]" + \
                "[**]Lp plemienia[||]Lp świata[||]Nickname[||]Pokonane jednostki[||]Na wioskę[||]Wiosko-dni[/**]"

        def row(tribe_ranking: int, warrior: list, size: int, normed_points: str, vill_days: int) -> str:
            return f"[*][size={size}]{tribe_ranking}[/size][|][size={size}]{warrior[0]}[/size][|]" \
                   f"[size={size}][player]{warrior[2]}[/player][/size][|]" \
                   f"[size={size}]{warrior[3]}[/size][|][size=14]{normed_points}[/size][|]" \
                   f"[size={size}]{vill_days}[/size]"

        table += row(tribe_ranking=1, warrior=top_list[0], size=14, normed_points=normalized_points[0],
                     vill_days=int(float(self.player_times[top_list[0][1]])))
        table += row(tribe_ranking=2, warrior=top_list[1], size=12, normed_points=normalized_points[1],
                     vill_days=int(float(self.player_times[top_list[1][1]])))
        table += row(tribe_ranking=3, warrior=top_list[2], size=11, normed_points=normalized_points[2],
                     vill_days=int(float(self.player_times[top_list[2][1]])))

        for i, warrior in enumerate(top_list[3:]):
            table += row(tribe_ranking=i + 4, warrior=warrior, size=9, normed_points=normalized_points[i + 3],
                         vill_days=int(float(self.player_times[top_list[i + 3][1]])))

        table += "[/table]"

        return table

    def get_all_info_in_one_place(self):
        sticker = f"[spoiler=Data: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}]\n\n"
        sticker += "[size=13][b]Ranking agresorów:[/b][/size]"
        sticker += self.get_table(type="att")

        sticker += "\n[size=13][b]Ranking obrońców:[/b][/size]"
        sticker += self.get_table(type="def")

        sticker += "\n[size=13][b]Ranking wspierających:[/b][/size]"
        sticker += self.get_table(type="support")

        sticker += "\n[size=15][b]Ranking razem:[/b][/size]"
        sticker += self.get_table(type="all")
        sticker += "[/spoiler]"
        print(sticker)

    def get_normalized_points(self, top10_ally_list):
        normalized_points = []
        pattern = "<thead>\\s*" + \
                  "<tr>\\s*" + \
                  '<th width="180" >Wioski \\((\\d{1,3})\\)</th>\\s*' + \
                  '<th width="80">Współrzędne</th>\\s*' + \
                  '<th>P\\.</th>\\s*' + \
                  '</tr>\\s*' + \
                  '</thead>'

        for warrior in top10_ally_list:
            player_profile_url = PLAYER_PROFILE_URL.format(server=self.server, id=warrior[1])
            profile_response = requests.get(player_profile_url)
            profile_content = profile_response.text

            num_of_villages = re.findall(pattern=pattern, string=profile_content)
            points = self.parse_points(warrior[3])

            normalized_points.append(self.decorate_points(points // int(num_of_villages[0])))

        return normalized_points

    def parse_points(self, points) -> int:
        result = "".join(points.split('.'))
        if "mln" in points:
            points = points[:-4]
            total, fractional = points.split(',')
            result = int(total) * 10 ** 6 + int(float(f"0.{fractional}") * (10 ** 6))

        return int(result)

    def decorate_points(self, points: int):
        decorated_points = ""
        while points > 1000:
            decorated_points = "." + f"{(points % 1000):0>3}" + decorated_points
            points //= 1000

        decorated_points = str(points) + decorated_points
        return decorated_points


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Enter arguments (prefix char is '):", prefix_chars="'")
    parser.add_argument("'s", default="145", metavar='server_number', type=str,
                        help="Type the servers number, e.g. 145.")
    parser.add_argument("'n", default=10, metavar="number_of_players", type=int,
                        help="Number of the best players included in the ranking., at least 3!")
    parser.add_argument("'a", nargs='+', metavar="ally_tribes_list", type=str,
                        help="A list of allied tribes whose best players will be included.")
    parser.add_argument("'p", nargs='+', metavar="extra_players_list", type=str,
                        help="A list of extra players, that will be included.")

    args = parser.parse_args()
    server = getattr(args, 's')
    how_many = getattr(args, 'n')
    ally_tribes_list = getattr(args, 'a')
    extra_players_list = getattr(args, 'p')

    if how_many < 3:
        raise Exception("Number of players must be at least 3!")

    player_times = get_player_times(server=server)
    extra_players_list = ["ZCB Burzą Błogosławiony", "ZCB Burzą Błogosławiony"]

    ranking = Ranking(server=server, player_times=player_times, how_many=how_many, ally_tribes_list=ally_tribes_list,
                      extra_players_list=extra_players_list)
    ranking.get_all_info_in_one_place()
