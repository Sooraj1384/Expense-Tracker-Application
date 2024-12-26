document.addEventListener("DOMContentLoaded", function() {
    const items = document.querySelectorAll('.animate-item');
    items.forEach((item, index) => {
        setTimeout(() => {
            item.style.opacity = 1;
        }, index * 150); // Stagger animation
    });
});
