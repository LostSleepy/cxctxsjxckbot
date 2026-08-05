# 🌩️ Fortnite Video Proxy (Cloudflare Worker)

El reproductor de Discord no reproduce inline los vídeos del CDN de
Fortnite.GG (`fnggcdn.com`) — se queda congelado en el primer frame por la
protección de Cloudflare del CDN de terceros. Este Worker re-sirve los
vídeos desde **tu propio dominio** de Cloudflare, y así Discord los
reproduce sin problema.

**Ventaja clave:** el bot de Discord **no descarga nada** (cero tráfico en
Koyeb). Solo envía el enlace del Worker, y el Worker trafica con fnggcdn.

## 🚀 Despliegue (2 minutos, gratis, sin tarjeta)

1. Entra en **https://dash.cloudflare.com** → crea cuenta si no tienes.
2. Menú **Workers & Pages** → **Create** → **Worker**.
3. En el editor, borra el código de ejemplo y pega el contenido de
   [`worker.js`](./worker.js).
4. Pulsa **Deploy**.
5. Copia tu URL del Worker, con este formato:
   `https://TU-NOMBRE.TU-SUBDOMINIO.workers.dev`

## ⚙️ Configurar el bot

1. En **Koyeb**, añade la variable de entorno a tu servicio:

   ```
   FNGG_VIDEO_PROXY_URL=https://TU-NOMBRE.TU-SUBDOMINIO.workers.dev
   ```

2. Redespliega / reinicia el bot.

3. Prueba en tu server:

   ```
   cx!fn video escenario
   ```

   El bot enviará el enlace del Worker y Discord debería reproducir el
   baile inline 🎬

## 🧪 Verificación manual

Puedes comprobar que el Worker funciona con:

```bash
curl -s -o /dev/null -w '%{http_code} %{content_type}\n' \
  'https://TU-NOMBRE.TU-SUBDOMINIO.workers.dev/items/3971/video.mp4'
```

Esperado: `200 video/mp4` (o `206 video/mp4` con `-H 'Range: bytes=0-100'`).

## ❌ Fallback

Si el Worker no está configurado (`FNGG_VIDEO_PROXY_URL` vacío), el bot
envía el enlace directo de fnggcdn como antes (puede verse congelado en
Discord, pero funciona al abrirlo en el navegador).
