import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FiSave, FiArrowLeft } from 'react-icons/fi';
import { toast } from 'react-toastify';
import { coursesAPI } from '../../services/api';
import './Admin.css';

const CourseForm = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const isEdit = Boolean(slug);

  const [formData, setFormData] = useState({
    title: '', slug: '', description: '', short_description: '',
    thumbnail: '', category: '', level: 'beginner', status: 'draft',
    duration_hours: 0, is_featured: false, prerequisites: '', learning_objectives: ''
  });
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchCategories();
    if (isEdit) fetchCourse();
  }, [slug]);

  const fetchCategories = async () => {
    try {
      const response = await coursesAPI.categories();
      setCategories(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchCourse = async () => {
    try {
      const response = await coursesAPI.get(slug);
      setFormData({
        title: response.data.title || '',
        slug: response.data.slug || '',
        description: response.data.description || '',
        short_description: response.data.short_description || '',
        thumbnail: response.data.thumbnail || '',
        category: response.data.category?.id || '',
        level: response.data.level || 'beginner',
        status: response.data.status || 'draft',
        duration_hours: response.data.duration_hours || 0,
        is_featured: response.data.is_featured || false,
        prerequisites: response.data.prerequisites || '',
        learning_objectives: response.data.learning_objectives || ''
      });
    } catch (error) {
      toast.error('Course not found');
      navigate('/admin/courses');
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const generateSlug = () => {
    const slug = formData.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
    setFormData(prev => ({ ...prev, slug }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (isEdit) {
        await coursesAPI.update(slug, formData);
        toast.success('Course updated!');
      } else {
        await coursesAPI.create(formData);
        toast.success('Course created!');
      }
      navigate('/admin/courses');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save course');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="course-form-page">
      <div className="page-header">
        <button onClick={() => navigate('/admin/courses')} className="btn btn-outline">
          <FiArrowLeft /> Back
        </button>
        <h1>{isEdit ? 'Edit Course' : 'Create Course'}</h1>
      </div>

      <form onSubmit={handleSubmit} className="card course-form">
        <div className="form-grid">
          <div className="form-group">
            <label className="label">Title *</label>
            <input type="text" name="title" className="input" value={formData.title}
              onChange={handleChange} onBlur={!isEdit ? generateSlug : undefined} required />
          </div>
          <div className="form-group">
            <label className="label">Slug *</label>
            <input type="text" name="slug" className="input" value={formData.slug}
              onChange={handleChange} required />
          </div>
          <div className="form-group full-width">
            <label className="label">Short Description</label>
            <input type="text" name="short_description" className="input"
              value={formData.short_description} onChange={handleChange} maxLength={300} />
          </div>
          <div className="form-group full-width">
            <label className="label">Description *</label>
            <textarea name="description" className="input" value={formData.description}
              onChange={handleChange} rows={4} required />
          </div>
          <div className="form-group">
            <label className="label">Category</label>
            <select name="category" className="input" value={formData.category} onChange={handleChange}>
              <option value="">Select category</option>
              {categories.map(cat => <option key={cat.id} value={cat.id}>{cat.name}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="label">Level</label>
            <select name="level" className="input" value={formData.level} onChange={handleChange}>
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>
          <div className="form-group">
            <label className="label">Status</label>
            <select name="status" className="input" value={formData.status} onChange={handleChange}>
              <option value="draft">Draft</option>
              <option value="published">Published</option>
              <option value="archived">Archived</option>
            </select>
          </div>
          <div className="form-group">
            <label className="label">Duration (hours)</label>
            <input type="number" name="duration_hours" className="input"
              value={formData.duration_hours} onChange={handleChange} min={0} />
          </div>
          <div className="form-group full-width">
            <label className="label">Thumbnail URL</label>
            <input type="url" name="thumbnail" className="input"
              value={formData.thumbnail} onChange={handleChange} />
          </div>
          <div className="form-group full-width">
            <label className="label">Learning Objectives</label>
            <textarea name="learning_objectives" className="input"
              value={formData.learning_objectives} onChange={handleChange} rows={3}
              placeholder="One objective per line" />
          </div>
          <div className="form-group full-width">
            <label className="label">Prerequisites</label>
            <textarea name="prerequisites" className="input"
              value={formData.prerequisites} onChange={handleChange} rows={2} />
          </div>
          <div className="form-group">
            <label className="checkbox-label">
              <input type="checkbox" name="is_featured" checked={formData.is_featured}
                onChange={handleChange} />
              Featured Course
            </label>
          </div>
        </div>
        <div className="form-actions">
          <button type="button" onClick={() => navigate('/admin/courses')} className="btn btn-outline">
            Cancel
          </button>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            <FiSave /> {loading ? 'Saving...' : 'Save Course'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CourseForm;
