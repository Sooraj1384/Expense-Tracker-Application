document.addEventListener("DOMContentLoaded", function () {
    // Animate table rows
    const items = document.querySelectorAll(".animate-item");
    items.forEach((item, index) => {
        setTimeout(() => {
            item.style.opacity = 1;
        }, index * 150);
    });

    // // Delete confirmation
    // document.querySelectorAll(".delete-btn").forEach(button => {
    //     button.addEventListener("click", function () {
    //         const expenseId = this.dataset.id;
    //         if (confirm("Are you sure you want to delete this expense?")) {
    //             window.location.href = `/delete/${expenseId}`;
    //         }
    //     });
    // });

    document.querySelectorAll(".delete-btn").forEach(button => {
        button.addEventListener("click", function () {
            const expenseId = this.dataset.id;
            if (confirm("Are you sure you want to delete this expense?")) {
                window.location.href = `/delete/${expenseId}`;
            }
        });
    });
});
