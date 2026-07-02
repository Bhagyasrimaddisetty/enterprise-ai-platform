import { AppBar, Toolbar, Typography, Button, Box } from "@mui/material";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function NavBar() {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <AppBar position="static" color="primary" elevation={1}>
      <Toolbar sx={{ gap: 2 }}>
        <Typography variant="h6" component={Link} to="/" sx={{ flexGrow: 1, color: "inherit", textDecoration: "none" }}>
          AI Talent &amp; Knowledge Platform
        </Typography>
        {isAuthenticated && (
          <Box sx={{ display: "flex", gap: 2, alignItems: "center" }}>
            <Button color="inherit" component={Link} to="/dashboard">Dashboard</Button>
            <Button color="inherit" component={Link} to="/resumes">Resume Analyzer</Button>
            <Button color="inherit" component={Link} to="/documents">Document Q&amp;A</Button>
            <Button color="inherit" component={Link} to="/interview">Interview Prep</Button>
            <Typography variant="body2">{user?.fullName}</Typography>
            <Button color="inherit" onClick={handleLogout}>Logout</Button>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
}
