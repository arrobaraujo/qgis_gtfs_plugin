# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QMetaType, QVariant
from qgis.core import QgsField


def _qmeta_type_from_qvariant(qvariant_type):
    """Returns a QMetaType enum value compatible with both Qt5/Qt6 APIs."""
    type_name_by_variant = {
        QVariant.String: "QString",
        QVariant.Int: "Int",
        QVariant.Double: "Double",
    }
    type_name = type_name_by_variant.get(qvariant_type)
    if not type_name:
        return None

    enum_container = getattr(QMetaType, "Type", None)
    if enum_container and hasattr(enum_container, type_name):
        return getattr(enum_container, type_name)
    if hasattr(QMetaType, type_name):
        return getattr(QMetaType, type_name)
    return None


def build_field(name: str, qvariant_type) -> QgsField:
    """Creates QgsField with a modern type API and a safe backward fallback."""
    qmeta_type = _qmeta_type_from_qvariant(qvariant_type)
    if qmeta_type is not None:
        try:
            return QgsField(name, qmeta_type)
        except TypeError:
            pass
    return QgsField(name, qvariant_type)
