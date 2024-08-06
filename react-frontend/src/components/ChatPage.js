import React, { useState, useEffect } from 'react';
import axios from 'axios';
import CircularProgress from '@mui/material/CircularProgress';
import './PageStyle.css';
import { SERVER_URL } from '../Constants';
import { useNavigate } from "react-router-dom";

function ChatPage({ setSnackbarOpen, setSnackbarMessage, setSnackbarSeverity }) {
    const [question, setQuestion] = useState('');
    const [loading, setLoading] = useState(false);
    const [response, setResponse] = useState(null);
    const [history, setHistory] = useState([]);
    const [isDropdownVisible, setIsDropdownVisible] = useState(false);
    const navigate = useNavigate();

    const handleInputChange = (e) => {
        setQuestion(e.target.value);
        setIsDropdownVisible(e.target.value.length > 0);
    };

    useEffect(() => {
        const savedHistory = localStorage.getItem('inputHistory');
        if (savedHistory) {
            setHistory(JSON.parse(savedHistory));
        }
    }, []);

    useEffect(() => {
        localStorage.setItem('inputHistory', JSON.stringify(history));
    }, [history]);

    const sendQuestion = async () => {
        if (!question.trim()) {
            console.log('Question is empty');
            setSnackbarMessage('Please enter a question!');
            setSnackbarSeverity('warning');
            setSnackbarOpen(true);
            return;
        }
        if (question.trim()) {
            setHistory(prevHistory => [...prevHistory, question]);
          }
          setIsDropdownVisible(false);
        try {
            setLoading(true);
            const requestBody = { question: question };
            const response = await axios.post(SERVER_URL + '/ask/question', requestBody);
            setResponse(response.data)
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };

    const navigateHome = async () => {
        navigate('/upload');
    };

    const handleHistoryClick = (item) => {
        setQuestion(item);
        setIsDropdownVisible(false);
      };

    return (
        <div className="chat-container">
            <h2>QnA on the Content Provided</h2>
            <div className="input-container">
                <input
                    type="text"
                    value={question}
                    onChange={handleInputChange}
                    onFocus={() => setIsDropdownVisible(question.length > 0)}
                    onBlur={() => setTimeout(() => setIsDropdownVisible(false), 100)}
                    placeholder="Type your question..."
                    className="input-field"
                    onKeyDown={(e) => {
                        if (e.key === "Enter")
                            sendQuestion();
                    }}
                />
                <button onClick={sendQuestion} className="button">
                    Ask
                </button>
                <button onClick={navigateHome} className="button">
                    Provide New Context
                </button>
            </div>
            {isDropdownVisible && (
                <ul style={{
                    border: '2px solid #ccc',
                    width: '20%',
                    position: 'absolute',
                    listStyleType: 'none',
                    padding: '0',
                    margin: '0',
                    backgroundColor: '#fff',
                    maxHeight: '5%',
                    overflowY: 'auto',
                }}>
                    {history
                        .filter(item => item.toLowerCase().includes(question.toLowerCase()))
                        .map((item, index) => (
                            <li
                                key={index}
                                onMouseDown={() => handleHistoryClick(item)}
                                style={{ padding: '5px', cursor: 'pointer' }}
                            >
                                {item}
                            </li>
                        ))}
                </ul>
            )}
            {loading && (
                <div className="loading-indicator">
                    <CircularProgress />
                </div>
            )}
            <div className="chat-messages">
                {/* Display chat messages here */}
                {response && !loading && <div className="bot-message">{response.answer}</div>}
            </div>
        </div>
    );
}

export default ChatPage;