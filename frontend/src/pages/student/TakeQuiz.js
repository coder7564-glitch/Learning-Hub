import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FiClock, FiCheckCircle, FiXCircle } from 'react-icons/fi';
import { toast } from 'react-toastify';
import { quizzesAPI } from '../../services/api';
import './Student.css';

const TakeQuiz = () => {
  const { slug, quizId } = useParams();
  const navigate = useNavigate();
  const [quiz, setQuiz] = useState(null);
  const [attempt, setAttempt] = useState(null);
  const [answers, setAnswers] = useState({});
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [timeLeft, setTimeLeft] = useState(null);

  useEffect(() => {
    startQuiz();
  }, [quizId]);

  useEffect(() => {
    if (timeLeft === null || timeLeft <= 0 || result) return;
    const timer = setInterval(() => setTimeLeft(t => t - 1), 1000);
    return () => clearInterval(timer);
  }, [timeLeft, result]);

  useEffect(() => {
    if (timeLeft === 0 && !result) {
      handleSubmit();
    }
  }, [timeLeft]);

  const startQuiz = async () => {
    try {
      const quizRes = await quizzesAPI.get(quizId);
      setQuiz(quizRes.data);

      const attemptRes = await quizzesAPI.start(quizId);
      setAttempt(attemptRes.data);

      if (quizRes.data.time_limit_minutes > 0) {
        setTimeLeft(quizRes.data.time_limit_minutes * 60);
      }
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to start quiz');
      navigate(`/courses/${slug}`);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSelect = (questionId, answerId, isMultiple = false) => {
    setAnswers(prev => {
      if (isMultiple) {
        const current = prev[questionId] || [];
        if (current.includes(answerId)) {
          return { ...prev, [questionId]: current.filter(id => id !== answerId) };
        }
        return { ...prev, [questionId]: [...current, answerId] };
      }
      return { ...prev, [questionId]: [answerId] };
    });
  };

  const handleTextAnswer = (questionId, text) => {
    setAnswers(prev => ({ ...prev, [questionId]: text }));
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const responses = Object.entries(answers).map(([questionId, answer]) => ({
        question_id: parseInt(questionId),
        selected_answer_ids: Array.isArray(answer) ? answer : [],
        text_response: typeof answer === 'string' ? answer : ''
      }));

      const response = await quizzesAPI.submit({
        attempt_id: attempt.id,
        responses
      });

      setResult(response.data);
      toast.success('Quiz submitted!');
    } catch (error) {
      toast.error('Failed to submit quiz');
    } finally {
      setSubmitting(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return <div className="page-loading">Loading quiz...</div>;
  }

  if (result) {
    return (
      <div className="quiz-result-page">
        <div className="card quiz-result">
          <div className={`result-icon ${result.passed ? 'passed' : 'failed'}`}>
            {result.passed ? <FiCheckCircle size={64} /> : <FiXCircle size={64} />}
          </div>
          <h1>{result.passed ? 'Congratulations!' : 'Keep Trying!'}</h1>
          <p className="result-message">
            {result.passed 
              ? 'You have successfully passed the quiz.' 
              : 'You did not pass this time. Review the material and try again.'}
          </p>
          <div className="result-score">
            <span className="score-value">{Math.round(result.score)}%</span>
            <span className="score-label">Your Score</span>
          </div>
          <div className="result-stats">
            <div className="result-stat">
              <span>Passing Score</span>
              <span>{quiz.passing_score}%</span>
            </div>
            <div className="result-stat">
              <span>Time Taken</span>
              <span>{Math.floor(result.time_taken_seconds / 60)} minutes</span>
            </div>
          </div>
          <div className="result-actions">
            <button onClick={() => navigate(`/courses/${slug}`)} className="btn btn-primary">
              Back to Course
            </button>
          </div>
        </div>
      </div>
    );
  }

  const question = quiz?.questions?.[currentQuestion];

  return (
    <div className="quiz-page">
      <div className="quiz-header">
        <h1>{quiz?.title}</h1>
        <div className="quiz-meta">
          <span>Question {currentQuestion + 1} of {quiz?.questions?.length}</span>
          {timeLeft !== null && (
            <span className={`timer ${timeLeft < 60 ? 'warning' : ''}`}>
              <FiClock /> {formatTime(timeLeft)}
            </span>
          )}
        </div>
      </div>

      <div className="quiz-progress">
        <div className="progress-bar">
          <div 
            className="progress-bar-fill" 
            style={{ width: `${((currentQuestion + 1) / quiz?.questions?.length) * 100}%` }}
          />
        </div>
      </div>

      {question && (
        <div className="card quiz-question">
          <h2>{question.question_text}</h2>

          <div className="answers-list">
            {question.question_type === 'short_answer' ? (
              <textarea
                className="input"
                placeholder="Type your answer..."
                value={answers[question.id] || ''}
                onChange={(e) => handleTextAnswer(question.id, e.target.value)}
                rows={4}
              />
            ) : (
              question.answers?.map((answer) => {
                const isSelected = (answers[question.id] || []).includes(answer.id);
                const isMultiple = question.question_type === 'multiple_select';

                return (
                  <label 
                    key={answer.id} 
                    className={`answer-option ${isSelected ? 'selected' : ''}`}
                  >
                    <input
                      type={isMultiple ? 'checkbox' : 'radio'}
                      name={`question-${question.id}`}
                      checked={isSelected}
                      onChange={() => handleAnswerSelect(question.id, answer.id, isMultiple)}
                    />
                    <span className="answer-text">{answer.answer_text}</span>
                  </label>
                );
              })
            )}
          </div>
        </div>
      )}

      <div className="quiz-navigation">
        <button
          className="btn btn-outline"
          onClick={() => setCurrentQuestion(c => c - 1)}
          disabled={currentQuestion === 0}
        >
          Previous
        </button>

        {currentQuestion < quiz?.questions?.length - 1 ? (
          <button
            className="btn btn-primary"
            onClick={() => setCurrentQuestion(c => c + 1)}
          >
            Next
          </button>
        ) : (
          <button
            className="btn btn-success"
            onClick={handleSubmit}
            disabled={submitting}
          >
            {submitting ? 'Submitting...' : 'Submit Quiz'}
          </button>
        )}
      </div>
    </div>
  );
};

export default TakeQuiz;
