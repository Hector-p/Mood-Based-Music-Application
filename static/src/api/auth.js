import { apiUrl } from "./base";

const API_BASE = apiUrl("/auth");

export async function registerUser(payload) {
    try {
        const res = await fetch(`${API_BASE}/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify(payload)
        });
        
        if (!res.ok) {
            const error = await res.json();
            throw new Error(error.msg || 'Registration failed');
        }
        
        return await res.json();
    } catch (error) {
        console.error('Register error:', error);
        throw error;
    }
}

export async function loginUser(payload) {
    try {
        const res = await fetch(`${API_BASE}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify(payload)
        });
        
        if (!res.ok) {
            const error = await res.json();
            throw new Error(error.msg || 'Login failed');
        }
        
        return await res.json();
    } catch (error) {
        console.error('Login error:', error);
        throw error;
    }
}

export async function getCurrentUser(token) {
    try {
        const res = await fetch(`${API_BASE}/me`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            credentials: "include"
        });
        
        if (!res.ok) {
            const errorData = await res.json().catch(() => ({ msg: 'Unknown error' }));
            console.error('Auth error:', res.status, errorData);
            return { error: true, message: errorData.msg || 'Authentication failed', status: res.status };
        }
        
        return await res.json();
    } catch (error) {
        console.error('getCurrentUser error:', error);
        return { error: true, message: error.message };
    }
}
