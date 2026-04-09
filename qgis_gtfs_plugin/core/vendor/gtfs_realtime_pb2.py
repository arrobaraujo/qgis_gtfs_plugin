# -*- coding: utf-8 -*-
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

_sym_db = _symbol_database.Default()

# Definindo Descritores Manuais (sem serialized_pb para evitar erros de parsing)
# Esta abordagem é mais robusta para diferentes ambientes QGIS.

DESCRIPTOR = _descriptor.FileDescriptor(
    name='gtfs-realtime.proto',
    package='transit_realtime',
    syntax='proto2',
    serialized_options=None,
)

# --- Position ---
_POSITION = _descriptor.Descriptor(
    name='Position',
    full_name='transit_realtime.Position',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(name='latitude', full_name='transit_realtime.Position.latitude', index=0, number=1, type=2, cpp_type=6, label=2, default_value=float(0), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None),
        _descriptor.FieldDescriptor(name='longitude', full_name='transit_realtime.Position.longitude', index=1, number=2, type=2, cpp_type=6, label=2, default_value=float(0), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None),
        _descriptor.FieldDescriptor(name='bearing', full_name='transit_realtime.Position.bearing', index=2, number=3, type=2, cpp_type=6, label=1, default_value=float(0), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None),
        _descriptor.FieldDescriptor(name='speed', full_name='transit_realtime.Position.speed', index=3, number=5, type=2, cpp_type=6, label=1, default_value=float(0), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    oneofs=[],
    serialized_options=None,
    is_extendable=False,
    syntax='proto2'
)

# --- TripDescriptor ---
_TRIPDESCRIPTOR = _descriptor.Descriptor(
    name='TripDescriptor',
    full_name='transit_realtime.TripDescriptor',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(name='trip_id', full_name='transit_realtime.TripDescriptor.trip_id', index=0, number=1, type=9, cpp_type=9, label=1, default_value=u"", message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None),
        _descriptor.FieldDescriptor(name='route_id', full_name='transit_realtime.TripDescriptor.route_id', index=1, number=5, type=9, cpp_type=9, label=1, default_value=u"", message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    oneofs=[],
    serialized_options=None,
    is_extendable=False,
    syntax='proto2'
)

# --- VehicleDescriptor ---
_VEHICLEDESCRIPTOR = _descriptor.Descriptor(
    name='VehicleDescriptor',
    full_name='transit_realtime.VehicleDescriptor',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(name='id', full_name='transit_realtime.VehicleDescriptor.id', index=0, number=1, type=9, cpp_type=9, label=1, default_value=u"", message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    oneofs=[],
    serialized_options=None,
    is_extendable=False,
    syntax='proto2'
)

# --- VehiclePosition ---
_VEHICLEPOSITION = _descriptor.Descriptor(
    name='VehiclePosition',
    full_name='transit_realtime.VehiclePosition',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(name='trip', full_name='transit_realtime.VehiclePosition.trip', index=0, number=1, type=11, cpp_type=10, label=1, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None),
        _descriptor.FieldDescriptor(name='vehicle', full_name='transit_realtime.VehiclePosition.vehicle', index=1, number=8, type=11, cpp_type=10, label=1, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None),
        _descriptor.FieldDescriptor(name='position', full_name='transit_realtime.VehiclePosition.position', index=2, number=2, type=11, cpp_type=10, label=1, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None),
        _descriptor.FieldDescriptor(name='timestamp', full_name='transit_realtime.VehiclePosition.timestamp', index=3, number=5, type=4, cpp_type=4, label=1, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    oneofs=[],
    serialized_options=None,
    is_extendable=True,
    syntax='proto2'
)

# --- FeedEntity ---
_FEEDENTITY = _descriptor.Descriptor(
    name='FeedEntity',
    full_name='transit_realtime.FeedEntity',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(name='id', full_name='transit_realtime.FeedEntity.id', index=0, number=1, type=9, cpp_type=9, label=2, default_value=u"", message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None),
        _descriptor.FieldDescriptor(name='vehicle', full_name='transit_realtime.FeedEntity.vehicle', index=1, number=4, type=11, cpp_type=10, label=1, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    oneofs=[],
    serialized_options=None,
    is_extendable=True,
    syntax='proto2'
)

# --- FeedHeader ---
_FEEDHEADER = _descriptor.Descriptor(
    name='FeedHeader',
    full_name='transit_realtime.FeedHeader',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(name='gtfs_realtime_version', full_name='transit_realtime.FeedHeader.gtfs_realtime_version', index=0, number=1, type=9, cpp_type=9, label=2, default_value=u"", message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None),
        _descriptor.FieldDescriptor(name='timestamp', full_name='transit_realtime.FeedHeader.timestamp', index=1, number=3, type=4, cpp_type=4, label=1, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    oneofs=[],
    serialized_options=None,
    is_extendable=False,
    syntax='proto2'
)

# --- FeedMessage ---
_FEEDMESSAGE = _descriptor.Descriptor(
    name='FeedMessage',
    full_name='transit_realtime.FeedMessage',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(name='header', full_name='transit_realtime.FeedMessage.header', index=0, number=1, type=11, cpp_type=10, label=2, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None),
        _descriptor.FieldDescriptor(name='entity', full_name='transit_realtime.FeedMessage.entity', index=1, number=2, type=11, cpp_type=10, label=3, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    oneofs=[],
    serialized_options=None,
    is_extendable=True,
    syntax='proto2'
)

# Relacionamentos de tipos
_FEEDMESSAGE.fields_by_name['header'].message_type = _FEEDHEADER
_FEEDMESSAGE.fields_by_name['entity'].message_type = _FEEDENTITY
_FEEDENTITY.fields_by_name['vehicle'].message_type = _VEHICLEPOSITION
_VEHICLEPOSITION.fields_by_name['trip'].message_type = _TRIPDESCRIPTOR
_VEHICLEPOSITION.fields_by_name['vehicle'].message_type = _VEHICLEDESCRIPTOR
_VEHICLEPOSITION.fields_by_name['position'].message_type = _POSITION

# Registro de Classes
FeedMessage = _reflection.GeneratedProtocolMessageType('FeedMessage', (_message.Message,), {
    'DESCRIPTOR': _FEEDMESSAGE,
    '__module__': 'gtfs_realtime_pb2'
})
FeedHeader = _reflection.GeneratedProtocolMessageType('FeedHeader', (_message.Message,), {
    'DESCRIPTOR': _FEEDHEADER,
    '__module__': 'gtfs_realtime_pb2'
})
FeedEntity = _reflection.GeneratedProtocolMessageType('FeedEntity', (_message.Message,), {
    'DESCRIPTOR': _FEEDENTITY,
    '__module__': 'gtfs_realtime_pb2'
})
VehiclePosition = _reflection.GeneratedProtocolMessageType('VehiclePosition', (_message.Message,), {
    'DESCRIPTOR': _VEHICLEPOSITION,
    '__module__': 'gtfs_realtime_pb2'
})
Position = _reflection.GeneratedProtocolMessageType('Position', (_message.Message,), {
    'DESCRIPTOR': _POSITION,
    '__module__': 'gtfs_realtime_pb2'
})
TripDescriptor = _reflection.GeneratedProtocolMessageType('TripDescriptor', (_message.Message,), {
    'DESCRIPTOR': _TRIPDESCRIPTOR,
    '__module__': 'gtfs_realtime_pb2'
})
VehicleDescriptor = _reflection.GeneratedProtocolMessageType('VehicleDescriptor', (_message.Message,), {
    'DESCRIPTOR': _VEHICLEDESCRIPTOR,
    '__module__': 'gtfs_realtime_pb2'
})

_sym_db.RegisterMessage(FeedMessage)
_sym_db.RegisterMessage(FeedHeader)
_sym_db.RegisterMessage(FeedEntity)
_sym_db.RegisterMessage(VehiclePosition)
_sym_db.RegisterMessage(Position)
_sym_db.RegisterMessage(TripDescriptor)
_sym_db.RegisterMessage(VehicleDescriptor)
