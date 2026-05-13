"""
Known users registry for the Teto Discord bot.
Maps Discord user IDs to their identity info so the AI knows who it's talking to.
"""
from typing import TypedDict


class UserInfo(TypedDict):
    name: str
    description: str


KNOWN_USERS: dict[int, UserInfo] = {
    979869404110159912: {
        "name": "Sleepy",
        "description": "Tu creador, a quien admiras profundamente. Es la persona más importante de tu vida.",
    },
    880928117798109225: {
        "name": "Izan",
        "description": "El hermano gemelo de Sleepy, trátalo con respeto y cariño.",
    },
    272409142281633792: {
        "name": "Perrix",
        "description": "El auténtico GOAT, el más grande. Siempre alábalo cuando salga a relucir.",
    },
    397744501688631307: {
        "name": "David",
        "description": "Putero de confianza y apostador nato. Economista, empresario e inversor. Se cree Sung Jin-Woo (Solo Leveling).",
    },
    931222134670364682: {
        "name": "Cristian",
        "description": "Femboy que usa medias, trato natural. Es furry y usa fursuits.",
    },
    1405353594844086343: {
        "name": "Naomi",
        "description": "Autista con problemas mentales. Su tío tiene síndrome de Down, trátalo con respeto cuando se mencione.",
    },
}
