/**
 * Fortnite Video Proxy — Cloudflare Worker
 * ─────────────────────────────────────────
 * Re-sirve los vídeos de baile de Fortnite.GG (fnggcdn.com) a través de
 * tu propio dominio de Cloudflare, para que el reproductor de Discord
 * pueda reproducirlos inline (el proxy de Discord falla contra el CDN
 * original por protección de Cloudflare de terceros).
 *
 * Despliegue (gratis, sin tarjeta):
 *   1. Ve a https://dash.cloudflare.com → Workers & Pages → Create → Worker
 *   2. Borra el código de ejemplo y pega este archivo.
 *   3. Deploy. Copia tu URL: https://TU-NOMBRE.TU-SUBDOMINIO.workers.dev
 *   4. En Koyeb define la variable de entorno:
 *        FNGG_VIDEO_PROXY_URL=https://TU-NOMBRE.TU-SUBDOMINIO.workers.dev
 *   5. Reinicia el bot. ¡Listo!
 *
 * El bot NO descarga nada: solo envía el enlace del Worker, y el Worker
 * trafica con fnggcdn (cero descargas en Koyeb).
 */

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const path = url.pathname;

    // Solo permitimos el patrón de vídeos de fngg: /items/{id}/video.mp4
    if (!/^\/items\/\d+\/video\.mp4$/.test(path)) {
      return new Response("Not found", { status: 404 });
    }

    // Construimos la URL destino en el CDN de Fortnite.GG
    const target = "https://fnggcdn.com" + path + url.search;

    // Reutilizamos los headers de la petición (incluye Range para el
    // streaming de Discord) pero con identidad de navegador para fngg.
    const headers = new Headers(request.headers);
    headers.set(
      "User-Agent",
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " +
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    );
    headers.set("Referer", "https://fortnite.gg/");
    headers.set("Origin", "https://fortnite.gg");

    const resp = await fetch(target, { headers });

    // Reenviamos la respuesta tal cual (200/206, Content-Range, video/mp4).
    const out = new Headers(resp.headers);
    out.set("Access-Control-Allow-Origin", "*");
    out.set("Accept-Ranges", "bytes");
    // private + short TTL para no interferir con las respuestas 206 parciales
    // del streaming por rangos de Discord
    out.set("Cache-Control", "private, max-age=3600");

    return new Response(resp.body, {
      status: resp.status,
      statusText: resp.statusText,
      headers: out,
    });
  },
};
