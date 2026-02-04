import React, { useState, useEffect } from 'react';
import { getCommunities, joinCommunity, leaveCommunity, createCommunity, getCommunity, getTopics, getChatMessages, sendChatMessage } from '../api';

export default function Communities({ user }) {
    const [communities, setCommunities] = useState([]);
    const [selectedCommunity, setSelectedCommunity] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showCreateModal, setShowCreateModal] = useState(false);

    useEffect(() => {
        loadCommunities();
    }, []);

    async function loadCommunities() {
        try {
            const data = await getCommunities();
            setCommunities(data);
        } catch (err) {
            console.error('Failed to load communities:', err);
        } finally {
            setLoading(false);
        }
    }

    async function handleJoin(id) {
        try {
            await joinCommunity(id);
            await loadCommunities();
        } catch (err) {
            alert(err.message);
        }
    }

    async function handleLeave(id) {
        try {
            await leaveCommunity(id);
            await loadCommunities();
            setSelectedCommunity(null);
        } catch (err) {
            console.error('Failed to leave:', err);
        }
    }

    if (selectedCommunity) {
        return (
            <CommunityDetail
                communityId={selectedCommunity}
                user={user}
                onBack={() => setSelectedCommunity(null)}
                onLeave={handleLeave}
            />
        );
    }

    if (loading) {
        return <div className="flex justify-center py-12"><div className="animate-spin">⏳</div></div>;
    }

    return (
        <div className="max-w-6xl mx-auto px-4 py-8">
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-bold">👥 Communities</h1>
                {user && (
                    <button
                        onClick={() => setShowCreateModal(true)}
                        className="bg-blue-600 text-white px-6 py-2 rounded-full font-semibold hover:bg-blue-700"
                    >
                        + Create Community
                    </button>
                )}
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {communities.map(community => (
                    <div
                        key={community.id}
                        className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition cursor-pointer"
                        onClick={() => setSelectedCommunity(community.id)}
                    >
                        <h3 className="text-xl font-bold mb-2">{community.name}</h3>
                        <p className="text-gray-600 mb-4 line-clamp-3">{community.description}</p>

                        <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                            <span>👥 {community.member_count} members</span>
                            {community.is_paid && <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded">💰 ${community.price}</span>}
                        </div>

                        {user && (
                            <div onClick={(e) => e.stopPropagation()}>
                                {community.is_member ? (
                                    <button
                                        onClick={() => handleLeave(community.id)}
                                        className="w-full bg-gray-200 text-gray-800 py-2 rounded-lg hover:bg-gray-300"
                                    >
                                        Leave
                                    </button>
                                ) : (
                                    <button
                                        onClick={() => handleJoin(community.id)}
                                        className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
                                    >
                                        {community.is_paid ? 'Purchase Access' : 'Join Free'}
                                    </button>
                                )}
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {showCreateModal && (
                <CreateCommunityModal
                    onClose={() => setShowCreateModal(false)}
                    onCreated={loadCommunities}
                />
            )}
        </div>
    );
}

// ============ COMMUNITY DETAIL VIEW ============

function CommunityDetail({ communityId, user, onBack, onLeave }) {
    const [community, setCommunity] = useState(null);
    const [topics, setTopics] = useState([]);
    const [selectedTopic, setSelectedTopic] = useState(null);
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadCommunityData();
    }, [communityId]);

    useEffect(() => {
        if (selectedTopic) {
            loadMessages();
            const interval = setInterval(loadMessages, 5000); // Refresh every 5s
            return () => clearInterval(interval);
        }
    }, [selectedTopic]);

    async function loadCommunityData() {
        try {
            const [communityData, topicsData] = await Promise.all([
                getCommunity(communityId),
                getTopics(communityId)
            ]);
            setCommunity(communityData);
            setTopics(topicsData);
            if (topicsData.length > 0) {
                setSelectedTopic(topicsData[0].id);
            }
        } catch (err) {
            console.error('Failed to load community:', err);
        } finally {
            setLoading(false);
        }
    }

    async function loadMessages() {
        if (!selectedTopic) return;
        try {
            const data = await getChatMessages(selectedTopic);
            setMessages(data);
        } catch (err) {
            console.error('Failed to load messages:', err);
        }
    }

    async function handleSendMessage(e) {
        e.preventDefault();
        if (!newMessage.trim()) return;

        try {
            await sendChatMessage({
                topic: selectedTopic,
                content: newMessage
            });
            setNewMessage('');
            await loadMessages();
        } catch (err) {
            alert('Failed to send message');
        }
    }

    if (loading) {
        return <div className="flex justify-center py-12"><div className="animate-spin">⏳</div></div>;
    }

    return (
        <div className="max-w-6xl mx-auto px-4 py-4">
            {/* Header */}
            <div className="bg-white rounded-lg shadow-sm border p-6 mb-4">
                <button onClick={onBack} className="text-blue-600 hover:underline mb-4">
                    ← Back to Communities
                </button>
                <div className="flex justify-between items-start">
                    <div>
                        <h1 className="text-3xl font-bold mb-2">{community.name}</h1>
                        <p className="text-gray-600 mb-4">{community.description}</p>
                        <div className="flex gap-4 text-sm text-gray-500">
                            <span>👥 {community.member_count} members</span>
                            <span>👤 Created by {community.creator.username}</span>
                            {community.is_paid && <span className="text-yellow-600">💰 ${community.price}</span>}
                        </div>
                    </div>
                    {user && community.is_member && (
                        <button
                            onClick={() => onLeave(communityId)}
                            className="bg-red-100 text-red-600 px-4 py-2 rounded-lg hover:bg-red-200"
                        >
                            Leave Community
                        </button>
                    )}
                </div>
            </div>

            {/* Chat Interface (WhatsApp-style) */}
            <div className="grid md:grid-cols-4 gap-4">
                {/* Topics Sidebar */}
                <div className="md:col-span-1 bg-white rounded-lg shadow-sm border p-4">
                    <h3 className="font-bold mb-4">📋 Topics</h3>
                    <div className="space-y-2">
                        {topics.map(topic => (
                            <button
                                key={topic.id}
                                onClick={() => setSelectedTopic(topic.id)}
                                className={`w-full text-left p-3 rounded-lg ${selectedTopic === topic.id
                                        ? 'bg-blue-100 text-blue-600 font-semibold'
                                        : 'hover:bg-gray-100'
                                    }`}
                            >
                                <div className="font-semibold">{topic.name}</div>
                                <div className="text-xs text-gray-500">{topic.message_count} messages</div>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Chat Messages */}
                <div className="md:col-span-3 bg-white rounded-lg shadow-sm border flex flex-col" style={{ height: '600px' }}>
                    {/* Messages Area */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-3">
                        {messages.length === 0 ? (
                            <div className="text-center text-gray-500 py-12">
                                No messages yet. Start the conversation!
                            </div>
                        ) : (
                            messages.map(msg => (
                                <div key={msg.id} className="flex gap-3">
                                    <div className="w-10 h-10 rounded-full bg-blue-600 text-white flex items-center justify-center font-semibold flex-shrink-0">
                                        {msg.author.username.charAt(0).toUpperCase()}
                                    </div>
                                    <div className="flex-1">
                                        <div className="flex items-baseline gap-2">
                                            <span className="font-semibold">{msg.author.username}</span>
                                            <span className="text-xs text-gray-500">
                                                {new Date(msg.created_at).toLocaleTimeString()}
                                            </span>
                                        </div>
                                        <div className="text-gray-800">{msg.content}</div>
                                        {msg.file && (
                                            <div className="mt-2 text-sm text-blue-600">📎 File attached</div>
                                        )}
                                    </div>
                                </div>
                            ))
                        )}
                    </div>

                    {/* Message Input */}
                    {user && community.is_member ? (
                        <form onSubmit={handleSendMessage} className="border-t p-4">
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    value={newMessage}
                                    onChange={(e) => setNewMessage(e.target.value)}
                                    placeholder="Type a message..."
                                    className="flex-1 border rounded-lg px-4 py-2"
                                />
                                <button
                                    type="submit"
                                    className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
                                >
                                    Send
                                </button>
                            </div>
                        </form>
                    ) : (
                        <div className="border-t p-4 text-center text-gray-500">
                            Join this community to participate in discussions
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

// ============ CREATE MODAL ============

function CreateCommunityModal({ onClose, onCreated }) {
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [isPaid, setIsPaid] = useState(false);
    const [price, setPrice] = useState('');

    async function handleSubmit(e) {
        e.preventDefault();
        try {
            await createCommunity({
                name,
                description,
                is_paid: isPaid,
                price: isPaid ? parseFloat(price) : 0
            });
            onCreated();
            onClose();
        } catch (err) {
            alert('Failed to create community');
        }
    }

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={onClose}>
            <div className="bg-white rounded-lg p-6 max-w-lg w-full mx-4" onClick={(e) => e.stopPropagation()}>
                <h2 className="text-2xl font-bold mb-4">Create Community</h2>
                <form onSubmit={handleSubmit}>
                    <input
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="Community Name"
                        className="w-full border rounded-lg p-3 mb-4"
                        required
                    />

                    <textarea
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        placeholder="Description"
                        className="w-full border rounded-lg p-3 mb-4 h-32"
                        required
                    />

                    <label className="flex items-center gap-2 mb-4">
                        <input
                            type="checkbox"
                            checked={isPaid}
                            onChange={(e) => setIsPaid(e.target.checked)}
                        />
                        <span>Paid Community</span>
                    </label>

                    {isPaid && (
                        <input
                            type="number"
                            value={price}
                            onChange={(e) => setPrice(e.target.value)}
                            placeholder="Price ($)"
                            className="w-full border rounded-lg p-3 mb-4"
                            step="0.01"
                            required
                        />
                    )}

                    <div className="flex gap-2 justify-end">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-6 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                        >
                            Create
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
