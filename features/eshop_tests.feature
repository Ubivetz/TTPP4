Feature: E-shop functionality
Testing all classes: Product, ShoppingCart, and Order with focus on boundary cases
#Product scenarios
Scenario: Product availability check with positive value
Given A product with name "laptop" price 1000 and amount 10
When I check availability for 5 items
Then The product should be available
Scenario: Product availability check with zero value
Given A product with name "smartphone" price 500 and amount 5
When I check availability for 0 items
Then The product should be available
Scenario: Product availability check with negative value
Given A product with name "tablet" price 300 and amount 3
When I check availability for -1 items
Then The product should be available
#ShoppingCart scenarios
Scenario: Add multiple products to cart and calculate total
Given A product with name "keyboard" price 80 and amount 15
And Another product with name "mouse" price 40 and amount 25
And An empty shopping cart
When I add the first product to the cart with amount 2
And I add the second product to the cart with amount 3
Then The cart total should be 280
Scenario: Try to add None as product to cart
Given An empty shopping cart
When I try to add None as a product with amount 5
Then An error should occur
Scenario: Try to add product with non-integer amount
Given A product with name "mouse" price 50 and amount 30
And An empty shopping cart
When I try to add product with string amount "five"
Then An error should occur
#Order scenarios
Scenario: Place order with products in cart
Given A product with name "monitor" price 200 and amount 10
And A shopping cart with the product added with amount 3
When I create an order from the cart
And I place the order
Then The product amount should be 7
And The cart should be empty
Scenario: Try to place order with boundary amount (exact available amount)
Given A product with name "charger" price 20 and amount 5
And A shopping cart with the product added with amount 5
When I create an order from the cart
And I place the order
Then The product amount should be 0
Scenario: Try to place order with multiple products
Given A product with name "speaker" price 150 and amount 8
And Another product with name "webcam" price 70 and amount 12
And A shopping cart with both products added
When I create an order from the cart
And I place the order
Then The first product amount should be 7
And The second product amount should be 10
Scenario: Edge case - make order with empty cart
Given An empty shopping cart
When I create an order from the cart
And I place the order
Then The cart should be empty