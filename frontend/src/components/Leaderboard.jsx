import { useState, useEffect } from 'react';
import { getLeaderboard } from '../api';

export default function Leaderboard({ refreshTrigger, onUserClick }) {
    const [leaders, setLeaders] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadLeaderboard();
    }, [refreshTrigger]);

    useEffect(() => {
        loadLeaderboard();
        const interval = setInterval(loadLeaderboard, 30000);
        return () => clearInterval(interval);
    }, []);

    async function loadLeaderboard() {
        try {
            const data = await getLeaderboard();
            setLeaders(data);
        } catch (err) {
            console.error('Failed to load leaderboard:', err);
        } finally {
            setLoading(false);
        }
    }

    if (loading) {
        return (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <div className="animate-pulse text-gray-400">Loading...</div>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <div className="p-4 border-b border-gray-100">
                <h2 className="font-semibold text-gray-900">Top Contributors</h2>
                <p className="text-xs text-gray-500 mt-0.5">Last 24 hours</p>
            </div>

            {leaders.length === 0 ? (
                <p className="text-gray-500 text-sm p-4">No activity yet</p>
            ) : (
                <ul>
                    {leaders.map((user, index) => (
                        <li
                            key={user.id}
                            className="flex items-center justify-between px-4 py-3 hover:bg-gray-50 transition-colors cursor-pointer border-b border-gray-50 last:border-0"
                            onClick={() => onUserClick && onUserClick(user.username)}
                        >
                            <div className="flex items-center gap-3">
                                <span className={`font-bold text-sm w-5 text-center ${index === 0 ? 'text-yellow-500' :
                                    index === 1 ? 'text-gray-400' :
                                        index === 2 ? 'text-amber-600' : 'text-gray-400'
                                    }`}>
                                    {index + 1}
                                </span>
                                <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-white text-xs font-bold overflow-hidden flex-shrink-0">
                                    {user.avatar ? (
                                        <img src={user.avatar} alt="" className="w-full h-full object-cover" />
                                    ) : (
                                        <div className="w-full h-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center">
                                            {(user.name || user.username)[0].toUpperCase()}
                                        </div>
                                    )}
                                </div>
                                <div className="flex flex-col">
                                    <span className="font-medium text-gray-900 text-sm">{user.name || user.username}</span>
                                    {user.name && <span className="text-xs text-gray-500">@{user.username}</span>}
                                </div>
                            </div>
                            <div className="text-right">
                                <span className="font-bold text-blue-600">{user.karma_24h}</span>
                                <span className="text-gray-400 text-xs ml-1">karma</span>
                            </div>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}
