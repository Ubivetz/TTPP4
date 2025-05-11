import uuid
import pytest
import boto3
from datetime import datetime, timedelta, timezone

from app.eshop import Product, ShoppingCart, Order, Shipment
from services import ShippingService
from services.repository import ShippingRepository
from services.publisher import ShippingPublisher
from services.config import AWS_ENDPOINT_URL, AWS_REGION, SHIPPING_QUEUE


# Тест 1: Розміщення замовлення з імітованим репозиторієм та видавцем
def test_place_order_with_mocked_services(mocker):
    mock_repo = mocker.Mock()
    mock_publisher = mocker.Mock()
    shipping_service = ShippingService(mock_repo, mock_publisher)

    shipping_id = str(uuid.uuid4())
    mock_repo.create_shipping.return_value = shipping_id

    cart = ShoppingCart()
    product = Product(name="Laptop", price=1200, available_amount=5)
    cart.add_product(product, amount=1)

    order_id = str(uuid.uuid4())
    order = Order(cart, shipping_service, order_id)
    due_date = datetime.now(timezone.utc) + timedelta(days=2)

    actual_shipping_id = order.place_order(
        ShippingService.list_available_shipping_type()[0],
        due_date=due_date
    )

    assert actual_shipping_id == shipping_id
    mock_repo.create_shipping.assert_called_once()
    mock_publisher.send_new_shipping.assert_called_once_with(shipping_id)
    mock_repo.update_shipping_status.assert_called_once_with(shipping_id, shipping_service.SHIPPING_IN_PROGRESS)


# Тест 2: Кілька товарів у порядку з імітацією послуг
def test_multiple_products_order_with_mocked_services(mocker):
    mock_repo = mocker.Mock()
    mock_publisher = mocker.Mock()
    shipping_service = ShippingService(mock_repo, mock_publisher)

    shipping_id = str(uuid.uuid4())
    mock_repo.create_shipping.return_value = shipping_id

    cart = ShoppingCart()
    product1 = Product(name="Laptop", price=1200, available_amount=5)
    product2 = Product(name="Mouse", price=20, available_amount=30)
    product3 = Product(name="Keyboard", price=50, available_amount=20)

    cart.add_product(product1, amount=1)
    cart.add_product(product2, amount=2)
    cart.add_product(product3, amount=1)

    order_id = str(uuid.uuid4())
    order = Order(cart, shipping_service, order_id)
    due_date = datetime.now(timezone.utc) + timedelta(days=2)

    actual_shipping_id = order.place_order(
        ShippingService.list_available_shipping_type()[1],
        due_date=due_date
    )

    assert actual_shipping_id == shipping_id
    mock_repo.create_shipping.assert_called_once()

    args, _ = mock_repo.create_shipping.call_args
    assert len(args[1]) == 3
    assert "Laptop" in args[1]
    assert "Mouse" in args[1]
    assert "Keyboard" in args[1]


# Тест 3: Замовлення з недійсною датою виконання
def test_order_with_invalid_due_date(mocker):
    mock_repo = mocker.Mock()
    mock_publisher = mocker.Mock()
    shipping_service = ShippingService(mock_repo, mock_publisher)

    cart = ShoppingCart()
    product = Product(name="Laptop", price=1200, available_amount=5)
    cart.add_product(product, amount=1)

    order = Order(cart, shipping_service)

    past_date = datetime.now(timezone.utc) - timedelta(hours=1)

    with pytest.raises(ValueError) as excinfo:
        order.place_order(
            ShippingService.list_available_shipping_type()[0],
            due_date=past_date
        )

    assert "Shipping due datetime must be greater than datetime now" in str(excinfo.value)
    mock_repo.create_shipping.assert_not_called()
    mock_publisher.send_new_shipping.assert_not_called()


# Тест 4: Замовлення з недійсним типом доставки
def test_order_with_invalid_shipping_type(mocker):
    mock_repo = mocker.Mock()
    mock_publisher = mocker.Mock()
    shipping_service = ShippingService(mock_repo, mock_publisher)

    cart = ShoppingCart()
    product = Product(name="Mouse", price=20, available_amount=10)
    cart.add_product(product, amount=2)

    order = Order(cart, shipping_service)
    due_date = datetime.now(timezone.utc) + timedelta(days=1)

    with pytest.raises(ValueError) as excinfo:
        order.place_order("Invalid Shipping Type", due_date=due_date)

    assert "Shipping type is not available" in str(excinfo.value)
    mock_repo.create_shipping.assert_not_called()
    mock_publisher.send_new_shipping.assert_not_called()


# Тест 5: Перевірка статусу доставки за допомогою фіктивного репозиторію
def test_check_shipping_status_with_mocked_repo(mocker):
    mock_repo = mocker.Mock()
    mock_publisher = mocker.Mock()
    shipping_service = ShippingService(mock_repo, mock_publisher)

    shipping_id = str(uuid.uuid4())
    mock_repo.get_shipping.return_value = {
        'shipping_id': shipping_id,
        'shipping_status': ShippingService.SHIPPING_IN_PROGRESS
    }

    shipment = Shipment(shipping_id, shipping_service)
    status = shipment.check_shipping_status()

    assert status == ShippingService.SHIPPING_IN_PROGRESS
    mock_repo.get_shipping.assert_called_once_with(shipping_id)


# Тест 6: Процес доставки з імітацією репозиторію та видавця
def test_process_shipping_with_mocked_repo(mocker):
    mock_repo = mocker.Mock()
    mock_publisher = mocker.Mock()
    shipping_service = ShippingService(mock_repo, mock_publisher)

    shipping_id = str(uuid.uuid4())
    future_date = datetime.now(timezone.utc) + timedelta(days=5)
    mock_repo.get_shipping.return_value = {
        'shipping_id': shipping_id,
        'shipping_status': ShippingService.SHIPPING_IN_PROGRESS,
        'due_date': future_date.isoformat()
    }

    mock_repo.update_shipping_status.return_value = {
        'ResponseMetadata': {'HTTPStatusCode': 200}
    }

    result = shipping_service.process_shipping(shipping_id)

    assert result['HTTPStatusCode'] == 200
    mock_repo.get_shipping.assert_called_once_with(shipping_id)
    mock_repo.update_shipping_status.assert_called_once_with(shipping_id, ShippingService.SHIPPING_COMPLETED)


# Тест 7: Обробка пакету доставки з імітацією видавця та репозиторію
def test_process_shipping_batch_with_mocked_services(mocker):
    mock_repo = mocker.Mock()
    mock_publisher = mocker.Mock()
    shipping_service = ShippingService(mock_repo, mock_publisher)

    shipping_ids = [str(uuid.uuid4()) for _ in range(3)]
    mock_publisher.poll_shipping.return_value = shipping_ids

    future_date = datetime.now(timezone.utc) + timedelta(days=5)
    mock_repo.get_shipping.return_value = {
        'shipping_id': "any_id",
        'shipping_status': ShippingService.SHIPPING_IN_PROGRESS,
        'due_date': future_date.isoformat()
    }

    mock_repo.update_shipping_status.return_value = {
        'ResponseMetadata': {'HTTPStatusCode': 200}
    }

    results = shipping_service.process_shipping_batch()

    assert len(results) == len(shipping_ids)
    for result in results:
        assert result['HTTPStatusCode'] == 200

    assert mock_publisher.poll_shipping.call_count == 1
    assert mock_repo.get_shipping.call_count == len(shipping_ids)
    assert mock_repo.update_shipping_status.call_count == len(shipping_ids)


# Тест 8: Невдала доставка після закінчення терміну доставки
def test_fail_shipping_when_due_date_passed(mocker):
    mock_repo = mocker.Mock()
    mock_publisher = mocker.Mock()
    shipping_service = ShippingService(mock_repo, mock_publisher)

    shipping_id = str(uuid.uuid4())
    past_date = datetime.now(timezone.utc) - timedelta(days=1)
    mock_repo.get_shipping.return_value = {
        'shipping_id': shipping_id,
        'shipping_status': ShippingService.SHIPPING_IN_PROGRESS,
        'due_date': past_date.isoformat()
    }

    mock_repo.update_shipping_status.return_value = {
        'ResponseMetadata': {'HTTPStatusCode': 200}
    }

    result = shipping_service.process_shipping(shipping_id)

    assert result['HTTPStatusCode'] == 200
    mock_repo.get_shipping.assert_called_once_with(shipping_id)
    mock_repo.update_shipping_status.assert_called_once_with(shipping_id, ShippingService.SHIPPING_FAILED)


# Тест 9: Замовлення з максимальною доступною кількістю товару
def test_order_with_maximum_available_product(mocker):
    mock_repo = mocker.Mock()
    mock_publisher = mocker.Mock()
    shipping_service = ShippingService(mock_repo, mock_publisher)

    shipping_id = str(uuid.uuid4())
    mock_repo.create_shipping.return_value = shipping_id

    cart = ShoppingCart()
    available_amount = 5
    product = Product(name="Limited Product", price=50, available_amount=available_amount)
    cart.add_product(product, amount=available_amount)

    order_id = str(uuid.uuid4())
    order = Order(cart, shipping_service, order_id)
    due_date = datetime.now(timezone.utc) + timedelta(days=2)

    actual_shipping_id = order.place_order(
        ShippingService.list_available_shipping_type()[0],
        due_date=due_date
    )

    assert actual_shipping_id == shipping_id
    assert product.available_amount == 0
    mock_repo.create_shipping.assert_called_once()
    mock_publisher.send_new_shipping.assert_called_once_with(shipping_id)


# Тест 10: Інтеграція з реальною чергою SQS для перевірки повідомлень
def test_order_places_message_in_sqs_queue():
    repo = ShippingRepository()
    publisher = ShippingPublisher()
    shipping_service = ShippingService(repo, publisher)

    cart = ShoppingCart()
    product = Product(name="Test SQS Product", price=100, available_amount=10)
    cart.add_product(product, amount=1)

    order = Order(cart, shipping_service)
    due_date = datetime.now(timezone.utc) + timedelta(minutes=10)
    shipping_id = order.place_order(
        ShippingService.list_available_shipping_type()[0],
        due_date=due_date
    )

    sqs_client = boto3.client(
        "sqs",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        aws_access_key_id="test",
        aws_secret_access_key="test"
    )

    queue_url = sqs_client.get_queue_url(QueueName=SHIPPING_QUEUE)["QueueUrl"]

    response = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=5
    )

    assert "Messages" in response, "No messages found in the queue"
    assert len(response["Messages"]) > 0, "Queue is empty"

    message = response["Messages"][0]
    assert message["Body"] == shipping_id, "Message body doesn't match the shipping ID"

    sqs_client.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=message["ReceiptHandle"]
    )