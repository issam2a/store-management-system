document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.querySelector(".sidebar");
    const sidebarToggle = document.querySelector(".sidebar-toggle");
    const mobileMenuButton = document.querySelector(".mobile-menu-button");

    /*
     * Desktop sidebar collapse
     */
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener("click", () => {
            document.body.classList.toggle("sidebar-collapsed");

            const expanded =
                !document.body.classList.contains("sidebar-collapsed");

            sidebarToggle.setAttribute("aria-expanded", expanded);
        });
    }

    /*
     * Mobile sidebar
     */
    if (mobileMenuButton && sidebar) {
        mobileMenuButton.addEventListener("click", () => {
            const isOpen = sidebar.classList.toggle("mobile-open");

            mobileMenuButton.setAttribute("aria-expanded", isOpen);
        });
    }

    /*
     * Revenue Chart
     */
    const chartDataElement = document.getElementById(
        "revenue-chart-data"
    );

    const revenueChartCanvas = document.getElementById(
        "revenueChart"
    );

    if (chartDataElement && revenueChartCanvas && typeof Chart !== "undefined") {
        const chartData = JSON.parse(
            chartDataElement.textContent
        );

        const labels = chartData.map((item) => item.label);
        const revenue = chartData.map((item) => item.revenue);

        new Chart(revenueChartCanvas, {
            type: "line",

            data: {
                labels: labels,

                datasets: [
                    {
                        label: "Revenue",
                        data: revenue,

                        fill: true,

                        tension: 0.35,

                        borderWidth: 2,

                        pointRadius: 3,

                        pointHoverRadius: 5,

                        borderColor: "#9DC08B",

                        backgroundColor: "rgba(157, 192, 139, 0.12)",
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
                            label: (context) => {
                                const value = context.parsed.y ?? 0;

                                return `Revenue: ${value.toLocaleString(
                                    undefined,
                                    {
                                        minimumFractionDigits: 2,
                                        maximumFractionDigits: 2,
                                    }
                                )}`;
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
                            color: "#7E8B7B",
                        },
                    },

                    y: {
                        beginAtZero: true,

                        grid: {
                            color: "rgba(237, 241, 214, 0.08)",
                        },

                        ticks: {
                            color: "#7E8B7B",

                            callback: (value) => {
                                return Number(value).toLocaleString();
                            },
                        },
                    },
                },
            },
        });
    }
});