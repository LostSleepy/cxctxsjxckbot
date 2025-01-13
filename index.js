// Archivo index.js
import 'dotenv/config';
import { Client, GatewayIntentBits, Events } from 'discord.js';
import fetch from 'node-fetch';

// Crear nuevo cliente discord
const client = new Client({
    intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages, GatewayIntentBits.MessageContent]
});

// Crear evento primero
client.on(Events.ClientReady, async () => {
    console.log(`Conectado como ${client.user.username}!`);
});

// Conectar cliente app de discord
import dotenv from 'dotenv';
dotenv.config();
client.login(process.env.BOT_TOKEN);
client.on(Events.MessageCreate, message => {
    if (message.content === '!hola') {
        message.reply('hola');
    } else if (message.content === '!adios') {
        message.reply('Bye Bye <:felis:1177336870930227210>');
    }
});
// Espacio para añadir comandos personalizados
client.on(Events.MessageCreate, message => {
    if (message.content.startsWith('!')) {
        const args = message.content.slice(1).split(' ');
        const command = args.shift().toLowerCase();

        // Comando personalizado 1
        if (command === 'perrix') {
            message.reply('Putero payaso <:vomitivo:1177336377214505131>');
        }

        // Comando personalizado 2
        else if (command === 'dvix') {
            message.reply('Dvix es el goat <:emocion1:1177337151059406860>');
        }

        // Añadir más comandos personalizados aquí
    }
});
client.on(Events.MessageCreate, async message => {
    if (message.content.startsWith('!rangif')) {
        const args = message.content.split(' ').slice(1);
        const searchTerm = args.join(' ');

        if (!searchTerm) {
            return message.reply('Por favor proporciona un término de búsqueda.');
        }

        try {
            const response = await fetch(`https://tenor.googleapis.com/v2/search?q=${encodeURIComponent(searchTerm)}&key=AIzaSyCSafaBlxpHV9plawIq7YaAIFtby4-_E2s&limit=1`);
            const data = await response.json();

            if (data.results && data.results.length > 0) {
                const gifUrl = data.results[0].url;
                message.reply(gifUrl);
            } else {
                message.reply('No se encontraron GIFs para esa búsqueda.');
            }
        } catch (error) {
            console.error('Error al buscar GIF:', error);
            message.reply('Hubo un error al buscar el GIF.');
        }
    }
});