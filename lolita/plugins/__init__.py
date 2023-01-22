def __list_all_modules():
    import glob
    from os.path import dirname, isfile

    work_dir = dirname(__file__)
    mod_paths = glob.glob(work_dir + "/*/*.py")

    all_module = [
        (((f.replace(work_dir, "")).replace("/", "."))[:-3])
        for f in mod_paths
        if isfile(f)
        and f.endswith(".py")
        and not f.endswith("__init__.py")
    ]

    return all_module


all_modules = sorted(__list_all_modules())
__all__ = all_modules + ["all_modules"]
