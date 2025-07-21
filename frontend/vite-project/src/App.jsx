// src/App.jsx
import React, { useEffect, useState } from "react";
import "./App.css";
import Create_Blog from "./pages/Create_Blog/Create_Blog";
import Update_Blog from "./pages/Update_Blog/Update_Blog";
import { Routes, Route } from 'react-router-dom';


function App() {
  
    
  return (
   <Routes>
      <Route path="/create" element={<Create_Blog />} />
      <Route path="/update" element={<Update_Blog />} />
      {/* catch-all route */}
      <Route path="*" element={<Create_Blog />} />
    </Routes>
  );
}


export default App;
