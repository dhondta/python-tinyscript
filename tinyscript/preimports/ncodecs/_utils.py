# -*- coding: UTF-8 -*-
import codecs
import re
import sys
import types
from functools import wraps
from six import b, binary_type, string_types, text_type


__all__ = ["b", "codecs", "ensure_str", "fix_inout_formats"]


isb = lambda s: isinstance(s, binary_type)
iss = lambda s: isinstance(s, string_types)

fix = lambda x, ref: b(x) if isb(ref) else ensure_str(x) if iss(ref) else x


def add_codec(ename, encode=None, decode=None, pattern=None, text_only=False):
    """
    This adds a new codec to the codecs module setting its encode and/or decode
     functions, eventually dynamically naming the encoding with a pattern and
     with file handling (if text_only is False).
    
    :param ename:     encoding name
    :param encode:    encoding function or None
    :param decode:    decoding function or None
    :param pattern:   pattern for dynamically naming the encoding
    :param text_only: whether to consider file handling with the codec
    """
    if encode and not isinstance(encode, types.FunctionType):
        raise ValueError("Bad encode function")
    if decode and not isinstance(decode, types.FunctionType):
        raise ValueError("Bad decode function")
    if not encode and not decode:
        raise ValueError("At least one function must be defined")
    # search function for the new encoding
    def getregentry(encoding):
        if encoding != ename and not (pattern and re.match(pattern, encoding)):
            return
        fenc, fdec, name = encode, decode, encoding
        # prepare CodecInfo input arguments
        class Codec(codecs.Codec):
            def encode(self, input, errors='strict'):
                if fenc is None:
                    raise NotImplementedError
                return fenc(input, errors)

            def decode(self, input, errors='strict'):
                if fdec is None:
                    raise NotImplementedError
                return fdec(input, errors)
        
        class IncrementalEncoder(codecs.IncrementalEncoder):
            def encode(self, input, final=False):
                if fenc is None:
                    raise NotImplementedError
                return b(fenc(input, self.errors)[0])
        
        class IncrementalDecoder(codecs.IncrementalDecoder):
            def decode(self, input, final=False):
                if fdec is None:
                    raise NotImplementedError
                return ensure_str(fdec(input, self.errors)[0])
        
        incrementalencoder = IncrementalEncoder
        incrementaldecoder = IncrementalDecoder
        streamwriter       = None
        streamreader       = None
        if pattern:
            m = re.match(pattern, encoding)
            try:
                g = m.group(1)
                fenc = fenc(g) if fenc else fenc
                fdec = fdec(g) if fdec else fdec
            except IndexError:
                pass
        if fenc:
            fenc = fix_inout_formats(fenc)
        if fdec:
            fdec = fix_inout_formats(fdec)
        
        if not text_only:
            
            class StreamWriter(Codec, codecs.StreamWriter):
                charbuffertype = bytes

            class StreamReader(Codec, codecs.StreamReader):
                charbuffertype = bytes
            
            streamwriter = StreamWriter
            streamreader = StreamReader

        return codecs.CodecInfo(
            name=name,
            encode=Codec().encode,
            decode=Codec().decode,
            incrementalencoder=incrementalencoder,
            incrementaldecoder=incrementaldecoder,
            streamwriter=streamwriter,
            streamreader=streamreader,
        )
    codecs.register(getregentry)
codecs.add_codec = add_codec


def ensure_str(s, encoding='utf-8', errors='strict'):
    """
    Similar to six.ensure_str. Adapted here to avoid messing up with six version
     errors.
    """
    if sys.version[0] == "2" and isinstance(s, text_type):
        return s.encode(encoding, errors)
    elif sys.version[0] == "3" and isinstance(s, binary_type):
        try:
            return s.decode(encoding, errors)
        except:
            return s.decode("latin-1")
    return s


# make conversion functions compatible with input/output strings/bytes
def fix_inout_formats(f):
    """
    This decorator ensures that the first output of f will have the same text
     format as the first input (str or bytes).
    """
    @wraps(f)
    def _wrapper(*args, **kwargs):
        a0 = args[0]
        a0 = ensure_str(a0) if iss(a0) or isb(a0) else a0
        r = f(a0, *args[1:], **kwargs)
        return (fix(r[0], args[0]), ) + r[1:] if isinstance(r, (tuple, list)) \
               else fix(r, args[0])
    return _wrapper
