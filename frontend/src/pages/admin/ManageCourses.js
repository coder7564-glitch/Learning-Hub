import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FiPlus, FiEdit2, FiTrash2, FiEye, FiSearch } from 'react-icons/fi';
import { toast } from 'react-toastify';
import { coursesAPI } from '../../services/api';
import './Admin.css';

const ManageCourses = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      const response = await coursesAPI.list();
      setCourses(response.data.results || response.data);
    } catch (error) {
      toast.error('Failed to load courses');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (slug) => {
    if (window.confirm('Are you sure you want to delete this course?')) {
      try {
        await coursesAPI.delete(slug);
        toast.success('Course deleted');
        fetchCourses();
      } catch (error) {
        toast.error('Failed to delete course');
      }
    }
  };

  const filteredCourses = courses.filter(course =>
    course.title.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="manage-courses">
      <div className="page-header">
        <div>
          <h1>Manage Courses</h1>
          <p>Create and manage your course content</p>
        </div>
        <Link to="/admin/courses/new" className="btn btn-primary">
          <FiPlus /> Add Course
        </Link>
      </div>

      <div className="card">
        <div className="table-header">
          <div className="search-box">
            <FiSearch />
            <input
              type="text"
              placeholder="Search courses..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>

        {loading ? (
          <div className="page-loading">Loading...</div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Course</th>
                <th>Category</th>
                <th>Status</th>
                <th>Students</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredCourses.map((course) => (
                <tr key={course.id}>
                  <td>
                    <div className="course-cell">
                      <strong>{course.title}</strong>
                      <span>{course.total_videos} videos</span>
                    </div>
                  </td>
                  <td>{course.category_name || '-'}</td>
                  <td>
                    <span className={`badge badge-${course.status}`}>
                      {course.status}
                    </span>
                  </td>
                  <td>{course.enrolled_students_count}</td>
                  <td>
                    <div className="action-buttons">
                      <Link to={`/courses/${course.slug}`} className="btn-icon" title="View">
                        <FiEye />
                      </Link>
                      <Link to={`/admin/courses/${course.slug}/edit`} className="btn-icon" title="Edit">
                        <FiEdit2 />
                      </Link>
                      <button onClick={() => handleDelete(course.slug)} className="btn-icon danger" title="Delete">
                        <FiTrash2 />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default ManageCourses;
