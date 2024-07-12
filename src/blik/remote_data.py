import pooch

from .reader import read_layers


def load_hiv_dataset():
    reg = pooch.create(
        path=pooch.os_cache("blik"),
        base_url='doi:10.5281/zenodo.6504891/',
    )
    reg.load_registry_from_doi()

    paths = [reg.fetch(f) for f in reg.registry_files]
    return read_layers(*paths)
