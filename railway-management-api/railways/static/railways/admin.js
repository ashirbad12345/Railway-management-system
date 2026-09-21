const $ = (selector) => document.querySelector(selector);

function showToast(message) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 3200);
}

async function request(path, options = {}) {
  const response = await fetch(`/api${path}`, { ...options, headers: { "Content-Type": "application/json", ...(options.headers || {}) } });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || Object.values(data).flat().join(" ") || "Request failed.");
  return data;
}

async function loadTrains() {
  try {
    const trains = await request("/trains/catalog/");
    $("#admin-trains").innerHTML = trains.length ? trains.map((train) => `<div class="booking-row"><div><div class="booking-ref">${train.train_number} · ${train.name}</div><div class="booking-route">${train.source} → ${train.destination}</div></div><div class="booking-seats">${train.available_seats} / ${train.total_seats} SEATS</div></div>`).join("") : '<div class="empty-state compact"><span>—</span><p>No trains in the database.</p></div>';
  } catch (error) { $("#admin-trains").innerHTML = `<div class="empty-state compact"><span>!</span><p>${error.message}</p></div>`; }
}

$("#refresh-trains").addEventListener("click", loadTrains);
$("#admin-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = $("#admin-message");
  message.textContent = "Saving train...";
  const payload = { train_number: $("#admin-number").value.trim(), name: $("#admin-name").value.trim(), source: $("#admin-source").value.trim(), destination: $("#admin-destination").value.trim(), total_seats: Number($("#admin-seats").value) };
  try {
    await request("/admin/trains/", { method: "POST", headers: { "X-API-Key": $("#admin-key").value }, body: JSON.stringify(payload) });
    message.textContent = "Train added to the database.";
    event.target.reset();
    showToast("Train inventory updated.");
    loadTrains();
  } catch (error) { message.textContent = error.message; }
});

loadTrains();
