import { apiUrl } from "./base";

const API_BASE = apiUrl("/music");
const SPOTIFY_API_BASE = apiUrl("/spotify");

function getAuthHeaders() {
    const token = localStorage.getItem('token');
    return {
        "Content-Type": "application/json",
        ...(token && { "Authorization": `Bearer ${token}` })
    };
}

// UPDATED: Now uses multi-tier fallback (Spotify → Deezer → Jamendo)
export async function searchMusic(query, limit = 20) {
    const res = await fetch(`${SPOTIFY_API_BASE}/search?q=${encodeURIComponent(query)}&limit=${limit}`, {
        method: "GET",
        headers: getAuthHeaders(),
        credentials: "include"
    });
    
    if (!res.ok) {
        throw new Error('Failed to search music');
    }
    
    return await res.json();
}

// UPDATED: Now uses multi-tier fallback (Spotify → Deezer → Jamendo)
export async function getRecommendations(mood = 'happy', limit = 25) {
    const res = await fetch(`${SPOTIFY_API_BASE}/recommendations/${mood}?limit=${limit}`, {
        method: "GET",
        headers: getAuthHeaders(),
        credentials: "include"
    });
    
    if (!res.ok) {
        throw new Error('Failed to get recommendations');
    }
    
    return await res.json();
}

export async function getFavorites() {
    const res = await fetch(`${API_BASE}/favorites`, {
        method: "GET",
        headers: getAuthHeaders(),
        credentials: "include"
    });
    
    if (!res.ok) {
        throw new Error('Failed to get favorites');
    }
    
    return await res.json();
}

export async function addFavorite(track) {
    const res = await fetch(`${API_BASE}/favorites`, {
        method: "POST",
        headers: getAuthHeaders(),
        credentials: "include",
        body: JSON.stringify({
            track_id: track.id,
            track_name: track.title || track.name,
            artist_name: track.artists?.[0]?.name || track.artist || 'Unknown',
            album_name: track.album?.name || 'Unknown',
            preview_url: track.song_url || track.preview_url
        })
    });
    
    if (!res.ok) {
        throw new Error('Failed to add favorite');
    }
    
    return await res.json();
}

export async function removeFavorite(trackId) {
    const res = await fetch(`${API_BASE}/favorites/${trackId}`, {
        method: "DELETE",
        headers: getAuthHeaders(),
        credentials: "include"
    });
    
    if (!res.ok) {
        throw new Error('Failed to remove favorite');
    }
    
    return await res.json();
}

export async function addToHistory(track) {
    const res = await fetch(`${API_BASE}/history`, {
        method: "POST",
        headers: getAuthHeaders(),
        credentials: "include",
        body: JSON.stringify({
            track_id: track.id,
            track_name: track.title || track.name
        })
    });
    
    if (!res.ok) {
        throw new Error('Failed to add to history');
    }
    
    return await res.json();
}

export async function getHistory(limit = 50) {
    const res = await fetch(`${API_BASE}/history?limit=${limit}`, {
        method: "GET",
        headers: getAuthHeaders(),
        credentials: "include"
    });
    
    if (!res.ok) {
        throw new Error('Failed to get history');
    }
    
    return await res.json();
}
