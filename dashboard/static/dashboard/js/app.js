
    /*
 * ============================================================
 * Global Helpers
 * ============================================================
 */

    function getCsrfToken() {
        const csrfInput =
            document.querySelector(
                "[name=csrfmiddlewaretoken]"
            );

        return csrfInput
            ? csrfInput.value
            : "";
    }

       const escapeHtml = (value) => {
        const element =
            document.createElement("div");

        element.textContent =
            value ?? "";

        return element.innerHTML;
    };



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
 * Also:
 *
 *   - Enforces whole-number quantities for count-based units.
 *   - Allows decimal quantities for measurement-based units.
 *   - Prevents decreases that would result in negative stock.
 *   - Keeps the submit button disabled when the input is invalid.
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

        /*
         * --------------------------------------------------------
         * Units that represent countable items.
         * These units only allow whole-number quantities.
         * --------------------------------------------------------
         */

        const INTEGER_UNITS = new Set([
            "pc",
            "pcs",
            "piece",
            "pieces",
            "box",
            "boxes",
            "pack",
            "packs",
            "bag",
            "bags",
            "bottle",
            "bottles",
            "can",
            "cans",
        ]);


        /*
         * --------------------------------------------------------
         * Unit helpers
         * --------------------------------------------------------
         */

        const isIntegerUnit = (unit) => {
            return INTEGER_UNITS.has(
                String(unit).trim().toLowerCase()
            );
        };


        const formatInventoryStock = (
            value,
            unit
        ) => {
            const numericValue = Number(value);

            if (isIntegerUnit(unit)) {
                return `${numericValue.toLocaleString(
                    undefined,
                    {
                        maximumFractionDigits: 0,
                    }
                )} ${unit}`;
            }

            return `${numericValue.toLocaleString(
                undefined,
                {
                    maximumFractionDigits: 3,
                }
            )} ${unit}`;
        };


        /*
         * --------------------------------------------------------
         * Error helpers
         * --------------------------------------------------------
         */

        const clearInventoryStockError = () => {
            inventoryStockError.textContent = "";
            inventoryStockError.hidden = true;

            inventoryProjectedStockField.classList.remove(
                "form-input-error"
            );

            inventoryQuantityField.classList.remove(
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


        /*
         * --------------------------------------------------------
         * Configure quantity input according to product unit.
         *
         * Count units:
         *   - text input
         *   - numeric keyboard on mobile
         *   - whole numbers only
         *
         * Measurement units:
         *   - number input
         *   - decimal keyboard
         *   - decimals allowed
         * --------------------------------------------------------
         */

        const configureInventoryQuantityInput = () => {
            const productId =
                inventoryProductField.value;

            const product =
                inventoryProductStockData[productId];

            if (!product) {
                inventoryQuantityField.type = "number";
                inventoryQuantityField.inputMode = "decimal";
                inventoryQuantityField.step = "0.001";
                inventoryQuantityField.min = "0.001";
                inventoryQuantityField.pattern = "";

                return;
            }

            const unit =
                product.unit || "";

            if (isIntegerUnit(unit)) {
                inventoryQuantityField.type = "text";
                inventoryQuantityField.inputMode = "numeric";
                inventoryQuantityField.pattern = "[0-9]*";
                inventoryQuantityField.step = "";
                inventoryQuantityField.min = "";
            } else {
                inventoryQuantityField.type = "number";
                inventoryQuantityField.inputMode = "decimal";
                inventoryQuantityField.step = "0.001";
                inventoryQuantityField.min = "0.001";
                inventoryQuantityField.pattern = "";
            }
        };


        /*
         * --------------------------------------------------------
         * Validate quantity format.
         *
         * Important:
         *
         * We do NOT modify invalid input.
         *
         * Example:
         *
         *   2.5 pcs
         *
         * remains 2.5 and is rejected.
         *
         * It is never silently changed to 2.
         * --------------------------------------------------------
         */

        const validateInventoryQuantity = () => {
            const productId =
                inventoryProductField.value;

            const product =
                inventoryProductStockData[productId];

            const rawQuantity =
                inventoryQuantityField.value.trim();

            inventoryQuantityField.classList.remove(
                "form-input-error"
            );

            if (!product || rawQuantity === "") {
                return true;
            }

            const unit =
                product.unit || "";

            if (isIntegerUnit(unit)) {
                if (!/^\d+$/.test(rawQuantity)) {
                    inventoryQuantityField.classList.add(
                        "form-input-error"
                    );

                    showInventoryStockError(
                        "This product only allows whole-number quantities."
                    );

                    return false;
                }
            }

            return true;
        };


        /*
         * --------------------------------------------------------
         * Update stock preview.
         * --------------------------------------------------------
         */

        const updateInventoryStockPreview = () => {
            const productId =
                inventoryProductField.value;

            const adjustmentType =
                inventoryAdjustmentTypeField.value;

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

                configureInventoryQuantityInput();

                return;
            }

            const currentStock =
                Number(product.stock);

            const unit =
                product.unit || "";

            /*
             * Configure quantity input for this unit.
             */

            configureInventoryQuantityInput();

            /*
             * Show current stock.
             */

            inventoryCurrentStockField.value =
                formatInventoryStock(
                    currentStock,
                    unit
                );

            /*
             * Validate quantity format.
             */

            if (!validateInventoryQuantity()) {
                inventoryProjectedStockField.value = "—";
                inventoryApplyButton.disabled = true;

                return;
            }

            /*
             * Convert quantity to number after
             * format validation has passed.
             */

            const quantity =
                Number(
                    inventoryQuantityField.value
                );

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

            /*
             * Calculate projected stock.
             */

            let projectedStock =
                currentStock;

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
                formatInventoryStock(
                    projectedStock,
                    unit
                );

            /*
             * Prevent negative projected stock.
             */

            if (projectedStock < 0) {
                showInventoryStockError(
                    `Insufficient stock. Available: ${formatInventoryStock(
                        currentStock,
                        unit
                    )}.`
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
         * --------------------------------------------------------
         * Product changed.
         * --------------------------------------------------------
         */

        inventoryProductField.addEventListener(
            "change",
            () => {
                configureInventoryQuantityInput();
                updateInventoryStockPreview();
            }
        );


        /*
         * --------------------------------------------------------
         * Adjustment type changed.
         * --------------------------------------------------------
         */

        inventoryAdjustmentTypeField.addEventListener(
            "change",
            updateInventoryStockPreview
        );


        /*
         * --------------------------------------------------------
         * Quantity changed.
         * --------------------------------------------------------
         */

        inventoryQuantityField.addEventListener(
            "input",
            updateInventoryStockPreview
        );


        /*
         * --------------------------------------------------------
         * Prevent invalid submission.
         *
         * The form may use novalidate, so we explicitly
         * validate before allowing submission.
         * --------------------------------------------------------
         */

        const inventoryForm =
            inventoryQuantityField.closest("form");

        if (inventoryForm) {
            inventoryForm.addEventListener(
                "submit",
                (event) => {
                    if (!validateInventoryQuantity()) {
                        event.preventDefault();

                        inventoryApplyButton.disabled = true;

                        inventoryQuantityField.focus();

                        return;
                    }

                    updateInventoryStockPreview();

                    if (
                        inventoryApplyButton.disabled
                    ) {
                        event.preventDefault();
                    }
                }
            );
        }


        /*
         * --------------------------------------------------------
         * Initial state.
         * --------------------------------------------------------
         */

        inventoryApplyButton.disabled = true;

        configureInventoryQuantityInput();

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
                                        title: (items) => {
                                            if (!items.length) {
                                                return "";
                                            }

                                            return items[0].label;
                                        },

                                        label: (context) => {
                                            const value =
                                                context.parsed.y ?? 0;

                                            return `Revenue: ${value.toLocaleString(
                                                undefined,
                                                {
                                                    minimumFractionDigits: 2,

                                                    maximumFractionDigits: 2,
                                                }
                                            )}`;
                                        },

                                        afterLabel: (context) => {
                                            const index =
                                                context.dataIndex;

                                            const item =
                                                chartData[index];

                                            if (!item) {
                                                return "";
                                            }

                                            return [
                                                `Sales: ${item.transactions.toLocaleString()}`,

                                                `Units sold: ${Number(
                                                    item.units_sold
                                                ).toLocaleString(
                                                    undefined,
                                                    {
                                                        maximumFractionDigits: 3,
                                                    }
                                                )}`,
                                            ];
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

                                        maxRotation: 0,

                                        autoSkip: false,
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

    let highlightedIndex = -1;
    let currentSearchResults = [];
    quantityField?.addEventListener(
        "keydown",
        (event) => {
            if (event.key === "Enter") {
                event.preventDefault();

                if (!addSaleItemButton.disabled) {
                    saleItemForm.requestSubmit();
                }
            }
        }
    );

    amountField?.addEventListener(
        "keydown",
        (event) => {
            if (event.key === "Enter") {
                event.preventDefault();

                if (!addSaleItemButton.disabled) {
                    saleItemForm.requestSubmit();
                }
            }
        }
    );

    const focusQuantityInput = () => {
        if (quantityInput.hidden) {
            amountField.focus();
        } else {
            quantityField.focus();
        }
    };

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

    const INTEGER_UNITS = new Set([
        "pc",
        "pcs",
        "piece",
        "pieces",
        "box",
        "boxes",
        "pack",
        "packs",
        "bag",
        "bags",
        "bottle",
        "bottles",
        "can",
        "cans",
    ]);

    const QUANTITY_DECIMAL_PLACES = 3;
    const MONEY_DECIMAL_PLACES = 2;

    const showQuantityError = (message) => {
        let errorElement =
            document.querySelector(
                "#sale-quantity-error"
            );

        if (!errorElement) {
            errorElement =
                document.createElement("div");

            errorElement.id =
                "sale-quantity-error";

            errorElement.className =
                "form-error";

            quantityField
                .closest(".form-group")
                ?.appendChild(
                    errorElement
                );
        }

        errorElement.textContent =
            message;

        errorElement.hidden = false;
    };


    const clearQuantityError = () => {
        const errorElement =
            document.querySelector(
                "#sale-quantity-error"
            );

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


    const isIntegerUnit = (unit) => {
        if (!unit) {
            return false;
        }

        return INTEGER_UNITS.has(
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

    const validateQuantityAgainstStock = () => {
        if (!selectedProduct) {
            clearStockError();
            disableAddButton();
            return false;
        }

        const quantityValue =
            quantityField.value.trim();

        const quantity =
            Number(quantityValue);

        const availableStock =
            getAvailableStock();

        const unit =
            getSelectedUnit();

        quantityField.setCustomValidity("");
        clearStockError();

        if (!quantityValue) {
            disableAddButton();
            return false;
        }

        if (!Number.isFinite(quantity)) {
            const message =
                saleItemForm.dataset.quantityInvalid;

            quantityField.setCustomValidity(message);
            showStockError(message);

            disableAddButton();
            return false;
        }

        if (quantity <= 0) {
            const message =
                saleItemForm.dataset.quantityPositive;

            quantityField.setCustomValidity(message);
            showStockError(message);

            disableAddButton();
            return false;
        }

        /*
        * Count-based units MUST be whole numbers.
        *
        * Example:
        * 1      -> valid
        * 2      -> valid
        * 1.5    -> invalid
        * 2.25   -> invalid
        */
        if (
            isIntegerUnit(unit) &&
            !Number.isInteger(quantity)
        ) {
            const message =
                saleItemForm.dataset.quantityWhole;

            quantityField.setCustomValidity(message);
            showStockError(message);

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

        quantityField.setCustomValidity("");
        clearStockError();

        enableAddButton();

        return true;
    };
    /*
     * ============================================================
     * Value-based synchronization
     * ============================================================
     */

    const validateAmountBasedSale = () => {
        if (!selectedProduct) {
            disableAddButton();
            return false;
        }

        const amount = Number(amountField.value);
        const quantity = Number(quantityField.value);
        const availableStock = getAvailableStock();

        clearFieldErrors();

        if (!Number.isFinite(amount) || amount <= 0) {
            disableAddButton();
            return false;
        }

        if (!Number.isFinite(quantity) || quantity <= 0) {
            disableAddButton();
            return false;
        }

        if (!Number.isFinite(availableStock)) {
            amountField.setCustomValidity(
                "Unable to determine available stock."
            );
            disableAddButton();
            return false;
        }

        if (quantity > availableStock) {
            amountField.setCustomValidity(
                "The requested amount exceeds available stock."
            );
            disableAddButton();
            return false;
        }

        enableAddButton();
        return true;
    };


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

        setTimeout(() => {
            focusQuantityInput();
        }, 50);

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
        if (isIntegerUnit(product.unit)) {
            quantityField.step = "1";
            quantityField.min = "1";
            quantityField.inputMode = "numeric";
        } else {
            quantityField.step = "0.001";
            quantityField.min = "0.001";
            quantityField.inputMode = "decimal";
        }


        /*
         * Weight / volume product
         */

        if (valueBasedProduct) {
            quantityInput.hidden = false;
            amountInput.hidden = false;

            disableAddButton();

            quantityField.focus();
            quantityField.select();

            return;
        }


        /*
         * Count-based product
         */

        quantityInput.hidden = false;
        amountInput.hidden = true;

        quantityField.value = "1";

        quantityField.focus();
        quantityField.select();

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
            currentSearchResults = products;
            highlightedIndex = -1;
            productSearchResultsBody.innerHTML = "";

            if (!products.length) {
                productSearchResultsBody.innerHTML = `
                    <tr>
                        <td colspan="4">
                            No products found.
                        </td>
                    </tr>
                `;

                productSearchResults.hidden = false;

                return;
            }

            products.forEach(
                (product, index) => {
                    const row =
                        document.createElement(
                            "tr"
                        );
                    row.dataset.index = index;
                    row.style.cursor = "pointer";

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
                            →
                        </td>
                    `;

                    row.addEventListener(
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

    const highlightRow = (index) => {
        const rows =
            productSearchResultsBody.querySelectorAll("tr");

        rows.forEach((row) => {
            row.classList.remove(
                "pos-highlight"
            );
        });

        if (
            index >= 0 &&
            rows[index]
        ) {
            rows[index].classList.add(
                "pos-highlight"
            );

            highlightedIndex = index;
        }
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

            /*
            * Measurement-based product
            */
            if (
                isValueBasedUnit(
                    getSelectedUnit()
                )
            ) {
                syncAmountFromQuantity();
                return;
            }

            /*
            * Count-based product
            *
            * Do NOT modify the user's input.
            *
            * If they enter 1.5 pcs,
            * keep 1.5 visible and show
            * the validation error.
            */
            validateQuantityAgainstStock();
        }
    );
    
    quantityField.addEventListener(
        "keydown",
        (event) => {
            if (event.key === "Enter") {
                event.preventDefault();

                if (!addSaleItemButton.disabled) {
                    saleItemForm.requestSubmit();
                }
            }
        }
    );

    amountField.addEventListener(
        "keydown",
        (event) => {
            if (event.key === "Enter") {
                event.preventDefault();

                if (!addSaleItemButton.disabled) {
                    saleItemForm.requestSubmit();
                }
            }
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
    console.count("SALE FORM LISTENER");

    let isSubmitting = false;

    saleItemForm.addEventListener(
        "submit",
        async (event) => {

            event.preventDefault();

            /*
            * Prevent duplicate submissions.
            */
            if (isSubmitting) {
                return;
            }

            isSubmitting = true;
            addSaleItemButton.disabled = true;

            try {

                const response =
                    await fetch(
                        saleItemForm.action,
                        {
                            method: "POST",
                            body: new FormData(saleItemForm),
                            headers: {
                                "X-Requested-With":
                                    "XMLHttpRequest",
                            },
                        }
                    );

                const data =
                    await response.json();

                

                if (!response.ok || !data.success) {
                    alert(
                        data.error ||
                        "Failed to add item."
                    );

                    return;
                }

                /*
                * Add/update the product in the table.
                */
                addSaleItemToTable(
                    data.item
                );
                console.log(
                    document.getElementById(
                        "sale-empty-state"
                    ).hidden
                );
                /*
                * Update subtotal and total.
                */
               const subtotalElement =
                    document.getElementById(
                        "sale-subtotal"
                    );

                const totalElement =
                    document.getElementById(
                        "sale-total"
                    );

                if (subtotalElement) {
                    subtotalElement.textContent =
                        Number(
                            data.sale.subtotal
                        ).toFixed(2);
                }

                if (totalElement) {
                    totalElement.textContent =
                        Number(
                            data.sale.total
                        ).toFixed(2);
                }

                /*
                * Reset product-entry form.
                */
                productSearchInput.value = "";

                selectedProductName.textContent =
                    saleItemForm.dataset.noProductSelected ||
                    "";

                quantityField.value = "";
                amountField.value = "";

                selectedProduct = null;
                productSearchInput.focus();

            } catch (error) {

                console.error(error);

                alert(
                    "Unexpected error."
                );

            } finally {

                isSubmitting = false;

                addSaleItemButton.disabled = false;

                addSaleItemButton.textContent =
                    window.saleTranslations.addItem;
            }
            
        }
    );
    
    function addSaleItemToTable(item) {

        const tbody =
            document.getElementById(
                "sale-items-body"
            );

        if (!tbody) {
            console.error(
                "Sale items table body was not found."
            );

            return;
        }

        /*
        * Check whether this product is already
        * present in the current sale.
        */
        let existingRow =
            tbody.querySelector(
                `[data-product-id="${item.product_id}"]`
            );

        if (existingRow) {

            const quantityInput =
                existingRow.querySelector(
                    ".sale-item-quantity"
                );

            const lineTotalCell =
                existingRow.querySelector(
                    ".sale-item-line-total"
                );

            if (quantityInput) {
                quantityInput.value =
                    item.quantity;
            }

            if (lineTotalCell) {
                lineTotalCell.textContent =
                    Number(
                        item.line_total
                    ).toFixed(2);
            }

            return;
        }

        /*
        * Product is new — create a new row.
        */
        const row =
            document.createElement("tr");

        row.dataset.productId =
            item.product_id;

        row.innerHTML = `
            <td></td>

            <td>
                ${escapeHtml(item.product_name)}
            </td>

            <td>
                <input
                    type="number"
                    name="quantity"
                    value="${escapeHtml(item.quantity)}"
                    class="form-input sale-item-quantity"
                    min="0.001"
                    step="0.001"
                    data-item-id="${item.id}"
                    data-unit="${escapeHtml(item.unit)}"
                    data-update-url="${escapeHtml(item.update_url)}"
                    aria-label="Quantity"
                >
            </td>

            <td>
                ${escapeHtml(item.unit)}
            </td>

            <td>
                ${Number(item.unit_price).toFixed(2)}
            </td>

            <td class="sale-item-line-total">
                ${Number(item.line_total).toFixed(2)}
            </td>

            <td>
                <div class="table-actions">
                    <form
                        method="post"
                        action="${escapeHtml(item.remove_url)}"
                        class="inline-form"
                    >
                        <input
                            type="hidden"
                            name="csrfmiddlewaretoken"
                            value="${getCsrfToken()}"
                        >

                        <button
                            type="submit"
                            class="btn-danger btn-small"
                        >
                            ${window.saleTranslations.remove}
                        </button>
                    </form>
                </div>
            </td>
        `;
        const emptyState =
            document.getElementById(
                "sale-empty-state"
            );

        if (emptyState) {
            emptyState.hidden = true;
        }
        tbody.appendChild(row);

        /*
        * Recalculate row numbers.
        */
        updateSaleItemRowNumbers();
    }

    function updateSaleItemRowNumbers() {

        const tbody =
            document.getElementById(
                "sale-items-body"
            );

        if (!tbody) {
            return;
        }

        const rows =
            tbody.querySelectorAll("tr");

        rows.forEach(
            (row, index) => {

                const numberCell =
                    row.querySelector(
                        "td:first-child"
                    );

                if (numberCell) {
                    numberCell.textContent =
                        index + 1;
                }
            }
        );
    }

 
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

    productSearchInput.addEventListener(
        "keydown",
        (event) => {

            if (
                !currentSearchResults.length
            ) {
                return;
            }

            if (
                event.key === "ArrowDown"
            ) {
                event.preventDefault();

                const nextIndex =
                    Math.min(
                        highlightedIndex + 1,
                        currentSearchResults.length - 1
                    );

                highlightRow(nextIndex);
            }

            if (
                event.key === "ArrowUp"
            ) {
                event.preventDefault();

                const nextIndex =
                    Math.max(
                        highlightedIndex - 1,
                        0
                    );

                highlightRow(nextIndex);
            }

            if (
                event.key === "Enter"
            ) {
                if (
                    highlightedIndex >= 0
                ) {
                    event.preventDefault();

                    selectProduct(
                        currentSearchResults[
                            highlightedIndex
                        ]
                    );
                }
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

    quantityField.addEventListener(
        "keydown",
        (event) => {
            if (event.key === "Enter") {
                event.preventDefault();

                if (!addSaleItemButton.disabled) {
                    saleItemForm.requestSubmit();
                }
            }
        }
    );

    amountField.addEventListener(
        "keydown",
        (event) => {
            if (event.key === "Enter") {
                event.preventDefault();

                if (!addSaleItemButton.disabled) {
                    saleItemForm.requestSubmit();
                }
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

document.addEventListener("DOMContentLoaded", () => {
    const canvas = document.getElementById("analyticsRevenueChart");

    if (!canvas) {
        return;
    }

    const dataElement = document.getElementById("analytics-chart-data");

    if (!dataElement) {
        return;
    }

    const chartData = JSON.parse(dataElement.textContent);

    if (!chartData.length) {
        return;
    }

    const ctx = canvas.getContext("2d");

    const gradient = ctx.createLinearGradient(0, 0, 0, 320);

    gradient.addColorStop(0, "rgba(157, 192, 139, 0.25)");
    gradient.addColorStop(1, "rgba(157, 192, 139, 0)");

    new Chart(ctx, {
        type: "line",

        data: {
            labels: chartData.map(item => item.label),

            datasets: [
                {
                    label: "Revenue",

                    data: chartData.map(item => item.revenue),

                    borderColor: "#9DC08B",
                    backgroundColor: gradient,

                    borderWidth: 2,

                    fill: true,

                    tension: 0.4,

                    pointRadius: 0,

                    pointHoverRadius: 5,

                    pointHoverBackgroundColor: "#9DC08B",

                    pointHoverBorderColor: "#0F1510",

                    pointHoverBorderWidth: 2,
                }
            ],
        },

        options: {
            responsive: true,

            maintainAspectRatio: false,

            interaction: {
                intersect: false,
                mode: "index",
            },

            plugins: {
                legend: {
                    display: false,
                },

                tooltip: {
                    callbacks: {
                        title: function(context) {
                            return chartData[context[0].dataIndex].label;
                        },

                        label: function(context) {
                            const item = chartData[context.dataIndex];

                            return [
                                `Revenue: ${Number(item.revenue).toFixed(2)}`,
                                `Transactions: ${item.transactions}`,
                                `Units sold: ${Number(item.units_sold).toFixed(2)}`,
                            ];
                        },
                    },
                },
            },

            scales: {
                x: {
                    grid: {
                        display: false,
                    },

                    ticks: {
                        maxTicksLimit: 10,
                    },
                },

                y: {
                    beginAtZero: true,

                    grid: {
                        color: "rgba(157, 192, 139, 0.08)",
                    },

                    ticks: {
                        callback: function(value) {
                            return Number(value).toLocaleString();
                        },
                    },
                },
            },
        },
    });
});
/*
 /* ============================================================
 * Inline Sale Item Quantity Editing
 * ============================================================
 */

const saleItemsBody =
    document.getElementById(
        "sale-items-body"
    );

if (saleItemsBody) {

    const updateSaleItemQuantity =
        async (input) => {

            const updateUrl =
                input.dataset.updateUrl;

            const quantity =
                input.value.trim();

            if (!quantity) {
                return;
            }

            const previousValue =
                input.dataset.previousValue ||
                input.defaultValue;

            input.disabled = true;

            const csrfToken =
                document.querySelector(
                    "[name=csrfmiddlewaretoken]"
                )?.value;

            try {

                const formData =
                    new FormData();

                formData.append(
                    "csrfmiddlewaretoken",
                    csrfToken
                );

                formData.append(
                    "quantity",
                    quantity
                );

                const response =
                    await fetch(
                        updateUrl,
                        {
                            method: "POST",
                            body: formData,
                            headers: {
                                "X-Requested-With":
                                    "XMLHttpRequest",
                            },
                        }
                    );

                const text =
                    await response.text();

                console.log(text);

                const data =
                    JSON.parse(text);

                if (
                    !response.ok ||
                    !data.success
                ) {
                    throw new Error(
                        data.error ||
                        "Update failed."
                    );
                }

                input.value =
                    data.item.quantity;

                input.dataset.previousValue =
                    data.item.quantity;

             

                const row =
                    input.closest("tr");

                if (row) {

                    const totalCell =
                        row.querySelector(
                            ".sale-item-line-total"
                        );

                    if (totalCell) {
                        totalCell.textContent =
                            Number(
                                data.item.line_total
                            ).toFixed(2);
                    }

                    row.classList.add(
                        "sale-item-updated"
                    );

                    setTimeout(() => {
                        row.classList.remove(
                            "sale-item-updated"
                        );
                    }, 800);
                }

                

            } catch (error) {

                console.error(error);

                input.value =
                    previousValue;

                alert(error.message);

            } finally {

                input.disabled = false;
            }
        };


    /*
     * Initialize previous value for existing inputs.
     *
     * Dynamically-created inputs are initialized
     * automatically when their first event occurs.
     */
    saleItemsBody
        .querySelectorAll(
            ".sale-item-quantity"
        )
        .forEach((input) => {

            input.dataset.previousValue =
                input.value;
        });


    /*
     * Event delegation.
     *
     * This works for both:
     *
     * 1. Items rendered by Django
     * 2. Items added later through AJAX
     */
    saleItemsBody.addEventListener(
        "keydown",
        (event) => {

            const input =
                event.target.closest(
                    ".sale-item-quantity"
                );

            if (!input) {
                return;
            }

            if (
                event.key !== "Enter"
            ) {
                return;
            }

            event.preventDefault();

            updateSaleItemQuantity(
                input
            );
        }
    );


    saleItemsBody.addEventListener(
        "focusin",
        (event) => {

            const input =
                event.target.closest(
                    ".sale-item-quantity"
                );

            if (!input) {
                return;
            }

            /*
             * Capture the current value when
             * the user starts editing.
             */
            input.dataset.previousValue =
                input.value;
        }
    );


    saleItemsBody.addEventListener(
        "blur",
        (event) => {

            const input =
                event.target.closest(
                    ".sale-item-quantity"
                );

            if (!input) {
                return;
            }

            if (
                input.value ===
                input.dataset.previousValue
            ) {
                return;
            }

            updateSaleItemQuantity(
                input
            );

        },
        true
    );
}

/* ============================================================
 * Expense AJAX
 * ============================================================
 */

const expenseForm =
    document.getElementById(
        "expense-form"
    );

const expenseTableBody =
    document.getElementById(
        "expense-table-body"
    );

const expenseEmptyState =
    document.getElementById(
        "expense-empty-state"
    );


/* ============================================================
 * Expense Translations
 * ============================================================
 */

const expenseRemoveLabel =
    expenseForm?.dataset.removeLabel ||
    "Remove";

const expenseRemoveConfirmation =
    expenseForm?.dataset.removeConfirmation ||
    "Are you sure you want to remove this expense?";

const expenseInvalidFormMessage =
    expenseForm?.dataset.invalidFormMessage ||
    "Please correct the errors below.";


/* ============================================================
 * Expense Table
 * ============================================================
 */

function updateExpenseRowNumbers() {

    if (!expenseTableBody) {
        return;
    }

    const rows =
        expenseTableBody.querySelectorAll(
            "tr"
        );

    rows.forEach(
        (row, index) => {

            const numberCell =
                row.querySelector(
                    "td:first-child"
                );

            if (numberCell) {
                numberCell.textContent =
                    index + 1;
            }
        }
    );

    if (expenseEmptyState) {
        expenseEmptyState.hidden =
            rows.length > 0;
    }
}

function clearExpenseErrors() {

    if (!expenseForm) {
        return;
    }

    const errorElements =
        expenseForm.querySelectorAll(
            ".expense-field-error"
        );

    errorElements.forEach(
        (element) => {

            element.textContent = "";
            element.hidden = true;
        }
    );

    const fields =
        expenseForm.querySelectorAll(
            ".form-input"
        );

    fields.forEach(
        (field) => {

            field.classList.remove(
                "form-input-error"
            );
        }
    );

    const formError =
        document.getElementById(
            "expense-form-error"
        );

    if (formError) {
        formError.textContent = "";
        formError.hidden = true;
    }
}


function showExpenseErrors(
    errors
) {

    clearExpenseErrors();

    if (!expenseForm) {
        return;
    }

    let firstErrorField = null;

    Object.entries(
        errors || {}
    ).forEach(
        ([fieldName, messages]) => {

            const errorElement =
                expenseForm.querySelector(
                    `[data-error-for="${fieldName}"]`
                );

            const field =
                expenseForm.querySelector(
                    `[name="${fieldName}"]`
                );

            if (field) {

                field.classList.add(
                    "form-input-error"
                );

                if (!firstErrorField) {
                    firstErrorField =
                        field;
                }
            }

            if (!errorElement) {
                return;
            }

            const messageList =
                Array.isArray(messages)
                    ? messages
                    : [messages];

            errorElement.textContent =
                messageList.join(" ");

            errorElement.hidden =
                false;
        }
    );

    const nonFieldErrors =
        errors?.__all__;

    if (
        nonFieldErrors &&
        nonFieldErrors.length
    ) {

        const formError =
            document.getElementById(
                "expense-form-error"
            );

        if (formError) {

            formError.textContent =
                nonFieldErrors.join(" ");

            formError.hidden =
                false;
        }
    }

    if (firstErrorField) {
        firstErrorField.focus();
    } else {

        const formError =
            document.getElementById(
                "expense-form-error"
            );

        if (formError) {

            formError.textContent =
                expenseInvalidFormMessage;

            formError.hidden =
                false;
        }
    }
}

function addExpenseRow(expense) {

    if (!expenseTableBody) {
        return;
    }

    const row =
        document.createElement(
            "tr"
        );

    row.dataset.expenseId =
        expense.id;

    row.innerHTML = `
        <td></td>

        <td>
            ${escapeHtml(expense.reference)}
        </td>

        <td>
            ${escapeHtml(expense.category)}
        </td>

        <td>
            ${Number(
                expense.amount
            ).toFixed(2)}
        </td>

        <td>
            ${escapeHtml(expense.payment_method)}
        </td>

        <td>
            ${escapeHtml(expense.expense_date)}
        </td>

        <td>
            <div class="table-actions">
                <button
                    type="button"
                    class="btn-danger btn-small expense-delete-btn"
                    data-expense-id="${expense.id}"
                    data-delete-url="${escapeHtml(
                        expense.delete_url
                    )}"
                >
                    ${escapeHtml(
                        expenseRemoveLabel
                    )}
                </button>
            </div>
        </td>
    `;

    expenseTableBody.prepend(
        row
    );

    updateExpenseRowNumbers();
}


/* ============================================================
 * Create Expense
 * ============================================================
 */

if (expenseForm) {

    let expenseSubmitting = false;

    expenseForm.addEventListener(
        "submit",
        async (event) => {

            event.preventDefault();

            if (expenseSubmitting) {
                return;
            }

            expenseSubmitting = true;

            const submitButton =
                expenseForm.querySelector(
                    'button[type="submit"]'
                );

            if (submitButton) {
                submitButton.disabled = true;
            }

            clearExpenseErrors();

            try {

                const response =
                    await fetch(
                        expenseForm.action,
                        {
                            method: "POST",

                            body:
                                new FormData(
                                    expenseForm
                                ),

                            headers: {
                                "X-Requested-With":
                                    "XMLHttpRequest",
                            },
                        }
                    );

                const data =
                    await response.json();

                console.log(
                    "Expense AJAX response:",
                    data
                );

                if (
                    !response.ok ||
                    !data.success
                ) {

                    if (data.errors) {

                        showExpenseErrors(
                            data.errors
                        );

                    } else {

                        const formError =
                            document.getElementById(
                                "expense-form-error"
                            );

                        if (formError) {

                            formError.textContent =
                                data.error ||
                                "Failed to record expense.";

                            formError.hidden =
                                false;
                        }
                    }

                    return;
                }

                addExpenseRow(
                    data.expense
                );

                expenseForm.reset();

                clearExpenseErrors();

                const categoryField =
                    expenseForm.querySelector(
                        '[name="category"]'
                    );

                if (categoryField) {
                    categoryField.focus();
                }
            } catch (error) {

                console.error(
                    "Expense creation failed:",
                    error
                );

                const formError =
                    document.getElementById(
                        "expense-form-error"
                    );

                if (formError) {

                    formError.textContent =
                        "Unexpected error.";

                    formError.hidden =
                        false;
                }

            } finally {

                expenseSubmitting = false;

                if (submitButton) {
                    submitButton.disabled = false;
                }
            }
        }
    );
}


/* ============================================================
 * Delete Expense
 * ============================================================
 */

async function deleteExpense(button) {

    const deleteUrl =
        button.dataset.deleteUrl;

    if (!deleteUrl) {

        console.error(
            "Expense delete URL is missing.",
            button
        );

        alert(
            "Unable to delete this expense."
        );

        return;
    }

    if (
        !confirm(
            expenseRemoveConfirmation
        )
    ) {
        return;
    }

    button.disabled = true;

    try {

        const response =
            await fetch(
                deleteUrl,
                {
                    method: "POST",

                    headers: {
                        "X-Requested-With":
                            "XMLHttpRequest",

                        "X-CSRFToken":
                            window.getCsrfToken(),
                    },
                }
            );

        const data =
            await response.json();

        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.error ||
                "Delete failed."
            );
        }

        const row =
            button.closest("tr");

        if (row) {
            row.remove();
        }

        updateExpenseRowNumbers();

    } catch (error) {

        console.error(
            "Expense deletion failed:",
            error
        );

        alert(
            error.message
        );

        button.disabled = false;
    }
}


/* ============================================================
 * Expense Delete Event Delegation
 * ============================================================
 */

document.addEventListener(
    "click",
    (event) => {

        const button =
            event.target.closest(
                ".expense-delete-btn"
            );

        if (!button) {
            return;
        }

        deleteExpense(
            button
        );
    }
);


/* ============================================================
 * Expense Initial State
 * ============================================================
 */

updateExpenseRowNumbers();


document.addEventListener("DOMContentLoaded", () => {
    const canvas = document.getElementById("profitabilityTrendChart");

    if (!canvas) {
        return;
    }

    const dataElement = document.getElementById("profitability-chart-data");

    if (!dataElement) {
        return;
    }

    const chartData = JSON.parse(dataElement.textContent);

    if (!chartData.length) {
        return;
    }

    const ctx = canvas.getContext("2d");

    new Chart(ctx, {
        type: "line",

        data: {
            labels: chartData.map(item => item.label),

            datasets: [
                {
                    label: "Revenue",
                    data: chartData.map(item => item.revenue),
                    borderColor: "#9DC08B",
                    backgroundColor: "rgba(157, 192, 139, 0.08)",
                    borderWidth: 2,
                    tension: 0.35,
                    pointRadius: 0,
                    pointHoverRadius: 5,
                },
                {
                    label: "COGS",
                    data: chartData.map(item => item.cogs),
                    borderColor: "#D6A85F",
                    backgroundColor: "transparent",
                    borderWidth: 2,
                    borderDash: [5, 5],
                    tension: 0.35,
                    pointRadius: 0,
                    pointHoverRadius: 5,
                },
            ],
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,

            interaction: {
                intersect: false,
                mode: "index",
            },

            plugins: {
                legend: {
                    display: true,
                    position: "top",
                },

                tooltip: {
                    callbacks: {
                        title: function(context) {
                            return chartData[context[0].dataIndex].label;
                        },

                        label: function(context) {
                            return `${context.dataset.label}: ${Number(context.raw).toLocaleString(undefined, {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2,
                            })}`;
                        },
                    },
                },
            },

            scales: {
                x: {
                    grid: {
                        display: false,
                    },
                    ticks: {
                        maxTicksLimit: 10,
                    },
                },

                y: {
                    beginAtZero: true,

                    grid: {
                        color: "rgba(157, 192, 139, 0.08)",
                    },

                    ticks: {
                        callback: function(value) {
                            return Number(value).toLocaleString();
                        },
                    },
                },
            },
        },
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const canvas = document.getElementById("categoryRevenueChart");

    if (!canvas) {
        return;
    }

    const dataElement = document.getElementById("category-chart-data");

    if (!dataElement) {
        return;
    }

    const chartData = JSON.parse(dataElement.textContent);

    if (!chartData.length) {
        return;
    }

    const ctx = canvas.getContext("2d");

    new Chart(ctx, {
        type: "bar",

        data: {
            labels: chartData.map(item => item.name),

            datasets: [
                {
                    label: "Revenue",
                    data: chartData.map(item => item.revenue),
                    backgroundColor: "rgba(157, 192, 139, 0.65)",
                    borderColor: "#9DC08B",
                    borderWidth: 1,
                    borderRadius: 6,
                },
            ],
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,

            plugins: {
                legend: {
                    display: false,
                },

                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Revenue: ${Number(context.raw).toLocaleString(undefined, {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2,
                            })}`;
                        },
                    },
                },
            },

            scales: {
                x: {
                    grid: {
                        display: false,
                    },
                },

                y: {
                    beginAtZero: true,

                    grid: {
                        color: "rgba(157, 192, 139, 0.08)",
                    },

                    ticks: {
                        callback: function(value) {
                            return Number(value).toLocaleString();
                        },
                    },
                },
            },
        },
    });
});


document.addEventListener("DOMContentLoaded", () => {
    const canvas = document.getElementById("categoryProfitChart");

    if (!canvas) {
        return;
    }

    const dataElement = document.getElementById("category-chart-data");

    if (!dataElement) {
        return;
    }

    const chartData = JSON.parse(dataElement.textContent);

    if (!chartData.length) {
        return;
    }

    const ctx = canvas.getContext("2d");

    new Chart(ctx, {
        type: "bar",

        data: {
            labels: chartData.map(item => item.name),

            datasets: [
                {
                    label: "Gross Profit",
                    data: chartData.map(item => item.gross_profit),
                    backgroundColor: "rgba(96, 153, 102, 0.65)",
                    borderColor: "#609966",
                    borderWidth: 1,
                    borderRadius: 6,
                },
            ],
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,

            plugins: {
                legend: {
                    display: false,
                },

                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Gross Profit: ${Number(context.raw).toLocaleString(undefined, {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2,
                            })}`;
                        },
                    },
                },
            },

            scales: {
                x: {
                    grid: {
                        display: false,
                    },
                },

                y: {
                    beginAtZero: true,

                    grid: {
                        color: "rgba(157, 192, 139, 0.08)",
                    },

                    ticks: {
                        callback: function(value) {
                            return Number(value).toLocaleString();
                        },
                    },
                },
            },
        },
    });
    const dayOfWeekDataElement = document.getElementById(
        "day-of-week-chart-data"
    );

    const salesByDayChartCanvas = document.getElementById(
        "salesByDayChart"
    );

    if (dayOfWeekDataElement && salesByDayChartCanvas) {
        const data = JSON.parse(dayOfWeekDataElement.textContent);

        new Chart(salesByDayChartCanvas, {
            type: "bar",
            data: {
                labels: data.map(item => item.label),
                datasets: [
                    {
                        label: "Revenue",
                        data: data.map(item => item.revenue),
                        backgroundColor: "rgba(96, 153, 102, 0.65)",
                        borderColor: "#609966",
                        borderWidth: 1,
                        borderRadius: 6,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: "index",
                },
                plugins: {
                    legend: {
                        display: false,
                    },
                },
                scales: {
                    y: {
                        beginAtZero: true,
                    },
                },
            },
        });
    }


    const hourlySalesDataElement = document.getElementById(
        "hourly-sales-chart-data"
    );

    const salesByHourChartCanvas = document.getElementById(
        "salesByHourChart"
    );

    if (hourlySalesDataElement && salesByHourChartCanvas) {
        const data = JSON.parse(hourlySalesDataElement.textContent);

        new Chart(salesByHourChartCanvas, {
            type: "line",
            data: {
                labels: data.map(item => item.label),
                datasets: [
                    {
                        label: "Revenue",
                        data: data.map(item => item.revenue),
                        borderColor: "#9DC08B",
                        backgroundColor: "rgba(157, 192, 139, 0.08)",
                        borderWidth: 2,
                        tension: 0.35,
                        pointRadius: 0,
                        pointHoverRadius: 5,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: "index",
                },
                plugins: {
                    legend: {
                        display: false,
                    },
                },
                scales: {
                    y: {
                        beginAtZero: true,
                    },
                },
            },
        });
    }

});

document.addEventListener("DOMContentLoaded", () => {
    const chartCards = document.querySelectorAll(
        ".analytics-chart-card"
    );

    if (!chartCards.length) {
        return;
    }

    let expandedCard = null;
    let overlay = null;

    function closeExpandedChart() {
        if (!expandedCard || !overlay) {
            return;
        }

        const chartContainer = overlay.querySelector(".chart-container");

        if (chartContainer) {
            expandedCard.appendChild(chartContainer);
        }

        overlay.remove();

        document.body.classList.remove(
            "analytics-chart-expanded"
        );

        expandedCard.classList.remove(
            "analytics-chart-card-expanded"
        );

        expandedCard = null;
        overlay = null;

        window.dispatchEvent(new Event("resize"));
    }

    function expandChart(card) {
        if (expandedCard) {
            closeExpandedChart();
        }

        const chartContainer = card.querySelector(
            ".chart-container"
        );

        if (!chartContainer) {
            return;
        }

        expandedCard = card;

        overlay = document.createElement("div");

        overlay.className = "analytics-chart-overlay";

        const overlayCard = document.createElement("div");

        overlayCard.className =
            "analytics-chart-overlay-card";

        const closeButton = document.createElement("button");

        closeButton.type = "button";
        closeButton.className =
            "analytics-chart-overlay-close";
        closeButton.setAttribute(
            "aria-label",
            "Close expanded chart"
        );
        closeButton.innerHTML = "×";

        const header = card.querySelector(".card-header");

        if (header) {
            const headerClone = header.cloneNode(true);
            overlayCard.appendChild(headerClone);
        }

        overlayCard.appendChild(closeButton);
        overlayCard.appendChild(chartContainer);

        overlay.appendChild(overlayCard);

        document.body.appendChild(overlay);

        document.body.classList.add(
            "analytics-chart-expanded"
        );

        card.classList.add(
            "analytics-chart-card-expanded"
        );

        closeButton.addEventListener(
            "click",
            (event) => {
                event.stopPropagation();
                closeExpandedChart();
            }
        );

        overlay.addEventListener(
            "click",
            (event) => {
                if (event.target === overlay) {
                    closeExpandedChart();
                }
            }
        );

        window.dispatchEvent(new Event("resize"));
    }

    chartCards.forEach((card) => {
        card.addEventListener("click", (event) => {
            /*
             * Ignore clicks on interactive chart elements after
             * the chart has already been expanded.
             */
            if (expandedCard === card) {
                return;
            }

            expandChart(card);
        });

        card.addEventListener("dblclick", (event) => {
            event.preventDefault();

            /*
             * If this card is already expanded, double-click
             * returns it to its normal position.
             */
            if (expandedCard === card) {
                closeExpandedChart();
            }
        });
    });

    document.addEventListener("keydown", (event) => {
        if (
            event.key === "Escape" &&
            expandedCard
        ) {
            closeExpandedChart();
        }
    });
});