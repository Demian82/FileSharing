import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');

  // Call when selecting a file
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  // Call file transfer
  const handleUpload = async () => {
    if (!file) {
      setUploadStatus('Please select a file to upload.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('sender_os', 'linux'); // Specify sender OS

    try {
      setUploadStatus('Uploading...');
      const response = await axios.post("http://localhost:8000/upload", formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setUploadStatus(`Successfully uploaded: ${response.data.file}`);
    } catch (error) {
      console.error(error);
      setUploadStatus('Error uploading file.');
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Local File Share</h1>

        <div className="upload-section"
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            setFile(e.dataTransfer.files[0]);
          }}>
            <p>Drag & drop a file here or click to select one</p>
            <input type="file" onChange={handleFileChange} />
            {file && <p>Selected file: <strong>{file.name}</strong></p>}
          </div>

          <button className="send-btn" onClick={handleUpload}>
            Send File to Ubuntu Server
          </button>"

          {uploadStatus && <p className="status-msg">{uploadStatus}</p>}
      </header>
    </div>
  );
}

export default App;