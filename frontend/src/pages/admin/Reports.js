import React, { useState, useEffect } from 'react';
import { FiDownload, FiTrendingUp, FiUsers, FiBook } from 'react-icons/fi';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { progressAPI } from '../../services/api';
import './Admin.css';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const Reports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchReports(); }, []);

  const fetchReports = async () => {
    try {
      const response = await progressAPI.studentReports();
      setReports(response.data || []);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const chartData = {
    labels: reports.slice(0, 10).map(r => r.user_name?.split(' ')[0] || 'User'),
    datasets: [{
      label: 'Course Progress (%)',
      data: reports.slice(0, 10).map(r => r.overall_progress || 0),
      backgroundColor: 'rgba(79, 70, 229, 0.8)',
    }]
  };

  const totalEnrolled = reports.reduce((sum, r) => sum + (r.courses_enrolled || 0), 0);
  const totalCompleted = reports.reduce((sum, r) => sum + (r.courses_completed || 0), 0);
  const avgScore = reports.length > 0 
    ? (reports.reduce((sum, r) => sum + (r.average_quiz_score || 0), 0) / reports.length).toFixed(1)
    : 0;

  if (loading) return <div className="page-loading">Loading reports...</div>;

  return (
    <div className="reports-page">
      <div className="page-header">
        <div>
          <h1>Reports & Analytics</h1>
          <p>Track student performance and course statistics</p>
        </div>
        <button className="btn btn-outline"><FiDownload /> Export</button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{backgroundColor: 'rgba(79, 70, 229, 0.1)'}}>
            <FiUsers color="#4F46E5" size={24} />
          </div>
          <div className="stat-info">
            <h3>{reports.length}</h3>
            <p>Total Students</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{backgroundColor: 'rgba(16, 185, 129, 0.1)'}}>
            <FiBook color="#10B981" size={24} />
          </div>
          <div className="stat-info">
            <h3>{totalEnrolled}</h3>
            <p>Enrollments</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{backgroundColor: 'rgba(245, 158, 11, 0.1)'}}>
            <FiTrendingUp color="#F59E0B" size={24} />
          </div>
          <div className="stat-info">
            <h3>{avgScore}%</h3>
            <p>Avg Quiz Score</p>
          </div>
        </div>
      </div>

      <div className="card">
        <h2>Student Progress Overview</h2>
        <div className="chart-container" style={{height: '300px'}}>
          <Bar data={chartData} options={{responsive: true, maintainAspectRatio: false}} />
        </div>
      </div>

      <div className="card">
        <h2>Detailed Report</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Student</th>
              <th>Enrolled</th>
              <th>Completed</th>
              <th>Quiz Score</th>
              <th>Certificates</th>
            </tr>
          </thead>
          <tbody>
            {reports.map((r) => (
              <tr key={r.user_id}>
                <td>{r.user_name}</td>
                <td>{r.courses_enrolled}</td>
                <td>{r.courses_completed}</td>
                <td>{r.average_quiz_score?.toFixed(1)}%</td>
                <td>{r.certificates_earned}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Reports;
