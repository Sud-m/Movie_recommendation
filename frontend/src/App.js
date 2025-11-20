import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [message, setMessage] = useState('');
  const [data, setData] = useState('');

  // useEffect(() => {
  //   // Fetch from backend on component mount
  //   fetch('http://localhost:5000/')
  //     .then(res => res.json())
  //     .then(data => setMessage(data.message))
  //     .catch(err => console.error('Error:', err));
  // }, []);

  // const fetchData = () => {
  //   fetch('http://localhost:5000/api/data')
  //     .then(res => res.json())
  //     .then(data => setData(data.data))
  //     .catch(err => console.error('Error:', err));
  // };

  // const sendData = () => {
  //   fetch('http://localhost:5000/api/data', {
  //     method: 'POST',
  //     headers: {
  //       'Content-Type': 'application/json',
  //     },
  //     body: JSON.stringify({ test: 'Hello from React!' }),
  //   })
  //     .then(res => res.json())
  //     .then(data => console.log('Response:', data))
  //     .catch(err => console.error('Error:', err));
  // };

  return (
    <div>
      <h1>Hello World</h1>
    </div>
  );
}

export default App;

