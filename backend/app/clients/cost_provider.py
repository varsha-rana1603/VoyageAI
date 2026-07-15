"""
cost_provider.py -- replaces the paid Numbeo dependency.

get_city_cost_data(city, country) returns DAILY TOURIST EXPENDITURE
(not cost of living) across three tiers, by combining:

  1. WorldBankClient   -> country-level cost index (GDP per capita, PPP)
  2. GeoClient          -> city-tier multiplier (capital/metro vs town)
  3. _BASE_RATES_USD    -> explicit, documented per-category USD assumptions
                           for a "reference" mid-income destination
  4. CurrencyClient     -> convert the USD-modeled figures to local currency
  5. WikivoyageClient   -> opportunistic override of the accommodation
                           budget figure when real text-mined data exists

No single free source gives per-city tourist prices, so steps 1-3 form an
explicit, versioned *model* rather than a lookup. That is the honest
tradeoff for "free + no approval + scalable to tens of thousands of
destinations" -- and matches the "good architecture over perfect accuracy"
brief. Step 5 pulls in real numbers wherever Wikivoyage happens to have them,
without the whole pipeline depending on that coverage being complete.

ARCHITECTURE NOTES FOR THE INGESTION PIPELINE
-----------------------------------------------
iter_destinations() -> get_city_cost_data(city, country) -> load_cost_profile()
    -> store JSONB in PostgreSQL

- Every network-touching sub-call (World Bank, Nominatim, Frankfurter,
  Wikivoyage) is cached via the injected Cache (see app/cache/cache.py),
  with TTLs chosen per source's actual update frequency -- not arbitrarily.
- Nominatim's 1 req/sec policy is enforced inside GeoClient itself, so a
  bulk ingestion loop calling get_city_cost_data() in sequence will
  naturally self-throttle rather than get banned. For a large one-time
  backfill, prefer batching city-tier resolution as its own pre-pass
  (dedupe (city,country) pairs first -- many destinations share a city)
  before running the full pipeline.
- The final CityCostProfile is what gets stored in Postgres as JSONB.
  It is NOT re-derived from cache at read time; once ingested, it's a
  point-in-time snapshot. Re-ingestion (e.g. annually, when World Bank
  publishes new GDP figures) is a deliberate re-run, not automatic.
"""

from __future__ import annotations

import httpx

from app.cache.cache import Cache, FileCache
from app.clients.currency_client import CurrencyClient
from app.clients.geo_client import GeoClient
from app.clients.wikivoyage_client import WikivoyageClient
from app.clients.worldbank_client import WorldBankClient
from app.models.cost_models import (
    CategoryCosts,
    CityCostProfile,
    CostConfidence,
    DailyCost,
)

# --------------------------------------------------------------------------
# Explicit, versioned model assumptions.
#
# These are daily USD costs per category for a "reference" mid-income
# destination at 1.0x country cost index and 1.0x city tier. Every other
# destination is this baseline scaled by (country_cost_index * city_tier).
#
# Sourcing note: there is no free, unapproved, per-city API for these
# numbers -- that's the actual reason Numbeo/BudgetYourTrip are paid
# products. These are calibrated, order-of-magnitude travel-cost estimates
# (consistent with widely-cited public travel-budget writeups), not
# per-destination facts. Bump CALIBRATION_VERSION when these change so
# ingested rows can be tied back to the assumptions that produced them.
# --------------------------------------------------------------------------
CALIBRATION_VERSION = "v1"

_BASE_RATES_USD: dict[str, CategoryCosts] = {
    "budget": CategoryCosts(
        accommodation=15, food=8, transport=4, activities=5, misc=3
    ),
    "mid_range": CategoryCosts(
        accommodation=60, food=25, transport=10, activities=20, misc=10
    ),
    "luxury": CategoryCosts(
        accommodation=220, food=70, transport=35, activities=60, misc=30
    ),
}


class CostProvider:
    def __init__(
        self,
        cache: Cache | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        cache = cache or FileCache(cache_dir=".cache/cost_pipeline")
        http_client = http_client or httpx.Client(timeout=10.0)

        self._worldbank = WorldBankClient(cache, http_client)
        self._geo = GeoClient(cache, http_client)
        self._currency = CurrencyClient(cache, http_client)
        self._wikivoyage = WikivoyageClient(cache, http_client)

    def get_city_cost_data(self, city: str, country: str) -> dict:
        """
        Public entry point matching the required output schema. Kept as a
        plain dict return (via CityCostProfile.to_storage_dict()) since
        that's the exact shape the ingestion pipeline stores as JSONB.
        """
        country_code = _resolve_country_code(country)

        cost_index = self._worldbank.get_cost_index(country_code)
        city_tier = self._geo.get_city_tier_multiplier(city, country)
        combined_multiplier = cost_index * city_tier

        currency = self._currency.get_currency_for_country(country_code)
        fx_rate = self._currency.get_exchange_rate("USD", currency)

        daily_cost = self._build_daily_cost(combined_multiplier, fx_rate)

        confidence = CostConfidence.MODELED
        wikivoyage_signal = self._wikivoyage.get_cost_signal(city)
        if wikivoyage_signal.found and wikivoyage_signal.accommodation_budget_usd:
            daily_cost.budget.accommodation = round(
                wikivoyage_signal.accommodation_budget_usd * fx_rate, 2
            )
            confidence = CostConfidence.WIKIVOYAGE_ENRICHED

        profile = CityCostProfile(
            city=city,
            country=country,
            currency=currency,
            daily_cost=daily_cost,
            source=(
                f"modeled(world_bank_gdp_ppp+osm_city_tier,{CALIBRATION_VERSION})"
                + ("+wikivoyage" if confidence == CostConfidence.WIKIVOYAGE_ENRICHED else "")
                + "+frankfurter_fx"
            ),
            confidence=confidence,
        )
        return profile.to_storage_dict()

    def _build_daily_cost(self, multiplier: float, fx_rate: float) -> DailyCost:
        def scale(base: CategoryCosts) -> CategoryCosts:
            return CategoryCosts(
                accommodation=round(base.accommodation * multiplier * fx_rate, 2),
                food=round(base.food * multiplier * fx_rate, 2),
                transport=round(base.transport * multiplier * fx_rate, 2),
                activities=round(base.activities * multiplier * fx_rate, 2),
                misc=round(base.misc * multiplier * fx_rate, 2),
            )

        return DailyCost(
            budget=scale(_BASE_RATES_USD["budget"]),
            mid_range=scale(_BASE_RATES_USD["mid_range"]),
            luxury=scale(_BASE_RATES_USD["luxury"]),
        )


def _resolve_country_code(country: str) -> str:
    """
    Accepts either an ISO2 code or a common country name and returns ISO2.
    Small static table -- country identity doesn't change, no reason for
    this to be a network call.
    """
    if len(country) == 2:
        return country.upper()
    return _COUNTRY_NAME_TO_ISO2.get(country.strip().lower(), "US")


_COUNTRY_NAME_TO_ISO2 = {
    "india": "IN", "united states": "US", "united kingdom": "GB",
    "france": "FR", "germany": "DE", "italy": "IT", "spain": "ES",
    "japan": "JP", "thailand": "TH", "indonesia": "ID", "australia": "AU",
    "canada": "CA", "singapore": "SG", "united arab emirates": "AE",
    "switzerland": "CH", "mexico": "MX", "brazil": "BR", "south africa": "ZA",
    "vietnam": "VN", "nepal": "NP", "sri lanka": "LK", "turkey": "TR",
    "egypt": "EG", "morocco": "MA",
}


# --------------------------------------------------------------------------
# Module-level convenience function -- matches the exact call signature
# named in the ingestion pipeline: get_city_cost_data(city, country)
# --------------------------------------------------------------------------
_default_provider: CostProvider | None = None


def get_city_cost_data(city: str, country: str) -> dict:
    global _default_provider
    if _default_provider is None:
        _default_provider = CostProvider()
    return _default_provider.get_city_cost_data(city, country)
