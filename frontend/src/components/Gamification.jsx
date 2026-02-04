import React, { useState, useEffect } from 'react';
import { getUserPoints, getLeaderboard } from '../api';

export default function Gamification({ user }) {
    const [points, setPoints] = useState(null);
    const [leaderboard, setLeaderboard] = useState([]);
    const [timeRange, setTimeRange] = useState('24h');

    useEffect(() => {
        if (user) {
            loadPoints();
        }
        loadLeaderboard();
    }, [user, timeRange]);

    async function loadPoints() {
        try {
            const data = await getUserPoints();
            setPoints(data);
        } catch (err) {
            console.error('Failed to load points:', err);
        }
    }

    async function loadLeaderboard() {
        try {
            const data = await getLeaderboard(timeRange);
            setLeaderboard(data);
        } catch (err) {
            console.error('Failed to load leaderboard:', err);
        }
    }

    return (
        <div className="max-w-4xl mx-auto px-4 py-8">
            {user && points && (
                <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-8 mb-8">
                    <h2 className="text-2xl font-bold mb-4">Your Stats</h2>
                    <div className="grid grid-cols-3 gap-6">
                        <div>
                            <div className="text-4xl font-bold">{points.total_points}</div>
                            <div className="text-blue-100">Total Points</div>
                        </div>
                        <div>
                            <div className="text-4xl font-bold">Level {points.level}</div>
                            <div className="text-blue-100">Current Level</div>
                        </div>
                        <div>
                            <div className="text-4xl font-bold">{points.streak_days}🔥</div>
                            <div className="text-blue-100">Day Streak</div>
                        </div>
                    </div>
                </div>
            )}

            <div className="bg-white rounded-lg shadow-sm border p-6">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold">🏆 Leaderboard</h2>
                    <select
                        value={timeRange}
                        onChange={(e) => setTimeRange(e.target.value)}
                        className="border rounded-lg px-4 py-2"
                    >
                        <option value="24h">Last 24 Hours</option>
                        <option value="7d">Last 7 Days</option>
                        <option value="all">All Time</option>
                    </select>
                </div>

                <div className="space-y-2">
                    {leaderboard.map((user, index) => (
                        <div
                            key={user.id}
                            className={`flex items-center justify-between p-4 rounded-lg ${index < 3 ? 'bg-gradient-to-r from-yellow-50 to-orange-50' : 'bg-gray-50'
                                }`}
                        >
                            <div className="flex items-center gap-4">
                                <div className={`text-2xl font-bold ${index === 0 ? 'text-yellow-500' :
                                        index === 1 ? 'text-gray-400' :
                                            index === 2 ? 'text-orange-600' :
                                                'text-gray-600'
                                    }`}>
                                    {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `#${index + 1}`}
                                </div>
                                <div>
                                    <div className="font-semibold">{user.username}</div>
                                    {timeRange === 'all' && (
                                        <div className="text-sm text-gray-500">Level {user.level}</div>
                                    )}
                                </div>
                            </div>
                            <div className="text-xl font-bold text-blue-600">
                                {timeRange === 'all' ? user.points : user.karma_24h} pts
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
