import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "../context/AuthContext";
import LoginPage from "../pages/LoginPage";
import { authApi } from "../api/endpoints";

vi.mock("../api/endpoints", () => ({
  authApi: {
    login: vi.fn(),
    register: vi.fn(),
    me: vi.fn(),
  },
}));

function renderLoginPage() {
  return render(
    <BrowserRouter>
      <AuthProvider>
        <LoginPage />
      </AuthProvider>
    </BrowserRouter>
  );
}

describe("LoginPage", () => {
  it("renders email and password fields", () => {
    renderLoginPage();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });

  it("calls authApi.login with entered credentials on submit", async () => {
    authApi.login.mockResolvedValue({
      data: { token: "fake-jwt", user: { id: 1, email: "sri@example.com", fullName: "Sri", role: "CANDIDATE" } },
    });

    renderLoginPage();

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: "sri@example.com" } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: "password123" } });
    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      expect(authApi.login).toHaveBeenCalledWith({ email: "sri@example.com", password: "password123" });
    });
  });

  it("shows an error message when login fails", async () => {
    authApi.login.mockRejectedValue({ response: { data: { message: "Invalid email or password" } } });

    renderLoginPage();

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: "sri@example.com" } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: "wrong" } });
    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(await screen.findByText(/invalid email or password/i)).toBeInTheDocument();
  });
});
