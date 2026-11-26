package v2_extended;

import java.time.Clock;
import java.util.List;
import java.util.Optional;

interface Transport {
    Optional<Integer> fetchPrice(String productId, String merchantId);
}

public class PriceCollectorV2 {
    private final SubscriptionService priceService;
    private final List<String> productIds;
    private final List<String> merchantIds;
    private final Transport transport;
    private final Clock clock;

    public PriceCollectorV2(SubscriptionService priceService, List<String> productIds, List<String> merchantIds, Transport transport, Clock clock) {
        this.priceService = priceService;
        this.productIds = productIds;
        this.merchantIds = merchantIds;
        this.transport = transport;
        this.clock = clock;
    }

    public void poll() {
        for (String productId : productIds) {
            for (String merchantId : merchantIds) {
                Optional<Integer> priceCentsOpt = transport.fetchPrice(productId, merchantId);
                if (priceCentsOpt.isPresent()) {
                    PriceRecord record = new PriceRecord(clock.instant().getEpochSecond(), priceCentsOpt.get(), true);
                    priceService.onPriceUpdate(productId, merchantId, record);
                }
            }
        }
    }
}
