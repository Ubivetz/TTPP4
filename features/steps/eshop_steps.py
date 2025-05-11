from behave import given, when, then
from eshop_lab1 import Product, ShoppingCart, Order

@given('A product with name "{name}" price {price:d} and amount {amount:d}')
def step_create_product(context, name, price, amount):
    context.product = Product(name=name, price=price, available_amount=amount)

@given('Another product with name "{name}" price {price:d} and amount {amount:d}')
def step_create_another_product(context, name, price, amount):
    context.another_product = Product(name=name, price=price, available_amount=amount)

@given('A shopping cart with the product added with amount {amount:d}')
def step_create_cart_with_product(context, amount):
    context.cart = ShoppingCart()
    context.cart.add_product(context.product, amount)

@when('I check availability for {amount:d} items')
def step_check_availability(context, amount):
    context.available = context.product.is_available(amount)

@then('The product should be available')
def step_assert_product_available(context):
    assert context.available is True, f"Expected product to be available but got {context.available}"

@then('The product should not be available')
def step_assert_product_not_available(context):
    assert context.available is False, f"Expected product to not be available but got {context.available}"

@then('The product amount should be {amount:d}')
def step_assert_product_amount(context, amount):
    assert context.product.available_amount == amount, f"Expected amount to be {amount} but got {context.product.available_amount}"

@given('A shopping cart with both products added')
def step_create_cart_with_both_products(context):
    context.cart = ShoppingCart()
    context.cart.add_product(context.product, 1)
    context.cart.add_product(context.another_product, 2)

@when('I add the first product to the cart with amount {amount:d}')
def step_add_first_product_to_cart(context, amount):
    try:
        context.cart.add_product(context.product, amount)
        context.error_occurred = False
    except Exception as e:
        context.error_occurred = True
        context.error_message = str(e)

@when('I add the second product to the cart with amount {amount:d}')
def step_add_second_product_to_cart(context, amount):
    try:
        context.cart.add_product(context.another_product, amount)
        context.error_occurred = False
    except Exception as e:
        context.error_occurred = True
        context.error_message = str(e)

@when('I try to add None as a product with amount {amount:d}')
def step_add_none_product_to_cart(context, amount):
    try:
        context.cart.add_product(None, amount)
        context.error_occurred = False
    except Exception as e:
        context.error_occurred = True
        context.error_message = str(e)

@when('I try to add product with string amount "{amount_str}"')
def step_add_product_with_string_amount(context, amount_str):
    try:
        context.cart.add_product(context.product, amount_str)
        context.error_occurred = False
    except Exception as e:
        context.error_occurred = True
        context.error_message = str(e)

@then('An error should occur')
def step_assert_error_occurred(context):
    assert context.error_occurred is True, "Expected an error to occur"

@then('The cart should be empty')
def step_assert_cart_empty(context):
    assert len(context.cart.products) == 0, "Cart should be empty"

@then('The cart total should be {total:d}')
def step_assert_cart_total(context, total):
    actual_total = context.cart.calculate_total()
    assert actual_total == total, f"Expected cart total to be {total} but got {actual_total}"

# Order steps
@when('I create an order from the cart')
def step_create_order(context):
    context.order = Order(context.cart)

@when('I place the order')
def step_place_order(context):
    try:
        context.order.place_order()
        context.error_occurred = False
    except Exception as e:
        context.error_occurred = True
        context.error_message = str(e)

@then('The first product amount should be {amount:d}')
def step_assert_first_product_amount(context, amount):
    assert context.product.available_amount == amount, f"Expected first product amount to be {amount} but got {context.product.available_amount}"

@then('The second product amount should be {amount:d}')
def step_assert_second_product_amount(context, amount):
    assert context.another_product.available_amount == amount, f"Expected second product amount to be {amount} but got {context.another_product.available_amount}"