import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { FiPlay, FiClock, FiUsers, FiCheckCircle, FiLock, FiFile, FiDownload } from 'react-icons/fi';
import { toast } from 'react-toastify';
import { coursesAPI, progressAPI } from '../../services/api';
import './Student.css';

const CourseDetail = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);
  const [enrolling, setEnrolling] = useState(false);

  useEffect(() => {
    fetchCourseData();
  }, [slug]);

  const fetchCourseData = async () => {
    try {
      const courseRes = await coursesAPI.get(slug);
      setCourse(courseRes.data);

      if (courseRes.data.is_enrolled) {
        const progressRes = await progressAPI.courseProgress(slug);
        setProgress(progressRes.data);
      }
    } catch (error) {
      console.error('Error fetching course:', error);
      toast.error('Course not found');
      navigate('/courses');
    } finally {
      setLoading(false);
    }
  };

  const handleEnroll = async () => {
    setEnrolling(true);
    try {
      await coursesAPI.enroll(slug);
      toast.success('Successfully enrolled!');
      fetchCourseData();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to enroll');
    } finally {
      setEnrolling(false);
    }
  };

  if (loading) {
    return <div className="page-loading">Loading course...</div>;
  }

  if (!course) {
    return null;
  }

  return (
    <div className="course-detail-page">
      {/* Course Header */}
      <div className="course-header">
        <div className="course-header-content">
          <span className="badge badge-primary">{course.level}</span>
          <h1>{course.title}</h1>
          <p className="course-description">{course.description}</p>
          
          <div className="course-stats">
            <span><FiPlay /> {course.total_videos} videos</span>
            <span><FiClock /> {course.total_duration_minutes} mins</span>
            <span><FiUsers /> {course.enrolled_students_count} students</span>
          </div>

          <div className="course-instructor">
            <span>Instructor: <strong>{course.instructor_name}</strong></span>
          </div>

          {!course.is_enrolled ? (
            <button 
              className="btn btn-primary btn-lg"
              onClick={handleEnroll}
              disabled={enrolling}
            >
              {enrolling ? 'Enrolling...' : 'Enroll Now'}
            </button>
          ) : (
            <div className="enrolled-badge">
              <FiCheckCircle /> Enrolled
              {progress && (
                <span className="progress-text">{progress.progress_percentage}% complete</span>
              )}
            </div>
          )}
        </div>
        
        {course.thumbnail && (
          <div className="course-header-image">
            <img src={course.thumbnail} alt={course.title} />
          </div>
        )}
      </div>

      <div className="course-content">
        {/* Learning Objectives */}
        {course.learning_objectives && (
          <div className="card course-section">
            <h2>What You'll Learn</h2>
            <div className="objectives-list">
              {course.learning_objectives.split('\n').map((obj, index) => (
                <div key={index} className="objective-item">
                  <FiCheckCircle className="check-icon" />
                  <span>{obj}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Course Modules */}
        <div className="card course-section">
          <h2>Course Content</h2>
          <div className="modules-list">
            {course.modules?.map((module, moduleIndex) => (
              <div key={module.id} className="module-item">
                <div className="module-header">
                  <h3>Module {moduleIndex + 1}: {module.title}</h3>
                  <span className="module-meta">
                    {module.videos?.length} videos • {module.total_duration_minutes} mins
                  </span>
                </div>
                
                <div className="videos-list">
                  {module.videos?.map((video, videoIndex) => {
                    const videoProgress = progress?.video_progress?.find(
                      vp => vp.video === video.id
                    );
                    const isCompleted = videoProgress?.is_completed;
                    const canAccess = course.is_enrolled || video.is_preview;

                    return (
                      <div key={video.id} className={`video-item ${isCompleted ? 'completed' : ''}`}>
                        <div className="video-icon">
                          {isCompleted ? (
                            <FiCheckCircle className="completed-icon" />
                          ) : canAccess ? (
                            <FiPlay />
                          ) : (
                            <FiLock />
                          )}
                        </div>
                        <div className="video-info">
                          <span className="video-title">{video.title}</span>
                          <span className="video-duration">{video.duration_minutes} mins</span>
                        </div>
                        {canAccess && (
                          <Link 
                            to={`/courses/${slug}/video/${video.id}`}
                            className="btn btn-sm btn-outline"
                          >
                            {isCompleted ? 'Rewatch' : 'Watch'}
                          </Link>
                        )}
                        {video.is_preview && !course.is_enrolled && (
                          <span className="badge badge-success">Preview</span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Resources */}
        {course.resources?.length > 0 && (
          <div className="card course-section">
            <h2>Resources</h2>
            <div className="resources-list">
              {course.resources.map((resource) => (
                <a 
                  key={resource.id}
                  href={resource.google_drive_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="resource-item"
                >
                  <FiFile />
                  <span>{resource.title}</span>
                  <FiDownload />
                </a>
              ))}
            </div>
          </div>
        )}

        {/* Prerequisites */}
        {course.prerequisites && (
          <div className="card course-section">
            <h2>Prerequisites</h2>
            <p>{course.prerequisites}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default CourseDetail;
