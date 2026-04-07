//cart.js file
// Toggle cart drawer
function toggleCart() {
    let drawer = document.getElementById('cart-drawer');
    drawer.classList.toggle('translate-x-full');
    if (!drawer.classList.contains('translate-x-full')) {
        loadCart(); // load items when opened
    }
}

// Add item to cart
function addToCart(id) {
    fetch(`/cart/add/${id}/`)
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            toggleCart(); // open drawer
            loadCart();   // load items
        }
    });
}

// Handle +, -, remove buttons
document.addEventListener('click', function (e) {
    if (e.target.classList.contains('cart-btn')) {
        let action = e.target.dataset.action;
        let id = e.target.dataset.productId;

        fetch(`/cart/${action}/${id}/`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                loadCart(); // reload cart drawer dynamically
            }
        });
    }
});

// Load cart items dynamically
function loadCart() {
    fetch('/cart/api/')
    .then(res => res.json())
    .then(html => {
        document.getElementById('cart-items').innerHTML = html;

        // Update drawer total
        let total = document.getElementById('drawer-total');
        if (total) {
            let tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;
            let drawerTotal = tempDiv.querySelector('#drawer-total');
            if (drawerTotal) total.textContent = drawerTotal.textContent;
        }
    });
}