// Archivo index.js
const { Client, GatewayIntentBits, Events } = require('discord.js');

// Crear nuevo cliente discord
const client = new Client({
    intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages, GatewayIntentBits.MessageContent]
});

// Crear evento primero
client.on(Events.ClientReady, async () => {
    console.log(`Conectado como ${client.user.username}!`);
});

// Conectar cliente app de discord
client.login('MTMwNTQ4OTkwNjAwODg1NDU3OA.GJz5cb.hHy1kF2hG1n-YbfLvT0IPwTWowAxNU_JMCH5yU');
client.on(Events.MessageCreate, message => {
    if (message.content === '!hola') {
        message.reply('hola');
    } else if (message.content === '!adios') {
        message.reply('Bye Bye :fnes_corazon:');
    }
});
// Espacio para añadir comandos personalizados
client.on(Events.MessageCreate, message => {
    if (message.content.startsWith('!')) {
        const args = message.content.slice(1).split(' ');
        const command = args.shift().toLowerCase();

        // Comando personalizado 1
        if (command === 'comando1') {
            message.reply('Respuesta para comando1');
        }

        // Comando personalizado 2
        else if (command === 'comando2') {
            message.reply('Respuesta para comando2');
        }

        // Añadir más comandos personalizados aquí
    }
});