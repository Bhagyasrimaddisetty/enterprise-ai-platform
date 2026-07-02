import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider, createTheme, CssBaseline } from "@mui/material";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import NavBar from "./components/NavBar";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import ResumeAnalyzerPage from "./pages/ResumeAnalyzerPage";
import DocumentQAPage from "./pages/DocumentQAPage";
import InterviewPrepPage from "./pages/InterviewPrepPage";

const theme = createTheme({
  palette: {
    primary: { main: "#1a237e" },
    secondary: { main: "#00897b" },
  },
});

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <BrowserRouter>
          <NavBar />
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
            <Route path="/resumes" element={<ProtectedRoute><ResumeAnalyzerPage /></ProtectedRoute>} />
            <Route path="/documents" element={<ProtectedRoute><DocumentQAPage /></ProtectedRoute>} />
            <Route path="/interview" element={<ProtectedRoute><InterviewPrepPage /></ProtectedRoute>} />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}
