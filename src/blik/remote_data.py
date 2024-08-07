import pooch

from .reader import read_layers


def load_hiv_dataset():
    reg_tomo = pooch.create(
        path=pooch.os_cache("blik"),
        base_url="doi:10.5281/zenodo.6504891/",
    )
    reg_tomo.load_registry_from_doi()

    # made separate zenodo entry for star file with pixel size
    reg_picks = pooch.create(
        path=pooch.os_cache("blik"),
        base_url="doi:10.5281/zenodo.12743309/",
    )
    reg_picks.load_registry_from_doi()

    paths = [
        reg_tomo.fetch("01_10.00Apx.mrc"),
        reg_picks.fetch("01_10.00Apx.star"),
    ]

    return read_layers(*paths)
