from payment_service import PaymentService


def main() -> None:
    service = PaymentService()
    print(service.describe())


if __name__ == "__main__":
    main()
