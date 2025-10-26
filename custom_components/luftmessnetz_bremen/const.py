"""Constants for the Luftmessnetz Bremen integration."""

from datetime import timedelta
import logging

DOMAIN = "luftmessnetz_bremen"

CSV_URL = "https://luftmessnetz.bremen.de/station/{station}.csv"
DEFAULT_STATION = "DEHB002"  # Bremen-Ost

CONF_STATION = "station"

DEFAULT_UPDATE_INTERVAL = timedelta(minutes=15)

LOGGER = logging.getLogger(__name__)
