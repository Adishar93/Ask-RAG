import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from "react-router-dom";
import { SERVER_URL } from '../Constants';

function UploadPage({ history }) {
    const [selectedFile, setSelectedFile] = useState(null);
    const navigate = useNavigate();
    const handleFileChange = (e) => {
        setSelectedFile(e.target.files[0]);
    };

    const handleUpload = async () => {
        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const response = await axios.post(SERVER_URL + '/upload/process/pdf', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            console.log(response.text);
            navigate('/chat');
        } catch (error) {
            console.error('Error uploading PDF:', error);
        }
    };

    return (
        <div>
            <h1>Upload PDF</h1>
            <input type="file" onChange={handleFileChange} />
            <button onClick={handleUpload}>Upload</button>
        </div>
    );
}

export default UploadPage;