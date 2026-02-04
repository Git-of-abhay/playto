import { useState, useEffect } from 'react';
import { getPosts, getCurrentUser, logout } from './api';
import PostCard from './components/PostCard';
import CreatePost from './components/CreatePost';
import AuthModal from './components/AuthModal';
import ProfileModal from './components/ProfileModal';
import Communities from './components/Communities';
import Courses from './components/Courses';
import Gamification from './components/Gamification';
import NotificationBell from './components/NotificationBell';

export default function App() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);
  const [showAuth, setShowAuth] = useState(false);
  const [viewingProfile, setViewingProfile] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [activeTab, setActiveTab] = useState('home'); // home | communities | courses | learn

  useEffect(() => {
    checkUser();
    loadPosts();

    // Auto-refresh feed every 60 seconds
    const interval = setInterval(loadPosts, 60000);
    return () => clearInterval(interval);
  }, []);

  async function checkUser() {
    const currentUser = await getCurrentUser();
    setUser(currentUser);
  }

  async function loadPosts() {
    const data = await getPosts();
    setPosts(data);
    setLoading(false);
  }

  async function handleLogout() {
    await logout();
    setUser(null);
    window.location.reload();
  }

  async function handleProfileUpdate() {
    // Force full page reload to update avatar everywhere
    window.location.reload();
  }

  function handleInteraction() {
    // Removed automatic refresh - keeps interactions instant
  }

  function handleUserClick(username) {
    setViewingProfile(username);
  }

  // Render content based on active tab
  function renderContent() {
    switch (activeTab) {
      case 'communities':
        return <Communities user={user} />;
      case 'courses':
        return <Courses user={user} />;
      case 'leaderboard':
        return <Gamification user={user} />;
      default:
        return (
          <div className="max-w-2xl mx-auto px-4 py-4 space-y-4">
            {user && <CreatePost user={user} onCreate={loadPosts} />}

            {loading ? (
              <div className="flex justify-center py-12">
                <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
              </div>
            ) : posts.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                <p className="text-gray-500">No posts yet. Be the first to share!</p>
              </div>
            ) : (
              posts
                .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
                .map(post => (
                  <PostCard
                    key={`${post.id}-${refreshTrigger}`}
                    post={post}
                    user={user}
                    onUpdate={handleInteraction}
                    onUserClick={handleUserClick}
                  />
                ))
            )}
          </div>
        );
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 pb-20 md:pb-0">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1
              className="text-2xl font-bold text-blue-600 cursor-pointer"
              onClick={() => setActiveTab('home')}
            >
              Playto
            </h1>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex gap-6">
              <NavButton active={activeTab === 'home'} onClick={() => setActiveTab('home')}>
                🏠 Home
              </NavButton>
              <NavButton active={activeTab === 'communities'} onClick={() => setActiveTab('communities')}>
                👥 Communities
              </NavButton>
              <NavButton active={activeTab === 'courses'} onClick={() => setActiveTab('courses')}>
                📚 Courses
              </NavButton>
              <NavButton active={activeTab === 'leaderboard'} onClick={() => setActiveTab('leaderboard')}>
                🏆 Leaderboard
              </NavButton>
            </nav>
          </div>

          <div className="flex items-center gap-3">
            <NotificationBell user={user} />

            {user ? (
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setViewingProfile(user.username)}
                  className="flex items-center gap-2 hover:bg-gray-100 rounded-lg px-3 py-2"
                >
                  {user.avatar ? (
                    <img src={user.avatar} alt={user.name || user.username} className="w-8 h-8 rounded-full object-cover" />
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-semibold">
                      {(user.name || user.username).charAt(0).toUpperCase()}
                    </div>
                  )}
                  <span className="hidden md:inline font-semibold">{user.name || user.username}</span>
                </button>
                <button
                  onClick={handleLogout}
                  className="text-gray-600 hover:text-gray-800 px-3 py-2  hover:bg-gray-100 rounded-lg"
                >
                  Logout
                </button>
              </div>
            ) : (
              <button
                onClick={() => setShowAuth(true)}
                className="bg-blue-600 text-white px-6 py-2 rounded-full font-semibold hover:bg-blue-700"
              >
                Get Started
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main>
        {renderContent()}
      </main>

      {/* Mobile Bottom Navigation */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t shadow-lg z-40">
        <div className="flex justify-around">
          <MobileNavButton
            active={activeTab === 'home'}
            onClick={() => setActiveTab('home')}
            icon="🏠"
            label="Home"
          />
          <MobileNavButton
            active={activeTab === 'communities'}
            onClick={() => setActiveTab('communities')}
            icon="👥"
            label="Communities"
          />
          <MobileNavButton
            active={activeTab === 'courses'}
            onClick={() => setActiveTab('courses')}
            icon="📚"
            label="Courses"
          />
          <MobileNavButton
            active={activeTab === 'leaderboard'}
            onClick={() => setActiveTab('leaderboard')}
            icon="🏆"
            label="Rank"
          />
        </div>
      </nav>

      {showAuth && (
        <AuthModal onClose={() => setShowAuth(false)} onLogin={() => { setShowAuth(false); checkUser(); }} />
      )}

      {viewingProfile && (
        <ProfileModal
          username={viewingProfile}
          currentUser={user}
          onClose={() => setViewingProfile(null)}
          onUpdate={handleProfileUpdate}
        />
      )}
    </div>
  );
}

// Desktop nav button
function NavButton({ children, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 rounded-lg font-semibold ${active ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-100'
        }`}
    >
      {children}
    </button>
  );
}

// Mobile bottom nav button
function MobileNavButton({ icon, label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`flex-1 flex flex-col items-center gap-1 py-3 ${active ? 'text-blue-600' : 'text-gray-600'
        }`}
    >
      <span className="text-2xl">{icon}</span>
      <span className="text-xs font-semibold">{label}</span>
    </button>
  );
}
