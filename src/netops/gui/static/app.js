const state = {
  overview: null,
  workspace: null,
  people: [],
  selectedPersonId: null,
  selectedDossier: null,
  activeView: "dashboard",
  dossierTab: "dossier",
  peopleMode: "directory",
  directorySearch: "",
};

const content = document.querySelector("#content");
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
  return `<div class="${className}" title="${escapeHtml(person.name)}"><span>${escapeHtml(initials(person.name))}</span><img src="${url}" alt="" onerror="this.remove()" /></div>`;
}

async function load() {
  const settings = await api("/api/settings");
  document.querySelector("#database-path").textContent = settings.database_path;
  state.catalog = await api("/api/catalog");
  state.overview = await api("/api/overview");
  state.workspace = await api("/api/workspace");
  state.people = state.overview.people || [];
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
  const rows = matchingPeople(state.directorySearch);
  content.innerHTML = `<div class="page-heading"><div><div class="eyebrow">Your network</div><h1>People</h1></div><button class="primary-button" data-action="person">+ New Person</button></div><label class="directory-search">Search directory<input id="directory-search" type="search" value="${escapeHtml(state.directorySearch)}" placeholder="Name, role, organization or tag" /></label><div id="directory-count" class="muted">${rows.length} people</div><div id="people-list" class="people-directory">${peopleRows(rows)}</div>`;
}

function matchingPeople(query) {
  const needle = query.trim().toLowerCase();
  return state.people.filter(p => [p.name, p.alias, p.role, p.organization, p.location, ...(p.tags || [])].filter(Boolean).join(" ").toLowerCase().includes(needle));
}

function peopleRows(rows) {
  if (!rows.length) return `<div class="empty">No people match this view.</div>`;
  return rows
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

}

function render() {
  document.querySelectorAll(".nav-item").forEach((item) => {
    item.classList.toggle("active", item.dataset.view === state.activeView);
  });
  if (state.activeView === "dashboard") return renderDashboard();
  if (state.activeView === "tags") return renderTags();
  if (state.activeView === "people") return state.peopleMode === "profile" ? renderDossier() : renderPeople();
  if (state.activeView === "interactions") return renderCollection("Interactions", state.workspace?.interactions || [], renderRecord, "interaction");
  if (state.activeView === "signals") return renderCollection("Intel", state.workspace?.signals || [], renderSignalRecord, "signal");
  if (state.activeView === "opportunities") return renderCollection("Opportunities", state.workspace?.opportunities || [], renderOpportunityRecord);
  if (state.activeView === "relationships") return renderCollection("Relationships", state.workspace?.relationships || [], renderRelationshipRecord, "relationship");
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
        ${(overview.follow_ups || []).map(renderFollowUp).join("") || `<div class="empty">No follow-ups recorded.</div>`}
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
  if (state.dossierTab !== "dossier") {
    const tabs = {
      interactions: ["Timeline", "interaction", renderRecord],
      signals: ["Intel", "signal", renderSignalRecord],
      opportunities: ["Opportunities", "opportunity", renderOpportunityRecord],
      connections: ["Relationships", "relationship", renderRelationshipRecord],
      contacts: ["Contact", "contact", (x) => `<div class="record-row">${escapeHtml(x.type)}: ${escapeHtml(x.value)}</div>`],
    };
    const [title, action, renderer] = tabs[state.dossierTab];
    renderCollection(`${person.name} / ${title}`, dossier.folder_payloads[state.dossierTab] || [], renderer);
    content.insertAdjacentHTML("afterbegin", backToPeople() + dossierTabs() + `<button class="primary-button" data-scope="profile" data-action="${action}">+ New ${title === "Timeline" ? "Interaction" : title === "Relationships" ? "Relationship" : title === "Opportunities" ? "Opportunity" : title}</button>`);
    return;
  }
  const folders = dossier.folder_payloads;
  const action = (kind, label) => `<button class="action-link" data-action="${kind}">${label}</button>`;
  const context = [["current_goals", "Goals"], ["interests", "Interests"], ["preferences", "Preferences"], ["communication_style", "Communication style"], ["potential_value", "Potential value"], ["importance_reason", "Why this connection matters"]];
  content.innerHTML = `${backToPeople()}
    <section class="profile-hero">${avatar(person, "avatar-large")}<div class="hero-copy">
    <h1>${escapeHtml(person.name)}</h1><h2>${escapeHtml(person.role)}</h2><div class="muted">${escapeHtml(person.organization)} · ${escapeHtml(person.location)}</div>
    <dl class="identity-indicators"><div><dt>Category</dt><dd>${escapeHtml(person.relationship_type || "Unset")}</dd></div><div><dt>Status</dt><dd>${escapeHtml(person.relationship_status || "Unset")}</dd></div><div><dt>Strength</dt><dd>${escapeHtml(person.relationship_strength || "Unset")}</dd></div></dl>
    <div class="assigned-tags"><span class="muted">Tags</span> ${(person.tags || []).map(t=>`<span class="tag-chip">${escapeHtml(t)}</span>`).join("") || "None assigned"}</div>
    </div><div class="hero-actions">${action("edit", "Edit Person")}${action("photo", "Change photo")}</div></section>
    ${dossierTabs()}
    <div class="casefile-columns"><div>
      <section class="panel"><div class="section-heading"><h3>Identity</h3>${action("edit", "Edit identity")}</div><p>${escapeHtml(person.alias || "No alias recorded")}</p>
      <div class="section-heading"><h4>Contacts</h4>${action("contact", "Add contact")}</div>${(folders.contacts || []).map(c=>`<p>${escapeHtml(c.type)} · ${escapeHtml(c.value)} ${escapeHtml(c.label)}</p>`).join("") || '<p class="muted">No contacts recorded.</p>'}</section>
      <section class="panel"><div class="section-heading"><h3>Relationship context</h3>${action("relationship-context", "Edit context")}</div><p>${multiline(person.origin_story)}</p><p>First met: ${escapeHtml(person.first_met || "Unknown")}</p>
      ${(folders.connections || []).map(renderRelationshipRecord).join("")}${action("relationship", "Add relationship")}</section>
      <section class="panel"><div class="section-heading"><h3>Knowledge / current read</h3>${action("signal", "Add Intel")}</div>${(folders.signals || []).map(renderSignalRecord).join("") || '<p class="muted">No structured Intel recorded.</p>'}</section>
      <section class="panel"><div class="section-heading"><h3>Case-file sections</h3><button class="action-link" data-section-action="add">Add section</button></div>
      ${(dossier.sections || []).map(section=>`<article class="dossier-section" data-section-id="${section.section_id}"><div class="section-heading"><h4>${escapeHtml(section.title)}</h4><div>
      <button class="action-link" data-section-action="edit" data-section="${section.section_id}">Edit</button>
      <button class="action-link" data-section-action="append" data-section="${section.section_id}">Append</button>
      ${section.revision ? `<button class="action-link" data-section-action="history" data-section="${section.section_id}">History</button>` : ""}</div></div><div class="document-body">${section.html}</div></article>`).join("") || '<p class="muted">Add background or context as individual sections.</p>'}</section>
    </div><div>
      <section class="panel"><h3>Current context</h3>${context.map(([key,label])=>`<div class="mini-section"><div class="section-heading"><h4>${label}</h4><button class="action-link" data-context="${key}" data-label="${label}">Edit</button></div><p>${multiline(person[key]) || '<span class="muted">Not recorded</span>'}</p></div>`).join("")}</section>
      <section class="panel"><div class="section-heading"><h3>Open loops / follow-ups</h3>${action("follow-up", "Edit next action")}</div>${(dossier.follow_ups || []).map(renderFollowUp).join("") || '<p class="muted">No pending actions.</p>'}</section>
      <section class="panel"><div class="section-heading"><h3>Recent history</h3>${action("interaction", "Log Interaction")}</div>${(folders.interactions || []).slice(0,5).map(renderRecord).join("") || '<p class="muted">No interactions recorded.</p>'}</section>
      <section class="panel"><div class="section-heading"><h3>Opportunities</h3>${action("opportunity", "Add opportunity")}</div>${(folders.opportunities || []).map(renderOpportunityRecord).join("") || '<p class="muted">No opportunities recorded.</p>'}</section>
    </div></div>`;
}

function renderCollection(title, items, renderer, action = "") {
  content.innerHTML = `
    <div class="page-heading"><h1>${escapeHtml(title)}</h1>${action ? `<button class="primary-button" data-action="${action}">+ New ${action === "signal" ? "Intel" : action[0].toUpperCase() + action.slice(1)}</button>` : ""}</div>
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
        ${(item.participants || []).length ? `<div class="participant-avatars">${item.participants.map(p=>avatar(p) + `<span>${escapeHtml(p.name)}</span>`).join("")}</div>` : ""}
        ${item.follow_up_completed_at ? `<div class="muted">Follow-up completed</div>` : item.follow_up_required ? completeButton(item) : ""}
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
        ${item.follow_up_completed_at ? `<div class="muted">Follow-up completed</div>` : item.follow_up_date && !["closed", "complete", "completed", "archived"].includes(item.status) ? completeButton(item) : ""}
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

function openModal(kind, scoped = false) {
  const selected = scoped ? state.selectedDossier?.person : null;
  const peopleOptions = state.people.map((person) => `<option value="${person.person_id}">${escapeHtml(person.name)}</option>`).join("");
  const selectedOption = selected?.person_id || "";
  const forms = {
    tag: {title:"New tag",endpoint:"/api/tags",method:"POST",fields:[field("name","Tag name","text",true)]},
    person: {
      title: "New Person",
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
        tagPicker([]),
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
        field("alias", "Alias", "text", false, selected?.alias),
        tagPicker(selected?.tags || []),
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
      title: "New Interaction",
      endpoint: "/api/interactions",
      method: "POST",
      fields: [
        participantPicker(selectedOption ? [selectedOption] : []),
        field("interaction_date", "Date", "date", true, localToday()),
        typePicker("interaction", "interaction_type", "Type", "Meeting"),
        field("summary", "Summary", "textarea"),
        field("takeaways", "Takeaways", "textarea"),
        field("action_items", "Action Items", "textarea"),
        field("follow_up_date", "Follow-Up Date"),
        `<label class="field"><span><input name="follow_up_required" type="checkbox" /> Follow-up required (date optional)</span></label>`,
      ],
    },
    signal: {
      title: "New Intel",
      endpoint: "/api/people/__subject__/signals",
      method: "POST",
      fields: [
        select("subject_id", "Person", state.people.map((person) => [person.person_id, person.name + (person.organization ? ` · ${person.organization}` : "")]), selectedOption),
        field("text", "Information", "textarea", true),
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
        typePicker("relationship", "relationship_type", "Relationship Type"),
        field("description", "Description", "textarea"),
      ],
    },
  };
  forms["relationship-context"] = {title:"Edit relationship context", endpoint:`/api/people/${selectedOption}`, method:"PATCH", fields:[
    field("origin_story", "How we know each other", "textarea", false, selected?.origin_story),
    field("first_met", "First met", "text", false, selected?.first_met),
    field("relationship_type", "Category", "text", false, selected?.relationship_type),
    field("relationship_status", "Relationship Status", "text", false, selected?.relationship_status),
    field("relationship_strength", "Relationship Strength", "text", false, selected?.relationship_strength)]};
  forms["follow-up"] = {title:"Edit next action", endpoint:`/api/people/${selectedOption}`, method:"PATCH", fields:[
    field("next_action", "Next Action", "textarea", false, selected?.next_action), field("follow_up_date", "Follow-Up Date", "text", false, selected?.follow_up_date)]};
  forms.photo = {title:"Profile photo", endpoint:`/api/people/${selectedOption}/photo`, method:"POST", fields:[
    '<div class="field full"><label for="photo-file">Choose a still PNG, JPEG or WebP (up to 8 MB)</label><input id="photo-file" type="file" accept="image/png,image/jpeg,image/webp"><img id="photo-preview" class="photo-preview" alt="Selected photo preview" hidden></div>',
    '<label class="field"><span><input type="checkbox" name="remove"> Remove current photo</span></label>']};
  showForm(forms[kind] || forms.person, kind);
}
function showForm(config, kind) {
  modalForm.dataset.photoData = "";
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

let saving = false;
let searchGeneration = 0;
function feedback(message, error = false) {
  const box = document.querySelector("#feedback");
  box.textContent = message;
  box.classList.toggle("error", error);
}
function dossierTabs() {
  return `<div class="tabbar">${[["dossier", "Dossier"], ["interactions", "Timeline"], ["signals", "Intel"], ["opportunities", "Opportunities"], ["connections", "Relationships"], ["contacts", "Contact"]].map(([id, title]) => `<button class="tab ${state.dossierTab === id ? "active" : ""}" data-tab="${id}">${title}</button>`).join("")}</div>`;
}
function backToPeople() { return `<button class="action-link back-link" id="back-to-people">← Back to People</button>`; }
function completeButton(item) {
  return `<button class="action-link" data-complete="${escapeHtml(item.id)}" data-kind="${escapeHtml(item.kind)}">Complete follow-up</button>`;
}
function renderFollowUp(item) {
  return `<div class="record-row follow-up-row"><div>${escapeHtml(item.action || item.title)}<div class="muted">${escapeHtml(item.follow_up_date || "Unscheduled")}</div></div>${completeButton(item)}</div>`;
}
modalForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (saving) return;
  const payload = Object.fromEntries(new FormData(modalForm).entries());
  if (modalForm.querySelector('[name="tag_choice"]') || ["person", "edit"].includes(modalForm.dataset.kind)) payload.tags = new FormData(modalForm).getAll("tag_choice");
  delete payload.tag_choice;
  if (modalForm.dataset.kind === "interaction") payload.people = new FormData(modalForm).getAll("participants");
  delete payload.participants;
  if (modalForm.dataset.photoData) payload.data = modalForm.dataset.photoData;
  if (payload.person_id) { payload.people = [payload.person_id]; delete payload.person_id; }
  const endpoint = modalForm.dataset.endpoint.replace("__subject__", encodeURIComponent(payload.subject_id || ""));
  const method = modalForm.dataset.method;
  saving = true;
  modalForm.querySelector('[type="submit"]').disabled = true;
  try {
    const result = await api(endpoint, { method, body: JSON.stringify(payload) });
    if (endpoint === "/api/people" && method === "POST") {
      searchInput.value = "";
      state.selectedPersonId = result.person_id;
      state.activeView = "people";
      state.peopleMode = "profile";
      state.directorySearch = "";
      state.dossierTab = "dossier";
    }
    feedback("Saved successfully.");
    try { await load(); } catch (error) { feedback(`Saved, but refresh failed: ${error.message}. Reload to view the saved record.`, true); }
    closeModal();
  } catch (error) {
    const box = document.querySelector("#form-error");
    box.textContent = error.message;
    box.classList.remove("hidden");
  } finally {
    saving = false;
    const submit = modalForm.querySelector('[type="submit"]');
    if (submit) submit.disabled = false;
  }
});
document.addEventListener("click", async (event) => {
  const button = event.target.closest("button");
  if (!button || button.disabled) return;
  try {
    if (button.id === "create-inline-tag") {
      const name = modalForm.querySelector("#new-tag-name").value;
      const tag = await api("/api/tags", {method:"POST",body:JSON.stringify({name})});
      state.catalog = await api("/api/catalog");
      const chosen = new FormData(modalForm).getAll("tag_choice"); chosen.push(tag.name);
      modalForm.querySelector("#tag-picker").outerHTML = tagPicker(chosen); return;
    }
    if (button.dataset.createType) {
      const kind = button.dataset.createType;
      const label = modalForm.querySelector("#custom-" + kind).value;
      const type = await api("/api/types/" + kind, {method:"POST",body:JSON.stringify({label})});
      state.catalog = await api("/api/catalog");
      const selectElement = modalForm.querySelector('[name="' + kind + '_type"]');
      selectElement.innerHTML = state.catalog[kind].map(t=>`<option value="${escapeHtml(t.label)}">${escapeHtml(t.label)}</option>`).join("");
      selectElement.value = type.label; return;
    }
    if (button.dataset.sectionAction) { await openSection(button.dataset.sectionAction, button.dataset.section); return; }
    if (button.dataset.context) {
      const key = button.dataset.context;
      showForm({title:`Edit ${button.dataset.label}`, endpoint:`/api/people/${state.selectedPersonId}`, method:"PATCH",
        fields:[field(key,button.dataset.label,"textarea",false,state.selectedDossier.person[key])]}, "context"); return;
    }
    if (button.id === "nav-toggle") { setNavigation(!document.body.classList.contains("nav-collapsed")); return; }
    if (button.id === "new-toggle") { const menu = document.querySelector("#new-menu"); menu.classList.toggle("hidden"); button.setAttribute("aria-expanded", String(!menu.classList.contains("hidden"))); return; }
    if (button.id === "modal-close" || button.id === "form-cancel") { if (!saving) closeModal(); return; }
    if (button.id === "back-to-people") { state.peopleMode = "directory"; render(); return; }
    if (button.dataset.person) {
      state.selectedPersonId = button.dataset.person;
      state.activeView = "people";
      state.peopleMode = "profile";
      state.dossierTab = "dossier";
      document.querySelector("#search-results").classList.add("hidden");
      await loadSelectedDossier(); render();
    } else if (button.dataset.tab) {
      state.dossierTab = button.dataset.tab; render();
    } else if (button.dataset.view) {
      state.activeView = button.dataset.view;
      if (state.activeView === "people") state.peopleMode = "directory";
      render();
    } else if (button.dataset.action) {
      const scoped = button.dataset.scope === "profile" || (state.activeView === "people" && state.peopleMode === "profile" && content.contains(button));
      openModal(button.dataset.action, scoped);
      document.querySelector("#new-menu").classList.add("hidden");
      document.querySelector("#new-toggle").setAttribute("aria-expanded", "false");
    } else if (button.dataset.complete) {
      button.disabled = true;
      await api(`/api/follow-ups/${encodeURIComponent(button.dataset.kind)}/${encodeURIComponent(button.dataset.complete)}/complete`, { method: "POST", body: "{}" });
      feedback("Follow-up completed."); await load();
    }
  } catch (error) { feedback(error.message, true); button.disabled = false; }
});
searchInput.addEventListener("input", () => {
  const results = document.querySelector("#search-results");
  results.classList.toggle("hidden", !searchInput.value.trim());
  results.innerHTML = peopleRows(matchingPeople(searchInput.value));
});
document.addEventListener("input", (event) => {
  if (event.target.id !== "directory-search") return;
  state.directorySearch = event.target.value;
  const rows = matchingPeople(state.directorySearch);
  document.querySelector("#people-list").innerHTML = peopleRows(rows);
  document.querySelector("#directory-count").textContent = `${rows.length} people`;
});
function setNavigation(collapsed) {
  document.body.classList.toggle("nav-collapsed", collapsed);
  const button = document.querySelector("#nav-toggle");
  button.setAttribute("aria-expanded", String(!collapsed));
  button.setAttribute("aria-label", collapsed ? "Expand navigation" : "Collapse navigation");
  button.title = button.getAttribute("aria-label");
  try { localStorage.setItem("netops.navCollapsed", JSON.stringify(collapsed)); } catch {}
}
try { setNavigation(localStorage.getItem("netops.navCollapsed") === "true"); } catch {}
document.querySelector(".brand").addEventListener("click", event => { event.preventDefault(); state.activeView = "dashboard"; render(); });

load().catch((error) => {
  content.innerHTML = `<div class="empty">NetworkOps could not load: ${escapeHtml(error.message)}</div>`;
});
async function openSection(action, id) {
  const section = (state.selectedDossier.sections || []).find(s=>s.section_id === id);
  const endpoint = `/api/people/${state.selectedPersonId}/sections${id ? "/" + id : ""}`;
  if (action === "history") {
    const rows = await api(endpoint + "/history");
    showForm({title:"Section history", endpoint:"", method:"GET", fields:rows.map(r=>`<article class="field full document-body"><h4>${escapeHtml(r.title)}</h4><div class="muted">Preserved before ${escapeHtml(r.recorded_at)}</div>${r.html}</article>`)}, "history");
    modalForm.querySelector('[type="submit"]').remove(); return;
  }
  const node = document.createElement("div"); node.innerHTML = section?.html || "";
  document.body.append(node); const plain = node.innerText; node.remove();
  showForm({title:action === "add" ? "Add section" : action === "append" ? "Append to section" : "Edit section", endpoint, method:id ? "PATCH" : "POST", fields:[
    field("title","Section title","text",true,section?.title),
    field("body",action === "append" ? "Addition" : "Section text","textarea",true,action === "edit" ? plain : ""),
    `<input type="hidden" name="revision" value="${section?.revision || 0}">${action === "append" ? '<input type="hidden" name="append" value="1">' : ""}`,
    '<p class="muted field full">Write ordinary prose. Edits save plain text; previous content and formatting remain available in section history.</p>'
  ]}, "section");
}
modalForm.addEventListener("change", event=>{
  if (event.target.id !== "photo-file") return;
  const file = event.target.files[0]; if (!file) return;
  const reader = new FileReader();
  reader.onload = () => { modalForm.dataset.photoData = String(reader.result).split(",")[1]; const preview = document.querySelector("#photo-preview"); preview.src = reader.result; preview.hidden = false; };
  reader.readAsDataURL(file);
});
function typePicker(kind, name, label, value = "") {
  return select(name,label,(state.catalog?.[kind] || []).map(t=>t.label), value) + `<div class="field"><label for="custom-${kind}">Custom ${label.toLowerCase()}</label><div class="inline-create"><input id="custom-${kind}" placeholder="New reusable type"><button class="action-link" type="button" data-create-type="${kind}">Create type</button></div></div>`;
}
function tagPicker(chosen) {
  const selected = new Set(chosen.map(t=>t.toLowerCase()));
  return `<fieldset class="field full" id="tag-picker"><legend>Tags</legend><label for="tag-search">Search tags</label><input id="tag-search" type="search"><div class="choice-list">${(state.catalog?.tags || []).map(t=>`<label class="tag-choice"><input name="tag_choice" type="checkbox" value="${escapeHtml(t.name)}" ${selected.has(t.name.toLowerCase()) ? "checked" : ""}> ${escapeHtml(t.name)}</label>`).join("")}</div><label for="new-tag-name">New tag name</label><div class="inline-create"><input id="new-tag-name"><button type="button" class="action-link" id="create-inline-tag">Create tag</button></div></fieldset>`;
}
function renderTags() {
  content.innerHTML = `<div class="page-heading"><h1>Tags</h1><button class="primary-button" data-action="tag">+ New Tag</button></div><section class="panel">${(state.catalog?.tags || []).map(t=>`<div class="record-row"><div><span class="tag-chip">${escapeHtml(t.name)}</span><p class="muted">${t.usage} people</p></div></div>`).join("") || '<p>No tags yet.</p>'}</section>`;
}
modalForm.addEventListener("input", event=>{
  if (event.target.id === "tag-search") for (const label of modalForm.querySelectorAll(".tag-choice")) label.hidden = !label.textContent.toLowerCase().includes(event.target.value.toLowerCase());
});
function localToday() { const now = new Date(); return [now.getFullYear(), String(now.getMonth()+1).padStart(2,"0"), String(now.getDate()).padStart(2,"0")].join("-"); }
function participantPicker(chosen) {
  return `<fieldset class="field full"><legend>Participants</legend><label for="participant-search">Search participants</label><input id="participant-search" type="search"><div class="choice-list">${state.people.map(p=>`<label class="participant-choice"><input type="checkbox" name="participants" value="${p.person_id}" ${chosen.includes(p.person_id) ? "checked" : ""}> ${escapeHtml(p.name)}${p.organization ? " · " + escapeHtml(p.organization) : ""}</label>`).join("")}</div></fieldset>`;
}
modalForm.addEventListener("input", event=>{
  if (event.target.id === "participant-search") for (const label of modalForm.querySelectorAll(".participant-choice")) label.hidden = !label.textContent.toLowerCase().includes(event.target.value.toLowerCase());
});
