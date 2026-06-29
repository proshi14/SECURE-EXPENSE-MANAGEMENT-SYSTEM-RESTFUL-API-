const apiBase = "";
const appState = {
    token: null,
    currentExpenseId: null,
    page: 1,
    limit: 10,
};

const elements = {
    authSection: document.getElementById("auth-section"),
    mainSection: document.getElementById("main-section"),
    messageBox: document.getElementById("message"),
    currentUser: document.getElementById("current-user"),
    logoutButton: document.getElementById("logout-button"),
    loginForm: document.getElementById("login-form"),
    registerForm: document.getElementById("register-form"),
    expenseForm: document.getElementById("expense-form"),
    cancelEditButton: document.getElementById("cancel-edit"),
    filterForm: document.getElementById("filter-form"),
    clearFiltersButton: document.getElementById("clear-filters"),
    tableBody: document.getElementById("expense-table-body"),
    expenseCount: document.getElementById("expense-count"),
    pageLabel: document.getElementById("page-label"),
    prevPage: document.getElementById("prev-page"),
    nextPage: document.getElementById("next-page"),
    summaryTotal: document.getElementById("summary-total"),
    summaryTransactions: document.getElementById("summary-transactions"),
    summaryHighest: document.getElementById("summary-highest"),
    summaryTopCategory: document.getElementById("summary-top-category"),
    categoryBreakdown: document.getElementById("category-breakdown"),
    monthlySummary: document.getElementById("monthly-summary"),
    exportExcel: document.getElementById("export-excel"),
    exportPdf: document.getElementById("export-pdf"),
};

function showMessage(text, type = "success") {
    const message = typeof text === "object"
        ? JSON.stringify(text, null, 2)
        : String(text);

    elements.messageBox.textContent = message;
    elements.messageBox.className = `message ${type}`;
    elements.messageBox.classList.remove("hidden");
    window.clearTimeout(showMessage.hideTimeout);
    showMessage.hideTimeout = window.setTimeout(() => {
        elements.messageBox.classList.add("hidden");
    }, 5000);
}

function normalizeErrorMessage(message) {
    if (message === null || message === undefined) {
        return "An unknown error occurred.";
    }
    if (typeof message === "string") {
        return message;
    }
    if (Array.isArray(message)) {
        return message
            .map((item) => normalizeErrorMessage(item))
            .join("; ");
    }
    if (typeof message === "object") {
        if (message.detail) {
            return normalizeErrorMessage(message.detail);
        }
        return JSON.stringify(message, null, 2);
    }
    return String(message);
}

function setSession(token, email) {
    appState.token = token;
    localStorage.setItem("expense_tracker_token", token);
    localStorage.setItem("expense_tracker_user", email);
    elements.authSection.classList.add("hidden");
    elements.mainSection.classList.remove("hidden");
    elements.logoutButton.classList.remove("hidden");
    elements.currentUser.textContent = `Signed in as ${email}`;
}

function clearSession() {

    appState.token = null;
    appState.currentExpenseId = null;

    localStorage.removeItem(
        "expense_tracker_token"
    );

    localStorage.removeItem(
        "expense_tracker_user"
    );

    elements.authSection.classList.remove(
        "hidden"
    );

    elements.mainSection.classList.add(
        "hidden"
    );

    elements.logoutButton.classList.add(
        "hidden"
    );

    elements.currentUser.textContent = "";

    resetExpenseForm();
}

function getAuthHeaders() {
    if (!appState.token) {
        return {};
    }
    return {
        Authorization: `Bearer ${appState.token}`,
        "Content-Type": "application/json",
    };
}

function buildQueryString(params) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== "") {
            query.append(key, value);
        }
    });
    return query.toString() ? `?${query.toString()}` : "";
}

async function request(path, options = {}) {
    const headers = options.headers || {};
    Object.assign(headers, getAuthHeaders());
    if (!headers["Content-Type"]) {
        headers["Content-Type"] = "application/json";
    }
    const response = await fetch(`${apiBase}${path}`, {
        ...options,
        headers,
    });
    if (!response.ok) {
        const errorText = await response.text();
        let message = errorText;
        try {
            const payload = JSON.parse(errorText);
            message = normalizeErrorMessage(payload.detail ?? payload);
        } catch {
            message = normalizeErrorMessage(errorText);
        }
        throw new Error(message || `Request failed: ${response.status}`);
    }
    return response;
}

async function login(event) {
    event.preventDefault();
    const email = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-password").value;
    try {
        const response = await request("/users/login", {
            method: "POST",
            body: JSON.stringify({ email, password }),
        });
        const data = await response.json();
        setSession(data.access_token, email);
        showMessage("Login successful.");
        await refreshData();
    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function registerUser(event) {
    event.preventDefault();
    const username = document.getElementById("register-username").value.trim();
    const email = document.getElementById("register-email").value.trim();
    const password = document.getElementById("register-password").value;
    try {
        await request("/users/register", {
            method: "POST",
            body: JSON.stringify({ username, email, password }),
        });
        showMessage("Registration succeeded. Please log in.");
        document.getElementById("register-form").reset();
    } catch (error) {
        console.error(error);
        showMessage(normalizeErrorMessage(error.message || "Registration failed"), "error");
    }
}

async function saveExpense(event) {

    event.preventDefault();

    const payload = {

        title:
            document
            .getElementById(
                "expense-title"
            )
            .value
            .trim(),

        amount: Number(
            document
            .getElementById(
                "expense-amount"
            )
            .value
        ),

        category:
            document
            .getElementById(
                "expense-category"
            )
            .value,

        date:
            document
            .getElementById(
                "expense-date"
            )
            .value
            ||
            new Date()
                .toISOString()
                .split("T")[0]
    };

    try {

        if (
            appState.currentExpenseId
        ) {

            await request(
                `/expenses/${appState.currentExpenseId}`,
                {
                    method: "PUT",
                    body: JSON.stringify(
                        payload
                    )
                }
            );

            showMessage(
                "Expense Updated"
            );

        } else {

            await request(
                "/expenses/",
                {
                    method: "POST",
                    body: JSON.stringify(
                        payload
                    )
                }
            );

            showMessage(
                "Expense Added"
            );
        }

        resetExpenseForm();

        await refreshData();

    } catch (error) {

        showMessage(
            error.message,
            "error"
        );
    }
}

async function loadExpenses() {
    const keyword = document.getElementById("filter-keyword").value.trim();
    const category = document.getElementById("filter-category").value;
    const sort = document.getElementById("filter-sort").value;
    const start_date = document.getElementById("filter-start-date").value;
    const end_date = document.getElementById("filter-end-date").value;
    const query = buildQueryString({ keyword, category, sort, start_date, end_date, page: appState.page, limit: appState.limit });
    try {
        const response = await request(`/expenses/${query}`);
        const expenses = await response.json();
        renderExpenses(expenses);
    } catch (error) {
        showMessage(error.message, "error");
    }
}

function renderExpenses(expenses) {

    elements.tableBody.innerHTML = "";

    if (!expenses || expenses.length === 0) {

        elements.tableBody.innerHTML = `
            <tr>
                <td colspan="5">
                    No expenses found
                </td>
            </tr>
        `;

        elements.expenseCount.textContent = "0 Expenses";

        return;
    }

    expenses.forEach((expense) => {

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${expense.date}</td>
            <td>${expense.title}</td>
            <td>${expense.category}</td>
            <td>₹${Number(expense.amount).toFixed(2)}</td>

            <td>

                <button
                    class="secondary-button"
                    data-action="edit"
                    data-id="${expense.id}">
                    Edit
                </button>

                <button
                    class="secondary-button"
                    data-action="delete"
                    data-id="${expense.id}">
                    Delete
                </button>

            </td>
        `;

        elements.tableBody.appendChild(row);
    });

    elements.expenseCount.textContent =
        `${expenses.length} Expenses`;

    elements.pageLabel.textContent =
        `Page ${appState.page}`;
}
async function fetchReport(path) {
    const response = await request(path);
    return response.json();
}

function populateReport(section, data, formatter) {
    section.innerHTML = "";
    if (!data || Object.keys(data).length === 0) {
        section.innerHTML = `<li>No data available</li>`;
        return;
    }
    Object.entries(data).forEach(([key, value]) => {
        const item = document.createElement("li");
        item.textContent = formatter ? formatter(key, value) : `${key}: $${value.toFixed(2)}`;
        section.appendChild(item);
    });
}

async function loadReports() {

    try {

        const dashboard =
            await fetchReport(
                "/summary/dashboard"
            );

        elements.summaryTotal.textContent =
            `₹${dashboard.total_expenses || 0}`;

        elements.summaryTransactions.textContent =
            dashboard.total_transactions || 0;

        elements.summaryHighest.textContent =
            `₹${dashboard.highest_expense || 0}`;

        elements.summaryTopCategory.textContent =
            dashboard.top_category || "None";

        const byCategory =
            await fetchReport(
                "/summary/category"
            );

        populateReport(
            elements.categoryBreakdown,
            byCategory,
            (key, value) =>
                `${key}: ₹${value}`
        );

        const monthly =
            await fetchReport(
                "/summary/monthly"
            );

        populateReport(
            elements.monthlySummary,
            monthly,
            (key, value) =>
                `${key}: ₹${value}`
        );

    } catch (error) {

        console.error(error);

    }
}

async function refreshData() {

    try {

        await Promise.all([
            loadExpenses(),
            loadReports()
        ]);

    } catch (error) {

        showMessage(
            error.message,
            "error"
        );
    }
}
async function handleTableAction(event) {
    const button = event.target.closest("button");
    if (!button) {
        return;
    }
    const id = button.dataset.id;
    const action = button.dataset.action;
    if (action === "edit") {
        await startEditExpense(id);
    } else if (action === "delete") {
        await deleteExpense(id);
    }
}

async function startEditExpense(id) {
    try {
        const response = await request(`/expenses/${id}`);
        const expense = await response.json();
        document.getElementById("expense-title").value = expense.title;
        document.getElementById("expense-amount").value = expense.amount;
        document.getElementById("expense-category").value = expense.category;
        document.getElementById("expense-date").value = expense.date;
        appState.currentExpenseId = id;
        elements.cancelEditButton.classList.remove("hidden");
        showMessage("Editing expense. Update the form and save.");
    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function deleteExpense(id) {
    if (!confirm("Delete this expense permanently?")) {
        return;
    }
    try {
        await request(`/expenses/${id}`, { method: "DELETE" });
        showMessage("Expense deleted.");
        await refreshData();
    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function exportReport(type) {

    try {

        const response =
            await request(
                `/export/${type}`
            );

        const blob =
            await response.blob();

        const url =
            window.URL.createObjectURL(
                blob
            );

        const link =
            document.createElement("a");

        link.href = url;

        link.download =
            type === "excel"
            ? "expenses.xlsx"
            : "expenses.pdf";

        document.body.appendChild(
            link
        );

        link.click();

        link.remove();

        showMessage(
            `${type.toUpperCase()} downloaded`
        );

    } catch (error) {

        showMessage(
            error.message,
            "error"
        );
    }
}
function restoreSession() {
    const token = localStorage.getItem("expense_tracker_token");
    const email = localStorage.getItem("expense_tracker_user");
    if (token && email) {
        appState.token = token;
        setSession(token, email);
        refreshData().catch(() => {
            clearSession();
        });
    }
}

function resetExpenseForm() {
    appState.currentExpenseId = null;
    elements.cancelEditButton.classList.add("hidden");
    elements.expenseForm.reset();
}

function clearFilters() {
    document.getElementById("filter-keyword").value = "";
    document.getElementById("filter-category").value = "";
    document.getElementById("filter-sort").value = "";
    document.getElementById("filter-start-date").value = "";
    document.getElementById("filter-end-date").value = "";
    appState.page = 1;
}

async function initialize() {
    elements.loginForm.addEventListener("submit", login);
    elements.registerForm.addEventListener("submit", registerUser);
    elements.expenseForm.addEventListener("submit", saveExpense);
    elements.cancelEditButton.addEventListener("click", () => {
        resetExpenseForm();
    });
    elements.filterForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        appState.page = 1;
        await loadExpenses();
    });
    elements.clearFiltersButton.addEventListener("click", async () => {
        clearFilters();
        await loadExpenses();
    });
    elements.exportExcel.addEventListener("click", () => exportReport("excel"));
    elements.exportPdf.addEventListener("click", () => exportReport("pdf"));
    elements.prevPage.addEventListener("click", async () => {
        if (appState.page > 1) {
            appState.page -= 1;
            await loadExpenses();
        }
    });
    elements.nextPage.addEventListener("click", async () => {
        appState.page += 1;
        await loadExpenses();
    });
    document.querySelector(".expense-table tbody").addEventListener("click", handleTableAction);
    elements.logoutButton.addEventListener("click", () => {
        clearSession();
        showMessage("Logged out.");
    });
    restoreSession();
}

initialize();
