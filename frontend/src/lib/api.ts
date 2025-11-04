const BASE_URL = "http://localhost:8080" // TODO move to env

export const api = async (endpoint: string, options?: RequestInit) => {
    console.log(`API Request: ${endpoint}`, options);
    const res = await fetch(`${BASE_URL}${endpoint}`, {
        headers: {
            "Content-Type": "application/json",
        },
        ...options,
    });

    if (!res.ok) {
        throw new Error(`API error: ${res.statusText}`);
    }

    return res;
}