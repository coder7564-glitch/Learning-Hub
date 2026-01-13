import React, { useState, useEffect } from 'react';
import { FiAward, FiDownload, FiShare2 } from 'react-icons/fi';
import { toast } from 'react-toastify';
import { progressAPI } from '../../services/api';
import './Student.css';

const Certificates = () => {
  const [certificates, setCertificates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCertificates();
  }, []);

  const fetchCertificates = async () => {
    try {
      const response = await progressAPI.myCertificates();
      setCertificates(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching certificates:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleShare = (certificate) => {
    const url = `${window.location.origin}/verify/${certificate.certificate_number}`;
    navigator.clipboard.writeText(url);
    toast.success('Certificate link copied!');
  };

  if (loading) {
    return <div className="page-loading">Loading certificates...</div>;
  }

  return (
    <div className="certificates-page">
      <div className="page-header">
        <h1>My Certificates</h1>
        <p>Your achievements and accomplishments</p>
      </div>

      {certificates.length === 0 ? (
        <div className="empty-state">
          <FiAward size={48} />
          <h3>No certificates yet</h3>
          <p>Complete courses to earn certificates</p>
        </div>
      ) : (
        <div className="certificates-grid">
          {certificates.map((cert) => (
            <div key={cert.id} className="card certificate-card">
              <div className="certificate-badge">
                <FiAward size={48} />
              </div>
              <div className="certificate-info">
                <h3>{cert.course_title}</h3>
                <p className="certificate-number">Certificate #{cert.certificate_number}</p>
                <p className="certificate-date">
                  Issued on {new Date(cert.issued_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </p>
              </div>
              <div className="certificate-actions">
                {cert.pdf_url && (
                  <a 
                    href={cert.pdf_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="btn btn-primary"
                  >
                    <FiDownload /> Download
                  </a>
                )}
                <button 
                  className="btn btn-outline"
                  onClick={() => handleShare(cert)}
                >
                  <FiShare2 /> Share
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Certificates;
