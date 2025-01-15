// Archivo index.js
import "dotenv/config";
import { Client, GatewayIntentBits, Events, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle, ComponentType } from "discord.js";
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
    if (message.content.startsWith("!")) {
        const args = message.content.slice(1).split(" ");
        const command = args.shift().toLowerCase();
        switch (command) {
            case "hola":
                message.reply("hola");
                break;
            case "adios":
                message.reply("Bye Bye <:felis:1177336870930227210>");
                break;
            case "perrix":
                message.reply("Hosteame el bot wapo <:emocion1:1177337151059406860>");
                break;
            case "dvix":
                message.reply("Dvix es el goat <:emocion1:1177337151059406860>");
                break;
            case "bdayc":
               handlebdayccommand(message);
                break;
            case "rangif":
                handleRangifCommand(message, args);
                break;
            case "bf":
                handleBfCommand(message);
                break;
            case "ping":
                const latency = Date.now() - message.createdTimestamp;
                message.reply(`Pong! Latencia: ${latency}ms`);
                break;
            case "roll":
                const rollResult = Math.floor(Math.random() * 6) + 1;
                message.reply(`Has sacado un ${rollResult}`);
                break;
            case "de":
                handleDeCommand(message, args);
                break;
            case "help":
                message.reply("Comandos disponibles: !hola, !adios, !perrix, !dvix, !bdayc, !rangif, !bf, !ping, !roll, !de, !help");
                break;
        }
    }
});

const gifUrls = [
    'https://media1.tenor.com/m/tw9sVj7rctkAAAAd/spongebob-spongebob-domain-expansion.gif',
    'https://media1.tenor.com/m/MuMLDWrW95gAAAAd/gojo-domain-expansion.gif',
    'https://media1.tenor.com/m/Cvbseddkre8AAAAd/megumi-fushiguro-megumi-domain-expansion.gif',
    'https://media1.tenor.com/m/rzLycKqpA_EAAAAd/mahito-domain-expansion.gif',
    'https://media1.tenor.com/m/EJW3gcpVvWgAAAAd/jogo-domain-expansion.gif',
    'https://media1.tenor.com/m/G_HN1fYl61kAAAAd/domain-expansion-yuta.gif',
    // Añade más URLs de GIFs aquí
];
async function handlebdayccommand(message) {
    const today = new Date();
    const currentYear = today.getFullYear();
    const birthday = new Date(currentYear, 8, 4); // 8 is September (0-indexed)

    if (today > birthday) {
        birthday.setFullYear(currentYear + 1);
    }

    const diffTime = Math.abs(birthday - today);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    message.reply(`Mi creador cumple años el 4 de septiembre. Faltan ${diffDays} días. Es decir <t:1756936800:R> `);
}

async function handleDeCommand(message, args) {
    const mentionedUser = message.mentions.users.first();
    
    // Verificar si el usuario mencionando es el mismo que el autor del mensaje
    if (!mentionedUser) {
        return message.reply("Por favor menciona a un usuario.");
    }
    
    if (mentionedUser.id === message.author.id) {
        return message.reply("No puedes expandir tu dominio sobre ti mismo.");
    }

    const randomGif = gifUrls[Math.floor(Math.random() * gifUrls.length)];
    const embed = new EmbedBuilder()
        .setDescription(`${message.author} le ha expandido su dominio a ${mentionedUser}`)
        .setImage(randomGif);

    const button = new ButtonBuilder()
        .setCustomId('respond_domain')
        .setLabel('😨Responder al dominio😱')
        .setStyle(ButtonStyle.Primary);

    const row = new ActionRowBuilder().addComponents(button);

    const sentMessage = await message.reply({ embeds: [embed], components: [row] });

    const filter = i => i.customId === 'respond_domain' && i.user.id === mentionedUser.id;
    const collector = sentMessage.createMessageComponentCollector({ filter, componentType: ComponentType.Button, time: 60000 });

    collector.on('collect', async i => {
        if (i.customId === 'respond_domain') {
            const responseEmbed = new EmbedBuilder()
                .setDescription(`¡ ${mentionedUser} ha respondido al dominio de ${message.author} expandiendo su propio dominio, generando así una guerra de dominios! 😮`)
                .setImage('https://media1.tenor.com/m/SN-uCACOmacAAAAd/yuta-ryu.gif'); // Reemplaza 'URL_DEL_GIF' con la URL del GIF que desees
            await i.update({ embeds: [responseEmbed], components: [] });
        }
    });

    collector.on('end', collected => {
        if (collected.size === 0) {
            sentMessage.edit({ components: [] });
        }
    });
}

async function handleRangifCommand(message, args) {
    const searchTerm = args.join(" ");

    if (!searchTerm) {
        return message.reply("Por favor proporciona un término de búsqueda.");
    }

    try {
        const response = await fetch(
            `https://tenor.googleapis.com/v2/search?q=${encodeURIComponent(
                searchTerm
            )}&key=AIzaSyCSafaBlxpHV9plawIq7YaAIFtby4-_E2s&limit=5`  // Aumenta el límite a 10 resultados
        );
        const data = await response.json();

        if (data.results && data.results.length > 0) {
            // Aquí seleccionamos un GIF aleatorio
            const randomIndex = Math.floor(Math.random() * data.results.length);  // Genera un índice aleatorio
            const randomGifUrl = data.results[randomIndex].url;  // Obtiene la URL del GIF aleatorio

            message.reply(randomGifUrl);  // Envía el GIF aleatorio al canal
        } else {
            message.reply("No se encontraron GIFs para esa búsqueda.");
        }
    } catch (error) {
        console.error("Error al buscar GIF:", error);
        message.reply("Hubo un error al buscar el GIF.");
    }
}


async function handleBfCommand(message) {
    const args = message.mentions.users;

    // Lista de GIFs que puedes especificar
    const gifUrls = [
        'https://media1.tenor.com/m/-nZnQBzGa7EAAAAd/jujutsu-kaisen-jujutsu-kaisen-season-2.gif',
        'https://media1.tenor.com/m/tIs0aEeP3AIAAAAd/black-flash-itadori.gif',
        'https://media1.tenor.com/m/boeIVtEUfRAAAAAd/jjk-jjk-s2.gif',
        'https://media1.tenor.com/m/EIlj3qUSKDUAAAAd/jjk-jujutsu-kaisen.gif',
        'https://media1.tenor.com/m/FILnhw_rozUAAAAd/black-flash-jujutsu-kaisen.gif',
        'https://media1.tenor.com/m/1-1s1sRLsHEAAAAd/jujutsu-kaisen-jjk.gif',
        'https://media1.tenor.com/m/EpZRa2Ox2asAAAAd/jujutsu-kaisen-yuji-itadori.gif',
        'https://media1.tenor.com/m/SA78kvgb6SIAAAAd/nanami-nanami-kento.gif'
    ];

    // Si no se menciona a ningún usuario, se responde con un GIF aleatorio de la lista
    if (args.size === 0) {
        const randomGif = gifUrls[Math.floor(Math.random() * gifUrls.length)];
        message.reply(randomGif);
    } else {
        const mentionedUser = args.first();

        if (mentionedUser.id === message.author.id) {
            message.reply('No puedes usar el black flash contra ti mismo.');
        } else {
            const now = new Date();
            const timestamp = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;

            // Seleccionar un GIF aleatorio de la lista
            const randomGif = gifUrls[Math.floor(Math.random() * gifUrls.length)];

            const embed = new EmbedBuilder()
                .setDescription(`${message.author} utilizó black flash contra ${mentionedUser}`)
                .setImage(randomGif);  // Establecer la imagen del GIF aleatorio

            message.reply({ embeds: [embed] });
        }
    }
}
