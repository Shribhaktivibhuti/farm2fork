const API_BASE_URL = 'http://localhost:8000';

export interface LoginRequest {
  phone: string;
  otp: string;
}

export interface LoginResponse {
  success: boolean;
  token: string;
  farmer_id: string;
  farmer_name: string;
}

export const api = {
  login: async (phone: string, otp: string): Promise<LoginResponse> => {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ phone, otp }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Login failed');
    }

    return response.json();
  },
};
