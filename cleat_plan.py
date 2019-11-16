import math
import re

import requests

N_DEFF_UNITS = 5
N_ALL_UNITS = 7
tw_s145_url_base = "https://pl145.plemiona.pl"
ALL_UNITS = ["pikinier", "miecznik", "lekki kawalerzysta", "zwiadowca", "ciezki kawalerzysta", "taran", "szlachcic"]
DEFF_UNITS = ["pikinier", "miecznik", "lekki kawalerzysta", "ciezki kawalerzysta", "taran"]


def units_speed(unit) -> float:
    """Holds all unit speed in a dictionary

    **Returns:**
        time (in seconds) needed to travel one grid
    """

    switcher = {
        "pikinier": 18 * 60 + 60 * .749999999766,
        "miecznik": 22 * 60 + 60 * .916666665807,
        "topornik": 18 * 60 + 60 * .749999999766,
        "lucznik": 18 * 60 + 60 * .749999999766,
        "zwiadowca": 9 * 60 + 60 * .3749999988281,
        "lekki kawalerzysta": 10 * 60 + 60 * .416666666667,
        "lucznik na koniu": 10 * 60 + 60 * .416666666667,
        "ciezki kawalerzysta": 11 * 60 + 60 * .458333329753,
        "taran": 31 * 60 + 60 * .250000001953,
        "katapulta": 31 * 60 + 60 * .250000001953,
        "szlachcic": 36 * 60 + 60 * .458333336751
    }

    return switcher.get(unit, 0.)


def pl_to_eng(unit: str) -> str:
    """Converts Polish terminology to English"""

    switcher = {
        "pikinier": "spear",
        "miecznik": "sword",
        "topornik": "axe",
        "lucznik": "archer",
        "zwiadowca": "spy",
        "lekki kawalerzysta": "light",
        "lucznik na koniu": "marcher",
        "ciezki kawalerzysta": "heavy",
        "taran": "ram",
        "katapulta": "catapult",
        "szlachcic": "snob"
    }

    return switcher.get(unit, "error")


def h_m_s(seconds: float) -> tuple:
    return (int(seconds // 3600),
            int((seconds % 3600) // 60),
            round(seconds) % 60)


def parse_arrival_time(time: str) -> tuple:
    h = int(time[0:2])
    m = int(time[3:5])
    s = int(time[6:8])

    return h, m, s


def calculate_distance(first_coords: str, second_coords: str) -> float:
    return math.sqrt(
        (int(first_coords[:3]) - int(second_coords[:3])) ** 2 +
        (int(first_coords[4:]) - int(second_coords[4:])) ** 2
    )


def calculate_travel_length(d: float, unit: str) -> float:
    return d * units_speed(unit)


def calculate_attack_time(travel_length: float, arrival_time: str) -> str:
    tra_h, tra_m, tra_s = h_m_s(travel_length)
    arr_h, arr_m, arr_s = parse_arrival_time(arrival_time)

    carry_m, carry_h = 0, 0

    if arr_s < tra_s:
        carry_m -= 1

    if arr_m < tra_m:
        carry_h -= 1

    att_s = (arr_s - tra_s) % 60
    att_m = (arr_m - tra_m + carry_m) % 60
    att_h = (arr_h - tra_h + carry_h) % 24

    attack_time = f"{att_h:0>2}:{att_m:0>2}:{att_s:0>2}"

    return attack_time


def split_coords(coords: str) -> tuple:
    return int(coords[:3]), int(coords[4:])


def compare_function(attack_time: str):
    h, m, s = parse_arrival_time(attack_time)
    h = (h - 18) % 24

    return 3600 * h + 60 * m + s


class Attack:
    """Holds all data needed to make an attack plan"""

    def __init__(self,
                 nicknames: list,
                 units: list,
                 att_coords: list,
                 arrival_times: list,
                 deff_coords: str) -> None:
        """Holds unit, attack villages coordinates, defender
        village coordinates and arrival time"""

        self._nicknames = nicknames
        self._units = units
        self._att_coords = att_coords
        self._deff_coords = deff_coords
        self._arrival_times = arrival_times

    # attack = Attack(n_att_villages * N_DEFF_UNITS * [nickname],
    #                 n_att_villages * ["pikinier", "miecznik", "lekki kawalerzysta", "ciezki kawalerzysta", "taran"],
    #                 N_DEFF_UNITS * user.get_user_villages(),
    #                 N_DEFF_UNITS * n_att_villages * ["22:00:00"],
    #                 "426|506"
    #                 )

    def get_plan(self) -> str:
        """Returns attack plan in bb-codes"""

        sticker = f"\n[size=12]Plan ataku na wioske [village]{self._deff_coords}[/village]:[/size]" + "\n"
        used_nicks = {}

        for nickname, unit, att_coords, arrival_time \
                in zip(self._nicknames, self._units, self._att_coords, self._arrival_times):
            if nickname not in used_nicks:
                used_nicks[nickname] = []

            d = calculate_distance(att_coords, self._deff_coords)
            travel_length = calculate_travel_length(d, unit)
            attack_time = calculate_attack_time(travel_length, arrival_time)

            used_nicks[nickname].append([unit, att_coords, attack_time, arrival_time])

        for nick_key in used_nicks:
            used_nicks[nick_key].sort(key=lambda x: compare_function(x[2]))

        for nick_key in used_nicks:
            sticker += "\n[player]" + f"{nick_key}" + "[/player]:\n"

            for ls in used_nicks[nick_key]:
                sticker += f"Wyjscie [unit]{pl_to_eng(ls[0])}[/unit] z [village]" \
                           f"{ls[1]}[/village] o [b][u]{ls[2]}[/u][/b] " \
                           f"i wchodzi o [i]{ls[3]}[/i]" + "\n"

        print(sticker)
        return sticker


def get_user_id(nickname: str) -> str:
    nickname_pattern = '<a class="" href="/guest.php\\?screen=info_player&amp;id=(\\d{1,15})">\\n\\s*' + \
                       '<img src="https://dspl.innogamescdn.com/asset/\\w{1,15}/graphic/userimage/\\w{1,15}' + \
                       'thumb" alt="" class="userimage-tiny" />\\s*' + \
                       f'{nickname}\\s*' + \
                       '</a>'

    ranking_url = f"https://pl145.plemiona.pl/guest.php?name={nickname}"
    ranking_response = requests.get(ranking_url)
    ranking_content = ranking_response.text

    if re.search(pattern=nickname_pattern, string=ranking_content):
        regexed_user_id = re.findall(pattern=nickname_pattern, string=ranking_content)[0]
    else:
        raise Exception("Nickname not found!")

    return regexed_user_id


def get_villages_from_profile(profile_url: str) -> list:
    profile_response = requests.get(profile_url)
    profile_content = profile_response.text

    villages_pattern = "<td>(\\d{3}\\|\\d{3})</td>"  # \\d catches digits, {3} - 3, \\| - char '|'

    if re.search(pattern=villages_pattern, string=profile_content):
        regexed_user_villages = re.findall(pattern=villages_pattern, string=profile_content)
    else:
        raise Exception("Villages not found!")

    return regexed_user_villages


class User:  # TODO
    """Class that holds user data, as user id
       and user villages coordinates"""

    def __init__(self, nickname: str, purpose: str) -> None:
        """Initializes user data"""

        self.nickname = nickname
        self.purpose = purpose
        self.user_id = self._extract_user_id()
        self.user_villages = self._extract_user_villages()

    def _extract_user_id(self) -> str:
        nickname_pattern = '<a class="" href="/guest.php\\?screen=info_player&amp;id=(\\d{1,15})">\\n\\s*' + \
                           '<img src="https://dspl.innogamescdn.com/asset/\\w{1,15}/graphic/userimage/\\w{1,15}' + \
                           'thumb" alt="" class="userimage-tiny" />\\s*' + \
                           f'{self.nickname}\\s*' + \
                           '</a>'

        ranking_url = f"https://pl145.plemiona.pl/guest.php?name={self.nickname}"
        ranking_response = requests.get(ranking_url)
        ranking_content = ranking_response.text

        if re.search(pattern=nickname_pattern, string=ranking_content):
            regexed_user_id = re.findall(pattern=nickname_pattern, string=ranking_content)[0]
        else:
            raise Exception("Nickname not found!")

        return regexed_user_id

    def _extract_user_villages(self):
        profile_url = f"https://pl145.plemiona.pl/guest.php?screen=info_player&id={self.user_id}"
        profile_response = requests.get(profile_url)
        profile_content = profile_response.text

        villages_pattern = "<td>(\\d{3}\\|\\d{3})</td>"  # \\d catches digits, {3} - 3, \\| - char '|'

        if re.search(pattern=villages_pattern, string=profile_content):
            regexed_user_villages = re.findall(pattern=villages_pattern, string=profile_content)
        else:
            raise Exception("Villages not found!")

        return regexed_user_villages

    def get_user_villages(self):
        return self.user_villages


if __name__ == '__main__':
    nickname = "Lunesco"
    purpose = "klinowania wioski"  # ataku na wioske

    user = User(nickname=nickname, purpose=purpose)

    n_att_villages = len(user.get_user_villages())
    attack = Attack(n_att_villages * N_DEFF_UNITS * [nickname],
                    n_att_villages * ["pikinier", "miecznik", "lekki kawalerzysta", "ciezki kawalerzysta", "taran"],
                    N_DEFF_UNITS * user.get_user_villages(),
                    N_DEFF_UNITS * n_att_villages * ["22:00:00"],
                    "426|506"
                    )
    attack.get_plan()
