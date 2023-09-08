import pathlib

# CSS classes
SCROLLBAR_THUMB = "scroll__scrollbar-thumb"
ORGANIZATION = "search-snippet-view__link-overlay"
ORGANIZATION_NAME = "orgpage-header-view__header"
ORGANIZATION_ADDRESS = "business-contacts-view__address-link"
ORGANIZATION_WEBSITE = "business-urls-view__text"
ORGANIZATION_OPENING_HOURS = "openingHours"
ORGANIZATION_REVIEWS_COUNT = "business-header-rating-view__text"
ORGANIZATION_STARS = "business-rating-badge-view__stars"
STAR_FULL = "inline-image _loaded business-rating-badge-view__star _full _size_m"
STAR_HALF = "inline-image _loaded business-rating-badge-view__star _half _size_m"
TOPIC_CASE = "business-aspect-view"
TOPIC_NAME = "business-aspect-view__text"
TOPIC_COUNT = "business-aspect-view__count"
REVIEW = "business-review-view__info"
REVIEW_TEXT = "business-review-view__body-text"
REVIEW_DATE = "datePublished"
REVIEW_NAME = "name"
REVIEW_REACTION = "business-reactions-view__container"

# PATHS
ROOT_DIR = pathlib.Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
ORGANIZATION_LINKS_FILE_NAME = "organization_links_need_spb.json"#"organization_links.json"
ORGANIZATION_INFO_FILE_NAME = "need_spb.json"#"spb.json"  # "organization_info.json"
