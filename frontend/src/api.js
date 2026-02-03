const BASE_URL = import.meta.env.VITE_API_URL || '';

if (import.meta.env.PROD && !BASE_URL) {
    console.error('CRITICAL: VITE_API_URL is missing in production build!');
}

const API_BASE = `${BASE_URL}/api`;

async function fetchApi(url, options = {}) {
    const headers = { ...options.headers };
    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(url, {
        ...options,
        headers,
        credentials: 'include',
    });

    // 1. Check for HTML response (Critical Fix for "Unexpected token")
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.includes("text/html")) {
        const text = await response.text();
        console.error('API Error: Received HTML instead of JSON', { url, text });
        throw new Error(`System Error: Server returned HTML. URL: ${url}. Response: ${text.substring(0, 100)}...`);
    }

    // 2. Try to parse JSON
    let data;
    try {
        data = await response.json();
    } catch (err) {
        // Fallback if content-type wasn't html but parsing still failed
        throw new Error(`API Error: Failed to parse JSON response from ${url}`);
    }

    // 3. Handle HTTP Errors (400, 500 etc)
    if (!response.ok) {
        // Extract helpful error message from backend
        // Backend returns { error: "message" } or { detail: "message" }
        const errorMessage = data.error || data.detail || JSON.stringify(data);
        throw new Error(errorMessage);
    }

    // 4. Return just the data (simpler for callers)
    // Note: existing code expects response object or data depending on function
    // We need to preserve compatibility, so we attach data to response or return response
    // But getting into callers, they mostly do `res.json()`.
    // Let's stick to returning response object but "enhanced" with pre-parsed data?
    // Actually, looking at usages: `const res = await fetchApi(...)` then `res.json()`.
    // We already consumed the stream! match usage.

    // RE-ARCHITECTING fetchApi to return the parsed data directly would break callers.
    // Callers expect a Response object with .json() method.
    // Since we already consumed the body, we must mock the .json() method.

    return {
        ok: response.ok,
        status: response.status,
        statusText: response.statusText,
        headers: response.headers,
        json: async () => data,
        url: response.url
    };
}

// Posts
export async function getPosts() {
    const res = await fetchApi(`${API_BASE}/posts/`);
    return res.json();
}

export async function getPost(id) {
    const res = await fetchApi(`${API_BASE}/posts/${id}/`);
    return res.json();
}

export async function createPost(content) {
    const res = await fetchApi(`${API_BASE}/posts/`, {
        method: 'POST',
        body: JSON.stringify({ content }),
    });
    const data = await res.json();
    if (!res.ok) {
        throw new Error(data.detail || 'Failed to create post');
    }
    return data;
}

export async function likePost(id) {
    const res = await fetchApi(`${API_BASE}/posts/${id}/like/`, {
        method: 'POST',
    });
    const data = await res.json();
    if (!res.ok) {
        throw new Error(data.detail || 'Failed to like post');
    }
    return data;
}

// Comments
export async function createComment(postId, content, parentId = null) {
    const res = await fetchApi(`${API_BASE}/comments/`, {
        method: 'POST',
        body: JSON.stringify({ post: postId, content, parent: parentId }),
    });
    const data = await res.json();
    if (!res.ok) {
        throw new Error(data.detail || 'Failed to create comment');
    }
    return data;
}

export async function likeComment(id) {
    const res = await fetchApi(`${API_BASE}/comments/${id}/like/`, {
        method: 'POST',
    });
    const data = await res.json();
    if (!res.ok) {
        throw new Error(data.detail || 'Failed to like comment');
    }
    return data;
}

// Leaderboard
export async function getLeaderboard() {
    const res = await fetchApi(`${API_BASE}/leaderboard/`);
    return res.json();
}

// Auth
export async function register(username, password, name) {
    const res = await fetchApi(`${API_BASE}/register/`, {
        method: 'POST',
        body: JSON.stringify({ username, password, name }),
    });
    return res.json();
}

export async function login(username, password) {
    const res = await fetchApi(`${API_BASE}/login/`, {
        method: 'POST',
        body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) {
        throw new Error(data.error || 'Login failed');
    }
    return data;
}

export async function logout() {
    await fetchApi(`${API_BASE}/logout/`, {
        method: 'POST',
    });
}

export async function getCurrentUser() {
    const res = await fetchApi(`${API_BASE}/me/`);
    if (res.ok) {
        return res.json();
    }
    return null;
}

export async function getUserProfile(username) {
    const res = await fetchApi(`${API_BASE}/profile/${username}/`);
    if (!res.ok) {
        throw new Error('Profile not found');
    }
    return res.json();
}

export async function updateProfile(formData) {
    const res = await fetchApi(`${API_BASE}/me/`, {
        method: 'PUT',
        body: formData, // FormData doesn't need Content-Type header (browser sets it)
    });
    if (!res.ok) {
        throw new Error('Failed to update profile');
    }
    return res.json();
}
