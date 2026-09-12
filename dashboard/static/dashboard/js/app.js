
document.addEventListener("DOMContentLoaded", () => {

    /*
    * ============================================================
    * Inventory adjustment stock preview
    * ============================================================
    *
    * Shows:
    *
    *   Current Stock
    *   Projected Stock
    *
    * Also prevents the user from submitting a decrease that
    * would result in negative stock.
    *
    * Backend validation remains authoritative.
    * ============================================================
    */

    const inventoryProductField =
        document.getElementById("id_product");

    const inventoryAdjustmentTypeField =
        document.getElementById("id_adjustment_type");

    const inventoryQuantityField =
        document.getElementById("id_quantity");

    const inventoryCurrentStockField =
        document.getElementById("inventory-current-stock");

    const inventoryProjectedStockField =
        document.getElementById("inventory-projected-stock");

    const inventoryApplyButton =
        document.getElementById("inventory-apply-button");

    const inventoryStockError =
        document.getElementById("inventory-stock-error");

    const inventoryStockDataElement =
        document.getElementById(
            "inventory-product-stock-data"
        );

    if (
        inventoryProductField &&
        inventoryAdjustmentTypeField &&
        inventoryQuantityField &&
        inventoryCurrentStockField &&
        inventoryProjectedStockField &&
        inventoryApplyButton &&
        inventoryStockError &&
        inventoryStockDataElement
    ) {
        try {
            const inventoryProductStockData =
                JSON.parse(
                    inventoryStockDataElement.textContent
                );

            const clearInventoryStockError = () => {
                inventoryStockError.textContent = "";
                inventoryStockError.hidden = true;

                inventoryProjectedStockField.classList.remove(
                    "form-input-error"
                );
            };

            const showInventoryStockError = (message) => {
                inventoryStockError.textContent = message;
                inventoryStockError.hidden = false;

                inventoryProjectedStockField.classList.add(
                    "form-input-error"
                );
            };

            const updateInventoryStockPreview = () => {
                const productId =
                    inventoryProductField.value;

                const adjustmentType =
                    inventoryAdjustmentTypeField.value;

                const quantity =
                    Number(
                        inventoryQuantityField.value
                    );

                const product =
                    inventoryProductStockData[productId];

                clearInventoryStockError();

                /*
                * No product selected.
                */
                if (!product) {
                    inventoryCurrentStockField.value = "—";
                    inventoryProjectedStockField.value = "—";
                    inventoryApplyButton.disabled = true;
                    return;
                }

                const currentStock =
                    Number(product.stock);

                const unit =
                    product.unit || "";

                /*
                * Show current stock.
                */
                inventoryCurrentStockField.value =
                    `${currentStock.toLocaleString(
                        undefined,
                        {
                            maximumFractionDigits: 3,
                        }
                    )} ${unit}`;

                /*
                * Invalid quantity / adjustment.
                */
                if (
                    !Number.isFinite(quantity) ||
                    quantity <= 0 ||
                    !adjustmentType
                ) {
                    inventoryProjectedStockField.value = "—";
                    inventoryApplyButton.disabled = true;
                    return;
                }

                let projectedStock =
                    currentStock;

                /*
                * Calculate projected stock.
                */
                if (
                    adjustmentType === "INCREASE"
                ) {
                    projectedStock =
                        currentStock + quantity;
                } else if (
                    adjustmentType === "DECREASE"
                ) {
                    projectedStock =
                        currentStock - quantity;
                } else {
                    inventoryProjectedStockField.value = "—";
                    inventoryApplyButton.disabled = true;
                    return;
                }

                /*
                * Show projected stock.
                */
                inventoryProjectedStockField.value =
                    `${projectedStock.toLocaleString(
                        undefined,
                        {
                            maximumFractionDigits: 3,
                        }
                    )} ${unit}`;

                /*
                * Prevent negative projected stock.
                */
                if (projectedStock < 0) {
                    showInventoryStockError(
                        `Insufficient stock. Available: ` +
                        `${currentStock.toLocaleString(
                            undefined,
                            {
                                maximumFractionDigits: 3,
                            }
                        )} ${unit}.`
                    );

                    inventoryApplyButton.disabled = true;
                    return;
                }

                /*
                * Stock is valid.
                */
                inventoryApplyButton.disabled = false;
            };

            /*
            * Product changed.
            */
            inventoryProductField.addEventListener(
                "change",
                updateInventoryStockPreview
            );

            /*
            * Adjustment type changed.
            */
            inventoryAdjustmentTypeField.addEventListener(
                "change",
                updateInventoryStockPreview
            );

            /*
            * Quantity changed.
            */
            inventoryQuantityField.addEventListener(
                "input",
                updateInventoryStockPreview
            );

            /*
            * Initial state.
            */
            inventoryApplyButton.disabled = true;

            updateInventoryStockPreview();

        } catch (error) {
            console.error(
                "Unable to initialize inventory stock preview:",
                error
            );
        }
    }
        

    /*
     * ============================================================
     * Desktop sidebar collapse
     * ============================================================
     */

    const sidebar = document.querySelector(".sidebar");
    const sidebarToggle = document.querySelector(".sidebar-toggle");
    const mobileMenuButton = document.querySelector(
        ".mobile-menu-button"
    );

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener("click", () => {
            document.body.classList.toggle(
                "sidebar-collapsed"
            );

            const expanded =
                !document.body.classList.contains(
                    "sidebar-collapsed"
                );

            sidebarToggle.setAttribute(
                "aria-expanded",
                String(expanded)
            );
        });
    }


    /*
     * ============================================================
     * Mobile sidebar
     * ============================================================
     */

    if (mobileMenuButton && sidebar) {
        mobileMenuButton.addEventListener("click", () => {
            const isOpen =
                sidebar.classList.toggle(
                    "mobile-open"
                );

            mobileMenuButton.setAttribute(
                "aria-expanded",
                String(isOpen)
            );
        });
    }


    /*
     * ============================================================
     * KPI COUNT-UP ANIMATION
     * ============================================================
     *
     * This must run independently of the Sales POS.
     *
     * Dashboard:
     *   Revenue      → 0 → actual value
     *   Sales        → 0 → actual value
     *   Gross Profit → 0 → actual value
     *   Low Stock    → 0 → actual value
     * ============================================================
     */

    /* KPI count-up animation */
    const kpiValues = document.querySelectorAll(".kpi-value[data-count]");

    function animateKpiValue(element, index) {
        const rawValue = element.dataset.count;
        const target = parseFloat(rawValue);
        const decimals = parseInt(element.dataset.decimals || "0", 10);

        if (!Number.isFinite(target)) {
            console.warn("Invalid KPI value:", rawValue, element);
            return;
        }

        const duration = 1400;
        const delay = index * 120;
        const startTime = performance.now() + delay;

        function update(currentTime) {
            if (currentTime < startTime) {
                requestAnimationFrame(update);
                return;
            }

            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Smooth ease-out
            const eased = 1 - Math.pow(1 - progress, 3);
            const currentValue = target * eased;

            element.textContent = currentValue.toLocaleString(undefined, {
                minimumFractionDigits: decimals,
                maximumFractionDigits: decimals,
            });

            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                // Guarantee the exact final value
                element.textContent = target.toLocaleString(undefined, {
                    minimumFractionDigits: decimals,
                    maximumFractionDigits: decimals,
                });
            }
        }

        requestAnimationFrame(update);
    }

    kpiValues.forEach((element, index) => {
        animateKpiValue(element, index);
    });


    /*
     * ============================================================
     * Revenue chart
     * ============================================================
     */

    const chartDataElement =
        document.getElementById(
            "revenue-chart-data"
        );

    const revenueChartCanvas =
        document.getElementById(
            "revenueChart"
        );

    if (
        chartDataElement &&
        revenueChartCanvas &&
        typeof Chart !== "undefined"
    ) {
        try {
            const chartData = JSON.parse(
                chartDataElement.textContent
            );

            const labels = chartData.map(
                (item) => item.label
            );

            const revenue = chartData.map(
                (item) => item.revenue
            );


            /*
             * --------------------------------------------------------
             * Gradient for revenue area
             * --------------------------------------------------------
             */

            const ctx =
                revenueChartCanvas.getContext(
                    "2d"
                );

            const gradient =
                ctx.createLinearGradient(
                    0,
                    0,
                    0,
                    revenueChartCanvas.clientHeight
                );

            gradient.addColorStop(
                0,
                "rgba(157, 192, 139, 0.24)"
            );

            gradient.addColorStop(
                0.55,
                "rgba(157, 192, 139, 0.07)"
            );

            gradient.addColorStop(
                1,
                "rgba(157, 192, 139, 0)"
            );


            /*
             * --------------------------------------------------------
             * Create chart
             * --------------------------------------------------------
             */

            const revenueChart =
                new Chart(
                    revenueChartCanvas,
                    {
                        type: "line",

                        data: {
                            labels,

                            datasets: [
                                {
                                    label: "Revenue",

                                    data: revenue,

                                    fill: true,

                                    tension: 0.45,

                                    borderWidth: 3,

                                    borderColor:
                                        "#9DC08B",

                                    backgroundColor:
                                        gradient,

                                    pointRadius: 0,

                                    pointHoverRadius: 7,

                                    pointHoverBackgroundColor:
                                        "#C6F235",

                                    pointHoverBorderColor:
                                        "#EDF1D6",

                                    pointHoverBorderWidth: 2,
                                },
                            ],
                        },

                        options: {
                            responsive: true,

                            maintainAspectRatio: false,


                            /*
                             * ==================================================
                             * Entrance animation
                             * ==================================================
                             */

                            animation: {
                                duration: 2200,

                                easing:
                                    "easeOutQuart",

                                x: {
                                    duration: 2200,

                                    easing:
                                        "easeOutQuart",
                                },

                                y: {
                                    duration: 1800,

                                    delay: 250,

                                    easing:
                                        "easeOutCubic",
                                },

                                opacity: {
                                    duration: 1200,

                                    easing:
                                        "easeOutCubic",
                                },
                            },


                            /*
                             * ==================================================
                             * Interaction
                             * ==================================================
                             */

                            interaction: {
                                intersect: false,

                                mode: "index",
                            },


                            /*
                             * ==================================================
                             * Plugins
                             * ==================================================
                             */

                            plugins: {
                                legend: {
                                    display: false,
                                },

                                tooltip: {
                                    displayColors: false,

                                    backgroundColor:
                                        "rgba(20, 28, 22, 0.94)",

                                    borderColor:
                                        "rgba(198, 242, 53, 0.35)",

                                    borderWidth: 1,

                                    cornerRadius: 10,

                                    padding: 12,

                                    titleColor:
                                        "#EDF1D6",

                                    bodyColor:
                                        "#C6F235",

                                    callbacks: {
                                        label: (
                                            context
                                        ) => {
                                            const value =
                                                context
                                                    .parsed
                                                    .y ?? 0;

                                            return `Revenue: ${value.toLocaleString(
                                                undefined,
                                                {
                                                    minimumFractionDigits:
                                                        2,

                                                    maximumFractionDigits:
                                                        2,
                                                }
                                            )}`;
                                        },
                                    },
                                },
                            },


                            /*
                             * ==================================================
                             * Scales
                             * ==================================================
                             */

                            scales: {
                                x: {
                                    grid: {
                                        display: false,
                                    },

                                    ticks: {
                                        color:
                                            "#7E8B7B",
                                    },
                                },

                                y: {
                                    beginAtZero: true,

                                    grid: {
                                        color:
                                            "rgba(237, 241, 214, 0.08)",
                                    },

                                    ticks: {
                                        color:
                                            "#7E8B7B",

                                        callback:
                                            (value) =>
                                                Number(
                                                    value
                                                ).toLocaleString(),
                                    },
                                },
                            },
                        },
                    }
                );


            /*
             * ============================================================
             * Moving revenue glow
             * ============================================================
             */

            function animateRevenueGlow() {
                const chart =
                    revenueChart;

                const meta =
                    chart.getDatasetMeta(0);

                if (
                    !meta.data ||
                    !meta.data.length
                ) {
                    return;
                }

                const duration = 2600;

                const startTime =
                    performance.now();


                function animate(time) {
                    const elapsed =
                        time - startTime;

                    const progress =
                        Math.min(
                            elapsed /
                                duration,
                            1
                        );


                    /*
                     * Smooth ease-in-out.
                     */

                    const eased =
                        progress < 0.5
                            ? 2 *
                              progress *
                              progress
                            : 1 -
                              Math.pow(
                                  -2 *
                                      progress +
                                      2,
                                  2
                              ) /
                                  2;


                    /*
                     * Find the current position
                     * along the chart.
                     */

                    const index =
                        eased *
                        (meta.data.length - 1);

                    const lower =
                        Math.floor(index);

                    const upper =
                        Math.min(
                            lower + 1,
                            meta.data.length - 1
                        );

                    const localProgress =
                        index - lower;

                    const pointA =
                        meta.data[lower];

                    const pointB =
                        meta.data[upper];


                    const x =
                        pointA.x +
                        (pointB.x - pointA.x) *
                            localProgress;

                    const y =
                        pointA.y +
                        (pointB.y - pointA.y) *
                            localProgress;


                    /*
                     * Redraw chart.
                     */

                    chart.draw();


                    const context =
                        chart.ctx;


                    /*
                     * --------------------------------------------------------
                     * Soft outer glow
                     * --------------------------------------------------------
                     */

                    context.save();

                    const glow =
                        context.createRadialGradient(
                            x,
                            y,
                            0,
                            x,
                            y,
                            24
                        );

                    glow.addColorStop(
                        0,
                        "rgba(198, 242, 53, 0.45)"
                    );

                    glow.addColorStop(
                        0.35,
                        "rgba(157, 192, 139, 0.20)"
                    );

                    glow.addColorStop(
                        1,
                        "rgba(157, 192, 139, 0)"
                    );

                    context.fillStyle =
                        glow;

                    context.beginPath();

                    context.arc(
                        x,
                        y,
                        24,
                        0,
                        Math.PI * 2
                    );

                    context.fill();


                    /*
                     * --------------------------------------------------------
                     * Bright center
                     * --------------------------------------------------------
                     */

                    context.fillStyle =
                        "#C6F235";

                    context.shadowColor =
                        "rgba(198, 242, 53, 0.9)";

                    context.shadowBlur = 14;

                    context.beginPath();

                    context.arc(
                        x,
                        y,
                        3.5,
                        0,
                        Math.PI * 2
                    );

                    context.fill();

                    context.restore();


                    if (progress < 1) {
                        requestAnimationFrame(
                            animate
                        );
                    }
                }

                requestAnimationFrame(
                    animate
                );
            }


            /*
             * Wait for the main chart animation
             * before starting the moving glow.
             */

            setTimeout(
                animateRevenueGlow,
                2300
            );

        } catch (error) {
            console.error(
                "Unable to initialize revenue chart:",
                error
            );
        }
    }
    

    /*
     * ============================================================
     * Sales POS
     * ============================================================
     *
     * IMPORTANT:
     * The POS is optional on the dashboard.
     *
     * We return ONLY from the remaining POS code if the
     * POS elements don't exist.
     *
     * Sidebar, KPI animation and revenue chart have already
     * initialized above.
     * ============================================================
     */

    const productSearchInput =
        document.getElementById(
            "product-search"
        );

    const productSearchResults =
        document.getElementById(
            "sale-product-search-results"
        );

    const productSearchResultsBody =
        document.getElementById(
            "sale-product-search-results-body"
        );

    const selectedProductName =
        document.getElementById(
            "selected-product-name"
        );

    const addSaleItemButton =
        document.getElementById(
            "add-sale-item-button"
        );

    const saleItemForm =
        document.getElementById(
            "sale-item-form"
        );


    /*
     * Sales POS is not present on every page.
     *
     * Everything above this point continues to work.
     */

    if (
        !productSearchInput ||
        !productSearchResults ||
        !productSearchResultsBody ||
        !selectedProductName ||
        !addSaleItemButton ||
        !saleItemForm
    ) {
        return;
    }


    /*
     * ============================================================
     * Sales POS fields
     * ============================================================
     */

    const productField =
        document.getElementById(
            "id_product"
        );

    const quantityField =
        document.getElementById(
            "id_quantity"
        );

    const amountField =
        document.getElementById(
            "id_amount"
        );

    const quantityInput =
        document.getElementById(
            "sale-quantity-input"
        );

    const amountInput =
        document.getElementById(
            "sale-amount-input"
        );


    if (
        !productField ||
        !quantityField ||
        !amountField ||
        !quantityInput ||
        !amountInput
    ) {
        console.error(
            "Sales POS form elements are missing."
        );

        return;
    }


    /*
     * ============================================================
     * POS state
     * ============================================================
     */

    let selectedProduct = null;
    let searchTimeout = null;


    /*
     * ============================================================
     * Constants
     * ============================================================
     */

    const VALUE_BASED_UNITS = new Set([
        "kg",
        "g",
        "l",
        "ml",
    ]);

    const QUANTITY_DECIMAL_PLACES = 3;
    const MONEY_DECIMAL_PLACES = 2;

    const showStockError = (message) => {
        let errorElement =
            document.querySelector("#sale-stock-error");

        if (!errorElement) {
            errorElement = document.createElement("div");
            errorElement.id = "sale-stock-error";
            errorElement.className = "form-error";

            quantityField
                .closest(".form-group")
                ?.appendChild(errorElement);
        }

        errorElement.textContent = message;
        errorElement.hidden = false;
    };

    const clearStockError = () => {
        const errorElement =
            document.querySelector("#sale-stock-error");

        if (errorElement) {
            errorElement.textContent = "";
            errorElement.hidden = true;
        }
    };
    /*
     * ============================================================
     * Helpers
     * ============================================================
     */

    const isValueBasedUnit = (unit) => {
        if (!unit) {
            return false;
        }

        return VALUE_BASED_UNITS.has(
            unit.trim().toLowerCase()
        );
    };


    const roundQuantity = (value) => {
        return (
            Math.round(
                Number(value) * 1000
            ) / 1000
        );
    };


    const roundMoney = (value) => {
        return (
            Math.round(
                Number(value) * 100
            ) / 100
        );
    };


    const formatNumber = (value) => {
        const number = Number(value);

        if (!Number.isFinite(number)) {
            return "0";
        }

        return number.toLocaleString(
            undefined,
            {
                maximumFractionDigits:
                    QUANTITY_DECIMAL_PLACES,
            }
        );
    };


    const formatPrice = (value) => {
        const number = Number(value);

        if (!Number.isFinite(number)) {
            return "0.00";
        }

        return number.toLocaleString(
            undefined,
            {
                minimumFractionDigits:
                    MONEY_DECIMAL_PLACES,

                maximumFractionDigits:
                    MONEY_DECIMAL_PLACES,
            }
        );
    };


    const escapeHtml = (value) => {
        const element =
            document.createElement("div");

        element.textContent =
            value ?? "";

        return element.innerHTML;
    };


    const getSelectedUnit = () => {
        if (!selectedProduct) {
            return "";
        }

        return selectedProduct.unit
            .trim()
            .toLowerCase();
    };


    const getSelectedPrice = () => {
        if (!selectedProduct) {
            return NaN;
        }

        return Number(
            selectedProduct.price
        );
    };


    const getAvailableStock = () => {
        if (!selectedProduct) {
            return NaN;
        }

        return Number(
            selectedProduct.stock
        );
    };


    /*
     * ============================================================
     * POS validation
     * ============================================================
     */

    const clearFieldErrors = () => {
        quantityField.setCustomValidity("");
        amountField.setCustomValidity("");
    };


    const disableAddButton = () => {
        addSaleItemButton.disabled = true;
    };


    const enableAddButton = () => {
        addSaleItemButton.disabled = false;
    };


    const validateQuantityAgainstStock = () => {
        if (!selectedProduct) {
            clearStockError();
            disableAddButton();
            return false;
        }

        const quantity = Number(quantityField.value);
        const availableStock = getAvailableStock();

        quantityField.setCustomValidity("");
        clearStockError();

        if (
            !Number.isFinite(quantity) ||
            quantity <= 0
        ) {
            disableAddButton();
            return false;
        }

        if (!Number.isFinite(availableStock)) {
            const message =
                "Unable to determine available stock.";

            quantityField.setCustomValidity(message);
            showStockError(message);

            disableAddButton();
            return false;
        }

        if (quantity > availableStock) {
            const message =
                `Insufficient stock. Available: ` +
                `${selectedProduct.stock} ${selectedProduct.unit}. ` +
                `Requested: ${quantity} ${selectedProduct.unit}.`;

            quantityField.setCustomValidity(message);
            showStockError(message);

            disableAddButton();
            return false;
        }

        clearStockError();
        enableAddButton();
        return true;
    };


    const validateAmountBasedSale = () => {
        if (!selectedProduct) {
            disableAddButton();
            return false;
        }

        const amount =
            Number(amountField.value);

        const quantity =
            Number(quantityField.value);

        const availableStock =
            getAvailableStock();

        clearFieldErrors();

        if (
            !Number.isFinite(amount) ||
            amount <= 0
        ) {
            disableAddButton();
            return false;
        }

        if (
            !Number.isFinite(quantity) ||
            quantity <= 0
        ) {
            disableAddButton();
            return false;
        }

        if (
            !Number.isFinite(
                availableStock
            )
        ) {
            amountField.setCustomValidity(
                "Unable to determine available stock."
            );

            disableAddButton();
            return false;
        }

        if (
            quantity > availableStock
        ) {
            amountField.setCustomValidity(
                "The requested amount exceeds available stock."
            );

            disableAddButton();
            return false;
        }

        enableAddButton();
        return true;
    };


    /*
     * ============================================================
     * Value-based synchronization
     * ============================================================
     */

    const syncAmountFromQuantity = () => {
        if (!selectedProduct) {
            return;
        }

        const quantity =
            Number(quantityField.value);

        const price =
            getSelectedPrice();

        clearFieldErrors();

        if (
            !Number.isFinite(quantity) ||
            quantity <= 0
        ) {
            amountField.value = "";
            disableAddButton();
            return;
        }

        if (
            !Number.isFinite(price) ||
            price <= 0
        ) {
            amountField.value = "";

            quantityField.setCustomValidity(
                "This product does not have a valid selling price."
            );

            disableAddButton();
            return;
        }

        const amount =
            roundMoney(
                quantity * price
            );

        amountField.value =
            amount.toFixed(
                MONEY_DECIMAL_PLACES
            );

        validateAmountBasedSale();
    };


    const syncQuantityFromAmount = () => {
        if (!selectedProduct) {
            return;
        }

        const amount =
            Number(amountField.value);

        const price =
            getSelectedPrice();

        clearFieldErrors();

        if (
            !Number.isFinite(amount) ||
            amount <= 0
        ) {
            quantityField.value = "";
            disableAddButton();
            return;
        }

        if (
            !Number.isFinite(price) ||
            price <= 0
        ) {
            quantityField.value = "";

            amountField.setCustomValidity(
                "This product does not have a valid selling price."
            );

            disableAddButton();
            return;
        }

        const quantity =
            roundQuantity(
                amount / price
            );

        if (quantity <= 0) {
            quantityField.value = "";

            amountField.setCustomValidity(
                "The amount is too small to create a valid quantity."
            );

            disableAddButton();
            return;
        }

        quantityField.value =
            quantity.toFixed(
                QUANTITY_DECIMAL_PLACES
            );

        validateAmountBasedSale();
    };


    /*
     * ============================================================
     * Clear product selection
     * ============================================================
     */

    const clearProductSelection = () => {
        selectedProduct = null;

        productField.value = "";

        quantityField.value = "";
        amountField.value = "";

        selectedProductName.textContent =
            "No product selected.";

        quantityInput.hidden = false;
        amountInput.hidden = true;

        clearFieldErrors();

        disableAddButton();
    };


    /*
     * ============================================================
     * Select product
     * ============================================================
     */

    const selectProduct = (product) => {
        selectedProduct = product;

        productField.value =
            product.id;

        selectedProductName.textContent =
            `${product.name} — ${formatPrice(
                product.price
            )} / ${product.unit}`;

        productSearchInput.value =
            product.name;

        productSearchResults.hidden =
            true;

        productSearchResultsBody.innerHTML =
            "";

        quantityField.value = "";
        amountField.value = "";

        clearFieldErrors();

        const valueBasedProduct =
            isValueBasedUnit(
                product.unit
            );


        /*
         * Weight / volume product
         */

        if (valueBasedProduct) {
            quantityInput.hidden = false;
            amountInput.hidden = false;

            disableAddButton();

            quantityField.focus();

            return;
        }


        /*
         * Count-based product
         */

        quantityInput.hidden = false;
        amountInput.hidden = true;

        quantityField.value = "1";

        quantityField.focus();

        validateQuantityAgainstStock();
    };


    /*
     * ============================================================
     * Render product search results
     * ============================================================
     */

    const renderProductResults = (
        products
    ) => {
        productSearchResultsBody.innerHTML =
            "";

        if (!products.length) {
            productSearchResultsBody.innerHTML = `
                <tr>
                    <td colspan="4">
                        No products found.
                    </td>
                </tr>
            `;

            productSearchResults.hidden =
                false;

            return;
        }

        products.forEach(
            (product) => {
                const row =
                    document.createElement(
                        "tr"
                    );

                row.innerHTML = `
                    <td>
                        ${escapeHtml(
                            product.name
                        )}
                    </td>

                    <td>
                        ${formatNumber(
                            product.stock
                        )}
                        ${escapeHtml(
                            product.unit
                        )}
                    </td>

                    <td>
                        ${formatPrice(
                            product.price
                        )}
                    </td>

                    <td>
                        <button
                            type="button"
                            class="btn-secondary btn-small"
                            data-select-product
                        >
                            Select
                        </button>
                    </td>
                `;

                const selectButton =
                    row.querySelector(
                        "[data-select-product]"
                    );

                selectButton.addEventListener(
                    "click",
                    () => {
                        selectProduct(
                            product
                        );
                    }
                );

                productSearchResultsBody.appendChild(
                    row
                );
            }
        );

        productSearchResults.hidden =
            false;
    };


    /*
     * ============================================================
     * Product search
     * ============================================================
     */

    const searchProducts = async (
        query
    ) => {
        const searchUrl =
            productSearchInput.dataset
                .productSearchUrl;

        if (!searchUrl) {
            console.error(
                "Product search URL is missing."
            );

            return;
        }

        if (!query.trim()) {
            productSearchResults.hidden =
                true;

            productSearchResultsBody.innerHTML =
                "";

            return;
        }

        try {
            const url =
                `${searchUrl}?q=${encodeURIComponent(
                    query.trim()
                )}`;

            const response =
                await fetch(url, {
                    method: "GET",

                    headers: {
                        "X-Requested-With":
                            "XMLHttpRequest",
                    },
                });

            if (!response.ok) {
                throw new Error(
                    "Product search failed."
                );
            }

            const data =
                await response.json();

            renderProductResults(
                data.results || []
            );

        } catch (error) {
            console.error(
                "Product search error:",
                error
            );

            productSearchResultsBody.innerHTML = `
                <tr>
                    <td colspan="4">
                        Unable to search products.
                    </td>
                </tr>
            `;

            productSearchResults.hidden =
                false;
        }
    };


    /*
     * ============================================================
     * Search input
     * ============================================================
     */

    productSearchInput.addEventListener(
        "input",
        () => {
            const query =
                productSearchInput.value;

            clearProductSelection();

            clearTimeout(
                searchTimeout
            );

            searchTimeout =
                setTimeout(
                    () => {
                        searchProducts(
                            query
                        );
                    },
                    250
                );
        }
    );


    /*
     * ============================================================
     * Quantity input
     * ============================================================
     */

    quantityField.addEventListener(
        "input",
        () => {
            if (!selectedProduct) {
                return;
            }

            if (
                isValueBasedUnit(
                    getSelectedUnit()
                )
            ) {
                syncAmountFromQuantity();
                return;
            }

            validateQuantityAgainstStock();
        }
    );


    /*
     * ============================================================
     * Amount input
     * ============================================================
     */

    amountField.addEventListener(
        "input",
        () => {
            if (!selectedProduct) {
                return;
            }

            if (
                !isValueBasedUnit(
                    getSelectedUnit()
                )
            ) {
                return;
            }

            syncQuantityFromAmount();
        }
    );


    /*
     * ============================================================
     * Form submission
     * ============================================================
     */

    saleItemForm.addEventListener(
        "submit",
        (event) => {
            if (!selectedProduct) {
                event.preventDefault();

                productSearchInput.focus();

                return;
            }

            const valueBasedProduct =
                isValueBasedUnit(
                    getSelectedUnit()
                );


            /*
             * Value-based product
             */

            if (valueBasedProduct) {
                const valid =
                    validateAmountBasedSale();

                if (!valid) {
                    event.preventDefault();

                    if (
                        !amountField.checkValidity()
                    ) {
                        amountField.reportValidity();
                    } else {
                        quantityField.reportValidity();
                    }

                    return;
                }
            }


            /*
             * Count-based product
             */

            else {
                const valid =
                    validateQuantityAgainstStock();

                if (!valid) {
                    event.preventDefault();

                    quantityField.reportValidity();

                    return;
                }
            }


            /*
             * Final browser validation
             */

            if (
                !saleItemForm.checkValidity()
            ) {
                event.preventDefault();

                if (valueBasedProduct) {
                    amountField.reportValidity();
                } else {
                    quantityField.reportValidity();
                }

                return;
            }


            /*
             * Prevent duplicate submissions.
             */

            addSaleItemButton.disabled =
                true;

            addSaleItemButton.textContent =
                "Adding...";
        }
    );


    /*
     * ============================================================
     * Keyboard support
     * ============================================================
     */

    productSearchInput.addEventListener(
        "keydown",
        (event) => {
            if (event.key === "Escape") {
                productSearchInput.value = "";

                productSearchResults.hidden =
                    true;

                productSearchResultsBody.innerHTML =
                    "";

                clearProductSelection();

                return;
            }

            if (
                event.key === "Enter" &&
                selectedProduct
            ) {
                event.preventDefault();

                quantityField.focus();
            }
        }
    );


    quantityField.addEventListener(
        "keydown",
        (event) => {
            if (
                event.key === "Enter" &&
                !addSaleItemButton.disabled
            ) {
                event.preventDefault();

                saleItemForm.requestSubmit();
            }
        }
    );


    amountField.addEventListener(
        "keydown",
        (event) => {
            if (
                event.key === "Enter" &&
                !addSaleItemButton.disabled
            ) {
                event.preventDefault();

                saleItemForm.requestSubmit();
            }
        }
    );


    /*
     * ============================================================
     * Initial POS state
     * ============================================================
     */

    clearProductSelection();

});

