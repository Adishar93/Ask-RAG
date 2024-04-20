import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from "react-router-dom";
import { SERVER_URL } from '../Constants';
import CircularProgress from '@mui/material/CircularProgress';


function UploadPage({ setSnackbarOpen, setSnackbarMessage, setSnackbarSeverity }) {
    const [selectedFile, setSelectedFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const handleFileChange = (e) => {
        setSelectedFile(e.target.files[0]);
    };

    const handleUpload = async () => {
        const formData = new FormData();
        formData.append('file', selectedFile);
        setLoading(true);

        try {
            const response = await axios.post(SERVER_URL + '/upload/process/pdf', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            console.log(response.data.message);

            setLoading(false);
            setSnackbarMessage('File Uploaded and Processed Successfully!');
            setSnackbarSeverity('success');
            setSnackbarOpen(true);
            navigate('/');

        } catch (error) {
            console.error('Error uploading PDF:', error);
            setSnackbarMessage('Error uploading PDF. Please try again!');
            setSnackbarSeverity('error');
            setSnackbarOpen(true);
            setLoading(false)
        }
    };

    return (
        <div>
            <div className="upload-container"> {/* Apply common container styles */}
                <h2>Upload PDF</h2>
                <input type="file" onChange={handleFileChange} className="input-field" /> {/* Apply input field styles */}
                <button onClick={handleUpload} className="button">Upload</button> {/* Apply button styles */}
            </div>
            {loading && (
                <div className="loading-indicator-upload"> {/* Apply loading indicator styles */}
                    <CircularProgress />
                </div>
            )}
        </div>
    );
}

export default UploadPage;