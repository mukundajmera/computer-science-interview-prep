"""Tests for Facade Pattern implementations."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v1-basic"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v2-variant"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v3-advanced"))


class TestV1HomeTheaterFacade(unittest.TestCase):
    """Tests for V1 Basic Home Theater."""

    def test_home_theater_facade_exposes_simple_movie_workflow(self):
        from facade_demo import HomeTheaterFacade

        theater = HomeTheaterFacade()

        theater.watch_movie("Inception")
        theater.end_movie()


class TestV2CheckoutFacade(unittest.TestCase):
    """Tests for V2 Variant Checkout Workflow."""

    def test_checkout_places_order_and_reserves_inventory(self):
        from checkout_facade import (
            CheckoutFacade,
            InventoryService,
            NotificationService,
            PaymentService,
            ShippingService,
        )

        inventory = InventoryService({"book": 2})
        facade = CheckoutFacade(
            inventory,
            PaymentService(),
            ShippingService(),
            NotificationService(),
        )

        confirmation = facade.place_order(
            item_id="book",
            quantity=1,
            unit_price=20.00,
            card_token="tok_123",
            address="10 Main St",
            email="reader@example.com",
        )

        self.assertEqual(confirmation.order_id, "order-book-1")
        self.assertEqual(confirmation.payment_id, "pay-2500")
        self.assertEqual(inventory.available("book"), 1)

    def test_checkout_rejects_out_of_stock_item_before_payment(self):
        from checkout_facade import (
            CheckoutFacade,
            InventoryService,
            NotificationService,
            PaymentService,
            ShippingService,
        )

        facade = CheckoutFacade(
            InventoryService({"book": 0}),
            PaymentService(),
            ShippingService(),
            NotificationService(),
        )

        with self.assertRaises(ValueError):
            facade.place_order(
                item_id="book",
                quantity=1,
                unit_price=20.00,
                card_token="tok_123",
                address="10 Main St",
                email="reader@example.com",
            )


class TestV3CloudServicesFacade(unittest.TestCase):
    """Tests for V3 Advanced Cloud Services SDK."""

    def test_deploy_service_coordinates_cloud_subsystems(self):
        from cloud_services_facade import (
            CloudDeploymentFacade,
            ComputeService,
            MonitoringService,
            ObjectStorageService,
            QueueService,
        )

        facade = CloudDeploymentFacade(
            ObjectStorageService(),
            ComputeService(),
            QueueService(),
            MonitoringService(),
        )

        deployment = facade.deploy_service(
            service_name="feed-api",
            artifact_path="build/feed-api.zip",
            worker_count=3,
        )

        self.assertEqual(deployment.service_name, "feed-api")
        self.assertEqual(deployment.instance_ids, ["vm-feed-api-1", "vm-feed-api-2", "vm-feed-api-3"])
        self.assertEqual(deployment.queue_name, "queue-feed-api")
        self.assertEqual(deployment.dashboard_url, "/dashboards/feed-api")

    def test_rollback_stops_compute_instances(self):
        from cloud_services_facade import (
            CloudDeploymentFacade,
            ComputeService,
            MonitoringService,
            ObjectStorageService,
            QueueService,
        )

        compute = ComputeService()
        facade = CloudDeploymentFacade(
            ObjectStorageService(),
            compute,
            QueueService(),
            MonitoringService(),
        )
        deployment = facade.deploy_service("feed-api", "build/feed-api.zip", 2)

        stopped = facade.rollback(deployment)

        self.assertEqual(stopped, ["vm-feed-api-1", "vm-feed-api-2"])
        self.assertEqual(compute.running_instances, [])


if __name__ == "__main__":
    unittest.main()
