import React, { useState, useEffect } from 'react';
import { getNotifications, markAllNotificationsRead } from '../api';

export default function NotificationBell({ user }) {
    const [notifications, setNotifications] = useState([]);
    const [showDropdown, setShowDropdown] = useState(false);
    const [unreadCount, setUnreadCount] = useState(0);

    useEffect(() => {
        if (user) {
            loadNotifications();
            // Poll every 30 seconds
            const interval = setInterval(loadNotifications, 30000);
            return () => clearInterval(interval);
        }
    }, [user]);

    async function loadNotifications() {
        try {
            const data = await getNotifications();
            setNotifications(data);
            setUnreadCount(data.filter(n => !n.read).length);
        } catch (err) {
            console.error('Failed to load notifications:', err);
        }
    }

    async function handleMarkAllRead() {
        try {
            await markAllNotificationsRead();
            await loadNotifications();
        } catch (err) {
            console.error('Failed to mark read:', err);
        }
    }

    if (!user) return null;

    return (
        <div className="relative">
            <button
                onClick={() => setShowDropdown(!showDropdown)}
                className="relative p-2 hover:bg-gray-100 rounded-full"
            >
                🔔
                {unreadCount > 0 && (
                    <span className="absolute top-0 right-0 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                        {unreadCount}
                    </span>
                )}
            </button>

            {showDropdown && (
                <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border z-50 max-h-96 overflow-y-auto">
                    <div className="p-4 border-b flex justify-between items-center">
                        <h3 className="font-bold">Notifications</h3>
                        {unreadCount > 0 && (
                            <button
                                onClick={handleMarkAllRead}
                                className="text-sm text-blue-600 hover:underline"
                            >
                                Mark all read
                            </button>
                        )}
                    </div>

                    {notifications.length === 0 ? (
                        <div className="p-8 text-center text-gray-500">
                            No notifications yet
                        </div>
                    ) : (
                        notifications.map(notif => (
                            <div
                                key={notif.id}
                                className={`p-4 border-b hover:bg-gray-50 cursor-pointer ${!notif.read ? 'bg-blue-50' : ''
                                    }`}
                            >
                                <div className="text-sm">{notif.message}</div>
                                <div className="text-xs text-gray-500 mt-1">
                                    {new Date(notif.created_at).toLocaleDateString()}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            )}
        </div>
    );
}
