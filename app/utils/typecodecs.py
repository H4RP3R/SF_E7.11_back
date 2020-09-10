from bson.codec_options import TypeCodec
from bson.codec_options import TypeRegistry
from bson.codec_options import CodecOptions


class SetCodec(TypeCodec):
    python_type = set
    bson_type = list

    def transform_python(self, value):
        return list(value)

    def transform_bson(self, value):
        return value


set_codec = SetCodec()
type_registry = TypeRegistry([set_codec])
codec_options = CodecOptions(type_registry=type_registry)
