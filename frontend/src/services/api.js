import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          });

          const { access } = response.data;
          localStorage.setItem('access_token', access);

          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (email, password) => api.post('/auth/login/', { email, password }),
  register: (data) => api.post('/auth/register/', data),
  googleAuth: (accessToken) => api.post('/auth/google/', { access_token: accessToken }),
  logout: (refreshToken) => api.post('/auth/logout/', { refresh: refreshToken }),
  getProfile: () => api.get('/auth/profile/'),
  updateProfile: (data) => api.patch('/auth/profile/', data),
  changePassword: (data) => api.post('/auth/change-password/', data),
};

// Courses API
export const coursesAPI = {
  list: (params) => api.get('/courses/', { params }),
  get: (slug) => api.get(`/courses/${slug}/`),
  create: (data) => api.post('/courses/', data),
  update: (slug, data) => api.patch(`/courses/${slug}/`, data),
  delete: (slug) => api.delete(`/courses/${slug}/`),
  featured: () => api.get('/courses/featured/'),
  enroll: (slug) => api.post(`/courses/${slug}/enroll/`),
  myCourses: () => api.get('/courses/my-courses/'),
  
  // Categories
  categories: () => api.get('/courses/categories/'),
  
  // Modules
  getModules: (courseSlug) => api.get(`/courses/${courseSlug}/modules/`),
  createModule: (data) => api.post(`/courses/${data.courseSlug}/modules/`, data),
  updateModule: (id, data) => api.patch(`/courses/modules/${id}/`, data),
  deleteModule: (id) => api.delete(`/courses/modules/${id}/`),
  
  // Videos
  createVideo: (data) => api.post(`/courses/modules/${data.module}/videos/`, data),
  updateVideo: (id, data) => api.patch(`/courses/videos/${id}/`, data),
  deleteVideo: (id) => api.delete(`/courses/videos/${id}/`),
  
  // Enrollments
  enrollments: (params) => api.get('/courses/enrollments/', { params }),
  bulkEnroll: (data) => api.post('/courses/enrollments/bulk/', data),
  markComplete: (enrollmentId) => api.post(`/courses/enrollments/${enrollmentId}/complete/`),
};

// Students API (Admin)
export const studentsAPI = {
  list: (params) => api.get('/auth/students/', { params }),
  get: (id) => api.get(`/auth/students/${id}/`),
  update: (id, data) => api.patch(`/auth/students/${id}/`, data),
  delete: (id) => api.delete(`/auth/students/${id}/`),
};

// Quizzes API
export const quizzesAPI = {
  list: (params) => api.get('/quizzes/', { params }),
  get: (id) => api.get(`/quizzes/${id}/`),
  create: (data) => api.post('/quizzes/', data),
  update: (id, data) => api.patch(`/quizzes/${id}/`, data),
  delete: (id) => api.delete(`/quizzes/${id}/`),
  
  // Questions
  getQuestions: (quizId) => api.get(`/quizzes/${quizId}/questions/`),
  createQuestion: (quizId, data) => api.post(`/quizzes/${quizId}/questions/`, data),
  updateQuestion: (id, data) => api.patch(`/quizzes/questions/${id}/`, data),
  deleteQuestion: (id) => api.delete(`/quizzes/questions/${id}/`),
  
  // Taking quizzes
  start: (quizId) => api.post('/quizzes/start/', { quiz_id: quizId }),
  submit: (data) => api.post('/quizzes/submit/', data),
  myAttempts: (params) => api.get('/quizzes/attempts/', { params }),
  getAttempt: (id) => api.get(`/quizzes/attempts/${id}/`),
  
  // Admin
  allAttempts: (params) => api.get('/quizzes/all-attempts/', { params }),
  statistics: (quizId) => api.get(`/quizzes/${quizId}/statistics/`),
};

// Progress API
export const progressAPI = {
  myProgress: () => api.get('/progress/my-progress/'),
  courseProgress: (slug) => api.get(`/progress/courses/${slug}/`),
  updateVideo: (data) => api.post('/progress/video/update/', data),
  videoProgress: (slug) => api.get(`/progress/courses/${slug}/videos/`),
  
  // Certificates
  myCertificates: () => api.get('/progress/certificates/'),
  issueCertificate: (slug) => api.post(`/progress/courses/${slug}/certificate/`),
  verifyCertificate: (number) => api.get(`/progress/certificates/${number}/`),
  
  // Admin reports
  studentReports: () => api.get('/progress/reports/students/'),
  courseReport: (slug) => api.get(`/progress/reports/courses/${slug}/`),
};

// Google Drive API
export const driveAPI = {
  status: () => api.get('/drive/status/'),
  listFiles: (params) => api.get('/drive/files/', { params }),
  listFolders: (params) => api.get('/drive/folders/', { params }),
  getFile: (fileId) => api.get(`/drive/files/${fileId}/`),
  search: (params) => api.get('/drive/search/', { params }),
  embedUrl: (fileId) => api.get(`/drive/embed/${fileId}/`),
};

export default api;
