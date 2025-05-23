import './App.css'
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SignOut from './pages/SignOut/SignOut';
import SignIn from './pages/SignIn/SignIn';
import Dashboard from './pages/Dashboard/Dashboard';


function App() {
  return (
    <>
       <Router>
            <Routes>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/signout" element={<SignOut />} />
                <Route path="/signin" element={<SignIn />} />
            </Routes>
        </Router>
    </>
  )
}

export default App;
