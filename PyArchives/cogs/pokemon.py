"""
Pokemon cog for the Teto Discord bot.
Uses the PokeAPI (https://pokeapi.co/) to fetch Pokemon data in Spanish.
"""
import logging
from typing import Optional

import aiohttp
import discord
from discord.ext import commands

log = logging.getLogger(__name__)

POKEAPI_BASE = "https://pokeapi.co/api/v2"


def _get_spanish(entries: list[dict], key: str = "name") -> Optional[str]:
    """Extract the Spanish value from a localized entries list."""
    for entry in entries:
        lang = entry.get("language", {})
        if lang.get("name") == "es":
            return entry.get(key)
    return None


def _get_spanish_flavor(entries: list[dict]) -> Optional[str]:
    """Get the first Spanish flavor text entry."""
    for entry in entries:
        lang = entry.get("language", {})
        if lang.get("name") == "es":
            text = entry.get("flavor_text", "")
            # Clean up newlines and form feeds
            return text.replace("\n", " ").replace("\f", " ")
    return None


# Type emoji mapping
TYPE_EMOJIS: dict[str, str] = {
    "normal": "⚪", "fire": "🔥", "water": "💧", "electric": "⚡",
    "grass": "🌿", "ice": "❄️", "fighting": "🥊", "poison": "☠️",
    "ground": "🌍", "flying": "🕊️", "psychic": "🔮", "bug": "🐛",
    "rock": "🪨", "ghost": "👻", "dragon": "🐉", "dark": "🌑",
    "steel": "⚙️", "fairy": "🧚",
}

# Stat emoji mapping
STAT_EMOJIS: dict[str, str] = {
    "hp": "❤️", "attack": "⚔️", "defense": "🛡️",
    "special-attack": "✨", "special-defense": "🔰", "speed": "💨",
}


class Pokemon(commands.Cog):
    """Pokemon commands — fetch Pokemon info from PokeAPI."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._session: Optional[aiohttp.ClientSession] = None

    async def cog_unload(self) -> None:
        """Close the aiohttp session when the cog is unloaded."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    # Type cache to avoid N+1 API calls
    _type_cache: dict[str, str] = {}

    async def _get_spanish_type(self, type_url: str, fallback_name: str) -> str:
        """Get Spanish type name with caching."""
        if type_url in self._type_cache:
            return self._type_cache[type_url]

        type_data = await self._fetch_json(type_url)
        if type_data:
            type_names = type_data.get("names", [])
            es_type = _get_spanish(type_names)
            result = es_type or fallback_name
        else:
            result = fallback_name

        self._type_cache[type_url] = result
        return result

    async def _fetch_json(self, url: str) -> Optional[dict]:
        """Fetch JSON from a URL with error handling."""
        try:
            session = await self._get_session()
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    return await resp.json()
                return None
        except Exception as e:
            log.error("Error fetching %s: %s", url, e)
            return None

    @commands.command(name="pokemon", aliases=["poke", "pokedex"])
    async def pokemon_info(self, ctx: commands.Context, *, nombre: str) -> None:
        """🔍 Busca información de un Pokémon por su nombre."""
        async with ctx.typing():
            # Fetch pokemon data
            pokemon_name = nombre.strip().lower().replace(" ", "-")
            pokemon_data = await self._fetch_json(f"{POKEAPI_BASE}/pokemon/{pokemon_name}")

            if not pokemon_data:
                embed = discord.Embed(
                    title="❌ Pokémon no encontrado",
                    description=f"No encontré a **{nombre}**. Verifica el nombre e intenta de nuevo.",
                    color=discord.Color.red(),
                )
                await ctx.send(embed=embed)
                return

            # Fetch species data for Spanish info
            species_url = pokemon_data.get("species", {}).get("url", "")
            species_data = await self._fetch_json(species_url) if species_url else None

            # Get Spanish name
            spanish_name = None
            if species_data:
                names = species_data.get("names", [])
                spanish_name = _get_spanish(names)

            pokemon_display_name = spanish_name or pokemon_data.get("name", nombre).title()
            pokemon_id = pokemon_data.get("id", 0)

            # Get types in Spanish (with cache)
            types = []
            for t in pokemon_data.get("types", []):
                type_url = t.get("type", {}).get("url", "")
                fallback = t["type"]["name"]
                es_type = await self._get_spanish_type(type_url, fallback) if type_url else fallback
                types.append(es_type)

            # Get Spanish flavor text (description)
            description = None
            if species_data:
                flavor_entries = species_data.get("flavor_text_entries", [])
                description = _get_spanish_flavor(flavor_entries)

            # Get stats
            stats = []
            for s in pokemon_data.get("stats", []):
                stat_name = s.get("stat", {}).get("name", "")
                stat_value = s.get("base_stat", 0)
                emoji = STAT_EMOJIS.get(stat_name, "📊")
                stats.append(f"{emoji} **{stat_name.replace('-', ' ').title()}:** {stat_value}")

            # Get sprite URL
            sprite_url = (
                pokemon_data.get("sprites", {}).get("other", {})
                .get("official-artwork", {}).get("front_default")
                or pokemon_data.get("sprites", {}).get("front_default")
            )

            # Get height and weight
            height = pokemon_data.get("height", 0) / 10  # decimeters to meters
            weight = pokemon_data.get("weight", 0) / 10  # hectograms to kg

            # Create embed
            color = discord.Color.from_rgb(255, 105, 180)  # Pink for Teto bot
            embed = discord.Embed(
                title=f"#{pokemon_id} {pokemon_display_name}",
                color=color,
            )

            if description:
                embed.description = description

            if sprite_url:
                embed.set_thumbnail(url=sprite_url)

            # Types with emojis
            type_str = " / ".join(
                f"{TYPE_EMOJIS.get(t.lower(), '❓')} {t}" for t in types
            )
            embed.add_field(name="🔰 Tipo", value=type_str, inline=True)

            # Height and weight
            embed.add_field(name="📏 Altura", value=f"{height:.1f} m", inline=True)
            embed.add_field(name="⚖️ Peso", value=f"{weight:.1f} kg", inline=True)

            # Stats
            if stats:
                embed.add_field(name="📊 Estadísticas", value="\n".join(stats), inline=False)

            # Footer
            embed.set_footer(
                text=f"Datos de PokeAPI • Solicitado por {ctx.author.name}",
                icon_url=ctx.author.display_avatar.url,
            )

            await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Load the Pokemon cog."""
    await bot.add_cog(Pokemon(bot))
