let token = "";
export function setToken(value) {
  token = value;
}
export class ApiError extends Error {
  constructor(message, status, errors = []) {
    super(message);
    this.status = status;
    this.errors = errors;
  }
}
export async function api(
  path,
  { method = "GET", body, key, blob = false } = {},
) {
  const headers = {};
  if (token) headers.Authorization = `Bearer ${token}`;
  if (key) headers["Idempotency-Key"] = key;
  if (body && !(body instanceof FormData))
    headers["Content-Type"] = "application/json";
  let response;
  try {
    response = await fetch("/api" + path, {
      method,
      headers,
      body:
        body instanceof FormData
          ? body
          : body
            ? JSON.stringify(body)
            : undefined,
      signal: AbortSignal.timeout(25000),
      cache: "no-store",
    });
  } catch {
    throw new ApiError(
      "Aloqa uzildi. Internetni tekshiring va qayta urinib ko‘ring.",
      0,
    );
  }
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new ApiError(
      typeof error.detail === "string"
        ? error.detail
        : "Amal bajarilmadi. Qayta urinib ko‘ring.",
      response.status,
      error.errors || [],
    );
  }
  return blob ? response.blob() : response.json();
}
