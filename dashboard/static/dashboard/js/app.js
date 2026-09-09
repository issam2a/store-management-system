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
});