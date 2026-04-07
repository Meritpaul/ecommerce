# cart/cart.py
from products.models import Product


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')

        if not cart:
            cart = self.session['cart'] = {}

        self.cart = cart

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        for product in products:
            item = self.cart[str(product.id)]
            
            # ✅ HANDLE BOTH CASES
            if isinstance(item, dict):
                quantity = item.get('quantity', 0)
            else:
                quantity = item
                
            yield {
                'product': product,
                'quantity': quantity,
                'total_price': product.price * quantity
            }
            
    def get_total_quantity(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(item['total_price'] for item in self)

    def add(self, product_id):
        product = Product.objects.get(id=product_id)
        product_id = str(product_id)

        if product_id in self.cart:
            self.cart[product_id]['quantity'] += 1
        else:
            self.cart[product_id] = {
                'quantity': 1,
                'price': float(product.price)
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

    def save(self):
        self.session['cart'] = self.cart
        self.session.modified = True