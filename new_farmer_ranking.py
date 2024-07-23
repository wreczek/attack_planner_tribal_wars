import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pyperclip

# Base URL
base_url = 'https://pl204.plemiona.pl/guest.php?screen=ranking&mode=in_a_day&type=loot_res&offset='

# List of tribes to filter
tribes = ['NW', '*NW*', '!NW!', 'NW?', 'NW+']


# Function to get player data from a URL
def get_players(offset):
    url = f"{base_url}{offset}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', {'class': 'vis', 'width': '100%'})  # Find the table containing player data

    players = []
    if table:
        rows = table.find_all('tr')[1:]  # Skip the header row
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 5:  # Ensure the row contains player data
                rank = cols[0].get_text().strip()
                player_name = cols[1].get_text().strip()
                tribe_name = cols[2].get_text().strip()
                resources_looted = cols[3].get_text().strip()
                date = cols[4].get_text().strip()
                players.append((rank, player_name, tribe_name, resources_looted, date))
    return players


# Function to filter players by tribe
def filter_players_by_tribe(players, tribes):
    return [player for player in players if player[2] in tribes]


# Function to generate BBCode
def generate_bbcode(players):
    bbcode = "[spoiler={}]\n".format(datetime.today().strftime('%d.%m.%Y'))
    bbcode += "[table]\n"
    bbcode += "[**] LP [||] Ranking [||] Gracz [||] Plemie [||] Wynik [||] Kiedy [/**]\n"
    for i, player in enumerate(players, 1):
        bbcode += "[*] [b]{}[/b] [|] {} [|] [player]{}[/player] [|] [ally]{}[/ally] [|] [b]{}[/b] [|] {}\n".format(
            i, player[0], player[1], player[2], player[3], player[4])
    bbcode += "[/table]\n[/spoiler]"
    return bbcode


# Function to print BBCode and copy to clipboard
def print_and_copy_bbcode(bbcode):
    print(bbcode)
    pyperclip.copy(bbcode)
    print("\nBBCode has been copied to the clipboard.")


# Main script
all_players = []
offset = 0
increment = 25

while True:
    players = get_players(offset)
    if not players:  # Break the loop if no more players are found
        break
    all_players.extend(players)
    offset += increment

filtered_players = filter_players_by_tribe(all_players, tribes)
bbcode = generate_bbcode(filtered_players)
print_and_copy_bbcode(bbcode)
