import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FiBook, FiUsers, FiFileText, FiTrendingUp, FiPlus } from 'react-icons/fi';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';
import { coursesAPI, studentsAPI, progressAPI } from '../../services/api';
import './Admin.css';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

const AdminDashboard = () => {
  const [stats, setStats] = useState({
    totalCourses: 0,
    totalStudents: 0,
    totalEnrollments: 0,
    completionRate: 0
  });
  const [recentStudents, setRecentStudents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [coursesRes, studentsRes, reportsRes] = await Promise.all([
        coursesAPI.list({ status: 'published' }),
        studentsAPI.list({ page_size: 5 }),
        progressAPI.studentReports()
      ]);

      const courses = coursesRes.data.results || coursesRes.data;
      const students = studentsRes.data.results || studentsRes.data;
      const reports = reportsRes.data || [];

      const totalEnrollments = reports.reduce((sum, r) => sum + r.courses_enrolled, 0);
      const totalCompleted = reports.reduce((sum, r) => sum + r.courses_completed, 0);

      setStats({
        totalCourses: courses.length,
        totalStudents: students.length,
        totalEnrollments,
        completionRate: totalEnrollments > 0 
          ? Math.round((totalCompleted / totalEnrollments) * 100) 
          : 0
      });

      setRecentStudents(students.slice(0, 5));
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const completionData = {
    labels: ['Completed', 'In Progress'],
    datasets: [{
      data: [stats.completionRate, 100 - stats.completionRate],
      backgroundColor: ['#10B981', '#E5E7EB'],
      borderWidth: 0
    }]
  };

  if (loading) {
    return <div className="page-loading">Loading dashboard...</div>;
  }

  return (
    <div className="admin-dashboard">
      <div className="page-header">
        <div>
          <h1>Admin Dashboard</h1>
          <p>Overview of your learning management system</p>
        </div>
        <Link to="/admin/courses/new" className="btn btn-primary">
          <FiPlus /> Add Course
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ backgroundColor: 'rgba(79, 70, 229, 0.1)' }}>
            <FiBook color="#4F46E5" size={24} />
          </div>
          <div className="stat-info">
            <h3>{stats.totalCourses}</h3>
            <p>Total Courses</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ backgroundColor: 'rgba(16, 185, 129, 0.1)' }}>
            <FiUsers color="#10B981" size={24} />
          </div>
          <div className="stat-info">
            <h3>{stats.totalStudents}</h3>
            <p>Students</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ backgroundColor: 'rgba(245, 158, 11, 0.1)' }}>
            <FiFileText color="#F59E0B" size={24} />
          </div>
          <div className="stat-info">
            <h3>{stats.totalEnrollments}</h3>
            <p>Enrollments</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ backgroundColor: 'rgba(59, 130, 246, 0.1)' }}>
            <FiTrendingUp color="#3B82F6" size={24} />
          </div>
          <div className="stat-info">
            <h3>{stats.completionRate}%</h3>
            <p>Completion Rate</p>
          </div>
        </div>
      </div>

      <div className="dashboard-grid">
        {/* Recent Students */}
        <div className="card">
          <div className="card-header">
            <h2>Recent Students</h2>
            <Link to="/admin/students" className="view-all">View All</Link>
          </div>
          <div className="students-list">
            {recentStudents.map((student) => (
              <div key={student.id} className="student-item">
                <img 
                  src={student.profile_picture || '/default-avatar.png'} 
                  alt={student.full_name}
                  className="avatar-sm"
                />
                <div className="student-info">
                  <span className="student-name">{student.full_name}</span>
                  <span className="student-email">{student.email}</span>
                </div>
                <span className="student-courses">
                  {student.courses_enrolled} courses
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Completion Chart */}
        <div className="card">
          <div className="card-header">
            <h2>Course Completion</h2>
          </div>
          <div className="chart-container">
            <Doughnut 
              data={completionData} 
              options={{
                cutout: '70%',
                plugins: {
                  legend: { position: 'bottom' }
                }
              }}
            />
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card quick-actions">
        <h2>Quick Actions</h2>
        <div className="actions-grid">
          <Link to="/admin/courses/new" className="action-card">
            <FiBook size={24} />
            <span>Create Course</span>
          </Link>
          <Link to="/admin/students" className="action-card">
            <FiUsers size={24} />
            <span>Manage Students</span>
          </Link>
          <Link to="/admin/quizzes" className="action-card">
            <FiFileText size={24} />
            <span>Create Quiz</span>
          </Link>
          <Link to="/admin/reports" className="action-card">
            <FiTrendingUp size={24} />
            <span>View Reports</span>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
