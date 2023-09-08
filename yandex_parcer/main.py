from yandex_parcer.yandex_maps_parcer import (
    get_organizations_by_link,
    get_organization_info_by_link,
)
import logging.config
from yandex_parcer.utils.logging_conf import get_logging_conf
from tqdm import tqdm

logging.config.dictConfig(get_logging_conf())


def generate_map_url(latitude, longitude, zoom_level, search_text="Pyatyorochka"):
    return f"https://yandex.com/maps/2/saint-petersburg/?ll={longitude}%2C{latitude}&z={zoom_level}&mode=search&text={search_text}"


if __name__ == "__main__":
    start_latitude = 59.994696
    start_longitude = 30.152348

    end_latitude = 59.737494
    end_longitude = 30.623910

    zoom_level = 14

    count_steps_latitude = 8
    count_steps_longitude = 8
    for name in [
        "Pyatyorochka",
        "Perekrestok",
        "Magnit",
        "Diksi",
        "Krasnoe&Beloe"
        "Semishagoff",
        "Lenta",
        "Spar",
    ]:
        for i in tqdm(range(0, count_steps_latitude)):
            for j in tqdm(range(0, count_steps_longitude), leave=True):
                latitude = (
                        start_latitude
                        - (start_latitude - end_latitude) / count_steps_latitude * i
                )
                longitude = (
                        start_longitude
                        - (start_longitude - end_longitude) / count_steps_longitude * j
                )
                link = generate_map_url(latitude, longitude, zoom_level, name)
                logging.info(f"Получаем ссылки на организации по ссылке: {link}")
                organizations_href = get_organizations_by_link(link)
                get_organization_info_by_link(organizations_href)