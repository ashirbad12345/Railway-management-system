const state = { access: localStorage.getItem("railway_access"), refresh: localStorage.getItem("railway_refresh"), authMode: "login" };
const $ = (selector) => document.querySelector(selector);
const escapeHtml = (value) => String(value).replace(/[&<>'"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[character]));

function showToast(message) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 3200);
}

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (state.access) headers.Authorization = `Bearer ${state.access}`;
  const response = await fetch(`/api${path}`, { ...options, headers });
  const data = await response.json().catch(() => ({}));
  if (response.status === 401 && state.refresh && !options._retried) {
    try {
      const tokenResponse = await fetch("/api/auth/refresh/", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ refresh: state.refresh }) });
      if (tokenResponse.ok) {
        const tokens = await tokenResponse.json();
        state.access = tokens.access;
        localStorage.setItem("railway_access", state.access);
        return api(path, { ...options, _retried: true });
      }
    } catch (refreshError) {
      // Fall through and clear invalid credentials below.
    }
  }
  if (response.status === 401 && path !== "/auth/login/" && path !== "/auth/refresh/") {
    state.access = null;
    state.refresh = null;
    localStorage.removeItem("railway_access");
    localStorage.removeItem("railway_refresh");
  }
  if (!response.ok) {
    if (response.status === 401 && path.includes("/bookings")) throw new Error("Your login session expired. Please sign in again, then book your seat.");
    throw new Error(data.detail || Object.values(data).flat().join(" ") || `Request failed (${response.status}).`);
  }
  return data;
}

function renderResults(trains) {
  $("#result-count").textContent = `${trains.length} RESULT${trains.length === 1 ? "" : "S"}`;
  if (!trains.length) {
    $("#results").innerHTML = '<div class="empty-state"><span>∅</span><p>No direct connections found for this route.</p></div>';
    return;
  }
  $("#results").innerHTML = trains.map((train) => `
    <article class="train-card">
      <div><div class="train-name">${escapeHtml(train.name)}</div><div class="route-label">${escapeHtml(train.source)} → ${escapeHtml(train.destination)}</div></div>
      <div><div class="seat-number ${train.available_seats < 10 ? "low" : ""}">${train.available_seats}</div><div class="seat-label">SEATS AVAILABLE</div></div>
      <div><div class="seat-number">${train.total_seats}</div><div class="seat-label">TOTAL CAPACITY</div></div>
      <button class="book-button" data-train-id="${train.id}" ${state.access ? "" : "disabled"}>${state.access ? "Book seat" : "Sign in to book"}</button>
    </article>`).join("");
  document.querySelectorAll("[data-train-id]").forEach((button) => button.addEventListener("click", () => book(button.dataset.trainId)));
}

async function loadBookings() {
  if (!state.access) return;
  try {
    const bookings = await api("/bookings/");
    $("#bookings").innerHTML = bookings.length ? bookings.map((booking) => `
      <div class="booking-row"><div><div class="booking-ref">${escapeHtml(booking.booking_reference)}</div><div class="booking-route">Train #${booking.train}</div></div><div class="booking-seats">${booking.seats} SEAT${booking.seats === 1 ? "" : "S"}</div></div>`).join("") : '<div class="empty-state compact"><span>—</span><p>No bookings yet.</p></div>';
  } catch (error) { $("#bookings").innerHTML = `<div class="empty-state compact"><span>!</span><p>${escapeHtml(error.message)}</p></div>`; }
}

async function loadTrainOptions() {
  try {
    const trains = await api("/trains/catalog/");
    if (!Array.isArray(trains) || !trains.length) return;
    $("#train-select").innerHTML = '<option value="">Choose a train from the database</option>' + trains.map((train) => `<option value="${train.id}" data-source="${escapeHtml(train.source)}" data-destination="${escapeHtml(train.destination)}">${escapeHtml(train.train_number)} · ${escapeHtml(train.name)} — ${escapeHtml(train.source)} → ${escapeHtml(train.destination)} (${train.available_seats} seats)</option>`).join("");
    $("#train-count").textContent = `${trains.length} TRAINS AVAILABLE`;
  } catch (error) { /* The server-rendered options remain available. */ }
}

$("#train-select").addEventListener("change", (event) => {
  const option = event.target.selectedOptions[0];
  if (!option || !option.value) return;
  $("#source").value = option.dataset.source;
  $("#destination").value = option.dataset.destination;
  $("#search-form").dispatchEvent(new Event("submit"));
});

$("#search-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const source = $("#source").value.trim();
  const destination = $("#destination").value.trim();
  $("#search-message").textContent = "Loading live availability...";
  try { renderResults(await api(`/trains/?source=${encodeURIComponent(source)}&destination=${encodeURIComponent(destination)}`)); $("#search-message").textContent = ""; }
  catch (error) { $("#search-message").textContent = error.message; }
});

async function book(trainId) {
  const input = prompt("How many seats? Enter a number, for example 1.", "1");
  if (input === null) return;
  const seats = Number.parseInt(input, 10);
  if (!Number.isInteger(seats) || seats < 1) { showToast("Enter a valid number of seats, such as 1."); return; }
  try { const booking = await api(`/trains/${trainId}/bookings/`, { method: "POST", body: JSON.stringify({ seats }) }); showToast(`Booking ${booking.booking_reference} confirmed.`); loadBookings(); $("#search-form").dispatchEvent(new Event("submit")); }
  catch (error) { showToast(error.message); $("#search-message").textContent = error.message; }
}

function openAuth(mode = "login") {
  state.authMode = mode;
  $("#auth-title").textContent = mode === "login" ? "Welcome back." : "Create your account.";
  $("#auth-subtitle").textContent = mode === "login" ? "Sign in to reserve seats and view your booking." : "Register once, then book directly from the route board.";
  $("#email-field").classList.toggle("hidden", mode === "login");
  $("#auth-submit").innerHTML = `${mode === "login" ? "Sign in" : "Register"} <span>→</span>`;
  $("#toggle-auth").textContent = mode === "login" ? "Need an account? Register" : "Already registered? Sign in";
  $("#auth-dialog").showModal();
}

$("#open-auth").addEventListener("click", () => openAuth());
$("#close-auth").addEventListener("click", () => $("#auth-dialog").close());
$("#toggle-auth").addEventListener("click", () => openAuth(state.authMode === "login" ? "register" : "login"));
$("#auth-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = { username: $("#username").value, password: $("#password").value };
  if (state.authMode === "register") payload.email = $("#email").value;
  $("#auth-message").textContent = "";
  try {
    if (state.authMode === "register") { await api("/auth/register/", { method: "POST", body: JSON.stringify(payload) }); showToast("Account created. Sign in to continue."); openAuth("login"); return; }
    const tokens = await api("/auth/login/", { method: "POST", body: JSON.stringify(payload) });
    state.access = tokens.access; state.refresh = tokens.refresh; localStorage.setItem("railway_access", state.access); localStorage.setItem("railway_refresh", state.refresh); $("#auth-dialog").close(); $("#open-auth").textContent = "Signed in"; loadBookings(); showToast("You can now reserve seats.");
  } catch (error) { $("#auth-message").textContent = error.message; }
});

$("#refresh-bookings").addEventListener("click", loadBookings);

loadTrainOptions();
if (state.access) { $("#open-auth").textContent = "Signed in"; loadBookings(); }