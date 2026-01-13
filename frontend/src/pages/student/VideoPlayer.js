import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiArrowRight, FiCheckCircle, FiList } from 'react-icons/fi';
import { toast } from 'react-toastify';
import { coursesAPI, progressAPI } from '../../services/api';
import './Student.css';

const VideoPlayer = () => {
  const { slug, videoId } = useParams();
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [currentVideo, setCurrentVideo] = useState(null);
  const [allVideos, setAllVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const progressInterval = useRef(null);
  const watchedTime = useRef(0);

  useEffect(() => {
    fetchVideoData();
    return () => {
      if (progressInterval.current) {
        clearInterval(progressInterval.current);
      }
    };
  }, [slug, videoId]);

  const fetchVideoData = async () => {
    try {
      const courseRes = await coursesAPI.get(slug);
      setCourse(courseRes.data);

      // Flatten all videos from modules
      const videos = [];
      courseRes.data.modules?.forEach(module => {
        module.videos?.forEach(video => {
          videos.push({ ...video, moduleName: module.title });
        });
      });
      setAllVideos(videos);

      // Find current video
      const video = videos.find(v => v.id === parseInt(videoId));
      if (video) {
        setCurrentVideo(video);
      } else {
        toast.error('Video not found');
        navigate(`/courses/${slug}`);
      }
    } catch (error) {
      console.error('Error fetching video:', error);
      navigate(`/courses/${slug}`);
    } finally {
      setLoading(false);
    }
  };

  const updateProgress = async (completed = false) => {
    try {
      await progressAPI.updateVideo({
        video_id: parseInt(videoId),
        watched_seconds: watchedTime.current,
        total_seconds: (currentVideo?.duration_minutes || 1) * 60,
        is_completed: completed
      });
    } catch (error) {
      console.error('Error updating progress:', error);
    }
  };

  const handleVideoProgress = () => {
    watchedTime.current += 10;
    
    // Update progress every 30 seconds
    if (watchedTime.current % 30 === 0) {
      updateProgress();
    }
  };

  const handleVideoComplete = () => {
    updateProgress(true);
    toast.success('Video completed!');
  };

  const currentIndex = allVideos.findIndex(v => v.id === parseInt(videoId));
  const prevVideo = currentIndex > 0 ? allVideos[currentIndex - 1] : null;
  const nextVideo = currentIndex < allVideos.length - 1 ? allVideos[currentIndex + 1] : null;

  if (loading) {
    return <div className="page-loading">Loading video...</div>;
  }

  return (
    <div className="video-player-page">
      {/* Video Section */}
      <div className={`video-main ${!sidebarOpen ? 'full-width' : ''}`}>
        <div className="video-header">
          <Link to={`/courses/${slug}`} className="back-link">
            <FiArrowLeft /> Back to Course
          </Link>
          <button 
            className="btn btn-outline btn-sm toggle-sidebar"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            <FiList /> {sidebarOpen ? 'Hide' : 'Show'} Playlist
          </button>
        </div>

        <div className="video-container">
          {currentVideo && (
            <iframe
              src={`https://drive.google.com/file/d/${currentVideo.google_drive_file_id}/preview`}
              title={currentVideo.title}
              allowFullScreen
              allow="autoplay"
              onLoad={() => {
                progressInterval.current = setInterval(handleVideoProgress, 10000);
              }}
            />
          )}
        </div>

        <div className="video-info-section">
          <h1>{currentVideo?.title}</h1>
          <p className="video-module">{currentVideo?.moduleName}</p>
          {currentVideo?.description && (
            <p className="video-description">{currentVideo.description}</p>
          )}

          <div className="video-navigation">
            {prevVideo ? (
              <Link 
                to={`/courses/${slug}/video/${prevVideo.id}`}
                className="btn btn-outline"
              >
                <FiArrowLeft /> Previous
              </Link>
            ) : (
              <div />
            )}
            
            <button 
              className="btn btn-success"
              onClick={handleVideoComplete}
            >
              <FiCheckCircle /> Mark as Complete
            </button>

            {nextVideo ? (
              <Link 
                to={`/courses/${slug}/video/${nextVideo.id}`}
                className="btn btn-primary"
              >
                Next <FiArrowRight />
              </Link>
            ) : (
              <Link to={`/courses/${slug}`} className="btn btn-primary">
                Finish Course
              </Link>
            )}
          </div>
        </div>
      </div>

      {/* Sidebar Playlist */}
      {sidebarOpen && (
        <aside className="video-sidebar">
          <div className="sidebar-header">
            <h3>Course Content</h3>
          </div>
          <div className="playlist">
            {course?.modules?.map((module, moduleIndex) => (
              <div key={module.id} className="playlist-module">
                <h4>Module {moduleIndex + 1}: {module.title}</h4>
                <div className="playlist-videos">
                  {module.videos?.map((video) => (
                    <Link
                      key={video.id}
                      to={`/courses/${slug}/video/${video.id}`}
                      className={`playlist-item ${video.id === parseInt(videoId) ? 'active' : ''}`}
                    >
                      <span className="playlist-icon">
                        {video.id === parseInt(videoId) ? (
                          <FiCheckCircle className="playing" />
                        ) : (
                          <FiCheckCircle />
                        )}
                      </span>
                      <span className="playlist-title">{video.title}</span>
                      <span className="playlist-duration">{video.duration_minutes}m</span>
                    </Link>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </aside>
      )}
    </div>
  );
};

export default VideoPlayer;
