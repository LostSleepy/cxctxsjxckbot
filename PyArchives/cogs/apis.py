"""
Unified APIs cog for the Teto Discord bot.
Combines Pokemon, Geography, Anime, Dogs, Cocktails, and Space commands.
All APIs are free and require no API key (except NASA APOD uses DEMO_KEY).
"""
import asyncio
import logging
import re
import urllib.parse
import time
from typing import Optional

import aiohttp
import discord
from discord.ext import commands

log = logging.getLogger(__name__)

# ── API Base URLs ────────────────────────────────────────────────────────────
POKEAPI_BASE = "https://pokeapi.co/api/v2"
REST_COUNTRIES_BASE = "https://restcountries.com/v3.1"
OPEN_METEO_BASE = "https://api.open-meteo.com/v1"
JIKAN_BASE = "https://api.jikan.moe/v4"
DOG_CEO_BASE = "https://dog.ceo/api"
COCKTAIL_DB_BASE = "https://www.thecocktaildb.com/api/json/v1/1"
NASA_APOD_URL = "https://api.nasa.gov/planetary/apod"
JOKEAPI_BASE = "https://v2.jokeapi.dev"
MYMEMORY_BASE = "https://api.mymemory.translated.net"
THEMEALDB_BASE = "https://www.themealdb.com/api/json/v1/1"
CATFACT_URL = "https://catfact.ninja/fact"


# ── Helper: extract Spanish from localized entries ──────────────────────────
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
            return text.replace("\n", " ").replace("\f", " ")
    return None


# ── Type emoji mapping (Pokemon) ────────────────────────────────────────────
TYPE_EMOJIS: dict[str, str] = {
    "normal": "⚪", "fire": "🔥", "water": "💧", "electric": "⚡",
    "grass": "🌿", "ice": "❄️", "fighting": "🥊", "poison": "☠️",
    "ground": "🌍", "flying": "🕊️", "psychic": "🔮", "bug": "🐛",
    "rock": "🪨", "ghost": "👻", "dragon": "🐉", "dark": "🌑",
    "steel": "⚙️", "fairy": "🧚",
}

STAT_EMOJIS: dict[str, str] = {
    "hp": "❤️", "attack": "⚔️", "defense": "🛡️",
    "special-attack": "✨", "special-defense": "🔰", "speed": "💨",
}

REGION_EMOJIS: dict[str, str] = {
    "africa": "🌍", "americas": "🌎", "asia": "🌏",
    "europe": "🏰", "oceania": "🌊", "antarctic": "🧊",
}

WMO_CODES: dict[int, str] = {
    0: "☀️ Despejado", 1: "🌤️ Mayormente despejado", 2: "⛅ Parcialmente nublado",
    3: "☁️ Nublado", 45: "🌫️ Niebla", 48: "🌫️ Niebla con escarcha",
    51: "🌦️ Lluvia ligera", 53: "🌦️ Lluvia moderada", 55: "🌧️ Lluvia intensa",
    61: "🌧️ Lluvia", 63: "🌧️ Lluvia moderada", 65: "🌧️ Lluvia fuerte",
    71: "🌨️ Nieve ligera", 73: "🌨️ Nieve moderada", 75: "❄️ Nieve fuerte",
    80: "🌦️ Chubascos", 81: "🌧️ Chubascos moderados", 82: "⛈️ Chubascos violentos",
    95: "⛈️ Tormenta", 96: "⛈️ Tormenta con granizo", 99: "⛈️ Tormenta con granizo fuerte",
}

# Language names for translation
LANG_NAMES: dict[str, str] = {
    "es": "Español", "en": "Inglés", "fr": "Francés", "de": "Alemán",
    "it": "Italiano", "pt": "Portugués", "ja": "Japonés", "ko": "Coreano",
    "zh": "Chino", "ru": "Ruso", "ar": "Árabe",
}


class Apis(commands.Cog):
    """Unified API commands — Pokemon, Geography, Anime, Dogs, Cocktails, Space."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._session: Optional[aiohttp.ClientSession] = None
        self._type_cache: dict[str, str] = {}
        self._jikan_last_call: float = 0.0
        self._jikan_lock: asyncio.Lock = asyncio.Lock()

    async def cog_unload(self) -> None:
        """Close the aiohttp session when the cog is unloaded."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

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

    def _sanitize(self, text: str) -> str:
        """Sanitize input: strip, lowercase, remove special chars."""
        return re.sub(r"[^a-záéíóúñü\s-]", "", text.strip().lower()).strip()

    # ═══════════════════════════════════════════════════════════════════════════
    # POKEMON
    # ═══════════════════════════════════════════════════════════════════════════

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

    @commands.command(name="pokemon", aliases=["poke", "pokedex"])
    async def pokemon_info(self, ctx: commands.Context, *, nombre: str) -> None:
        """🔍 Busca información de un Pokémon por su nombre."""
        async with ctx.typing():
            pokemon_name = re.sub(r"[^a-z0-9\s-]", "", nombre.strip().lower())
            pokemon_name = re.sub(r"\s+", "-", pokemon_name).strip("-")

            if not pokemon_name:
                embed = discord.Embed(
                    title="❌ Nombre no válido",
                    description="Escribe el nombre de un Pokémon. Ej: `cx!pokemon pikachu`",
                    color=discord.Color.red(),
                )
                await ctx.send(embed=embed)
                return

            pokemon_data = await self._fetch_json(f"{POKEAPI_BASE}/pokemon/{pokemon_name}")

            if not pokemon_data:
                embed = discord.Embed(
                    title="❌ Pokémon no encontrado",
                    description=f"No encontré a **{nombre}**. Verifica el nombre e intenta de nuevo.",
                    color=discord.Color.red(),
                )
                await ctx.send(embed=embed)
                return

            species_url = pokemon_data.get("species", {}).get("url", "")
            species_data = await self._fetch_json(species_url) if species_url else None

            spanish_name = None
            if species_data:
                spanish_name = _get_spanish(species_data.get("names", []))

            pokemon_display_name = spanish_name or pokemon_data.get("name", nombre).title()
            pokemon_id = pokemon_data.get("id", 0)

            types = []
            for t in pokemon_data.get("types", []):
                type_url = t.get("type", {}).get("url", "")
                fallback = t["type"]["name"]
                es_type = await self._get_spanish_type(type_url, fallback) if type_url else fallback
                types.append(es_type)

            description = None
            if species_data:
                description = _get_spanish_flavor(species_data.get("flavor_text_entries", []))

            stats = []
            for s in pokemon_data.get("stats", []):
                stat_name = s.get("stat", {}).get("name", "")
                stat_value = s.get("base_stat", 0)
                emoji = STAT_EMOJIS.get(stat_name, "📊")
                stats.append(f"{emoji} **{stat_name.replace('-', ' ').title()}:** {stat_value}")

            sprite_url = (
                pokemon_data.get("sprites", {}).get("other", {})
                .get("official-artwork", {}).get("front_default")
                or pokemon_data.get("sprites", {}).get("front_default")
            )

            height = pokemon_data.get("height", 0) / 10
            weight = pokemon_data.get("weight", 0) / 10

            embed = discord.Embed(title=f"#{pokemon_id} {pokemon_display_name}", color=discord.Color.from_rgb(255, 105, 180))
            if description:
                embed.description = description
            if sprite_url:
                embed.set_thumbnail(url=sprite_url)

            type_str = " / ".join(f"{TYPE_EMOJIS.get(t.lower(), '❓')} {t}" for t in types)
            embed.add_field(name="🔰 Tipo", value=type_str, inline=True)
            embed.add_field(name="📏 Altura", value=f"{height:.1f} m", inline=True)
            embed.add_field(name="⚖️ Peso", value=f"{weight:.1f} kg", inline=True)
            if stats:
                embed.add_field(name="📊 Estadísticas", value="\n".join(stats), inline=False)
            embed.set_footer(text=f"PokeAPI • {ctx.author.name}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    # ═══════════════════════════════════════════════════════════════════════════
    # GEOGRAPHY (Pais + Clima)
    # ═══════════════════════════════════════════════════════════════════════════

    @commands.command(name="pais", aliases=["country", "país", "paises"])
    async def pais_info(self, ctx: commands.Context, *, nombre: str) -> None:
        """🌍 Busca información de un país por su nombre (en español)."""
        async with ctx.typing():
            search = self._sanitize(nombre)
            if not search:
                embed = discord.Embed(title="❌ Nombre no válido", description="Escribe el nombre de un país. Ej: `cx!pais España`", color=discord.Color.red())
                await ctx.send(embed=embed)
                return

            fields = "name,capital,population,region,subregion,languages,currencies,flags,timezones,car,area,borders"
            data = await self._fetch_json(f"{REST_COUNTRIES_BASE}/translation/{search}?fields={fields}")
            if not data:
                data = await self._fetch_json(f"{REST_COUNTRIES_BASE}/name/{search}?fields={fields}")

            if not data or not isinstance(data, list) or len(data) == 0:
                embed = discord.Embed(title="❌ País no encontrado", description=f"No encontré a **{nombre}**. Verifica el nombre.", color=discord.Color.red())
                await ctx.send(embed=embed)
                return

            country = data[0]
            name_data = country.get("name", {})
            official_name = name_data.get("official", "")

            native = name_data.get("nativeName", {})
            spanish_name = ""
            for lang_code in ("spa", "est", "arg", "mex", "col"):
                if lang_code in native:
                    spanish_name = native[lang_code].get("common", "")
                    break

            display_name = spanish_name or name_data.get("common", nombre)
            capital = ", ".join(country.get("capital", ["Desconocida"]))
            population = country.get("population", 0)
            area = country.get("area", 0)
            region = country.get("region", "Desconocida")
            subregion = country.get("subregion", "")

            all_timezones = country.get("timezones", [])
            tz_display = ", ".join(all_timezones[:3])
            if len(all_timezones) > 3:
                tz_display += f" (+{len(all_timezones) - 3} más)"

            langs = country.get("languages", {})
            lang_str = ", ".join(langs.values()) if langs else "N/A"

            currencies = country.get("currencies", {})
            curr_list = [f"{info.get('name', code)} ({info.get('symbol', '')})" for code, info in currencies.items()]
            curr_str = ", ".join(curr_list) if curr_list else "N/A"

            flag_url = country.get("flags", {}).get("png", "")
            car = country.get("car", {})
            driving_side = "Izquierda 🇬🇧" if car.get("side") == "left" else "Derecha 🚗"
            region_emoji = REGION_EMOJIS.get(region.lower(), "🌍")
            pop_formatted = f"{population:,}".replace(",", ".")

            embed = discord.Embed(title=f"{region_emoji} {display_name}", description=f"**{official_name}**" if official_name else None, color=discord.Color.from_rgb(255, 105, 180))
            if flag_url:
                embed.set_thumbnail(url=flag_url)
            embed.add_field(name="🏛️ Capital", value=capital, inline=True)
            embed.add_field(name="👥 Población", value=f"{pop_formatted} hab.", inline=True)
            embed.add_field(name="📏 Área", value=f"{area:,.0f} km²", inline=True)
            embed.add_field(name="🌐 Región", value=f"{region}" + (f" ({subregion})" if subregion else ""), inline=True)
            embed.add_field(name="🗣️ Idiomas", value=lang_str, inline=True)
            embed.add_field(name="💱 Monedas", value=curr_str, inline=True)
            embed.add_field(name="🕐 Zonas horarias", value=tz_display, inline=False)
            embed.add_field(name="🚗 Conducir por", value=driving_side, inline=True)
            embed.set_footer(text=f"REST Countries API • {ctx.author.name}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    @commands.command(name="clima", aliases=["weather", "tiempo"])
    async def clima_info(self, ctx: commands.Context, *, ciudad: str) -> None:
        """🌤️ Consulta el clima actual de una ciudad."""
        async with ctx.typing():
            search = self._sanitize(ciudad)
            if not search:
                embed = discord.Embed(title="❌ Ciudad no válida", description="Escribe el nombre de una ciudad. Ej: `cx!clima Madrid`", color=discord.Color.red())
                await ctx.send(embed=embed)
                return

            geo_data = await self._fetch_json(f"https://geocoding-api.open-meteo.com/v1/search?name={search}&count=1&language=es")
            if not geo_data or not geo_data.get("results"):
                embed = discord.Embed(title="❌ Ciudad no encontrada", description=f"No encontré **{ciudad}**.", color=discord.Color.red())
                await ctx.send(embed=embed)
                return

            location = geo_data["results"][0]
            lat, lon = location["latitude"], location["longitude"]
            city_name = location.get("name", ciudad)
            country = location.get("country", "")
            admin1 = location.get("admin1", "")

            weather_data = await self._fetch_json(
                f"{OPEN_METEO_BASE}/forecast?latitude={lat}&longitude={lon}"
                "&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,wind_direction_10m"
                "&timezone=auto"
            )

            if not weather_data or "current" not in weather_data:
                embed = discord.Embed(title="❌ Error", description="No pude obtener el clima.", color=discord.Color.red())
                await ctx.send(embed=embed)
                return

            current = weather_data["current"]
            temp = current.get("temperature_2m", 0)
            feels_like = current.get("apparent_temperature", 0)
            humidity = current.get("relative_humidity_2m", 0)
            precipitation = current.get("precipitation", 0)
            weather_code = current.get("weather_code", 0)
            wind_speed = current.get("wind_speed_10m", 0)
            wind_dir = current.get("wind_direction_10m", 0)

            weather_desc = WMO_CODES.get(weather_code, f"Código {weather_code}")
            dirs = ["N", "NE", "E", "SE", "S", "SO", "O", "NO"]
            cardinal = dirs[int((wind_dir + 22.5) / 45) % 8]

            location_str = city_name
            if admin1:
                location_str += f", {admin1}"
            if country:
                location_str += f" ({country})"

            embed = discord.Embed(title=f"🌤️ Clima en {location_str}", color=discord.Color.from_rgb(255, 165, 0))
            embed.add_field(name="🌡️ Temperatura", value=f"**{temp}°C** (sensación: {feels_like}°C)", inline=False)
            embed.add_field(name="☁️ Condición", value=weather_desc, inline=True)
            embed.add_field(name="💧 Humedad", value=f"{humidity}%", inline=True)
            embed.add_field(name="🌧️ Precipitación", value=f"{precipitation} mm", inline=True)
            embed.add_field(name="💨 Viento", value=f"{wind_speed} km/h {cardinal}", inline=True)
            embed.set_footer(text=f"Open-Meteo • {ctx.author.name}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    # ═══════════════════════════════════════════════════════════════════════════
    # ANIME (Jikan / MyAnimeList)
    # ═══════════════════════════════════════════════════════════════════════════

    async def _jikan_rate_limit(self) -> None:
        """Enforce Jikan's 2 req/s rate limit with a lock."""
        async with self._jikan_lock:
            elapsed = time.time() - self._jikan_last_call
            if elapsed < 0.5:
                await asyncio.sleep(0.5 - elapsed)
            self._jikan_last_call = time.time()

    @commands.command(name="anime", aliases=["mal", "myanimelist"])
    async def anime_info(self, ctx: commands.Context, *, nombre: str) -> None:
        """🎬 Busca información de un anime en MyAnimeList."""
        async with ctx.typing():
            search = self._sanitize(nombre)
            if not search:
                embed = discord.Embed(title="❌ Nombre no válido", description="Escribe el nombre de un anime. Ej: `cx!anime naruto`", color=discord.Color.red())
                await ctx.send(embed=embed)
                return

            await self._jikan_rate_limit()
            data = await self._fetch_json(f"{JIKAN_BASE}/anime?q={search}&limit=1")

            if not data or not data.get("data"):
                embed = discord.Embed(title="❌ Anime no encontrado", description=f"No encontré **{nombre}** en MyAnimeList.", color=discord.Color.red())
                await ctx.send(embed=embed)
                return

            anime = data["data"][0]
            title = anime.get("title", nombre)
            title_english = anime.get("title_english", "")
            synopsis = anime.get("synopsis", "Sin sinopsis.")
            episodes = anime.get("episodes", "?")
            status = anime.get("status", "Desconocido")
            score = anime.get("score", "N/A")
            rank = anime.get("rank", "?")
            url = anime.get("url", "")
            image_url = anime.get("images", {}).get("jpg", {}).get("large_image_url", "")
            genres = ", ".join(g.get("name", "") for g in anime.get("genres", []))
            type_ = anime.get("type", "?")
            aired = anime.get("aired", {}).get("string", "?")
            rating = anime.get("rating", "?")

            # Truncate synopsis
            if synopsis and len(synopsis) > 300:
                synopsis = synopsis[:300] + "..."

            embed = discord.Embed(title=f"🎬 {title}", description=f"*{title_english}*" if title_english and title_english != title else None, color=discord.Color.from_rgb(255, 105, 180))
            if image_url:
                embed.set_thumbnail(url=image_url)
            embed.add_field(name="📝 Sinopsis", value=synopsis or "N/A", inline=False)
            embed.add_field(name="📺 Tipo", value=type_, inline=True)
            embed.add_field(name="📚 Episodios", value=str(episodes), inline=True)
            embed.add_field(name="⭐ Puntuación", value=str(score), inline=True)
            embed.add_field(name="🏅 Ranking", value=f"#{rank}", inline=True)
            embed.add_field(name="📌 Estado", value=status, inline=True)
            embed.add_field(name="🎯 Géneros", value=genres or "N/A", inline=True)
            embed.add_field(name="📅 Emitido", value=aired, inline=True)
            embed.add_field(name="🔞 Clasificación", value=rating, inline=True)
            if url:
                embed.add_field(name="🔗 MAL", value=f"[Ver en MyAnimeList]({url})", inline=False)
            embed.set_footer(text=f"Jikan API (MyAnimeList) • {ctx.author.name}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    # ═══════════════════════════════════════════════════════════════════════════
    # DOG IMAGES (Dog CEO)
    # ═══════════════════════════════════════════════════════════════════════════

    @commands.command(name="perro", aliases=["dog", "perrito", "doggo"])
    async def perro_aleatorio(self, ctx: commands.Context, raza: Optional[str] = None) -> None:
        """🐕 Envía una imagen aleatoria de perro."""
        async with ctx.typing():
            if raza:
                search = self._sanitize(raza).replace(" ", "")
                data = await self._fetch_json(f"{DOG_CEO_BASE}/breed/{search}/images/random")
            else:
                data = await self._fetch_json(f"{DOG_CEO_BASE}/images/random")

            if not data or data.get("status") != "success":
                embed = discord.Embed(title="❌ Perro no encontrado", description="No encontré esa raza. Prueba: `cx!perro husky`", color=discord.Color.red())
                await ctx.send(embed=embed)
                return

            image_url = data.get("message", "")

            embed = discord.Embed(title="🐕 ¡Perrito!", color=discord.Color.from_rgb(255, 180, 100))
            embed.set_image(url=image_url)
            embed.set_footer(text=f"Dog CEO API • {ctx.author.name}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    @commands.command(name="razas", aliases=["breeds"])
    async def razas_perro(self, ctx: commands.Context) -> None:
        """🐕 Lista todas las razas de perro disponibles."""
        async with ctx.typing():
            data = await self._fetch_json(f"{DOG_CEO_BASE}/breeds/list/all")

            if not data or data.get("status") != "success":
                await ctx.send("❌ No pude obtener la lista de razas.")
                return

            breeds = list(data.get("message", {}).keys())
            breeds_str = ", ".join(breeds[:50])
            if len(breeds) > 50:
                breeds_str += f"\n... y {len(breeds) - 50} más."

            embed = discord.Embed(title="🐕 Razas de perro", description=f"**{len(breeds)} razas** disponibles.\nUsa `cx!perro <raza>` para ver una.", color=discord.Color.from_rgb(255, 180, 100))
            embed.add_field(name="Razas", value=breeds_str, inline=False)
            embed.set_footer(text=f"Dog CEO API • {ctx.author.name}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    # ═══════════════════════════════════════════════════════════════════════════
    # COCKTAILS (TheCocktailDB)
    # ═══════════════════════════════════════════════════════════════════════════

    @commands.command(name="coctel", aliases=["cocktail", "coctail", "drink"])
    async def coctel_info(self, ctx: commands.Context, *, nombre: str) -> None:
        """🍸 Busca una receta de coctel."""
        async with ctx.typing():
            search = self._sanitize(nombre)
            if not search:
                embed = discord.Embed(title="❌ Nombre no válido", description="Escribe el nombre de un coctel. Ej: `cx!coctel margarita`", color=discord.Color.red())
                await ctx.send(embed=embed)
                return

            data = await self._fetch_json(f"{COCKTAIL_DB_BASE}/search.php?s={search}")

            if not data or not data.get("drinks"):
                embed = discord.Embed(title="❌ Coctel no encontrado", description=f"No encontré **{nombre}**.", color=discord.Color.red())
                await ctx.send(embed=embed)
                return

            drink = data["drinks"][0]
            name = drink.get("strDrink", nombre)
            instructions = drink.get("strInstructions", "Sin instrucciones.")
            image_url = drink.get("strDrinkThumb", "")
            category = drink.get("strCategory", "?")
            glass = drink.get("strGlass", "?")
            is_alcoholic = drink.get("strAlcoholic", "?")

            # Extract ingredients
            ingredients = []
            for i in range(1, 16):
                ing = drink.get(f"strIngredient{i}")
                measure = drink.get(f"strMeasure{i}")
                if ing and ing.strip():
                    ing_str = ing.strip()
                    if measure and measure.strip():
                        ing_str = f"{measure.strip()} {ing_str}"
                    ingredients.append(ing_str)

            # Truncate instructions
            if instructions and len(instructions) > 400:
                instructions = instructions[:400] + "..."

            embed = discord.Embed(title=f"🍸 {name}", description=instructions, color=discord.Color.from_rgb(255, 105, 180))
            if image_url:
                embed.set_thumbnail(url=image_url)
            embed.add_field(name="📋 Ingredientes", value="\n".join(ingredients[:10]) if ingredients else "N/A", inline=True)
            embed.add_field(name="🍺 Tipo", value=f"{is_alcoholic} • {category}", inline=True)
            embed.add_field(name="🥤 Vaso", value=glass, inline=True)
            embed.set_footer(text=f"TheCocktailDB • {ctx.author.name}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    @commands.command(name="coctelaleatorio", aliases=["randomdrink", "randomcoctel"])
    async def coctel_aleatorio(self, ctx: commands.Context) -> None:
        """🍸 Envía una receta de coctel aleatoria."""
        async with ctx.typing():
            data = await self._fetch_json(f"{COCKTAIL_DB_BASE}/random.php")

            if not data or not data.get("drinks"):
                await ctx.send("❌ No pude obtener un coctel aleatorio.")
                return

            drink = data["drinks"][0]
            name = drink.get("strDrink", "??")
            instructions = drink.get("strInstructions", "Sin instrucciones.")
            image_url = drink.get("strDrinkThumb", "")

            ingredients = []
            for i in range(1, 16):
                ing = drink.get(f"strIngredient{i}")
                measure = drink.get(f"strMeasure{i}")
                if ing and ing.strip():
                    ing_str = ing.strip()
                    if measure and measure.strip():
                        ing_str = f"{measure.strip()} {ing_str}"
                    ingredients.append(ing_str)

            if instructions and len(instructions) > 400:
                instructions = instructions[:400] + "..."

            embed = discord.Embed(title=f"🍸 {name}", description=instructions, color=discord.Color.from_rgb(255, 105, 180))
            if image_url:
                embed.set_thumbnail(url=image_url)
            embed.add_field(name="📋 Ingredientes", value="\n".join(ingredients[:10]) if ingredients else "N/A", inline=True)
            embed.set_footer(text=f"TheCocktailDB • {ctx.author.name}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    # ═══════════════════════════════════════════════════════════════════════════
    # SPACE (NASA APOD)
    # ═══════════════════════════════════════════════════════════════════════════

    @commands.command(name="espacio", aliases=["space", "nasa", "apod"])
    async def espacio_hoy(self, ctx: commands.Context) -> None:
        """🚀 Imagen astronómica del día de la NASA."""
        async with ctx.typing():
            data = await self._fetch_json(f"{NASA_APOD_URL}?api_key=DEMO_KEY")

            if not data or data.get("error"):
                embed = discord.Embed(title="❌ Error", description="No pude obtener la imagen del día. " + (data.get("error", "") if data else ""), color=discord.Color.red())
                await ctx.send(embed=embed)
                return

            title = data.get("title", "Imagen del día")
            explanation = data.get("explanation", "Sin descripción.")
            url = data.get("url", "")
            date = data.get("date", "")
            media_type = data.get("media_type", "image")

            # Truncate explanation
            if explanation and len(explanation) > 500:
                explanation = explanation[:500] + "..."

            embed = discord.Embed(title=f"🚀 {title}", description=explanation, color=discord.Color.from_rgb(20, 20, 80))

            # Only set image if it's an image (not video)
            if media_type == "image":
                embed.set_image(url=url)
            else:
                embed.add_field(name="🔗 Ver", value=f"[Haz click aquí]({url})", inline=False)

            embed.add_field(name="📅 Fecha", value=date, inline=True)
            embed.set_footer(text=f"NASA APOD • {ctx.author.name}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)


    # ═══════════════════════════════════════════════════════════════════════════
    # JOKES IN SPANISH (JokeAPI)
    # ═══════════════════════════════════════════════════════════════════════════

    @commands.command(name="chiste", aliases=["joke", "chistes"])
    async def chiste_aleatorio(self, ctx: commands.Context) -> None:
        """😂 Envía un chiste aleatorio en español."""
        async with ctx.typing():
            data = await self._fetch_json(f"{JOKEAPI_BASE}/joke/Any?lang=es&safe-mode")

            if not data or data.get("error"):
                await ctx.send("❌ No pude obtener un chiste ahora mismo.")
                return

            if data.get("type") == "single":
                joke_text = data.get("joke", "?")
                embed = discord.Embed(title="😂 Chiste", description=joke_text, color=discord.Color.from_rgb(255, 200, 50))
            else:
                setup_text = data.get("setup", "?")
                delivery = data.get("delivery", "?")
                embed = discord.Embed(title="😂 Chiste", color=discord.Color.from_rgb(255, 200, 50))
                embed.add_field(name="Pregunta", value=setup_text, inline=False)
                embed.add_field(name="Respuesta", value=f"||{delivery}||", inline=False)

            category = data.get("category", "?")
            embed.set_footer(text=f"JokeAPI ({category}) • {ctx.author.name}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    # ═══════════════════════════════════════════════════════════════════════════
    # TRANSLATION (MyMemory)
    # ═══════════════════════════════════════════════════════════════════════════

    @commands.command(name="traducir", aliases=["translate", "trad"])
    async def traducir_texto(self, ctx: commands.Context, *, texto: str) -> None:
        """🌐 Traduce texto a español (o especifica idioma: cx!traducir en|hola)."""
        async with ctx.typing():
            # Check if user specified a target language (e.g. "en|hola")
            if "|" in texto:
                parts = texto.split("|", 1)
                lang = parts[0].strip().lower()
                text_to_translate = parts[1].strip()
            else:
                lang = "es"
                text_to_translate = texto.strip()

            if not text_to_translate:
                embed = discord.Embed(title="❌ Texto vacío", description="Usa: `cx!traducir hola` o `cx!traducir en|hola`", color=discord.Color.red())
                await ctx.send(embed=embed)
                return

            # Truncate if too long
            if len(text_to_translate) > 500:
                text_to_translate = text_to_translate[:500]

            data = await self._fetch_json(
                f"{MYMEMORY_BASE}/?q={urllib.parse.quote(text_to_translate)}&langpair=auto|{lang}"
            )

            if not data or data.get("responseStatus") != 200:
                await ctx.send("❌ No pude traducir el texto.")
                return

            translated = data.get("responseData", {}).get("translatedText", "")

            # Language name mapping
            lang_name = LANG_NAMES.get(lang, lang.upper())

            embed = discord.Embed(title="🌐 Traducción", color=discord.Color.from_rgb(100, 200, 255))
            embed.add_field(name=f"Original ({lang_name})", value=f"||{text_to_translate}||" if len(text_to_translate) > 200 else text_to_translate, inline=False)
            embed.add_field(name="Traducción", value=translated, inline=False)
            embed.set_footer(text=f"MyMemory • {ctx.author.name}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    # ═══════════════════════════════════════════════════════════════════════════
    # RECIPES (TheMealDB)
    # ═══════════════════════════════════════════════════════════════════════════

    @commands.command(name="receta", aliases=["recipe", "comida"])
    async def receta_info(self, ctx: commands.Context, *, nombre: str) -> None:
        """🍳 Busca una receta de comida."""
        async with ctx.typing():
            search = self._sanitize(nombre)
            if not search:
                embed = discord.Embed(title="❌ Nombre no válido", description="Escribe el nombre de una comida. Ej: `cx!receta pasta`", color=discord.Color.red())
                await ctx.send(embed=embed)
                return

            data = await self._fetch_json(f"{THEMEALDB_BASE}/search.php?s={search}")

            if not data or not data.get("meals"):
                embed = discord.Embed(title="❌ Receta no encontrada", description=f"No encontré **{nombre}**. Prueba otro nombre.", color=discord.Color.red())
                await ctx.send(embed=embed)
                return

            meal = data["meals"][0]
            name = meal.get("strMeal", nombre)
            instructions = meal.get("strInstructions", "Sin instrucciones.")
            image_url = meal.get("strMealThumb", "")
            category = meal.get("strCategory", "?")
            area = meal.get("strArea", "?")
            tags = meal.get("strTags", "") or "N/A"

            # Extract ingredients
            ingredients = []
            for i in range(1, 21):
                ing = meal.get(f"strIngredient{i}")
                measure = meal.get(f"strMeasure{i}")
                if ing and ing.strip():
                    ing_str = ing.strip()
                    if measure and measure.strip():
                        ing_str = f"{measure.strip()} {ing_str}"
                    ingredients.append(ing_str)

            # Truncate instructions
            if instructions and len(instructions) > 400:
                instructions = instructions[:400] + "..."

            embed = discord.Embed(title=f"🍳 {name}", description=instructions, color=discord.Color.from_rgb(255, 140, 0))
            if image_url:
                embed.set_thumbnail(url=image_url)
            embed.add_field(name="📋 Ingredientes", value="\n".join(ingredients[:12]) if ingredients else "N/A", inline=True)
            embed.add_field(name="🏷️ Categoría", value=category, inline=True)
            embed.add_field(name="🌍 Origen", value=area, inline=True)
            embed.add_field(name="🏷️ Tags", value=tags[:100], inline=True)
            embed.set_footer(text=f"TheMealDB • {ctx.author.name}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    # ═══════════════════════════════════════════════════════════════════════════
    # CAT FACTS (Cat Facts)
    # ═══════════════════════════════════════════════════════════════════════════

    @commands.command(name="catfact", aliases=["gatofact", "factcat"])
    async def catfact_aleatorio(self, ctx: commands.Context) -> None:
        """🐱 Dato curioso aleatorio sobre gatos."""
        async with ctx.typing():
            data = await self._fetch_json(CATFACT_URL)

            if not data or not data.get("fact"):
                await ctx.send("❌ No pude obtener un dato de gatos.")
                return

            fact = data["fact"]
            length = data.get("length", len(fact))

            embed = discord.Embed(title="🐱 Dato curioso de gato", description=fact, color=discord.Color.from_rgb(255, 180, 100))
            embed.set_footer(text=f"Cat Facts ({length} chars) • {ctx.author.name}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Load the Apis cog."""
    await bot.add_cog(Apis(bot))
