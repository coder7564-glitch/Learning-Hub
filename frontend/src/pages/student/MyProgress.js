import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FiBook, FiCheckCircle, FiClock } from 'react-icons/fi';
import { progressAPI } from '../../services/api';
import './Student.css';

const MyProgress = () => {
  const [progress, setProgress] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProgress();
  }, []);

  const fetchProgress = async () => {
    try {
      const response = await progressAPI.myProgress();
      setProgress(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching progress:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="page-loading">Loading progress...</div>;
  }

  return (
    <div className="progress-page">
      <div className="page-header">
        <h1>My Progress</h1>
        <p>Track your learning journey</p>
      </div>

      {progress.length === 0 ? (
        <div className="empty-state">
          <FiBook size={48} />
          <h3>No progress yet</h3>
          <p>Start learning to track your progress</p>
          <Link to="/courses" className="btn btn-primary">Browse Courses</Link>
        </div>
      ) : (
        <div className="progress-list">
          {progress.map((item) => (
            <div key={item.id} className="card progress-card">
              <div className="progress-card-header">
                <h3>{item.course_title}</h3>
                {item.is_completed ? (
                  <span className="badge badge-success">
                    <FiCheckCircle /> Completed
                  </span>
                ) : (
                  <span className="badge badge-warning">
                    <FiClock /> In Progress
                  </span>
                )}
              </div>

              <div className="progress-stats">
                <div className="progress-stat">
                  <span className="stat-label">Videos</span>
                  <span className="stat-value">{item.videos_completed} / {item.total_videos}</span>
                </div>
                <div className="progress-stat">
                  <span className="stat-label">Quizzes</span>
                  <span className="stat-value">{item.quizzes_passed} / {item.total_quizzes}</span>
                </div>
                <div className="progress-stat">
                  <span className="stat-label">Started</span>
                  <span className="stat-value">
                    {new Date(item.started_at).toLocaleDateString()}
                  </span>
                </div>
              </div>

              <div className="progress-bar-section">
                <div className="progress-bar-header">
                  <span>Overall Progress</span>
                  <span>{item.progress_percentage}%</span>
                </div>
                <div className="progress-bar large">
                  <div 
                    className="progress-bar-fill" 
                    style={{ width: `${item.progress_percentage}%` }}
                  />
                </div>
              </div>

              <div className="progress-actions">
                <Link to={`/courses/${item.course_slug}`} className="btn btn-primary">
                  {item.is_completed ? 'Review Course' : 'Continue Learning'}
                </Link>
                {item.is_completed && (
                  <Link to="/certificates" className="btn btn-outline">
                    View Certificate
                  </Link>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MyProgress;
