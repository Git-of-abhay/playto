const API_BASE = import.meta.env.VITE_API_URL || '/api';

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

    return response;
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
