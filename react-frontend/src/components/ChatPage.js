import React, { useState } from 'react';
import axios from 'axios';
import CircularProgress from '@mui/material/CircularProgress';
import './PageStyle.css';
import { SERVER_URL } from '../Constants';
import { useNavigate } from "react-router-dom";

function ChatPage({setSnackbarOpen, setSnackbarMessage, setSnackbarSeverity}) {
    const [question, setQuestion] = useState('');
    const [loading, setLoading] = useState(false);
    const [response, setResponse] = useState(null);
    const navigate = useNavigate();

    const sendQuestion = async () => {
         if (!question.trim()) {
            console.log('Question is empty');
            setSnackbarMessage('Please enter a question!');
            setSnackbarSeverity('warning');
            setSnackbarOpen(true);
            return;
        }
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

    return (
        <div className="chat-container">
            <h2>Chat PDF</h2>
            <div className="input-container">
                <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
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
                    Upload New File
                </button>
            </div>
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