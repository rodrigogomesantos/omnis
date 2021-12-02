import colorsys
class ColorPrint:
    R = '\033[91m'
    G = '\033[92m'
    B = '\033[94m'
    C = '\033[96m'
    Y = '\033[93m'

    W = '\033[93m'+'[Aviso]: '+'\033[0m'
    E = '\033[91m'+'[Erro]:  '+'\033[0m'
    I = '\033[96m'+'[Info]:  '+'\033[0m'
    S = '\033[92m'+'[Success]:  '+'\033[0m'
    U = '\033[4m'
    B = '\033[1m'

def color(string, color):
    return str(getattr(ColorPrint, color)+str(string)+'\033[0m')



# https://gist.github.com/leetrout/2382411
def hex_to_rgb(hex_str):
    """Returns a tuple representing the given hex string as RGB.
    
    >>> hex_to_rgb('CC0000')
    (204, 0, 0)
    """
    if hex_str.startswith('#'):
        hex_str = hex_str[1:]
    return tuple([int(hex_str[i:i + 2], 16) for i in range(0, len(hex_str), 2)])


def rgb_to_hex(rgb):
    """Converts an rgb tuple to hex string for web.
    
    >>> rgb_to_hex((204, 0, 0))
    'CC0000'
    """
    return ''.join(["%0.2X" % c for c in rgb])


def scale_rgb_tuple(rgb, down=True):
    """Scales an RGB tuple up or down to/from values between 0 and 1.
    
    >>> scale_rgb_tuple((204, 0, 0))
    (.80, 0, 0)
    >>> scale_rgb_tuple((.80, 0, 0), False)
    (204, 0, 0)
    """
    if not down:
        return tuple([int(c*255) for c in rgb])
    return tuple([round(float(c)/255, 2) for c in rgb])


def make_triad(web_hex_str):
    """Returns a list 3 of hex strings in web format to be used for triad
    color schemes from the given base color.
    
    make_triad('CC0000')
    ['CC0000', 'A30000', '660000']
    """
    colors = [web_hex_str]
    orig_rgb = hex_to_rgb(web_hex_str)
    hue, sat, val = colorsys.rgb_to_hsv(*scale_rgb_tuple(orig_rgb))
    
    # make 40% more saturated
    d20 = (hue, min(1, sat / .6 ), val)#val * .75)
    colors.append(rgb_to_hex(scale_rgb_tuple(colorsys.hsv_to_rgb(*d20), False)))
    
    # make 70% darker or lighter
    if d20[1] < .8:
        d50 = (hue, min(1, sat / .4), val * .4)
    else:
        d50 = (hue, .1, 1)
    colors.append(rgb_to_hex(scale_rgb_tuple(colorsys.hsv_to_rgb(*d50), False)))
    
    return colors
