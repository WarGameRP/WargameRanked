// ─── Cloudflare Worker pour la signature de decks Wargame Ranked ─────────────
// Ce Worker reçoit un deck JSON, calcule sa signature SHA-256 avec un secret
// caché, et renvoie la signature. Le secret est stocké dans les variables
// d'environnement de Cloudflare Workers (plus sécurisé que côté client).
//
// DÉPLOIEMENT:
// 1. Créez un compte Cloudflare Workers (gratuit)
// 2. Installez wrangler: npm install -g wrangler
// 3. Connectez wrangler: wrangler login
// 4. Créez un worker: wrangler init wargame-api
// 5. Copiez ce code dans wrangler.toml ou le fichier index.js
// 6. Définissez le secret: wrangler secret put DECK_SIGNATURE_SALT
//    (Entrez votre secret quand demandé, ex: "WargameRankedSecretSalt")
// 7. Déployez: wrangler deploy
// 8. Mettez à jour SIGNATURE_API_URL dans script.js avec l'URL obtenue

export default {
  async fetch(request, env) {
    // Handle CORS preflight requests
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
      });
    }

    // Only accept POST requests
    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), {
        status: 405,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      });
    }

    try {
      const deckData = await request.json();

      // Validate the deck data
      if (!deckData || !deckData.name || !deckData.doctrine || !deckData.units) {
        return new Response(JSON.stringify({ error: 'Invalid deck data' }), {
          status: 400,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
          },
        });
      }

      // Stable stringify the deck data (same as client-side)
      const dataString = stableStringify(deckData);

      // Get the secret from environment variables
      const secret = env.DECK_SIGNATURE_SALT;
      if (!secret) {
        return new Response(JSON.stringify({ error: 'Secret not configured' }), {
          status: 500,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
          },
        });
      }

      // Calculate SHA-256 signature
      const signature = await sha256(dataString + secret);

      // Return the signature
      return new Response(JSON.stringify({ signature }), {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      });

    } catch (error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      });
    }
  },
};

// Stable stringify function (same as client-side)
function stableStringify(obj) {
  const allKeys = [];
  JSON.stringify(obj, (key, value) => {
    allKeys.push(key);
    return value;
  });
  allKeys.sort();
  return JSON.stringify(obj, allKeys);
}

// SHA-256 implementation for Cloudflare Workers
async function sha256(message) {
  const msgBuffer = new TextEncoder().encode(message);
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  return hashHex;
}
