def get_value(number, size_dict, default_number):
    return size_dict.get(number, default_number)


def generate_bb_text(data, size_dict, default_number, plunderer_score_dict=None):
    bb_text = ''
    for i, item in enumerate(data):
        size = get_value(i, size_dict, default_number)
        player_name = item['name']

        bb_text += f"[*][size={size}]{i+1}[/size][|]"
        bb_text += f"[size={size}]{item['ranking']}[/size][|]"
        bb_text += f"[size={size}][player]{player_name}[/player][/size][|]"
        bb_text += f"[size={size}][ally]{item['tribe']}[/ally][/size][|]"
        bb_text += f"[size={size}]{item['score']}[/size][|]"
        if plunderer_score_dict:
            bb_text += f"[size={size}]{plunderer_score_dict[player_name]}[/size]\n"
        else:
            bb_text += '\n'
    return bb_text


def format_number(number):
    if number < 1000:
        return f"{number}"
    suffixes = ["", "K", "M", "B", "T"]
    index = 0

    while number >= 1000 and index < len(suffixes) - 1:
        number /= 1000.0
        index += 1

    formatted_number = f"{number:.2f}{suffixes[index]}"

    return formatted_number
