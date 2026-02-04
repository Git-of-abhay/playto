// Enhanced API client with all new endpoints
const API_BASE = 'http://localhost:8000/api';

async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            credentials: 'include',
        });

        // Check content type before parsing
        const contentType = response.headers.get('content-type');

        if (!response.ok) {
            // Try to get error message from JSON, or use status text
            if (contentType && contentType.includes('application/json')) {
                const error = await response.json();
                throw new Error(error.error || error.message || 'Request failed');
            } else {
                // Got HTML or other non-JSON response
                throw new Error(`Server error: ${response.status} ${response.statusText}`);
            }
        }

        return response.json();
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}

// ============ AUTH ============
export const register = (username, password, name) => apiRequest('/register/', {
    method: 'POST',
    body: JSON.stringify({ username, password, name })
});
export const login = (username, password) => apiRequest('/login/', {
    method: 'POST',
    body: JSON.stringify({ username, password })
});
export const logout = () => apiRequest('/logout/', { method: 'POST' });
export const getCurrentUser = () => apiRequest('/me/');

export async function updateProfile(data) {
    const formData = new FormData();
    if (data.name) formData.append('name', data.name);
    if (data.avatar) formData.append('avatar', data.avatar);

    const response = await fetch(`${API_BASE}/me/`, {
        method: 'PUT',
        body: formData,
        credentials: 'include',
    });

    if (!response.ok) throw new Error('Profile update failed');
    return response.json();
}

// ============ POSTS & COMMENTS ============
export const getPosts = () => apiRequest('/posts/');
export const createPost = (content) => apiRequest('/posts/', { method: 'POST', body: JSON.stringify({ content }) });
export const likePost = (id) => apiRequest(`/posts/${id}/like/`, { method: 'POST' });
export const createComment = (data) => apiRequest('/comments/', { method: 'POST', body: JSON.stringify(data) });
export const likeComment = (id) => apiRequest(`/comments/${id}/like/`, { method: 'POST' });

// ============ SOCIAL FEATURES ============
export const followUser = (username) => apiRequest(`/users/${username}/follow/`, { method: 'POST' });
export const unfollowUser = (username) => apiRequest(`/users/${username}/follow/`, { method: 'DELETE' });
export const blockUser = (username) => apiRequest(`/users/${username}/block/`, { method: 'POST' });
export const unblockUser = (username) => apiRequest(`/users/${username}/block/`, { method: 'DELETE' });
export const muteUser = (username) => apiRequest(`/users/${username}/mute/`, { method: 'POST' });
export const unmuteUser = (username) => apiRequest(`/users/${username}/mute/`, { method: 'DELETE' });
export const reportContent = (data) => apiRequest('/report/', { method: 'POST', body: JSON.stringify(data) });

// ============ NOTIFICATIONS ============
export const getNotifications = () => apiRequest('/notifications/');
export const markNotificationRead = (id) => apiRequest(`/notifications/${id}/`, { method: 'PATCH', body: JSON.stringify({ read: true }) });
export const markAllNotificationsRead = () => apiRequest('/notifications/mark_all_read/', { method: 'POST' });

// ============ COMMUNITIES ============
export const getCommunities = () => apiRequest('/communities/');
export const getCommunity = (id) => apiRequest(`/communities/${id}/`);
export const createCommunity = (data) => apiRequest('/communities/', { method: 'POST', body: JSON.stringify(data) });
export const joinCommunity = (id) => apiRequest(`/communities/${id}/join/`, { method: 'POST' });
export const leaveCommunity = (id) => apiRequest(`/communities/${id}/leave/`, { method: 'POST' });

// ============ CHAT ============
export const getTopics = (communityId) => apiRequest(`/topics/?community=${communityId}`);
export const getChatMessages = (topicId) => apiRequest(`/chat/?topic=${topicId}`);
export const sendChatMessage = (data) => apiRequest('/chat/', { method: 'POST', body: JSON.stringify(data) });

// ============ COURSES ============
export const getCourses = () => apiRequest('/courses/');
export const getCourse = (id) => apiRequest(`/courses/${id}/`);
export const enrollInCourse = (id) => apiRequest(`/courses/${id}/enroll/`, { method: 'POST' });
export const getMyEnrollments = () => apiRequest('/enrollments/');
export const completeLesson = (id) => apiRequest(`/lessons/${id}/complete/`, { method: 'POST' });

// ============ GAMIFICATION ============
export const getLeaderboard = (range = '24h') => apiRequest(`/leaderboard/?range=${range}`);
export const getBadges = () => apiRequest('/badges/');
export const getUserPoints = () => apiRequest('/points/');

// ============ PROFILE ============
export const getUserProfile = (username) => apiRequest(`/profile/${username}/`);

// ============ UTILS ============
export const seedData = () => apiRequest('/seed_force_trigger/');
