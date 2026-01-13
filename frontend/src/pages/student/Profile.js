import React, { useState } from 'react';
import { FiUser, FiMail, FiPhone, FiSave } from 'react-icons/fi';
import { toast } from 'react-toastify';
import { useAuth } from '../../context/AuthContext';
import './Student.css';

const Profile = () => {
  const { user, updateProfile } = useAuth();
  const [formData, setFormData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    bio: user?.bio || '',
    phone_number: user?.phone_number || '',
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const result = await updateProfile(formData);
    
    if (result.success) {
      toast.success('Profile updated successfully!');
    } else {
      toast.error('Failed to update profile');
    }
    
    setLoading(false);
  };

  return (
    <div className="profile-page">
      <div className="page-header">
        <h1>My Profile</h1>
        <p>Manage your account settings</p>
      </div>

      <div className="profile-content">
        <div className="card profile-card">
          <div className="profile-header">
            <div className="profile-avatar">
              {user?.profile_picture ? (
                <img src={user.profile_picture} alt={user.full_name} />
              ) : (
                <div className="avatar-placeholder">
                  <FiUser size={40} />
                </div>
              )}
            </div>
            <div className="profile-info">
              <h2>{user?.full_name}</h2>
              <p className="profile-email">
                <FiMail /> {user?.email}
              </p>
              <span className="badge badge-primary">{user?.role}</span>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="profile-form">
            <div className="form-row">
              <div className="form-group">
                <label className="label">First Name</label>
                <input
                  type="text"
                  name="first_name"
                  className="input"
                  value={formData.first_name}
                  onChange={handleChange}
                />
              </div>
              <div className="form-group">
                <label className="label">Last Name</label>
                <input
                  type="text"
                  name="last_name"
                  className="input"
                  value={formData.last_name}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="form-group">
              <label className="label">Phone Number</label>
              <input
                type="tel"
                name="phone_number"
                className="input"
                value={formData.phone_number}
                onChange={handleChange}
                placeholder="Enter your phone number"
              />
            </div>

            <div className="form-group">
              <label className="label">Bio</label>
              <textarea
                name="bio"
                className="input"
                value={formData.bio}
                onChange={handleChange}
                placeholder="Tell us about yourself..."
                rows={4}
              />
            </div>

            <button type="submit" className="btn btn-primary" disabled={loading}>
              <FiSave /> {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </form>
        </div>

        <div className="card account-info">
          <h3>Account Information</h3>
          <div className="info-list">
            <div className="info-item">
              <span className="info-label">Email</span>
              <span className="info-value">{user?.email}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Role</span>
              <span className="info-value">{user?.role}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Member Since</span>
              <span className="info-value">
                {new Date(user?.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
