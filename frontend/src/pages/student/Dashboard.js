import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FiBook, FiClock, FiAward, FiPlay } from 'react-icons/fi';
import { useAuth } from '../../context/AuthContext';
import { coursesAPI, progressAPI } from '../../services/api';
import './Student.css';

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({ enrolled: 0, completed: 0, inProgress: 0 });
  const [enrolledCourses, setEnrolledCourses] = useState([]);
  const [featuredCourses, setFeaturedCourses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [coursesRes, featuredRes, progressRes] = await Promise.all([
        coursesAPI.myCourses(),
        coursesAPI.featured(),
        progressAPI.myProgress()
      ]);

      const enrolled = coursesRes.data.results || coursesRes.data;
      setEnrolledCourses(enrolled.slice(0, 4));
      
      setFeaturedCourses(featuredRes.data.slice(0, 3));
      
      const progress = progressRes.data.results || progressRes.data;
      setStats({
        enrolled: enrolled.length,
        completed: progress.filter(p => p.is_completed).length,
        inProgress: progress.filter(p => !p.is_completed && p.progress_percentage > 0).length
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="page-loading">Loading...</div>;
  }

  return (
    <div className="dashboard-page">
      <div className="page-header">
        <h1>Welcome back, {user?.first_name || 'Student'}!</h1>
        <p>Continue your learning journey</p>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ backgroundColor: 'rgba(79, 70, 229, 0.1)' }}>
            <FiBook color="#4F46E5" size={24} />
          </div>
          <div className="stat-info">
            <h3>{stats.enrolled}</h3>
            <p>Enrolled Courses</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ backgroundColor: 'rgba(245, 158, 11, 0.1)' }}>
            <FiClock color="#F59E0B" size={24} />
          </div>
          <div className="stat-info">
            <h3>{stats.inProgress}</h3>
            <p>In Progress</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ backgroundColor: 'rgba(16, 185, 129, 0.1)' }}>
            <FiAward color="#10B981" size={24} />
          </div>
          <div className="stat-info">
            <h3>{stats.completed}</h3>
            <p>Completed</p>
          </div>
        </div>
      </div>

      {/* Continue Learning */}
      {enrolledCourses.length > 0 && (
        <section className="dashboard-section">
          <div className="section-header">
            <h2>Continue Learning</h2>
            <Link to="/courses" className="view-all">View All</Link>
          </div>
          <div className="courses-grid">
            {enrolledCourses.map((enrollment) => (
              <div key={enrollment.id} className="course-card">
                <div className="course-thumbnail">
                  {enrollment.course?.thumbnail ? (
                    <img src={enrollment.course.thumbnail} alt={enrollment.course.title} />
                  ) : (
                    <div className="thumbnail-placeholder">
                      <FiPlay size={32} />
                    </div>
                  )}
                </div>
                <div className="course-info">
                  <h3>{enrollment.course?.title}</h3>
                  <div className="progress-info">
                    <div className="progress-bar">
                      <div 
                        className="progress-bar-fill" 
                        style={{ width: `${enrollment.progress || 0}%` }}
                      />
                    </div>
                    <span className="progress-text">{enrollment.progress || 0}% complete</span>
                  </div>
                  <Link 
                    to={`/courses/${enrollment.course?.slug}`} 
                    className="btn btn-primary btn-sm"
                  >
                    Continue
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Featured Courses */}
      <section className="dashboard-section">
        <div className="section-header">
          <h2>Featured Courses</h2>
          <Link to="/courses" className="view-all">Browse All</Link>
        </div>
        <div className="courses-grid">
          {featuredCourses.map((course) => (
            <div key={course.id} className="course-card">
              <div className="course-thumbnail">
                {course.thumbnail ? (
                  <img src={course.thumbnail} alt={course.title} />
                ) : (
                  <div className="thumbnail-placeholder">
                    <FiBook size={32} />
                  </div>
                )}
                <span className="badge badge-primary">{course.level}</span>
              </div>
              <div className="course-info">
                <h3>{course.title}</h3>
                <p className="course-description">{course.short_description}</p>
                <div className="course-meta">
                  <span><FiPlay size={14} /> {course.total_videos} videos</span>
                  <span><FiClock size={14} /> {course.duration_hours}h</span>
                </div>
                <Link to={`/courses/${course.slug}`} className="btn btn-outline btn-sm">
                  View Course
                </Link>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default Dashboard;
