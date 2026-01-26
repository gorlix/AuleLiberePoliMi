import math

def format_time(time_float):
    """
    Converts a float time (e.g. 15.25) to a string HH:MM (e.g. 15:15).
    """
    hours = int(time_float)
    minutes = int((time_float - hours) * 60)
    return f"{hours:02d}:{minutes:02d}"

def format_room(room, until_time, mode, texts):
    """
    Formats a single room string based on the selected mode.
    
    Args:
        room (dict): Room information containing 'name', 'link', 'powerPlugs', etc.
        until_time (float): The time until the room is free.
        mode (str): 'text' or 'emoji'.
        texts (dict): Dictionary of texts for the current language.
        
    Returns:
        str: Formatted string for the room.
    """
    # Use ideographic space (U+3000) for alignment if plug is missing
    # Normal space is too narrow compared to emoji.
    emoji_plug = "🔌" if room['powerPlugs'] else '\u3000'
    
    if mode == 'emoji':
        # Emoji Mode: <link>room</link> 🔌 🕒 ➜ 20:00
        formatted_time = format_time(until_time)
        return f' <a href ="{room["link"]}">{room["name"]:^10}</a> {emoji_plug} 🕒 ➜ {formatted_time}\n'
    else:
        # Text Mode (Classic): <link>room</link> (free until 20) 🔌
        # Matching the original format exactly for backward compatibility
        emoji_plug_text = "🔌" if room['powerPlugs'] else ''
        return f' <a href ="{room["link"]}">{room["name"]:^10}</a> ({texts["until"]} {until_time}) {emoji_plug_text}\n'
