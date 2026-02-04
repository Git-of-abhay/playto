import React, { useState, useEffect } from 'react';
import { getCourses, enrollInCourse, getMyEnrollments, getCourse, completeLesson } from '../api';

export default function Courses({ user }) {
    const [courses, setCourses] = useState([]);
    const [myEnrollments, setMyEnrollments] = useState([]);
    const [selectedCourse, setSelectedCourse] = useState(null);
    const [activeTab, setActiveTab] = useState('browse');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadCourses();
        if (user) {
            loadEnrollments();
        }
    }, [user]);

    async function loadCourses() {
        try {
            const data = await getCourses();
            setCourses(data);
        } catch (err) {
            console.error('Failed to load courses:', err);
        } finally {
            setLoading(false);
        }
    }

    async function loadEnrollments() {
        try {
            const data = await getMyEnrollments();
            setMyEnrollments(data);
        } catch (err) {
            console.error('Failed to load enrollments:', err);
        }
    }

    async function handleEnroll(id) {
        try {
            await enrollInCourse(id);
            await loadEnrollments();
            alert('Enrolled successfully!');
        } catch (err) {
            alert(err.message);
        }
    }

    if (selectedCourse) {
        return (
            <CourseDetail
                courseId={selectedCourse}
                user={user}
                onBack={() => setSelectedCourse(null)}
                onEnroll={handleEnroll}
            />
        );
    }

    if (loading) {
        return <div className="flex justify-center py-12"><div className="animate-spin">⏳</div></div>;
    }

    return (
        <div className="max-w-6xl mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold mb-8">📚 Courses</h1>

            {user && (
                <div className="flex gap-4 mb-8 border-b">
                    <button
                        onClick={() => setActiveTab('browse')}
                        className={`pb-2 px-4 ${activeTab === 'browse' ? 'border-b-2 border-blue-600 text-blue-600 font-semibold' : 'text-gray-600'}`}
                    >
                        Browse All
                    </button>
                    <button
                        onClick={() => setActiveTab('enrolled')}
                        className={`pb-2 px-4 ${activeTab === 'enrolled' ? 'border-b-2 border-blue-600 text-blue-600 font-semibold' : 'text-gray-600'}`}
                    >
                        My Courses ({myEnrollments.length})
                    </button>
                </div>
            )}

            {activeTab === 'browse' ? (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {courses.map(course => (
                        <CourseCard
                            key={course.id}
                            course={course}
                            user={user}
                            onClick={() => setSelectedCourse(course.id)}
                            onEnroll={() => handleEnroll(course.id)}
                        />
                    ))}
                </div>
            ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {myEnrollments.map(enrollment => (
                        <EnrollmentCard
                            key={enrollment.id}
                            enrollment={enrollment}
                            onClick={() => setSelectedCourse(enrollment.course.id)}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}

// ============ COURSE DETAIL VIEW ============

function CourseDetail({ courseId, user, onBack, onEnroll }) {
    const [course, setCourse] = useState(null);
    const [selectedLesson, setSelectedLesson] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadCourse();
    }, [courseId]);

    async function loadCourse() {
        try {
            const data = await getCourse(courseId);
            setCourse(data);
            // Auto-select first lesson of first module
            if (data.modules && data.modules.length > 0 && data.modules[0].lessons.length > 0) {
                setSelectedLesson(data.modules[0].lessons[0]);
            }
        } catch (err) {
            console.error('Failed to load course:', err);
        } finally {
            setLoading(false);
        }
    }

    async function handleCompleteLesson(lessonId) {
        try {
            await completeLesson(lessonId);
            alert('Lesson marked as complete! +20 points');
            await loadCourse(); // Refresh to update progress
        } catch (err) {
            alert('Failed to mark complete');
        }
    }

    if (loading) {
        return <div className="flex justify-center py-12"><div className="animate-spin">⏳</div></div>;
    }

    const isEnrolled = course.is_enrolled;
    const canViewContent = isEnrolled || selectedLesson?.is_free;

    return (
        <div className="max-w-7xl mx-auto px-4 py-4">
            {/* Header */}
            <div className="bg-white rounded-lg shadow-sm border p-6 mb-4">
                <button onClick={onBack} className="text-blue-600 hover:underline mb-4">
                    ← Back to Courses
                </button>
                <div className="flex justify-between items-start">
                    <div className="flex-1">
                        <h1 className="text-3xl font-bold mb-2">{course.title}</h1>
                        <p className="text-gray-600 mb-4">{course.description}</p>
                        <div className="flex gap-4 text-sm text-gray-500 mb-4">
                            <span>👤 {course.instructor.username}</span>
                            <span>📚 {course.modules?.length || 0} modules</span>
                            {course.is_paid && <span className="text-green-600 font-semibold">${course.price}</span>}
                        </div>
                    </div>
                    {user && !isEnrolled && (
                        <button
                            onClick={() => onEnroll(courseId)}
                            className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 font-semibold"
                        >
                            {course.is_paid ? `Enroll for $${course.price}` : 'Enroll Free'}
                        </button>
                    )}
                    {isEnrolled && (
                        <div className="bg-green-100 text-green-600 px-4 py-2 rounded-lg font-semibold">
                            ✓ Enrolled
                        </div>
                    )}
                </div>
            </div>

            {/* Course Content */}
            <div className="grid md:grid-cols-3 gap-4">
                {/* Curriculum Sidebar */}
                <div className="md:col-span-1 bg-white rounded-lg shadow-sm border p-4 overflow-y-auto" style={{ maxHeight: '600px' }}>
                    <h3 className="font-bold mb-4">📋 Curriculum</h3>
                    <div className="space-y-4">
                        {course.modules?.map((module, moduleIdx) => (
                            <div key={module.id} className="border rounded-lg p-3">
                                <div className="font-semibold mb-2">
                                    {moduleIdx + 1}. {module.title}
                                </div>
                                <div className="space-y-2">
                                    {module.lessons.map((lesson, lessonIdx) => (
                                        <button
                                            key={lesson.id}
                                            onClick={() => setSelectedLesson(lesson)}
                                            disabled={!canViewContent && !lesson.is_free}
                                            className={`w-full text-left text-sm p-2 rounded ${selectedLesson?.id === lesson.id
                                                    ? 'bg-blue-100 text-blue-600 font-semibold'
                                                    : 'hover:bg-gray-100'
                                                } ${!canViewContent && !lesson.is_free ? 'opacity-50 cursor-not-allowed' : ''}`}
                                        >
                                            <div className="flex items-center gap-2">
                                                <span>{getContentIcon(lesson.content_type)}</span>
                                                <span className="flex-1">
                                                    {lessonIdx + 1}. {lesson.title}
                                                </span>
                                                {lesson.is_free && <span className="text-xs bg-green-100 text-green-600 px-2 py-1 rounded">FREE</span>}
                                                {!canViewContent && !lesson.is_free && <span>🔒</span>}
                                            </div>
                                            <div className="text-xs text-gray-500 mt-1">{lesson.duration_minutes} min</div>
                                        </button>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Lesson Content */}
                <div className="md:col-span-2 bg-white rounded-lg shadow-sm border">
                    {selectedLesson ? (
                        <LessonViewer
                            lesson={selectedLesson}
                            canView={canViewContent}
                            isEnrolled={isEnrolled}
                            onComplete={handleCompleteLesson}
                        />
                    ) : (
                        <div className="p-12 text-center text-gray-500">
                            Select a lesson to start learning
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

// ============ LESSON VIEWER ============

function LessonViewer({ lesson, canView, isEnrolled, onComplete }) {
    if (!canView) {
        return (
            <div className="p-12 text-center">
                <div className="text-6xl mb-4">🔒</div>
                <h3 className="text-xl font-bold mb-2">Enroll to Access</h3>
                <p className="text-gray-600">Enroll in this course to unlock all lessons</p>
            </div>
        );
    }

    return (
        <div className="p-6">
            <div className="flex justify-between items-start mb-6">
                <div>
                    <h2 className="text-2xl font-bold mb-2">{lesson.title}</h2>
                    <div className="flex gap-4 text-sm text-gray-500">
                        <span>{getContentTypeLabel(lesson.content_type)}</span>
                        <span>⏱️ {lesson.duration_minutes} minutes</span>
                    </div>
                </div>
                {isEnrolled && (
                    <button
                        onClick={() => onComplete(lesson.id)}
                        className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700"
                    >
                        ✓ Mark Complete
                    </button>
                )}
            </div>

            {/* Content Display */}
            <div className="border rounded-lg p-6 min-h-96">
                {lesson.content_type === 'video' && lesson.video_url && (
                    <div className="aspect-video bg-gray-900 rounded flex items-center justify-center text-white">
                        <div className="text-center">
                            <div className="text-6xl mb-4">▶️</div>
                            <div className="text-sm">Video Player</div>
                            <div className="text-xs text-gray-400 mt-2">{lesson.video_url}</div>
                        </div>
                    </div>
                )}

                {lesson.content_type === 'text' && (
                    <div className="prose max-w-none">
                        <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">{lesson.content}</p>
                    </div>
                )}

                {lesson.content_type === 'quiz' && (
                    <div className="text-center py-12">
                        <div className="text-6xl mb-4">📝</div>
                        <h3 className="text-xl font-bold mb-2">Quiz Time!</h3>
                        <p className="text-gray-600">Complete the quiz to test your knowledge</p>
                        <button className="mt-6 bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700">
                            Start Quiz
                        </button>
                    </div>
                )}

                {lesson.content_type === 'assignment' && (
                    <div className="text-center py-12">
                        <div className="text-6xl mb-4">📋</div>
                        <h3 className="text-xl font-bold mb-2">Assignment</h3>
                        <p className="text-gray-600 mb-6">Submit your work for instructor review</p>
                        <textarea
                            className="w-full border rounded-lg p-4 mb-4"
                            rows="6"
                            placeholder="Write your answer here..."
                        />
                        <button className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700">
                            Submit Assignment
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}

// ============ HELPER COMPONENTS ============

function CourseCard({ course, user, onClick, onEnroll }) {
    return (
        <div
            className="bg-white rounded-lg shadow-sm border overflow-hidden hover:shadow-md transition cursor-pointer"
            onClick={onClick}
        >
            <div className="h-48 bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-6xl">
                📚
            </div>
            <div className="p-6">
                <h3 className="text-xl font-bold mb-2">{course.title}</h3>
                <p className="text-gray-600 mb-4 line-clamp-3">{course.description}</p>

                <div className="flex items-center gap-2 text-sm text-gray-500 mb-4">
                    <span>👤 {course.instructor.username}</span>
                    <span>•</span>
                    <span>{course.modules?.length || 0} modules</span>
                </div>

                {course.is_paid && (
                    <div className="text-2xl font-bold text-blue-600 mb-4">
                        ${course.price}
                    </div>
                )}

                {user && (
                    <div onClick={(e) => e.stopPropagation()}>
                        {course.is_enrolled ? (
                            <div className="text-green-600 font-semibold">✓ Enrolled</div>
                        ) : (
                            <button
                                onClick={onEnroll}
                                className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
                            >
                                {course.is_paid ? 'Purchase Course' : 'Enroll Free'}
                            </button>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}

function EnrollmentCard({ enrollment, onClick }) {
    return (
        <div
            className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition cursor-pointer"
            onClick={onClick}
        >
            <h3 className="text-xl font-bold mb-2">{enrollment.course.title}</h3>
            <p className="text-gray-600 mb-4 line-clamp-2">{enrollment.course.description}</p>

            <div className="mb-4">
                <div className="flex justify-between text-sm mb-1">
                    <span>Progress</span>
                    <span>{enrollment.progress_percentage}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                        className="bg-blue-600 h-2 rounded-full transition-all"
                        style={{ width: `${enrollment.progress_percentage}%` }}
                    />
                </div>
            </div>

            {enrollment.completed ? (
                <div className="text-green-600 font-semibold">🎉 Completed!</div>
            ) : (
                <button className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">
                    Continue Learning →
                </button>
            )}
        </div>
    );
}

// ============ UTILITIES ============

function getContentIcon(type) {
    const icons = {
        'video': '🎥',
        'text': '📄',
        'quiz': '📝',
        'assignment': '📋'
    };
    return icons[type] || '📚';
}

function getContentTypeLabel(type) {
    const labels = {
        'video': '🎥 Video Lesson',
        'text': '📄 Reading',
        'quiz': '📝 Quiz',
        'assignment': '📋 Assignment'
    };
    return labels[type] || 'Lesson';
}
