import math
import random

villages_to_fake = ["407|498", "415|498", "401|492", "410|490", "403|486", "402|491", "402|489", "409|473", "410|475",
                    "402|479", "405|490", "408|498", "411|499", "413|489", "401|495", "404|494", "402|485", "401|486",
                    "403|498", "404|499", "405|499", "403|497", "399|488", "400|487", "401|486", "402|489", "402|491",
                    "411|501", "409|494", "406|494", "408|492", "409|489", "407|488", "406|482", "413|470", "412|493",
                    "407|494", "405|491", "408|476", "414|498", "407|498", "444|490", "443|487", "445|488", "444|486",
                    "441|496", "441|495", "440|498", "448|491", "449|490", "448|492", "447|495", "429|487", "416|497",
                    "413|497", "443|485", "452|496", "411|497", "412|496", "440|484", "440|483", "440|485", "447|494",
                    "438|488", "451|479", "447|484", "414|494", "416|498", "417|496", "414|497", "413|496", "413|494",
                    "410|495"]


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
    h = (h - 12) % 24

    return 3600 * h + 60 * m + s


class Attack:
    """Holds all data needed to make an attack plan"""

    def __init__(self,
                 nickname: str,
                 unit: str,
                 att_coords: list,
                 arrival_times: list) -> None:
        """Holds unit, attack villages coordinates, defender
        village coordinates and arrival time"""

        self._nickname = nickname
        self._unit = unit
        self._att_coords = att_coords
        self._arrival_times = arrival_times

    def get_plan(self) -> str:
        """Returns attack plan in bb-codes"""

        sticker = "Witamy Cię bardzo serdecznie, \n\n"
        sticker += "przed nami akcja fejkowania, o której juz wspominaliśmy. Bardzo prosimy \n"
        sticker += "abyś wysłał następujące fejki(rozpiska w spoilerze):\n"

        sticker += f"[spoiler=rozpiska]Plan fejkowania dla gracza [player]{self._nickname}[/player]:" + "\n\n"
        attacks = []
        deff_coords_list = []

        for att_coords in self._att_coords:
            arrival_time = f"{random.randint(7, 14):0>2}:{random.randint(0, 60):0>2}:{random.randint(0, 60):0>2}"

            deff_coords = villages_to_fake[random.randint(0, len(villages_to_fake) - 1)]
            while calculate_distance(att_coords, deff_coords) >= 40 or deff_coords in deff_coords_list:
                deff_coords = villages_to_fake[random.randint(0, len(villages_to_fake))]
            deff_coords_list.append(deff_coords)

            d = calculate_distance(att_coords, deff_coords)

            travel_length = calculate_travel_length(d, unit)
            attack_time = calculate_attack_time(travel_length, arrival_time)

            attacks.append([unit, att_coords, attack_time, arrival_time, deff_coords])

        attacks.sort(key=lambda x: compare_function(x[2]))

        for attack in attacks:
            sticker += f"Wyjscie [unit]{pl_to_eng(attack[0])}[/unit] z [village]" \
                       f"{attack[1]}[/village] o [b][u]{attack[2]}[/u][/b] " \
                       f"i wchodzi o [i]{attack[3]}[/i] na wioske " \
                       f"[village]{attack[4]}[/village]" + "\n\n"

        sticker += "[/spoiler]\n"
        sticker += "Jeżeli nie dasz rady dokładnie o tej godzinie wysłać, to jeżeli się spóźnisz\n"
        sticker += "o kilka minut, to nic się nie stanie. Ważne, aby ataki wchodziły w godzinach\n"
        sticker += "7-14 w czwartek, dlatego możesz przesunąć wysyłkę ataków o jakąś stałą czasową :)\n\n"

        sticker += "Pamiętaj, że jest to Twój obowiązek i zostaniesz z tego rozliczony, gdyż od tej\n"
        sticker += "akcji zależy przyszłość naszego plemienia!\n\n"
        sticker += "Pozdrawiamy\n[b][i][u]Rada Plemienia Jagody[/u][/i][/b]"

        # print(sticker)
        with open(f"C:\\Users\\lunesco\\Desktop\\nicki_jagodek\\{self._nickname}.txt", "w") as file:
            file.write(sticker)
        return sticker


if __name__ == '__main__':
    nick = "Kejun"
    unit = "taran"
    attacker_coords = ['417|486']
    att = Attack(nick,
                 unit,
                 (5 * attacker_coords)[:6],
                 [f"{random.randint(7, 14):0>2}:{random.randint(0, 60):0>2}:{random.randint(0, 60):0>2}"
                  for _ in range(len(attacker_coords))
                  ]
                 )
    att.get_plan()
