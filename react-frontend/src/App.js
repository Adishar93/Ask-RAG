import UploadPage from './components/UploadPage';
import ChatPage from './components/ChatPage';
import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Snackbar from '@mui/material/Snackbar';
import MuiAlert from '@mui/material/Alert';

function App() {
  const [snackbarOpen, setSnackbarOpen] = useState(false);

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  return (
    <BrowserRouter>

      <Routes>
        <Route exact path="/" element={<UploadPage setSnackbarOpen={setSnackbarOpen} />} />
        <Route exact path="/chat" element={<ChatPage />} />
      </Routes>

      <Snackbar open={snackbarOpen} autoHideDuration={3000} onClose={handleSnackbarClose}>
        <MuiAlert onClose={handleSnackbarClose} severity="success" sx={{ width: '100%' }}>
          File Uploaded and Processed Successfully!
        </MuiAlert>
      </Snackbar>

    </BrowserRouter>

  );
}

export default App;