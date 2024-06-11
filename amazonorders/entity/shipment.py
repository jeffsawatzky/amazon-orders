__copyright__ = "Copyright (c) 2024 Alex Laird"
__license__ = "MIT"

import logging
from typing import List, Optional

from bs4 import Tag

from amazonorders import util
from amazonorders.conf import AmazonOrdersConfig
from amazonorders.entity.item import Item
from amazonorders.entity.parsable import Parsable

logger = logging.getLogger(__name__)


class Shipment(Parsable):
    """
    An Amazon Shipment, which should contain one or more :class:`~amazonorders.entity.item.Item`'s.
    """

    def __init__(self,
                 parsed: Tag,
                 config: AmazonOrdersConfig) -> None:
        super().__init__(parsed, config)

        #: The Shipment Items.
        self.items: List[Item] = self._parse_items()
        #: The Shipment delivery status.
        self.delivery_status: Optional[str] = self.safe_simple_parse(
            selector=self.config.selectors.FIELD_SHIPMENT_DELIVERY_STATUS_SELECTOR)
        #: The Shipment tracking link.
        self.tracking_link: Optional[str] = self.safe_simple_parse(
            selector=self.config.selectors.FIELD_SHIPMENT_TRACKING_LINK_SELECTOR,
            link=True)

    def __repr__(self) -> str:
        return f"<Shipment: \"{self.items}\">"

    def __str__(self) -> str:  # pragma: no cover
        return f"Shipment: {self.items}"

    def __lt__(self, other):
        if self.delivery_status:
            return self.delivery_status < str(other.delivery_status if other.delivery_status else "")
        else:
            return str(self.items) < str(other.items)

    def _parse_items(self) -> List[Item]:
        items = [Item(x, self.config) for x in util.select(self.parsed, self.config.selectors.ITEM_ENTITY_SELECTOR)]
        items.sort()
        return items
