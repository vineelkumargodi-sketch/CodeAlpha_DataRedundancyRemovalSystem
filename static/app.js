async function loadStats() {
    try {
        const response = await fetch("/api/stats");

        if (!response.ok) {
            throw new Error("Failed to load statistics.");
        }

        const data = await response.json();

        document.getElementById("uniqueRecords").textContent =
            data.unique_records;

        document.getElementById("duplicateAttempts").textContent =
            data.duplicate_attempts;

        document.getElementById("validationEvents").textContent =
            data.validation_events;

    } catch (error) {
        console.error("Statistics loading error:", error);
    }
}


async function loadRecords() {
    try {
        const response = await fetch("/api/records");

        if (!response.ok) {
            throw new Error("Failed to load records.");
        }

        const data = await response.json();

        const tableBody =
            document.getElementById("recordsTableBody");

        tableBody.innerHTML = "";

        if (data.records.length === 0) {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td colspan="6" style="text-align:center;">
                    No records found.
                </td>
            `;

            tableBody.appendChild(row);
            return;
        }

        data.records.forEach(record => {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${record.id}</td>
                <td>${escapeHtml(record.name)}</td>
                <td>${escapeHtml(record.email)}</td>
                <td>${escapeHtml(record.phone || "-")}</td>
                <td class="verified">
                    ${record.verified ? "Verified" : "Unverified"}
                </td>
                <td>
                    ${new Date(record.created_at).toLocaleString()}
                </td>
            `;

            tableBody.appendChild(row);
        });

    } catch (error) {
        console.error("Records loading error:", error);
    }
}


async function submitRecord(event) {
    event.preventDefault();

    const resultBox =
        document.getElementById("result");

    const submitButton =
        document.getElementById("submitButton");

    const name =
        document.getElementById("name").value.trim();

    const email =
        document.getElementById("email").value.trim();

    const phone =
        document.getElementById("phone").value.trim();

    if (!name || !email) {
        resultBox.className = "result error";
        resultBox.textContent =
            "✕ Name and email are required.";
        return;
    }

    submitButton.disabled = true;
    submitButton.textContent = "Checking...";

    resultBox.className = "result hidden";
    resultBox.textContent = "";

    try {
        const response = await fetch("/api/records", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name: name,
                email: email,
                phone: phone
            })
        });

        const data = await response.json();

        // UNIQUE
        if (response.status === 201 && data.status === "UNIQUE") {

            resultBox.className = "result success";

            resultBox.textContent =
                "✓ Unique and verified record stored.";

            document.getElementById("recordForm").reset();
        }

        // EXACT DUPLICATE
        else if (
            response.status === 409 &&
            data.status === "REDUNDANT"
        ) {

            resultBox.className = "result warning";

            resultBox.textContent =
                "⚠ Duplicate record rejected.";
        }

        // POSSIBLE DUPLICATE
        else if (
            response.status === 409 &&
            data.status === "POSSIBLE_DUPLICATE"
        ) {

            resultBox.className = "result warning";

            resultBox.textContent =
                "⚠ Possible duplicate detected. " +
                "The record was not stored automatically.";
        }

        // INVALID DATA
        else if (
            response.status === 400 &&
            data.status === "INVALID"
        ) {

            resultBox.className = "result error";

            resultBox.textContent =
                "✕ " + (
                    data.message ||
                    "Invalid record."
                );
        }

        // OTHER ERROR
        else {

            resultBox.className = "result error";

            resultBox.textContent =
                "✕ " + (
                    data.message ||
                    "Unable to process the record."
                );
        }

        // Refresh dashboard after processing
        await loadDashboard();

    } catch (error) {

        console.error("Record submission error:", error);

        resultBox.className = "result error";

        resultBox.textContent =
            "✕ Unable to connect to the server.";

    } finally {

        submitButton.disabled = false;

        submitButton.textContent =
            "Verify & Save Record";
    }
}


function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


async function loadDashboard() {
    await Promise.all([
        loadStats(),
        loadRecords()
    ]);
}


document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("recordForm");

    if (form) {
        form.addEventListener(
            "submit",
            submitRecord
        );
    }

    loadDashboard();
});