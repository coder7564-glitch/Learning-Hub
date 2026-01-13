import React, { useState, useEffect } from 'react';
import { FiSearch, FiMail, FiUser } from 'react-icons/fi';
import { toast } from 'react-toastify';
import { studentsAPI } from '../../services/api';
import './Admin.css';

const ManageStudents = () => {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => { fetchStudents(); }, []);

  const fetchStudents = async () => {
    try {
      const response = await studentsAPI.list();
      setStudents(response.data.results || response.data);
    } catch (error) {
      toast.error('Failed to load students');
    } finally {
      setLoading(false);
    }
  };

  const filteredStudents = students.filter(s =>
    s.email.toLowerCase().includes(search.toLowerCase()) ||
    s.full_name?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="manage-students">
      <div className="page-header">
        <h1>Manage Students</h1>
        <p>View and manage student accounts</p>
      </div>

      <div className="card">
        <div className="table-header">
          <div className="search-box">
            <FiSearch />
            <input type="text" placeholder="Search students..." value={search}
              onChange={(e) => setSearch(e.target.value)} />
          </div>
        </div>

        {loading ? <div className="page-loading">Loading...</div> : (
          <table className="table">
            <thead>
              <tr>
                <th>Student</th>
                <th>Email</th>
                <th>Enrolled</th>
                <th>Progress</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {filteredStudents.map((student) => (
                <tr key={student.id}>
                  <td>
                    <div className="student-cell">
                      <img src={student.profile_picture || '/default-avatar.png'} alt="" className="avatar-sm" />
                      <span>{student.full_name}</span>
                    </div>
                  </td>
                  <td>{student.email}</td>
                  <td>{student.courses_enrolled || 0} courses</td>
                  <td>
                    <div className="progress-bar" style={{width: '100px'}}>
                      <div className="progress-bar-fill" style={{width: `${student.overall_progress || 0}%`}} />
                    </div>
                  </td>
                  <td>
                    <span className={`badge ${student.is_active ? 'badge-success' : 'badge-danger'}`}>
                      {student.is_active ? 'Active' : 'Inactive'}
                    </span>
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

export default ManageStudents;
