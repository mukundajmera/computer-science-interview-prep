package v2_extended;

import java.util.Optional;

enum Channel {
    EMAIL, SMS, PUSH
}

class Product {
    final String id;
    final String name;

    Product(String id, String name) {
        this.id = id;
        this.name = name;
    }
}

class Merchant {
    final String id;
    final String name;

    Merchant(String id, String name) {
        this.id = id;
        this.name = name;
    }
}


class PriceAlertSubscription {
    final String id;
    final String userId;
    final String productId;
    final Optional<Integer> thresholdPrice;
    final Optional<Double> percentageDrop;
    final Channel channel;

    PriceAlertSubscription(String id, String userId, String productId, Optional<Integer> thresholdPrice, Optional<Double> percentageDrop, Channel channel) {
        this.id = id;
        this.userId = userId;
        this.productId = productId;
        this.thresholdPrice = thresholdPrice;
        this.percentageDrop = percentageDrop;
        this.channel = channel;
    }
}
