const API_BASE_URL = "https://url-shortener-es94.onrender.com";

/**
 * Sends a POST request to shorten a URL.
 * @param {string} longUrl The URL to shorten.
 * @returns {Promise<object>} The JSON response containing the shortened URL details.
 */
async function shortenUrl(longUrl) {
    const response = await fetch(`${API_BASE_URL}/shorten`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ long_url: longUrl })
    });
    
    if (!response.ok) {
        let errMsg = `Error shortening URL: ${response.status} ${response.statusText}`;
        try {
            const errorData = await response.json();
            if (errorData && errorData.detail) {
                errMsg = typeof errorData.detail === "string" ? errorData.detail : JSON.stringify(errorData.detail);
            }
        } catch (_) {
            // Fallback if JSON parsing fails
        }
        throw new Error(errMsg);
    }
    
    return await response.json();
}

/**
 * Retrieves analytics for a short code.
 * @param {string} shortCode The short code to lookup.
 * @returns {Promise<object>} The JSON response containing analytics data.
 */
async function getAnalytics(shortCode) {
    const response = await fetch(`${API_BASE_URL}/analytics/${shortCode}`);
    
    if (!response.ok) {
        let errMsg = `Error retrieving analytics: ${response.status} ${response.statusText}`;
        try {
            const errorData = await response.json();
            if (errorData && errorData.detail) {
                errMsg = typeof errorData.detail === "string" ? errorData.detail : JSON.stringify(errorData.detail);
            }
        } catch (_) {
            // Fallback if JSON parsing fails
        }
        throw new Error(errMsg);
    }
    
    return await response.json();
}

/**
 * Deletes a shortened URL by its short code.
 * @param {string} shortCode The short code to delete.
 * @returns {Promise<void>} Resolves if successful.
 */
async function deleteUrl(shortCode) {
    const response = await fetch(`${API_BASE_URL}/${shortCode}`, {
        method: "DELETE"
    });
    
    if (!response.ok) {
        let errMsg = `Error deleting URL: ${response.status} ${response.statusText}`;
        try {
            const errorData = await response.json();
            if (errorData && errorData.detail) {
                errMsg = typeof errorData.detail === "string" ? errorData.detail : JSON.stringify(errorData.detail);
            }
        } catch (_) {
            // Fallback if JSON parsing fails
        }
        throw new Error(errMsg);
    }
}

// DOM Setup
document.addEventListener("DOMContentLoaded", () => {
    const longUrlInput = document.getElementById("long-url");
    const shortenBtn = document.getElementById("shorten-btn");
    const resultDiv = document.getElementById("result");
    const recentLinksDiv = document.getElementById("recent-links");
    const analyticsCodeInput = document.getElementById("analytics-code");
    const analyticsBtn = document.getElementById("analytics-btn");
    const analyticsResultDiv = document.getElementById("analytics-result");

    const sessionHistory = [];

    // Shorten button handler
    shortenBtn.addEventListener("click", async (e) => {
        e.preventDefault();
        
        const longUrl = longUrlInput.value.trim();
        if (!longUrl) {
            showError(resultDiv, "Please enter a URL first.");
            return;
        }

        // Basic URL validation
        try {
            new URL(longUrl);
        } catch (_) {
            showError(resultDiv, "Please enter a valid URL (e.g., https://example.com).");
            return;
        }

        setLoadingState(true);
        resultDiv.innerHTML = "";

        try {
            const data = await shortenUrl(longUrl);
            renderResultCard(data);
            addToHistory(data);
        } catch (err) {
            let friendlyMsg = err.message || "An unexpected error occurred.";
            if (friendlyMsg.includes("Failed to fetch") || friendlyMsg.includes("fetch")) {
                friendlyMsg = "Unable to connect to the backend server. Please make sure the service is running.";
            }
            showError(resultDiv, friendlyMsg);
        } finally {
            setLoadingState(false);
        }
    });

    // Also support Enter key press in inputs
    longUrlInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            shortenBtn.click();
        }
    });

    analyticsCodeInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            analyticsBtn.click();
        }
    });

    // Analytics search handler
    analyticsBtn.addEventListener("click", async (e) => {
        e.preventDefault();
        
        const shortCode = analyticsCodeInput.value.trim();
        if (!shortCode) {
            showError(analyticsResultDiv, "Please enter a short code.");
            return;
        }

        analyticsBtn.disabled = true;
        analyticsBtn.innerHTML = `<span class="spinner"></span>Searching...`;
        analyticsResultDiv.innerHTML = "";

        try {
            const data = await getAnalytics(shortCode);
            renderAnalyticsResult(data);
        } catch (err) {
            showError(analyticsResultDiv, "No link found with that code");
        } finally {
            analyticsBtn.disabled = false;
            analyticsBtn.textContent = "Get Analytics";
        }
    });

    function setLoadingState(isLoading) {
        if (isLoading) {
            shortenBtn.disabled = true;
            shortenBtn.innerHTML = `<span class="spinner"></span>Shortening...`;
            shortenBtn.classList.add("loading");
        } else {
            shortenBtn.disabled = false;
            shortenBtn.textContent = "Shorten";
            shortenBtn.classList.remove("loading");
        }
    }

    function renderResultCard(data) {
        resultDiv.innerHTML = `
            <div class="result-card">
                <div class="result-url-wrapper">
                    <a href="${data.short_url}" target="_blank" class="short-url" id="short-url-link">${data.short_url}</a>
                    <button class="copy-btn" id="copy-btn">Copy</button>
                </div>
                <div class="original-url">${escapeHtml(data.long_url)}</div>
            </div>
        `;

        const copyBtn = document.getElementById("copy-btn");
        copyBtn.addEventListener("click", async () => {
            await copyText(data.short_url, copyBtn);
        });
    }

    function addToHistory(data) {
        // Prevent duplicate codes in current session history
        const existingIdx = sessionHistory.findIndex(item => item.short_code === data.short_code);
        if (existingIdx !== -1) {
            sessionHistory.splice(existingIdx, 1);
        }
        
        sessionHistory.unshift(data);
        
        // Cap the list to 10 entries
        if (sessionHistory.length > 10) {
            sessionHistory.pop();
        }
        
        renderHistory();
    }

    function renderHistory() {
        if (sessionHistory.length === 0) {
            recentLinksDiv.innerHTML = `<p class="empty-state">No links shortened this session.</p>`;
            return;
        }

        recentLinksDiv.innerHTML = sessionHistory.map((item, idx) => `
            <div class="history-card" data-index="${idx}">
                <div class="history-url-info">
                    <a href="${item.short_url}" target="_blank" class="history-short-url">${item.short_url}</a>
                    <div class="history-original-url">${escapeHtml(item.long_url)}</div>
                </div>
                <div class="history-actions">
                    <button class="history-copy-btn" data-url="${item.short_url}">Copy</button>
                    <button class="history-analytics-btn" data-code="${item.short_code}">Analytics</button>
                </div>
            </div>
        `).join("");

        // Attach action events to history card components
        recentLinksDiv.querySelectorAll(".history-copy-btn").forEach(btn => {
            btn.addEventListener("click", async () => {
                const url = btn.getAttribute("data-url");
                await copyText(url, btn);
            });
        });

        recentLinksDiv.querySelectorAll(".history-analytics-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const code = btn.getAttribute("data-code");
                analyticsCodeInput.value = code;
                analyticsBtn.click();
                analyticsCodeInput.scrollIntoView({ behavior: "smooth", block: "center" });
            });
        });
    }

    function renderAnalyticsResult(data) {
        const expiresVal = data.expires_at ? formatDate(data.expires_at) : "Never expires";
        analyticsResultDiv.innerHTML = `
            <div class="analytics-card">
                <div class="analytics-stat">
                    <span class="stat-value">${data.click_count}</span>
                    <span class="stat-label">Total Clicks</span>
                </div>
                <div class="analytics-details">
                    <div class="detail-row">
                        <span class="detail-label">Short Code:</span>
                        <span class="detail-val highlight-code">${data.short_code}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Original URL:</span>
                        <a href="${data.long_url}" target="_blank" class="detail-val long-url-link">${escapeHtml(data.long_url)}</a>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Created At:</span>
                        <span class="detail-val">${formatDate(data.created_at)}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Expires At:</span>
                        <span class="detail-val">${expiresVal}</span>
                    </div>
                </div>
            </div>
        `;
    }

    async function copyText(text, buttonEl) {
        try {
            await navigator.clipboard.writeText(text);
            const originalText = buttonEl.textContent;
            buttonEl.textContent = "Copied!";
            buttonEl.classList.add("copied");
            setTimeout(() => {
                buttonEl.textContent = originalText;
                buttonEl.classList.remove("copied");
            }, 2000);
        } catch (err) {
            console.error("Failed to copy text: ", err);
        }
    }

    function showError(element, message) {
        element.innerHTML = `
            <div class="error-card">
                <span class="error-icon">⚠️</span>
                <span class="error-message">${escapeHtml(message)}</span>
            </div>
        `;
    }

    function escapeHtml(text) {
        const div = document.createElement("div");
        div.innerText = text;
        return div.innerHTML;
    }

    function formatDate(dateStr) {
        try {
            const date = new Date(dateStr);
            return date.toLocaleString();
        } catch (_) {
            return dateStr;
        }
    }

    // Initialize history empty state
    renderHistory();
});
