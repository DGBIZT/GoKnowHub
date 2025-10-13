import stripe


def create_stripe_product(title, descriptions):
    product = stripe.Product.create(
        name=title,
        description=descriptions,
    )
    return product.id


def create_stripe_price(product_id, amount):
    price = stripe.Price.create(
        product=product_id,
        unit_amount=amount,
        currency="usd",
    )
    return price.id


def create_stripe_checkout_session(price_id, success_url):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {"price": price_id, "quantity": 1, "currency": "usd"},
        ],
        mode='payment',
        success_url=success_url,
    )
    return session