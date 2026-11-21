/*
 * Same-origin is the default: the FastAPI deployment serves this frontend.
 * If you host the frontend separately, replace the empty string with your public API origin.
 * Example: window.CROPCARE_API_BASE = "https://your-api-service.onrender.com";
 */
window.CROPCARE_API_BASE = window.CROPCARE_API_BASE || "";
