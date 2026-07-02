import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "../context/AuthContext";
import ProtectedRoute from "../components/ProtectedRoute";

function renderWithRoute(initialPath) {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<div>Login Page</div>} />
          <Route path="/dashboard" element={<ProtectedRoute><div>Dashboard Content</div></ProtectedRoute>} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>
  );
}

describe("ProtectedRoute", () => {
  it("redirects to /login when not authenticated", () => {
    localStorage.clear();
    renderWithRoute("/dashboard");
    expect(screen.getByText("Login Page")).toBeInTheDocument();
  });

  it("renders protected content when authenticated", () => {
    localStorage.setItem("user", JSON.stringify({ id: 1, email: "sri@example.com", fullName: "Sri" }));
    localStorage.setItem("token", "fake-token");
    renderWithRoute("/dashboard");
    expect(screen.getByText("Dashboard Content")).toBeInTheDocument();
    localStorage.clear();
  });
});
