import { useState, useEffect } from 'react';
import { getPosts, getPost, getCurrentUser, logout } from './api';
import PostCard from './components/PostCard';
import CreatePost from './components/CreatePost';
import Leaderboard from './components/Leaderboard';
import AuthModal from './components/AuthModal';
import ProfileModal from './components/ProfileModal';

export default function App() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);
  const [showAuth, setShowAuth] = useState(false);
  const [viewingProfile, setViewingProfile] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  useEffect(() => {
    checkUser();
    loadPosts();

    // Auto-refresh feed every 30 seconds
    const interval = setInterval(loadPosts, 30000);
    return () => clearInterval(interval);
  }, []);

  async function checkUser() {
    const currentUser = await getCurrentUser();
    setUser(currentUser);
  }

  async function loadPosts() {
    try {
      const data = await getPosts();
      const fullPosts = await Promise.all(
        data.map(p => getPost(p.id))
      );
      setPosts(fullPosts);
    } catch (err) {
      console.error('Failed to load posts:', err);
    } finally {
      setLoading(false);
    }
  }

  function handleInteraction() {
    loadPosts();
    setRefreshTrigger(t => t + 1);
  }

  function handleNewPost(newPost) {
    handleInteraction();
  }

  function handleUserClick(username) {
    setViewingProfile(username);
  }

  async function handleLogin() {
    setShowAuth(false);
    await checkUser();
    loadPosts();
  }

  async function handleLogout() {
    await logout();
    setUser(null);
    loadPosts();
    setViewingProfile(null);
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* LinkedIn-style Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-40 shadow-sm">
        <div className="max-w-5xl mx-auto px-4 py-2 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold text-blue-600 cursor-pointer" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
              Community
            </h1>
          </div>

          <div className="flex items-center gap-3">
            {user ? (
              <>
                <button
                  onClick={() => handleUserClick(user.username)}
                  className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-full hover:bg-gray-200 transition-colors"
                >
                  <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm font-semibold overflow-hidden">
                    {user.avatar ? (
                      <img src={user.avatar} alt="" className="w-full h-full object-cover" />
                    ) : (
                      (user.name || user.username)[0].toUpperCase()
                    )}
                  </div>
                  <span className="text-sm font-medium text-gray-700">{user.name || user.username}</span>
                </button>
                <button
                  onClick={handleLogout}
                  className="px-4 py-1.5 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-full transition-colors"
                >
                  Sign Out
                </button>
              </>
            ) : (
              <button
                onClick={() => setShowAuth(true)}
                className="px-5 py-2 bg-blue-600 text-white rounded-full font-semibold text-sm hover:bg-blue-700 transition-colors"
              >
                Sign In
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto py-6 px-4">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_300px] gap-6">
          {/* Feed */}
          <div className="space-y-4">
            {/* Create Post Card */}
            {user && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <CreatePost onCreated={handleNewPost} user={user} />
              </div>
            )}

            {loading ? (
              <div className="flex justify-center py-12">
                <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
              </div>
            ) : posts.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                <p className="text-gray-500">No posts yet. Be the first to share!</p>
              </div>
            ) : (
              posts.map(post => (
                <PostCard
                  key={post.id}
                  post={post}
                  user={user}
                  onUpdate={handleInteraction}
                  onUserClick={handleUserClick}
                />
              ))
            )}
          </div>

          {/* Sidebar */}
          <div className="hidden lg:block space-y-4">
            <Leaderboard
              refreshTrigger={refreshTrigger}
              onUserClick={handleUserClick}
            />

            {/* Karma Info Card */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <h3 className="font-semibold text-gray-900 mb-3">How Karma Works</h3>
              <div className="space-y-2 text-sm text-gray-600">
                <div className="flex items-center gap-2">
                  <span className="text-blue-600 font-bold">+5</span>
                  <span>When someone likes your post</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-blue-600 font-bold">+1</span>
                  <span>When someone likes your comment</span>
                </div>
              </div>
              <p className="mt-3 text-xs text-gray-400">Leaderboard resets every 24 hours</p>
            </div>
          </div>
        </div>
      </main>

      {/* Auth Modal */}
      {showAuth && (
        <AuthModal
          onLogin={handleLogin}
          onClose={() => setShowAuth(false)}
        />
      )}

      {/* Profile Modal */}
      {viewingProfile && (
        <ProfileModal
          username={viewingProfile}
          currentUser={user}
          onClose={() => setViewingProfile(null)}
          onUpdate={handleInteraction}
        />
      )}
    </div>
  );
}
