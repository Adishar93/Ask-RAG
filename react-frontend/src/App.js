import UploadPage from './components/UploadPage';
import ChatPage from './components/ChatPage';
import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Snackbar from '@mui/material/Snackbar';
import MuiAlert from '@mui/material/Alert';

function App() {
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('success');

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  return (
    <BrowserRouter>

      <Routes>
        <Route exact path="/" element={<ChatPage setSnackbarOpen={setSnackbarOpen} setSnackbarMessage={setSnackbarMessage} setSnackbarSeverity={setSnackbarSeverity}/>} />
        <Route exact path="/upload" element={<UploadPage setSnackbarOpen={setSnackbarOpen} setSnackbarMessage={setSnackbarMessage} setSnackbarSeverity={setSnackbarSeverity} />} />
      </Routes>

      <Snackbar open={snackbarOpen} autoHideDuration={3000} onClose={handleSnackbarClose}>
        <MuiAlert onClose={handleSnackbarClose} severity={snackbarSeverity} sx={{ width: '100%' }}>
          {snackbarMessage}
        </MuiAlert>
      </Snackbar>

    </BrowserRouter>

  );
}

export default App;