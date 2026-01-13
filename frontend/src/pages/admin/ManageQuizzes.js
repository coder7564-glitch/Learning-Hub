import React, { useState, useEffect } from 'react';
import { FiPlus, FiEdit2, FiTrash2, FiSearch } from 'react-icons/fi';
import { toast } from 'react-toastify';
import { quizzesAPI } from '../../services/api';
import './Admin.css';

const ManageQuizzes = () => {
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => { fetchQuizzes(); }, []);

  const fetchQuizzes = async () => {
    try {
      const response = await quizzesAPI.list();
      setQuizzes(response.data.results || response.data);
    } catch (error) {
      toast.error('Failed to load quizzes');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Delete this quiz?')) {
      try {
        await quizzesAPI.delete(id);
        toast.success('Quiz deleted');
        fetchQuizzes();
      } catch (error) {
        toast.error('Failed to delete');
      }
    }
  };

  const filteredQuizzes = quizzes.filter(q =>
    q.title.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="manage-quizzes">
      <div className="page-header">
        <div>
          <h1>Manage Quizzes</h1>
          <p>Create and manage course assessments</p>
        </div>
        <button className="btn btn-primary"><FiPlus /> Create Quiz</button>
      </div>

      <div className="card">
        <div className="table-header">
          <div className="search-box">
            <FiSearch />
            <input type="text" placeholder="Search quizzes..." value={search}
              onChange={(e) => setSearch(e.target.value)} />
          </div>
        </div>

        {loading ? <div className="page-loading">Loading...</div> : (
          <table className="table">
            <thead>
              <tr>
                <th>Quiz</th>
                <th>Questions</th>
                <th>Pass Score</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredQuizzes.map((quiz) => (
                <tr key={quiz.id}>
                  <td><strong>{quiz.title}</strong></td>
                  <td>{quiz.total_questions}</td>
                  <td>{quiz.passing_score}%</td>
                  <td>
                    <span className={`badge ${quiz.is_published ? 'badge-success' : 'badge-warning'}`}>
                      {quiz.is_published ? 'Published' : 'Draft'}
                    </span>
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button className="btn-icon"><FiEdit2 /></button>
                      <button onClick={() => handleDelete(quiz.id)} className="btn-icon danger"><FiTrash2 /></button>
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

export default ManageQuizzes;
