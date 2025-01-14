// Archivo index.js
import "dotenv/config";
import { Client, GatewayIntentBits, Events, EmbedBuilder } from "discord.js";
import fetch from "node-fetch";

// Crear nuevo cliente discord
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
    ],
});

// Crear evento primero
client.on(Events.ClientReady, async () => {
    console.log(`Conectado como ${client.user.username}!`);
});

// Conectar cliente app de discord
import dotenv from "dotenv";
dotenv.config();
client.login(process.env.BOT_TOKEN);

client.on(Events.MessageCreate, (message) => {
    if (message.content === "!hola") {
        message.reply("hola");
    } else if (message.content === "!adios") {
        message.reply("Bye Bye <:felis:1177336870930227210>");
    }
});

// Espacio para añadir comandos personalizados
client.on(Events.MessageCreate, (message) => {
    if (message.content.startsWith("!")) {
        const args = message.content.slice(1).split(" ");
        const command = args.shift().toLowerCase();

        // Comando personalizado 1
        if (command === "perrix") {
            message.reply("Putero payaso <:vomitivo:1177336377214505131>");
        }

        // Comando personalizado 2
        else if (command === "dvix") {
            message.reply("Dvix es el goat <:emocion1:1177337151059406860>");
        }

        // Comando de cumpleaños
        else if (command === "birthdaycreator" || command === "bdayc") {
            const today = new Date();
            const currentYear = today.getFullYear();
            const birthday = new Date(currentYear, 8, 4); // 8 is September (0-indexed)

            if (today > birthday) {
                birthday.setFullYear(currentYear + 1);
            }

            const diffTime = Math.abs(birthday - today);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

            const timestamp = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')} ${String(today.getHours()).padStart(2, '0')}:${String(today.getMinutes()).padStart(2, '0')}:${String(today.getSeconds()).padStart(2, '0')}`;

            message.reply(`Mi creador cumple años el 4 de septiembre. Faltan ${diffDays} días. Es decir <t:1756936800:R> `);
        }

        // Añadir más comandos personalizados aquí
    }
});

client.on(Events.MessageCreate, async (message) => {
    if (message.content.startsWith("!rangif")) {
        const args = message.content.split(" ").slice(1);
        const searchTerm = args.join(" ");

        if (!searchTerm) {
            return message.reply("Por favor proporciona un término de búsqueda.");
        }

        try {
            const response = await fetch(
                `https://tenor.googleapis.com/v2/search?q=${encodeURIComponent(
                    searchTerm
                )}&key=AIzaSyCSafaBlxpHV9plawIq7YaAIFtby4-_E2s&limit=1`
            );
            const data = await response.json();

            if (data.results && data.results.length > 0) {
                const gifUrl = data.results[0].url;
                message.reply(gifUrl);
            } else {
                message.reply("No se encontraron GIFs para esa búsqueda.");
            }
        } catch (error) {
            console.error("Error al buscar GIF:", error);
            message.reply("Hubo un error al buscar el GIF.");
        }
    }
});

client.on(Events.MessageCreate, async (message) => {
    if (message.content.startsWith('!bf')) {
        const args = message.mentions.users;
        const gifUrl = 'https://media1.tenor.com/m/-nZnQBzGa7EAAAAd/jujutsu-kaisen-jujutsu-kaisen-season-2.gif';

        if (args.size === 0) {
            message.reply(gifUrl);
        } else {
            const mentionedUser = args.first();
            if (mentionedUser.id === message.author.id) {
                message.reply('No puedes usar el black flash contra ti mismo.');
            } else {
                const now = new Date();
                const timestamp = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
                const embed = new EmbedBuilder()
                    .setDescription(`${message.author} utilizó black flash contra ${mentionedUser}`)
                    .setImage(gifUrl);  // Establecer la imagen del GIF
                message.reply({ embeds: [embed] });
            }
        }
    }
});
