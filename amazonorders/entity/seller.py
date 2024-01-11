import logging

from amazonorders.session import BASE_URL

__author__ = "Alex Laird"
__copyright__ = "Copyright 2023, Alex Laird"
__version__ = "0.0.3"

logger = logging.getLogger(__name__)


class Seller:
    def __init__(self,
                 parsed,
                 item=None,
                 order=None) -> None:
        self.parsed = parsed
        self.item = item
        self.order = order

        self.name = self._parse_name()
        self.link = self._parse_link()

    def __repr__(self) -> str:
        return "<Seller: \"{}\">".format(self.name)

    def __str__(self) -> str:  # pragma: no cover
        return self.name

    def _parse_name(self):
        try:
            return self.parsed.text.split("Sold by:")[1].strip()
        except (AttributeError, IndexError):
            logger.warning("When building Seller, `name` could not be parsed.", exc_info=True)

    def _parse_link(self):
        try:
            tag = self.parsed.find("a")
            if tag:
                return "{}{}".format(BASE_URL, tag.attrs["href"])
        except (AttributeError, IndexError):
            logger.warning("When building Seller, `link` could not be parsed.", exc_info=True)