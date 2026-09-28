const state = {
  overview: null,
  workspace: null,
  people: [],
  selectedPersonId: null,
  selectedDossier: null,
  activeView: "dashboard",
};

const content = document.querySelector("#content");
const peopleList = document.querySelector("#people-list");
const peopleCount = document.querySelector("#people-count");
const peopleTotal = document.querySelector("#people-total");
const searchInput = document.querySelector("#search-input");
const modal = document.querySelector("#modal");
const modalTitle = document.querySelector("#modal-title");
const modalForm = document.querySelector("#modal-form");

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.error || `Request failed: ${response.status}`);
  }
  return payload;
}

function text(value, fallback = "unset") {
  if (value === null || value === undefined) return fallback;
  const clean = String(value).trim();
  return clean || fallback;
}

function escapeHtml(value) {
  return text(value, "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function multiline(value) {
  return escapeHtml(value).replaceAll("\n", "<br />");
}

function initials(name) {
  return text(name, "NO")
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();
}

function avatar(person, className = "avatar") {
  const url = `/api/people/${encodeURIComponent(person.person_id)}/profile-photo`;
  return `
    <div class="${className}" title="${escapeHtml(person.name)}">
      <img src="${url}" alt="" onerror="this.remove(); this.parentElement.textContent='${initials(person.name)}';" />
    </div>
  `;
}

async function load() {
  state.overview = await api("/api/overview");
  state.workspace = await api("/api/workspace");
  state.people = state.overview.people || [];
  if (!state.selectedPersonId && state.people.length) {
    state.selectedPersonId = state.people[0].person_id;
  }
  renderPeople();
  await loadSelectedDossier();
  render();
}

async function loadSelectedDossier() {
  if (!state.selectedPersonId) {
    state.selectedDossier = null;
    return;
  }
  state.selectedDossier = await api(`/api/people/${encodeURIComponent(state.selectedPersonId)}/dossier`);
}

function renderPeople() {
  peopleCount.textContent = state.people.length;
  peopleTotal.textContent = `${state.people.length} total`;
  if (!state.people.length) {
    peopleList.innerHTML = `<div class="empty">No people yet. Add the first person to begin.</div>`;
    return;
  }
  peopleList.innerHTML = state.people
    .map((person) => `
      <button class="person-row ${person.person_id === state.selectedPersonId ? "active" : ""}" data-person="${person.person_id}">
        ${avatar(person)}
        <span>
          <span class="person-name">${escapeHtml(person.name)}</span>
          <span class="person-meta">${escapeHtml(person.role || person.relationship_type || "Person")}</span>
          <span class="person-org">${escapeHtml(person.organization || person.location || "NetworkOps")}</span>
        </span>
      </button>
    `)
    .join("");
  document.querySelectorAll("[data-person]").forEach((button) => {
    button.addEventListener("click", async () => {
      state.selectedPersonId = button.dataset.person;
      state.activeView = "people";
      await loadSelectedDossier();
      renderPeople();
      render();
    });
  });
}

function render() {
  document.querySelectorAll(".nav-item").forEach((item) => {
    item.classList.toggle("active", item.dataset.view === state.activeView);
  });
  if (state.activeView === "dashboard") return renderDashboard();
  if (state.activeView === "people") return renderDossier();
  if (state.activeView === "interactions") return renderCollection("Interactions", state.workspace?.interactions || [], renderRecord);
  if (state.activeView === "signals") return renderCollection("Signals", state.workspace?.signals || [], renderSignalRecord);
  if (state.activeView === "opportunities") return renderCollection("Opportunities", state.workspace?.opportunities || [], renderOpportunityRecord);
  if (state.activeView === "relationships") return renderCollection("Relationships", state.workspace?.relationships || [], renderRelationshipRecord);
  return renderPlaceholder();
}

function renderDashboard() {
  const overview = state.overview || { system_state: {}, recent_intel: [], follow_ups: [] };
  const system = overview.system_state || {};
  content.innerHTML = `
    <div class="breadcrumb">Dashboard</div>
    <div class="view-grid">
      <section class="dashboard-card">
        <h3>People Files</h3>
        <div class="metric">${system.files || 0}</div>
        <p class="muted">Active person intelligence records.</p>
      </section>
      <section class="dashboard-card">
        <h3>Open Loops</h3>
        <div class="metric">${system.open_loops || 0}</div>
        <p class="muted">Follow-ups and next actions.</p>
      </section>
      <section class="dashboard-card">
        <h3>Dormant</h3>
        <div class="metric">${system.dormant || 0}</div>
        <p class="muted">People without recent context.</p>
      </section>
    </div>
    <section class="panel">
      <h3>Recent Intel</h3>
      <div class="timeline-list">
        ${(overview.recent_intel || []).slice(0, 6).map(renderRecord).join("") || `<div class="empty">No recent intel yet.</div>`}
      </div>
    </section>
    <section class="panel">
      <h3>Follow-Ups</h3>
      <div class="timeline-list">
        ${(overview.follow_ups || []).map((item) => `
          <div class="record-row">
            <div class="date-block"><strong>${escapeHtml((item.follow_up_date || "--").slice(-2) || "--")}</strong>${escapeHtml(item.follow_up_date || "unscheduled")}</div>
            <div>
              <div class="card-title">${escapeHtml(item.title)}</div>
              <p>${escapeHtml(item.action || item.status || "pending")}</p>
            </div>
            <span class="risk-badge">${escapeHtml(item.kind)}</span>
          </div>
        `).join("") || `<div class="empty">No follow-ups recorded.</div>`}
      </div>
    </section>
  `;
}

function renderDossier() {
  const dossier = state.selectedDossier;
  if (!dossier) {
    content.innerHTML = `<div class="empty">No person selected. Add or select a person to open a dossier.</div>`;
    return;
  }
  const person = dossier.person;
  const contacts = dossier.folder_payloads.contacts || [];
  const interactions = dossier.folder_payloads.interactions || [];
  const signals = dossier.folder_payloads.signals || [];
  const opportunities = dossier.folder_payloads.opportunities || [];
  const connections = dossier.folder_payloads.connections || [];
  const status = dossier.summary_cards?.find((card) => card.id === "relationship_status")?.value;
  const bestMove = dossier.summary_cards?.find((card) => card.id === "best_move")?.value;
  const strength = person.relationship_strength || "unset";

  content.innerHTML = `
    <div class="dossier-grid">
      <div>
        <div class="breadcrumb">People > ${escapeHtml(person.name)}</div>
        <section class="profile-hero">
          ${avatar(person, "avatar-large")}
          <div class="hero-copy">
            <h1>${escapeHtml(person.name)}</h1>
            <h2>${escapeHtml(person.role || person.relationship_type || "Person")}</h2>
            <div class="muted">${escapeHtml(person.organization || "NetworkOps")}</div>
            <div class="chips">
              <span class="chip">${escapeHtml(person.relationship_type || "person")}</span>
              <span class="chip">${escapeHtml(person.relationship_status || status || "active")}</span>
              <span class="chip">Strength: ${escapeHtml(strength)}</span>
            </div>
            <div class="stat-strip">
              <div class="stat"><span>Last Contact</span><strong>${escapeHtml(person.last_contact || "unset")}</strong></div>
              <div class="stat"><span>Next Action</span><strong>${escapeHtml(bestMove || person.next_action || "unset")}</strong></div>
              <div class="stat"><span>Follow Up</span><strong>${escapeHtml(person.follow_up_date || "unset")}</strong></div>
              <div class="stat"><span>Open Opportunities</span><strong>${opportunities.length}</strong></div>
              <div class="stat"><span>Total Signals</span><strong>${signals.length}</strong></div>
            </div>
          </div>
        </section>

        <div class="tabbar">
          <button class="tab active">Dossier</button>
          <button class="tab" data-action="interaction">Timeline</button>
          <button class="tab" data-action="signal">Signals</button>
          <button class="tab" data-action="opportunity">Opportunities</button>
          <button class="tab" data-action="relationship">Relationships</button>
          <button class="tab" data-action="contact">Contact</button>
        </div>

        <section class="panel">
          <h3>Dossier</h3>
          <p>${multiline(dossier.current_read)}</p>
          <div class="two-col">
            <div class="mini-section">
              <h4>Current Goals</h4>
              ${bullets(person.current_goals)}
            </div>
            <div class="mini-section">
              <h4>Preferences</h4>
              ${bullets(person.preferences)}
            </div>
            <div class="mini-section">
              <h4>Communication Style</h4>
              <p>${multiline(person.communication_style)}</p>
            </div>
            <div class="mini-section">
              <h4>Potential Value</h4>
              <div class="value-tags">${splitLines(person.potential_value).map((item) => `<span class="value-tag">${escapeHtml(item)}</span>`).join("") || `<span class="muted">unset</span>`}</div>
            </div>
          </div>
        </section>

        <section class="panel">
          <h3>Recent Interactions</h3>
          <div class="timeline-list">
            ${interactions.slice(0, 5).map(renderRecord).join("") || `<div class="empty">No interactions logged.</div>`}
          </div>
        </section>
      </div>

      <aside class="right-rail">
        <div class="quote-card">
          <blockquote>"${escapeHtml(person.importance_reason || "Only logged, shared, observed, or publicly known info.")}"</blockquote>
        </div>
        <section class="side-panel">
          <h3>Connections</h3>
          <div class="connection-map">
            <div class="node-avatar center">${initials(person.name)}</div>
            ${connections.slice(0, 4).map((link) => `<div class="node-avatar">${initials(link.other_entity_label)}</div>`).join("")}
          </div>
          <div class="side-list">${connections.map(renderRelationshipRecord).join("") || `<div class="empty">No links yet.</div>`}</div>
        </section>
        <section class="side-panel">
          <h3>Open Opportunities</h3>
          <div class="side-list">${opportunities.slice(0, 3).map(renderOpportunityRecord).join("") || `<div class="empty">No opportunities.</div>`}</div>
        </section>
        <section class="side-panel">
          <h3>Quick Intel</h3>
          <div class="side-list">${signals.slice(0, 3).map(renderSignalRecord).join("") || `<div class="empty">No signals.</div>`}</div>
        </section>
        <section class="side-panel">
          <h3>Contact Information</h3>
          <div class="side-list">${contacts.map((contact) => `
            <div class="side-row">
              <span class="index-dot">${escapeHtml((contact.type || "?").slice(0, 1))}</span>
              <div>
                <div class="card-title">${escapeHtml(contact.value)}</div>
                <div class="muted">${escapeHtml(contact.label || contact.type)}</div>
              </div>
            </div>
          `).join("") || `<div class="empty">No contact methods.</div>`}</div>
        </section>
      </aside>
    </div>
  `;
}

function renderCollection(title, items, renderer) {
  content.innerHTML = `
    <div class="breadcrumb">${escapeHtml(title)}</div>
    <section class="panel">
      <h3>${escapeHtml(title)}</h3>
      <div class="timeline-list">
        ${items.map(renderer).join("") || `<div class="empty">No records yet.</div>`}
      </div>
    </section>
  `;
}

function renderPlaceholder() {
  content.innerHTML = `
    <div class="breadcrumb">${escapeHtml(state.activeView)}</div>
    <div class="empty">This view is reserved for a future NetworkOps pass. Core data is available through Dashboard, People, Interactions, Signals, Opportunities, and Relationships.</div>
  `;
}

function renderRecord(item) {
  return `
    <div class="record-row">
      <div class="date-block"><strong>${escapeHtml((item.date || "--").slice(-2) || "--")}</strong>${escapeHtml(item.date || "undated")}</div>
      <div>
        <div class="card-title">${escapeHtml(item.title || item.kind || "Record")}</div>
        <p>${multiline(item.summary || item.text || item.takeaways || "No summary recorded.")}</p>
      </div>
      <span class="risk-badge">${escapeHtml(item.person || item.kind || "intel")}</span>
    </div>
  `;
}

function renderSignalRecord(item) {
  return `
    <div class="side-row">
      <span class="index-dot">*</span>
      <div>
        <div class="card-title">${escapeHtml(item.text || "Signal")}</div>
        <div class="muted">${escapeHtml(item.confidence || "unknown confidence")}</div>
      </div>
    </div>
  `;
}

function renderOpportunityRecord(item, index = 0) {
  return `
    <div class="side-row">
      <span class="index-dot">${index + 1}</span>
      <div>
        <div class="card-title">${escapeHtml(item.title)}</div>
        <div class="muted">${escapeHtml(item.follow_up_date ? `Follow up by ${item.follow_up_date}` : item.description || "Opportunity")}</div>
      </div>
      <span class="risk-badge">${escapeHtml(item.status || "open")}</span>
    </div>
  `;
}

function renderRelationshipRecord(item) {
  return `
    <div class="side-row">
      <span class="index-dot">+</span>
      <div>
        <div class="card-title">${escapeHtml(item.other_entity_label || item.target_entity_id)}</div>
        <div class="muted">${escapeHtml(item.relationship_type || item.description || "relationship")}</div>
      </div>
    </div>
  `;
}

function bullets(value) {
  const items = splitLines(value);
  if (!items.length) return `<p class="muted">unset</p>`;
  return `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

function splitLines(value) {
  return text(value, "")
    .split(/\n|,/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function openModal(kind) {
  const selected = state.selectedDossier?.person;
  const peopleOptions = state.people.map((person) => `<option value="${person.person_id}">${escapeHtml(person.name)}</option>`).join("");
  const selectedOption = selected ? selected.person_id : state.people[0]?.person_id || "";
  const forms = {
    person: {
      title: "Add Person",
      endpoint: "/api/people",
      method: "POST",
      fields: [
        field("name", "Name", "text", true),
        field("alias", "Alias"),
        field("role", "Role"),
        field("organization", "Organization"),
        field("location", "Location"),
        field("relationship_type", "Relationship Type"),
        field("relationship_status", "Relationship Status"),
        field("relationship_strength", "Relationship Strength"),
        field("email", "Email"),
        field("phone", "Phone"),
        field("tags", "Tags"),
        field("dossier", "Dossier", "textarea"),
        field("current_goals", "Current Goals", "textarea"),
        field("potential_value", "Potential Value", "textarea"),
        field("next_action", "Next Action"),
        field("follow_up_date", "Follow-Up Date"),
      ],
    },
    edit: {
      title: "Edit Person",
      endpoint: `/api/people/${encodeURIComponent(selectedOption)}`,
      method: "PATCH",
      fields: [
        field("name", "Name", "text", true, selected?.name),
        field("role", "Role", "text", false, selected?.role),
        field("organization", "Organization", "text", false, selected?.organization),
        field("location", "Location", "text", false, selected?.location),
        field("relationship_status", "Relationship Status", "text", false, selected?.relationship_status),
        field("relationship_strength", "Relationship Strength", "text", false, selected?.relationship_strength),
        field("dossier", "Dossier", "textarea", false, selected?.dossier),
        field("communication_style", "Communication Style", "textarea", false, selected?.communication_style),
        field("preferences", "Preferences", "textarea", false, selected?.preferences),
        field("current_goals", "Current Goals", "textarea", false, selected?.current_goals),
        field("potential_value", "Potential Value", "textarea", false, selected?.potential_value),
        field("next_action", "Next Action", "text", false, selected?.next_action),
        field("follow_up_date", "Follow-Up Date", "text", false, selected?.follow_up_date),
      ],
    },
    contact: {
      title: "Add Contact Method",
      endpoint: `/api/people/${encodeURIComponent(selectedOption)}/contacts`,
      method: "POST",
      fields: [
        select("type", "Type", ["email", "phone", "linkedin", "github", "social", "other"]),
        field("label", "Label"),
        field("value", "Value", "text", true),
      ],
    },
    interaction: {
      title: "Log Interaction",
      endpoint: "/api/interactions",
      method: "POST",
      fields: [
        select("person_id", "Person", state.people.map((person) => [person.person_id, person.name]), selectedOption),
        field("interaction_date", "Date", "text", false, new Date().toISOString().slice(0, 10)),
        field("interaction_type", "Type", "text", false, "meeting"),
        field("summary", "Summary", "textarea"),
        field("takeaways", "Takeaways", "textarea"),
        field("action_items", "Action Items", "textarea"),
        field("follow_up_date", "Follow-Up Date"),
      ],
    },
    signal: {
      title: "Add Signal",
      endpoint: `/api/people/${encodeURIComponent(selectedOption)}/signals`,
      method: "POST",
      fields: [
        field("text", "Signal Text", "textarea", true),
        field("confidence", "Confidence"),
        field("source_description", "Source"),
      ],
    },
    opportunity: {
      title: "Add Opportunity",
      endpoint: "/api/opportunities",
      method: "POST",
      fields: [
        select("person_id", "Person", state.people.map((person) => [person.person_id, person.name]), selectedOption),
        field("title", "Title", "text", true),
        field("status", "Status", "text", false, "open"),
        field("description", "Description", "textarea"),
        field("follow_up_date", "Follow-Up Date"),
      ],
    },
    relationship: {
      title: "Add Relationship Link",
      endpoint: "/api/relationship-links",
      method: "POST",
      fields: [
        select("source_person_id", "Source Person", state.people.map((person) => [person.person_id, person.name]), selectedOption),
        select("target_person_id", "Target Person", state.people.map((person) => [person.person_id, person.name]), ""),
        field("relationship_type", "Relationship Type", "text", true),
        field("description", "Description", "textarea"),
      ],
    },
  };
  const config = forms[kind] || forms.person;
  modalTitle.textContent = config.title;
  modalForm.dataset.endpoint = config.endpoint;
  modalForm.dataset.method = config.method;
  modalForm.dataset.kind = kind;
  modalForm.innerHTML = `
    ${config.fields.join("")}
    <div id="form-error" class="error-box hidden"></div>
    <div class="form-actions">
      <button class="secondary-button" type="button" id="form-cancel">Cancel</button>
      <button class="primary-button" type="submit">Save</button>
    </div>
  `;
  modal.classList.remove("hidden");
  modal.setAttribute("aria-hidden", "false");
  document.querySelector("#form-cancel").addEventListener("click", closeModal);
}

function field(name, label, type = "text", required = false, value = "") {
  const tag = type === "textarea" ? "textarea" : "input";
  const full = type === "textarea" ? " full" : "";
  const requiredAttr = required ? "required" : "";
  const valueAttr = tag === "input" ? `value="${escapeHtml(value)}"` : "";
  const inner = tag === "textarea" ? escapeHtml(value) : "";
  return `
    <div class="field${full}">
      <label for="${name}">${label}</label>
      <${tag} id="${name}" name="${name}" type="${type}" ${requiredAttr} ${valueAttr}>${inner}</${tag}>
    </div>
  `;
}

function select(name, label, options, selected = "") {
  const normalized = options.map((option) => Array.isArray(option) ? option : [option, option]);
  return `
    <div class="field">
      <label for="${name}">${label}</label>
      <select id="${name}" name="${name}">
        <option value="">Select...</option>
        ${normalized.map(([value, labelText]) => `<option value="${escapeHtml(value)}" ${value === selected ? "selected" : ""}>${escapeHtml(labelText)}</option>`).join("")}
      </select>
    </div>
  `;
}

function closeModal() {
  modal.classList.add("hidden");
  modal.setAttribute("aria-hidden", "true");
  modalForm.innerHTML = "";
}

modalForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(modalForm);
  const payload = Object.fromEntries(formData.entries());
  if (payload.person_id) {
    payload.people = [payload.person_id];
    delete payload.person_id;
  }
  try {
    await api(modalForm.dataset.endpoint, {
      method: modalForm.dataset.method,
      body: JSON.stringify(payload),
    });
    closeModal();
    await load();
    if (state.activeView !== "dashboard") state.activeView = "people";
    render();
  } catch (error) {
    const box = document.querySelector("#form-error");
    box.textContent = error.message;
    box.classList.remove("hidden");
  }
});

document.querySelector("#modal-close").addEventListener("click", closeModal);
document.querySelectorAll("[data-view]").forEach((button) => {
  button.addEventListener("click", () => {
    state.activeView = button.dataset.view;
    render();
  });
});
document.querySelectorAll("[data-action]").forEach((button) => {
  button.addEventListener("click", () => openModal(button.dataset.action));
});
searchInput.addEventListener("input", async () => {
  state.people = await api(`/api/people?search=${encodeURIComponent(searchInput.value)}`);
  if (!state.people.some((person) => person.person_id === state.selectedPersonId)) {
    state.selectedPersonId = state.people[0]?.person_id || null;
    await loadSelectedDossier();
  }
  renderPeople();
  render();
});

load().catch((error) => {
  content.innerHTML = `<div class="empty">NetworkOps could not load: ${escapeHtml(error.message)}</div>`;
});
