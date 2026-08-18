// =============================
// Guard against duplicate document-level
// listeners when this script re-executes
// after an HTMX navigation to this page.
// =============================

if (!window.__invoiceJsBound) {
    window.__invoiceJsBound = true;

    // =============================
    // Remove Row
    // =============================
    document.addEventListener("click", function (e) {
        if (e.target.classList.contains("removeRow")) {
            let rows = document.querySelectorAll("#invoiceBody tr");
            if (rows.length > 1) {
                e.target.closest("tr").remove();
                calculateTotals();
            }
        }
    });

    // =============================
    // Service Change
    // =============================
    document.addEventListener("change", function (e) {
        if (e.target.classList.contains("service")) {
            const row = e.target.closest("tr");
            const serviceId = e.target.value;
            if (serviceId == "") {
                return;
            }
            fetch("/transaction/service/" + serviceId + "/")
                .then(response => response.json())
                .then(data => {
                    row.querySelector(".price").value = data.price;
                    row.querySelector(".gst").value = data.gst;
                    calculateRow(row);
                });
        }
    });

    // =============================
    // Quantity Change
    // =============================
    document.addEventListener("keyup", function (e) {
        if (e.target.classList.contains("qty")) {
            calculateRow(e.target.closest("tr"));
        }
    });

    document.addEventListener("change", function (e) {
        if (e.target.classList.contains("qty")) {
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

        const tbody = document.getElementById("invoiceBody");
        const row = tbody.rows[0].cloneNode(true);

        row.querySelector(".service").selectedIndex = 0;
        row.querySelector(".qty").value = 1;
        row.querySelector(".price").value = "";
        row.querySelector(".gst").value = "";
        row.querySelector(".gst_amount").value = "";
        row.querySelector(".total").value = "";

        tbody.appendChild(row);
    });
}

// =============================
// Row Calculation
// =============================

function calculateRow(row) {

    let qty = parseFloat(row.querySelector(".qty").value) || 0;
    let price = parseFloat(row.querySelector(".price").value) || 0;
    let gst = parseFloat(row.querySelector(".gst").value) || 0;

    let subtotal = qty * price;
    let gstAmount = subtotal * gst / 100;
    let total = subtotal + gstAmount;

    row.querySelector(".gst_amount").value = gstAmount.toFixed(2);
    row.querySelector(".total").value = total.toFixed(2);

    calculateTotals();
}

// =============================
// Grand Total
// =============================

function calculateTotals() {

    let subtotal = 0;
    let gstTotal = 0;
    let grandTotal = 0;

    document.querySelectorAll("#invoiceBody tr").forEach(function (row) {

        let qty = parseFloat(row.querySelector(".qty").value) || 0;
        let price = parseFloat(row.querySelector(".price").value) || 0;
        let gst = parseFloat(row.querySelector(".gst").value) || 0;

        subtotal += qty * price;
        gstTotal += (qty * price * gst / 100);
        grandTotal += parseFloat(row.querySelector(".total").value) || 0;
    });

    let discountField = document.getElementById("id_discount");
    let discount = 0;

    if (discountField) {
        discount = parseFloat(discountField.value) || 0;
    }

    grandTotal -= discount;

    document.getElementById("subtotal").value = subtotal.toFixed(2);
    document.getElementById("gstTotal").value = gstTotal.toFixed(2);
    document.getElementById("grandTotal").value = grandTotal.toFixed(2);
}

// =============================
// Discount Change
// (element-scoped — safe to rebind each render)
// =============================

let discountInput = document.getElementById("id_discount");

if (discountInput) {
    discountInput.addEventListener("keyup", calculateTotals);
    discountInput.addEventListener("change", calculateTotals);
}


