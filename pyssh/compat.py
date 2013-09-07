# -*- coding: utf-8 -*-

import six

if six.PY2:
    def to_bytes(data, encoding="utf-8"):
        return data.encode(encoding)
else:
    def to_bytes(data, encoding="utf-8"):
        return bytes(data, encoding)

text_type = six.text_type
binary_type = six.binary_type
