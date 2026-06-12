from products.models import Product


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    # ── Iteration ────────────────────────────────────────────
    def __iter__(self):
        product_ids = self.cart.keys()
        products    = Product.objects.filter(id__in=product_ids)
        product_map = {str(p.id): p for p in products}

        for pid, item in self.cart.items():
            product = product_map.get(pid)
            if not product:
                continue  # skip deleted products
            quantity = item.get('quantity', 0) if isinstance(item, dict) else item
            yield {
                'product':     product,
                'quantity':    quantity,
                'total_price': product.price * quantity,
            }

    def __len__(self):
        return self.get_total_quantity()

    # ── Read ─────────────────────────────────────────────────
    def get_total_quantity(self):
        total = 0
        for item in self.cart.values():
            qty = item.get('quantity', 0) if isinstance(item, dict) else item
            total += qty
        return total

    def get_total_price(self):
        return sum(item['total_price'] for item in self)

    # ── Write ─────────────────────────────────────────────────
    def add(self, product_id):
        product    = Product.objects.get(id=product_id)
        product_id = str(product_id)

        if product_id in self.cart:
            # Don't exceed stock
            current_qty = self.cart[product_id].get('quantity', 0)
            if current_qty < product.stock:
                self.cart[product_id]['quantity'] += 1
        else:
            self.cart[product_id] = {
                'quantity': 1,
                'price':    float(product.price),
            }
        self.save()

    def decrease(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            self.cart[product_id]['quantity'] -= 1
            if self.cart[product_id]['quantity'] <= 0:
                del self.cart[product_id]
        self.save()

    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
        self.save()

    def clear(self):
        self.session['cart'] = {}
        self.session.modified = True
        self.cart = {}

    def save(self):
        self.session['cart']   = self.cart
        self.session.modified  = True