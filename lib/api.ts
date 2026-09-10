const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";

async function request(endpoint: string) {
  const response = await fetch(
    `${API_URL}${endpoint}`,
    {
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error(
      `API request failed: ${endpoint}`
    );
  }

  return response.json();
}

export async function getDashboardStats() {
  return request("/api/dashboard");
}

export async function getOpenSignals() {
  return request("/api/signals");
}

export async function getTradeHistory() {
  return request("/api/trade-history");
}