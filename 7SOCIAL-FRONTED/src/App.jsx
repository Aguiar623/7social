import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Feed } from "./pages/Feed";
import  Navbar  from "./pages/Navbar";
import Home from "./pages/Home";
import { AuthProvider } from "./context/AuthContext";
import  Profile from "./pages/Profile";
import Chatbot from "./components/ChatbotWidget";
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';


function App() {
  return (
    <AuthProvider>
      <Router>
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/feed" element={<Feed />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/chatbot" element={<Chatbot />} />
        </Routes>
      </Router>
      <ToastContainer />
    </AuthProvider>
  );
}

export default App;
