// =============================
// Guard against duplicate document-level
// listeners when this script re-executes
// after an HTMX navigation to this page.
// =============================

if (!window.__quotationJsBound) {
    window.__quotationJsBound = true;

    // =============================
    // Remove Row
    // =============================
    document.addEventListener("click", function (e) {
        if (e.target.classList.contains("removeRow")) {
            let rows = document.querySelectorAll("#quotationBody tr");
            if (rows.length > 1) {
                e.target.closest("tr").remove();
                calculateTotals();
            }
        }
    });

    // =============================
    // Service Change (autofill description / HSN / rate)
    // =============================
    document.addEventListener("change", function (e) {
        if (e.target.classList.contains("service")) {
            const row = e.target.closest("tr");
            const option = e.target.options[e.target.selectedIndex];

            if (!option || option.value === "") {
                return;
            }

            const name = option.getAttribute("data-name") || "";
            const price = option.getAttribute("data-price") || "";
            const hsn = option.getAttribute("data-hsn") || "";

            const descField = row.querySelector(".description");
            if (descField && descField.value.trim() === "") {
                descField.value = name;
            }

            const hsnField = row.querySelector(".hsn");
            if (hsnField && hsnField.value.trim() === "") {
                hsnField.value = hsn;
            }

            const rateField = row.querySelector(".rate");
            if (rateField && rateField.value.trim() === "") {
                rateField.value = price;
            }

            calculateRow(row);
        }
    });

    // =============================
    // Qty / Rate Change
    // =============================
    document.addEventListener("keyup", function (e) {
        if (e.target.classList.contains("qty") || e.target.classList.contains("rate")) {
            calculateRow(e.target.closest("tr"));
        }
    });

    document.addEventListener("change", function (e) {
        if (e.target.classList.contains("qty") || e.target.classList.contains("rate")) {
            calculateRow(e.target.closest("tr"));
        }
    });
}

// =============================
// Add New Row
// (element-scoped listener — safe to rebind
//  each time this element is freshly rendered)
// =============================

const addRowBtn = document.getElementById("addRow");

if (addRowBtn) {
    addRowBtn.addEventListener("click", function () {

        const tbody = document.getElementById("quotationBody");
        const row = tbody.rows[0].cloneNode(true);

        row.querySelector(".service").selectedIndex = 0;
        row.querySelector(".description").value = "";
        row.querySelector(".hsn").value = "";
        row.querySelector(".qty").value = 1;
        row.querySelector(".rate").value = "";
        row.querySelector(".amount").value = "";

        tbody.appendChild(row);
    });
}

// =============================
// Row Calculation
// =============================

function calculateRow(row) {

    let qty = parseFloat(row.querySelector(".qty").value) || 0;
    let rate = parseFloat(row.querySelector(".rate").value) || 0;

    let amount = qty * rate;

    row.querySelector(".amount").value = amount.toFixed(2);

    calculateTotals();
}

// =============================
// Grand Total
// =============================

function calculateTotals() {

    let subtotal = 0;

    document.querySelectorAll("#quotationBody tr").forEach(function (row) {
        let qty = parseFloat(row.querySelector(".qty").value) || 0;
        let rate = parseFloat(row.querySelector(".rate").value) || 0;
        subtotal += qty * rate;
    });

    let taxRate = getActiveTaxRate();
    let taxDue = subtotal * taxRate / 100;

    let otherField = document.getElementById("id_other_charges");
    let other = otherField ? (parseFloat(otherField.value) || 0) : 0;

    let grandTotal = subtotal + taxDue + other;

    document.getElementById("subtotal").value = subtotal.toFixed(2);
    document.getElementById("taxDue").value = taxDue.toFixed(2);
    document.getElementById("grandTotal").value = grandTotal.toFixed(2);
}

function getActiveTaxRate() {

    const gstSelect = document.getElementById("id_gst");
    const manualInput = document.getElementById("manualTaxRate");

    if (gstSelect && gstSelect.value) {
        const dataEl = document.getElementById("gst-rates-data");
        if (dataEl) {
            try {
                const rates = JSON.parse(dataEl.textContent);
                if (rates && Object.prototype.hasOwnProperty.call(rates, gstSelect.value)) {
                    return parseFloat(rates[gstSelect.value]) || 0;
                }
            } catch (err) {
                // fall through to manual value
            }
        }
    }

    return manualInput ? (parseFloat(manualInput.value) || 0) : 0;
}

// =============================
// GST select / manual tax rate / other charges change
// (element-scoped — safe to rebind each render)
// =============================

const gstSelectEl = document.getElementById("id_gst");
if (gstSelectEl) {
    gstSelectEl.addEventListener("change", calculateTotals);
}

const manualTaxRateEl = document.getElementById("manualTaxRate");
if (manualTaxRateEl) {
    manualTaxRateEl.addEventListener("keyup", calculateTotals);
    manualTaxRateEl.addEventListener("change", calculateTotals);
}

const otherChargesEl = document.getElementById("id_other_charges");
if (otherChargesEl) {
    otherChargesEl.addEventListener("keyup", calculateTotals);
    otherChargesEl.addEventListener("change", calculateTotals);
}
