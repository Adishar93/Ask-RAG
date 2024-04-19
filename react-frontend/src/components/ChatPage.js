import React, { useState } from 'react';
import axios from 'axios';
import CircularProgress from '@mui/material/CircularProgress';
import './PageStyle.css';
import { SERVER_URL } from '../Constants';
import { useNavigate } from "react-router-dom";

function ChatPage() {
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const [response, setResponse] = useState(null);
    const navigate = useNavigate();

    const sendMessage = async () => {
        try {
            setLoading(true);
            const requestBody = { question: message };
            const response = await axios.post(SERVER_URL + '/ask/question', requestBody);
            setResponse(response.data)
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };

    const navigateHome = async () => {
        navigate('/');
    };

    return (
        <div className="chat-container">
            <h2>Chat PDF</h2>
            <div className="input-container">
                <input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Type your question..."
                    className="input-field"
                />
                <button onClick={sendMessage} className="button">
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