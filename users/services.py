import stripe
from django.conf import settings
from django.core.exceptions import ValidationError

stripe.api_key = settings.DJSTRIPE_API_KEY

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
            {"price": price_id, "quantity": 1},
        ],
        mode='payment',
        success_url=success_url,
        cancel_url=success_url
    )


# Пример использования
def create_full_stripe_flow(title, description, amount, success_url):
    try:
        # Создаем продукт
        product_id = create_stripe_product(title, description)

        # Создаем цену
        price_id = create_stripe_price(product_id, amount)

        # Создаем сессию оплаты
        session_id = create_stripe_checkout_session(price_id, success_url)

        return {
            "product_id": product_id,
            "price_id": price_id,
            "session_id": session_id,
            "checkout_url": f"https://checkout.stripe.com/c/pay/{session_id}"
        }
    except Exception as e:
        raise ValidationError(f"Произошла ошибка: {str(e)}")