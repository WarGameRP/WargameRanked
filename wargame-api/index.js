// ─── Cloudflare Worker pour la signature de decks Wargame Ranked ─────────────
// Ce Worker reçoit un deck JSON, calcule sa signature SHA-256 avec un secret
// caché, et renvoie la signature. Le secret est stocké dans les variables
// d'environnement de Cloudflare Workers (plus sécurisé que côté client).

// Rate limiting simple basé sur l'IP
const rateLimitMap = new Map();

function checkRateLimit(ip, env) {
  const now = Date.now();
  const maxRequests = parseInt(env.RATE_LIMIT_REQUESTS || "60");
  const windowMs = parseInt(env.RATE_LIMIT_WINDOW || "60") * 1000;
  
  const key = `rate_limit_${ip}`;
  const data = rateLimitMap.get(key);
  
  if (!data || data.resetTime < now) {
    // Nouvelle fenêtre ou fenêtre expirée
    rateLimitMap.set(key, {
      count: 1,
      resetTime: now + windowMs
    });
    return { allowed: true, remaining: maxRequests - 1 };
  }
  
  if (data.count >= maxRequests) {
    return { 
      allowed: false, 
      remaining: 0,
      resetTime: data.resetTime
    };
  }
  
  data.count++;
  return { allowed: true, remaining: maxRequests - data.count };
}

export default {
  async fetch(request, env) {
    // Get client IP
    const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
    
    // Check rate limit
    const rateLimit = checkRateLimit(ip, env);
    
    // Add rate limit headers
    const headers = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'X-RateLimit-Limit': env.RATE_LIMIT_REQUESTS || "60",
      'X-RateLimit-Remaining': rateLimit.remaining.toString(),
    };
    
    if (!rateLimit.allowed) {
      headers['Retry-After'] = Math.ceil((rateLimit.resetTime - Date.now()) / 1000).toString();
      return new Response(JSON.stringify({ error: 'Rate limit exceeded' }), {
        status: 429,
        headers: {
          ...headers,
          'Content-Type': 'application/json',
        },
      });
    }
    
    // Handle CORS preflight requests
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers });
    }

    // Only accept POST requests
    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), {
        status: 405,
        headers: {
          ...headers,
          'Content-Type': 'application/json',
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
            ...headers,
            'Content-Type': 'application/json',
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
            ...headers,
            'Content-Type': 'application/json',
          },
        });
      }

      // Calculate SHA-256 signature
      const signature = await sha256(dataString + secret);

      // Return the signature
      return new Response(JSON.stringify({ signature }), {
        status: 200,
        headers: {
          ...headers,
          'Content-Type': 'application/json',
        },
      });

    } catch (error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: {
          ...headers,
          'Content-Type': 'application/json',
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
