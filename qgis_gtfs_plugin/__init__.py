# -*- coding: utf-8 -*-


def classFactory(iface):
    from .plugin import GTFSLoader
    return GTFSLoader(iface)
