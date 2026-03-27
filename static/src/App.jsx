import React from "react";
import { Routes, Route } from "react-router-dom";
import PageNotFound from "./error/PageNotFound";
import Home from "./pages/Home";
import Login from "./pages/login";
import Register from "./pages/register";

const App = () => {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="*" element={<PageNotFound />} />
    </Routes>
  );
};

export default App;