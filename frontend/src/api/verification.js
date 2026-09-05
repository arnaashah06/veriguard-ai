// src/api/verification.js

const getCandidateUrls = () => {
  const urls = [
    '', // Relative URL first: uses Vite proxy in dev or direct host in production
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'http://127.0.0.1:8001',
    'http://localhost:8001',
  ];
  if (typeof window !== 'undefined' && window.location.origin) {
    urls.push(window.location.origin);
  }
  return [...new Set(urls)];
};

export const verifyDocuments = async (documents, selfie = null) => {
  const formData = new FormData();
  
  // Support array of files or single file
  const docList = Array.isArray(documents) ? documents : [documents];
  docList.forEach((file) => {
    formData.append('files', file);
  });

  if (selfie) {
    formData.append('selfie', selfie);
  }

  // Use /verify-multiple endpoint for multi-doc, /verify for single doc
  const endpointPath = docList.length > 1 ? '/verify-multiple' : '/verify';

  let lastError = null;
  const baseUrls = getCandidateUrls();

  for (const baseUrl of baseUrls) {
    try {
      const targetUrl = baseUrl ? `${baseUrl}${endpointPath}` : endpointPath;
      const response = await fetch(targetUrl, {
        method: 'POST',
        body: formData,
      });

      // If a dev server like Vite responds with 404, skip to the actual backend URL
      if (response.status === 404) {
        continue;
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Verification request failed (${response.status})`);
      }

      return await response.json();
    } catch (err) {
      lastError = err;
      // If it's a real API rejection (like 400 Bad Request, file too large, invalid format), don't retry other ports
      if (
        err.message &&
        !err.message.includes('Failed to fetch') &&
        !err.message.includes('NetworkError') &&
        !err.message.includes('Network request failed') &&
        !err.message.includes('404')
      ) {
        throw err;
      }
    }
  }

  throw new Error(
    'Cannot connect to VeriGuard backend. Please ensure the backend is running on http://127.0.0.1:8000',
    { cause: lastError }
  );
};

// Backward-compatible export
export const verifyDocument = verifyDocuments;