from pathlib import Path
import time
import requests


BASE_URL = "https://www.football-data.co.uk/mmz4281"

# Seasons to download.
#
# 2526 = 2025/26
# 2627 = 2026/27
#
# Add older seasons here if required.
SEASONS = [
    "2526",
]

# Divisions to download.
#
# E0 = Premier League
# E1 = Championship
# E2 = League One
# E3 = League Two
# EC = National League
#
# Add more if required.
DIVISIONS = [
    "E0",
]

OUTPUT_DIRECTORY = Path("data")

MAX_ATTEMPTS = 6
TIMEOUT_SECONDS = 30

session = requests.Session()

session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "Chrome/140.0 Safari/537.36"
    )
})


def download_file(season: str, division: str) -> None:
    url = f"{BASE_URL}/{season}/{division}.csv"

    output_path = (
        OUTPUT_DIRECTORY
        / season
        / f"{division}.csv"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    print(f"Downloading {url}")

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = session.get(
                url,
                timeout=TIMEOUT_SECONDS
            )

            print(
                f"Attempt {attempt}/{MAX_ATTEMPTS}: "
                f"HTTP {response.status_code}"
            )

            if response.status_code == 200:
                content = response.content

                if not content.strip():
                    raise RuntimeError(
                        f"Empty response received from {url}"
                    )

                output_path.write_bytes(content)

                print(
                    f"Saved {output_path} "
                    f"({len(content):,} bytes)"
                )

                return

            # These are temporary/server-side errors,
            # so retry rather than immediately failing.
            if response.status_code in {
                429,
                500,
                502,
                503,
                504,
            }:
                if attempt < MAX_ATTEMPTS:
                    wait_seconds = 5 * attempt

                    print(
                        f"Temporary HTTP error. "
                        f"Waiting {wait_seconds} seconds..."
                    )

                    time.sleep(wait_seconds)
                    continue

            response.raise_for_status()

        except requests.RequestException as error:
            print(f"Request failed: {error}")

            if attempt == MAX_ATTEMPTS:
                raise

            wait_seconds = 5 * attempt

            print(
                f"Retrying in {wait_seconds} seconds..."
            )

            time.sleep(wait_seconds)

    raise RuntimeError(
        f"Unable to download {url} "
        f"after {MAX_ATTEMPTS} attempts."
    )


def main() -> None:
    for season in SEASONS:
        for division in DIVISIONS:
            download_file(
                season,
                division
            )


if __name__ == "__main__":
    main()
