const API_BASE_URL = window.CARDLEARN_API_BASE_URL || "http://127.0.0.1:8000";
const SESSION_KEY = "user";

async function request(path, options = {}) {
  const { auth: needsAuth, ...fetchOptions } = options;
  const isFormData = typeof FormData !== "undefined" && fetchOptions.body instanceof FormData;
  const headers = {
    ...(isFormData ? {} : { "Content-Type": "application/json" }),
    ...(fetchOptions.headers || {})
  };

  if (needsAuth) {
    const token = auth.getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...fetchOptions,
    headers
  });

  let data = null;

  try {
    data = await response.json();
  } catch (_) {
    data = null;
  }

  if (!response.ok) {
    const message = data?.detail || data?.message || "API request failed. Please try again later.";
    throw new Error(message);
  }

  return data;
}

function normalizeSession(payload) {
  const rawUser = payload?.user || {};
  const user = {
    id: rawUser.id ?? payload?.id ?? null,
    name: rawUser.name ?? payload?.name ?? "",
    email: rawUser.email ?? payload?.email ?? "",
    role: rawUser.role ?? payload?.role ?? "student"
  };

  user.username = rawUser.username || payload?.username || user.name || user.email;

  return {
    access_token: payload?.access_token || payload?.token || "",
    token_type: payload?.token_type || "bearer",
    user,
    id: user.id,
    name: user.name,
    email: user.email,
    username: user.username,
    role: user.role
  };
}

function getLoginPath() {
  return "/pages/login.html";
}

const auth = {
  saveSession(payload) {
    const session = normalizeSession(payload);
    localStorage.setItem(SESSION_KEY, JSON.stringify(session));
    return session;
  },

  getSession() {
    const value = localStorage.getItem(SESSION_KEY);
    if (!value) return null;

    try {
      const parsed = JSON.parse(value);
      return normalizeSession(parsed);
    } catch (_) {
      localStorage.removeItem(SESSION_KEY);
      return null;
    }
  },

  getUser() {
    return this.getSession()?.user || null;
  },

  getToken() {
    return this.getSession()?.access_token || "";
  },

  requireLogin() {
    const session = this.getSession();
    if (!session) {
      const next = encodeURIComponent(window.location.pathname + window.location.search);
      window.location.href = `${getLoginPath()}?next=${next}`;
      return { access_token: "", user: { username: "", role: "" } };
    }
    return session;
  },

  logout() {
    localStorage.removeItem(SESSION_KEY);
    sessionStorage.removeItem("current_session_id");
    window.location.href = getLoginPath();
  }
};

window.api = {
  auth: {
    async login(email, password) {
      const payload = await request("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password })
      });

      return auth.saveSession(payload);
    },

    me() {
      return request("/auth/me", {
        method: "GET",
        auth: true
      });
    },

    logout() {
      auth.logout();
    }
  },

  sendOTP(email) {
    return request("/auth/send-otp", {
      method: "POST",
      body: JSON.stringify({ email })
    });
  },

  verifyOTP(email, otp) {
    return request("/auth/verify-otp", {
      method: "POST",
      body: JSON.stringify({ email, otp })
    });
  },

  register(payload) {
    return request("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },

  content: {
    options() {
      return request("/content/options");
    },

    parts(sdg) {
      const query = sdg ? `?sdg=${encodeURIComponent(sdg)}` : "";
      return request(`/content/parts${query}`);
    }
  },

  game: {
    startGame(username, sdg, level) {
      return request("/game/start", {
        method: "POST",
        auth: true,
        body: JSON.stringify({ username, sdg, level })
      });
    },

    content(sdg, level) {
      const query = new URLSearchParams({ sdg, level }).toString();
      return request(`/game/content?${query}`, {
        method: "GET",
        auth: true
      });
    },

    savePart(sessionId, partId, errors, duration, repeatListens = 0) {
      return request("/game/part", {
        method: "POST",
        auth: true,
        body: JSON.stringify({
          session_id: Number(sessionId),
          part_id: Number(partId),
          errors: Number(errors),
          repeat_listens: Number(repeatListens),
          duration: Number(duration)
        })
      });
    },

    endGame(sessionId) {
      return request("/game/end", {
        method: "POST",
        auth: true,
        body: JSON.stringify({ session_id: Number(sessionId) })
      });
    },

    getResults(sessionId) {
      return request(`/game/results/${encodeURIComponent(sessionId)}`, {
        method: "GET",
        auth: true
      });
    }
  },

  teacher: {
    content() {
      return request("/teacher/content", {
        method: "GET",
        auth: true
      });
    },

    importExcel(file) {
      const form = new FormData();
      form.append("file", file);
      return request("/teacher/import-excel", {
        method: "POST",
        auth: true,
        body: form
      });
    },

    importJson(file) {
      const form = new FormData();
      form.append("file", file);
      return request("/teacher/import-json", {
        method: "POST",
        auth: true,
        body: form
      });
    },

    saveSdg(payload) {
      return request("/teacher/sdgs", {
        method: "POST",
        auth: true,
        body: JSON.stringify(payload)
      });
    },

    saveDifficulty(payload) {
      return request("/teacher/difficulties", {
        method: "POST",
        auth: true,
        body: JSON.stringify(payload)
      });
    },

    savePart(payload) {
      return request("/teacher/parts", {
        method: "POST",
        auth: true,
        body: JSON.stringify(payload)
      });
    },

    saveSubTopic(payload) {
      return request("/teacher/sub-topics", {
        method: "POST",
        auth: true,
        body: JSON.stringify(payload)
      });
    },

    saveCard(payload) {
      return request("/teacher/cards", {
        method: "POST",
        auth: true,
        body: JSON.stringify(payload)
      });
    },

    deleteSdg(sdgLevel) {
      return request(`/teacher/sdgs/${encodeURIComponent(sdgLevel)}`, {
        method: "DELETE",
        auth: true
      });
    },

    deletePart(partId) {
      return request(`/teacher/parts/${encodeURIComponent(partId)}`, {
        method: "DELETE",
        auth: true
      });
    },

    deleteSubTopic(subTopicId) {
      return request(`/teacher/sub-topics/${encodeURIComponent(subTopicId)}`, {
        method: "DELETE",
        auth: true
      });
    },

    deleteCard(cardId) {
      return request(`/teacher/cards/${encodeURIComponent(cardId)}`, {
        method: "DELETE",
        auth: true
      });
    },

    gameRecords() {
      return request("/teacher/game-records", {
        method: "GET",
        auth: true
      });
    },

    deleteGameRecord(sessionId) {
      return request(`/teacher/game-records/${encodeURIComponent(sessionId)}`, {
        method: "DELETE",
        auth: true
      });
    },

    users() {
      return request("/teacher/users", {
        method: "GET",
        auth: true
      });
    },

    updateUserRole(userId, role) {
      return request(`/teacher/users/${encodeURIComponent(userId)}/role`, {
        method: "PATCH",
        auth: true,
        body: JSON.stringify({ role })
      });
    },

    deleteUser(userId) {
      return request(`/teacher/users/${encodeURIComponent(userId)}`, {
        method: "DELETE",
        auth: true
      });
    }
  }
};

window.auth = auth;
