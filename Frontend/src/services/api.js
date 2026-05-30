const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    const message = errorBody.detail || "Request failed";
    throw new Error(message);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export function listProducts() {
  return request("/products?limit=50&offset=0");
}

export function createProduct(payload) {
  return request("/products", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function deleteProduct(id) {
  return request(`/products/${id}`, {
    method: "DELETE"
  });
}

export function listSuppliers() {
  return request("/suppliers?limit=50&offset=0");
}

export function createSupplier(payload) {
  return request("/suppliers", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function deleteSupplier(id) {
  return request(`/suppliers/${id}`, {
    method: "DELETE"
  });
}
