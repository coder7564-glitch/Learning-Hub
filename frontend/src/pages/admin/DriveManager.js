import React, { useState, useEffect } from 'react';
import { FiFolder, FiVideo, FiFile, FiSearch, FiRefreshCw, FiCheck } from 'react-icons/fi';
import { toast } from 'react-toastify';
import { driveAPI } from '../../services/api';
import './Admin.css';

const DriveManager = () => {
  const [connected, setConnected] = useState(false);
  const [files, setFiles] = useState([]);
  const [folders, setFolders] = useState([]);
  const [currentFolder, setCurrentFolder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => { checkConnection(); }, []);

  const checkConnection = async () => {
    try {
      const response = await driveAPI.status();
      setConnected(response.data.connected);
      if (response.data.connected) fetchFiles();
      else setLoading(false);
    } catch (error) {
      setLoading(false);
    }
  };

  const fetchFiles = async (folderId = null) => {
    setLoading(true);
    try {
      const [filesRes, foldersRes] = await Promise.all([
        driveAPI.listFiles({ folder_id: folderId, type: 'video' }),
        driveAPI.listFolders({ parent_id: folderId })
      ]);
      setFiles(filesRes.data.files || []);
      setFolders(foldersRes.data.files || []);
      setCurrentFolder(folderId);
    } catch (error) {
      toast.error('Failed to load files');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!search) return fetchFiles(currentFolder);
    setLoading(true);
    try {
      const response = await driveAPI.search({ q: search, type: 'video' });
      setFiles(response.data.files || []);
      setFolders([]);
    } catch (error) {
      toast.error('Search failed');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (file) => {
    const data = JSON.stringify({
      google_drive_file_id: file.id,
      google_drive_url: file.embed_url,
      thumbnail_url: file.thumbnail_url,
      duration_minutes: file.duration_minutes || 0
    });
    navigator.clipboard.writeText(data);
    toast.success('Video data copied!');
  };

  if (!connected) {
    return (
      <div className="drive-manager">
        <div className="page-header">
          <h1>Google Drive</h1>
          <p>Manage your course videos</p>
        </div>
        <div className="card empty-state">
          <FiFolder size={48} />
          <h3>Connect Google Drive</h3>
          <p>Sign in with Google to access your Drive files</p>
          <a href="/auth/login/google-oauth2/?next=/admin/drive" className="btn btn-primary">
            Connect Google Drive
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="drive-manager">
      <div className="page-header">
        <div>
          <h1>Google Drive</h1>
          <p>Select videos to add to courses</p>
        </div>
        <button onClick={() => fetchFiles(currentFolder)} className="btn btn-outline">
          <FiRefreshCw /> Refresh
        </button>
      </div>

      <div className="card">
        <div className="table-header">
          <div className="search-box">
            <FiSearch />
            <input type="text" placeholder="Search videos..." value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()} />
          </div>
          {currentFolder && (
            <button onClick={() => fetchFiles(null)} className="btn btn-outline">
              Back to Root
            </button>
          )}
        </div>

        {loading ? <div className="page-loading">Loading...</div> : (
          <div className="drive-files">
            {folders.map((folder) => (
              <div key={folder.id} className="drive-item folder" onClick={() => fetchFiles(folder.id)}>
                <FiFolder size={24} />
                <span>{folder.name}</span>
              </div>
            ))}
            {files.map((file) => (
              <div key={file.id} className="drive-item">
                <div className="file-preview">
                  {file.thumbnail_url ? (
                    <img src={file.thumbnail_url} alt={file.name} />
                  ) : (
                    <FiVideo size={24} />
                  )}
                </div>
                <div className="file-info">
                  <strong>{file.name}</strong>
                  <span>{file.duration_minutes ? `${file.duration_minutes} min` : 'Video'}</span>
                </div>
                <button onClick={() => copyToClipboard(file)} className="btn btn-sm btn-primary">
                  <FiCheck /> Select
                </button>
              </div>
            ))}
            {files.length === 0 && folders.length === 0 && (
              <div className="empty-state">No files found</div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DriveManager;
