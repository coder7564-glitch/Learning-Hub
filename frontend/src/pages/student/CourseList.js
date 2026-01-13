import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { FiSearch, FiFilter, FiPlay, FiClock, FiUsers } from 'react-icons/fi';
import { coursesAPI } from '../../services/api';
import './Student.css';

const CourseList = () => {
  const [courses, setCourses] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchParams, setSearchParams] = useSearchParams();
  const [filters, setFilters] = useState({
    search: searchParams.get('search') || '',
    category: searchParams.get('category') || '',
    level: searchParams.get('level') || '',
  });

  useEffect(() => {
    fetchCourses();
    fetchCategories();
  }, [searchParams]);

  const fetchCourses = async () => {
    try {
      const params = {
        search: searchParams.get('search') || undefined,
        category: searchParams.get('category') || undefined,
        level: searchParams.get('level') || undefined,
        status: 'published',
      };
      const response = await coursesAPI.list(params);
      setCourses(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching courses:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await coursesAPI.categories();
      setCategories(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    updateFilters();
  };

  const updateFilters = () => {
    const params = new URLSearchParams();
    if (filters.search) params.set('search', filters.search);
    if (filters.category) params.set('category', filters.category);
    if (filters.level) params.set('level', filters.level);
    setSearchParams(params);
  };

  const clearFilters = () => {
    setFilters({ search: '', category: '', level: '' });
    setSearchParams({});
  };

  return (
    <div className="courses-page">
      <div className="page-header">
        <h1>Explore Courses</h1>
        <p>Discover new skills and advance your career</p>
      </div>

      {/* Search and Filters */}
      <div className="filters-section">
        <form onSubmit={handleSearch} className="search-form">
          <div className="search-input-wrapper">
            <FiSearch className="search-icon" />
            <input
              type="text"
              className="input search-input"
              placeholder="Search courses..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            />
          </div>
          <button type="submit" className="btn btn-primary">Search</button>
        </form>

        <div className="filter-controls">
          <select
            className="input filter-select"
            value={filters.category}
            onChange={(e) => {
              setFilters({ ...filters, category: e.target.value });
              setTimeout(updateFilters, 0);
            }}
          >
            <option value="">All Categories</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>{cat.name}</option>
            ))}
          </select>

          <select
            className="input filter-select"
            value={filters.level}
            onChange={(e) => {
              setFilters({ ...filters, level: e.target.value });
              setTimeout(updateFilters, 0);
            }}
          >
            <option value="">All Levels</option>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>

          {(filters.search || filters.category || filters.level) && (
            <button className="btn btn-outline" onClick={clearFilters}>
              Clear Filters
            </button>
          )}
        </div>
      </div>

      {/* Course Grid */}
      {loading ? (
        <div className="page-loading">Loading courses...</div>
      ) : courses.length === 0 ? (
        <div className="empty-state">
          <FiFilter size={48} />
          <h3>No courses found</h3>
          <p>Try adjusting your search or filters</p>
        </div>
      ) : (
        <div className="courses-grid large">
          {courses.map((course) => (
            <div key={course.id} className="course-card">
              <div className="course-thumbnail">
                {course.thumbnail ? (
                  <img src={course.thumbnail} alt={course.title} />
                ) : (
                  <div className="thumbnail-placeholder">
                    <FiPlay size={40} />
                  </div>
                )}
                <span className={`badge badge-${course.level}`}>{course.level}</span>
              </div>
              <div className="course-info">
                <span className="course-category">{course.category_name}</span>
                <h3>{course.title}</h3>
                <p className="course-description">{course.short_description}</p>
                <div className="course-meta">
                  <span><FiPlay size={14} /> {course.total_videos} videos</span>
                  <span><FiClock size={14} /> {course.duration_hours}h</span>
                  <span><FiUsers size={14} /> {course.enrolled_students_count}</span>
                </div>
                <div className="course-footer">
                  <span className="instructor">By {course.instructor_name}</span>
                  <Link to={`/courses/${course.slug}`} className="btn btn-primary btn-sm">
                    View Course
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CourseList;
