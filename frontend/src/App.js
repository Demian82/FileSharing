import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');

  // Store file list status
  const [fileList, setFileList] = useState([])

  const detectOS = () => {
    const userAgent = window.navigator.userAgent.toLowerCase();
    if (userAgent.indexOf("windows") !== -1) return "windows";
    if (userAgent.indexOf("mac") !== -1 ) return "mac";
    return "linux";
  };

  const fetchFiles = async () => {
    try {
      const serverIp = window.location.hostname;
      const response = await axios.get(`http://${serverIp}:8000/files`);
      setFileList(response.data.files);
    } catch (error) {
      console.error("Error fatching files:", error);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

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
    formData.append('sender_os', detectOS()); // Specify sender OS

    try {
      setUploadStatus('Uploading...');

      const serverIp = window.location.hostname;
      const apiUrl = `http://${serverIp}:8000/upload`;


      const response = await axios.post(apiUrl, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setUploadStatus(`Successfully uploaded: ${response.data.file}`);

      // initialize file list after upload success
      fetchFiles();
      setFile(null); // initialize selected files
    } catch (error) {
      console.error(error);
      setUploadStatus('Error uploading file.');
    }
  };

  // func processing file download
  const handleDownload = (filename) => {
    const serverIp = window.location.hostname;
    // file download to open new browser window
    window.open(`http://${serverIp}:8000/download/${filename}`, `_blank`)
  };

  // func processing file delete
  const handleDelete = async (filename) => {
    // block delete from mistake
    if (!window.confirm(`Are you sure you want to delete '${filename}'?`)) {
      return;
    }

    try {
      const serverIp = window.location.hostname;
      // send DELETE request in filename encoded
      await axios.delete(`http://${serverIp}:8000/files/${encodeURIComponent(filename)}`);

      // renew page to call file list what fixed
      fetchFiles();
    } catch (error) {
      console.error("Error deleting file:", error);
      alert("Failed to delete the file.");
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
          </button>

          {uploadStatus && <p className="status-msg">{uploadStatus}</p>}

          <hr style={{ width: '80%', margin: '30px 0' }} />

          <h2>Shared Files</h2>
          <div className="file-list-section">
            {fileList.length === 0 ? (
              <p>No files uploaded yet.</p>
            ) : (
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {fileList.map((filename, index) => (
                  <li key={index} style={{ margin: '10px 0', padding: '10px', border: '1px solid #ccc', borderRadius: '5px' }}>
                    <span style={{ marginRight: '15px' }}>{filename}</span>
                    <button onClick={() => handleDownload(filename)} style={{ padding: '5px 10px', cursor: 'pointer' }}>
                      Download
                    </button>
                    <button onClick={() => handleDelete(filename)} 
                    style={{ padding: '5px 10px', cursor: 'pointer', backgroundColor: '#ff4d4d', color: 'white', border: 'none', borderRadius: '3px' }}>
                      Delete
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

      </header>
    </div>
  );
}

export default App;