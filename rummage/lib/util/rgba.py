"""
RGBA.

Licensed under MIT
Copyright (c) 2012 - 2016 Isaac Muse <isaacmuse@gmail.com>
"""
from colorsys import rgb_to_hls, hls_to_rgb, rgb_to_hsv, hsv_to_rgb
import decimal

RGB_CHANNEL_SCALE = 1.0 / 255.0
HUE_SCALE = 1.0 / 360.0


def clamp(value, mn, mx):
    """Clamp the value to the the given minimum and maximum."""

    return max(min(value, mx), mn)


def round_int(dec):
    """Round float to nearest int using expected rounding."""

    return int(decimal.Decimal(dec).quantize(decimal.Decimal('0'), decimal.ROUND_HALF_UP))


class RGBA:
    """RGBA object for converting between color formats or applying filters to the color."""

    r = None
    g = None
    b = None
    a = None

    def __init__(self, r=0, g=0, b=0, a=255):
        """Initialize."""

        self.r = clamp(int(r), 0, 255)
        self.g = clamp(int(g), 0, 255)
        self.b = clamp(int(g), 0, 255)
        self.a = clamp(int(a), 0, 255)

    def get_rgba(self):
        """Get the RGB color with the alpha channel."""

        return (self.r, self.g, self.b, self.a)

    def get_rgb(self):
        """Get the RGB valuie."""

        return (self.r, self.g, self.b)

    def apply_alpha(self, r=0, g=0, b=0, a=255):
        """
        Apply the given transparency with the given background.

        This gives a color that represents what the eye sees with
        the transparent color against the given background.
        """

        r = clamp(int(r), 0, 255)
        g = clamp(int(g), 0, 255)
        b = clamp(int(g), 0, 255)
        a = clamp(int(a), 0, 255)

        def tx_alpha(cf, af, cb, ab):
            """Translate the color channel with the alpha channel and background channel color."""

            return round_int(
                abs(
                    cf * (af * RGB_CHANNEL_SCALE) + cb * (ab * RGB_CHANNEL_SCALE) * (1 - (af * RGB_CHANNEL_SCALE))
                )
            ) & 0xFF

        if self.a < 0xFF:
            self.r = tx_alpha(self.r, self.a, r, a)
            self.g = tx_alpha(self.g, self.a, g, a)
            self.b = tx_alpha(self.b, self.a, b, a)

        return self.get_rgb()

    def get_luminance(self):
        """Get percieved luminance."""

        return clamp(round_int(0.299 * self.r + 0.587 * self.g + 0.114 * self.b), 0, 255)

    def get_true_luminance(self):
        """Get true liminance."""

        l = self.tohls()[1]
        return clamp(round_int(l * 255.0), 0, 255)

    def alpha(self, factor):
        """Adjust alpha."""

        self.a = round_int(clamp(self.a + (255.0 * factor) - 255.0, 0.0, 255.0))

    def red(self, factor):
        """Adjust red."""

        self.r = round_int(clamp(self.r + (255.0 * factor) - 255.0, 0.0, 255.0))

    def green(self, factor):
        """Adjust green."""

        self.g = round_int(clamp(self.g + (255.0 * factor) - 255.0, 0.0, 255.0))

    def blue(self, factor):
        """Adjust blue."""

        self.b = round_int(clamp(self.b + (255.0 * factor) - 255.0, 0.0, 255.0))

    def luminance(self, factor):
        """Get true luminance."""

        h, l, s = self.tohls()
        l = clamp(l + factor - 1.0, 0.0, 1.0)
        self.fromhls(h, l, s)

    def tohsv(self):
        """Convert to HSV color format."""

        return rgb_to_hsv(self.r * RGB_CHANNEL_SCALE, self.g * RGB_CHANNEL_SCALE, self.b * RGB_CHANNEL_SCALE)

    def fromhsv(self, h, s, v):
        """Convert to RGB from HSV."""

        r, g, b = hsv_to_rgb(h, s, v)
        self.r = clamp(round_int(r * 255.0), 0, 255)
        self.g = clamp(round_int(g * 255.0), 0, 255)
        self.b = clamp(round_int(b * 255.0), 0, 255)

    def tohls(self):
        """Convert to HLS color format."""

        return rgb_to_hls(self.r * RGB_CHANNEL_SCALE, self.g * RGB_CHANNEL_SCALE, self.b * RGB_CHANNEL_SCALE)

    def fromhls(self, h, l, s):
        """Convert to RGB from HSL."""

        r, g, b = hls_to_rgb(h, l, s)
        self.r = clamp(round_int(r * 255.0), 0, 255)
        self.g = clamp(round_int(g * 255.0), 0, 255)
        self.b = clamp(round_int(b * 255.0), 0, 255)

    def tohwb(self):
        """Convert to HWB from RGB."""

        h, s, v = self.tohsv()
        w = (1.0 - s) * v
        b = 1.0 - v
        return h, w, b

    def fromhwb(self, h, w, b):
        """Convert to RGB from HWB."""

        # Normalize white and black
        # w + b <= 1.0
        if w + b > 1.0:
            norm_factor = 1.0 / (w + b)
            w *= norm_factor
            b *= norm_factor

        # Convert to HSV and then to RGB
        s = 1.0 - (w / (1.0 - b))
        v = 1.0 - b
        r, g, b = hsv_to_rgb(h, s, v)
        self.r = clamp(round_int(r * 255.0), 0, 255)
        self.g = clamp(round_int(g * 255.0), 0, 255)
        self.b = clamp(round_int(b * 255.0), 0, 255)

    def colorize(self, deg):
        """Colorize the color with the given hue."""

        h, l, s = self.tohls()
        h = clamp(deg * HUE_SCALE, 0.0, 1.0)
        self.fromhls(h, l, s)

    def hue(self, deg):
        """Shift the hue."""

        d = deg * HUE_SCALE
        h, l, s = self.tohls()
        h = h + d
        while h > 1.0:
            h -= 1.0
        while h < 0.0:
            h += 1.0
        self.fromhls(h, l, s)

    def contrast(self, factor):
        """Adjust contrast."""

        # Algorithm can't handle any thing beyond +/-255 (or a factor from 0 - 2)
        # Convert factor between (-255, 255)
        f = (clamp(factor, 0.0, 2.0) - 1.0) * 255.0
        f = (259 * (f + 255)) / (255 * (259 - f))

        # Increase/decrease contrast accordingly.
        self.r = clamp(round_int((f * (self.r - 128)) + 128), 0, 255)
        self.g = clamp(round_int((f * (self.g - 128)) + 128), 0, 255)
        self.b = clamp(round_int((f * (self.b - 128)) + 128), 0, 255)

    def invert(self):
        """Invert the color."""

        self.r ^= 0xFF
        self.g ^= 0xFF
        self.b ^= 0xFF

    def saturation(self, factor):
        """Saturate or unsaturate the color by the given factor."""

        h, l, s = self.tohls()
        s = clamp(s + factor - 1.0, 0.0, 1.0)
        self.fromhls(h, l, s)

    def grayscale(self):
        """Convert the color with a grayscale filter."""

        luminance = self.get_luminance()
        self.r = luminance
        self.g = luminance
        self.b = luminance

    def sepia(self):
        """Apply a sepia filter to the color."""

        r = clamp(round_int((self.r * .393) + (self.g * .769) + (self.b * .189)), 0, 255)
        g = clamp(round_int((self.r * .349) + (self.g * .686) + (self.b * .168)), 0, 255)
        b = clamp(round_int((self.r * .272) + (self.g * .534) + (self.b * .131)), 0, 255)
        self.r, self.g, self.b = r, g, b

    def _get_overage(self, c):
        """Get overage."""

        if c < 0.0:
            o = 0.0 + c
            c = 0.0
        elif c > 255.0:
            o = c - 255.0
            c = 255.0
        else:
            o = 0.0
        return o, c

    def _distribute_overage(self, c, o, s):
        """Distribute overage."""

        channels = len(s)
        if channels == 0:
            return c
        parts = o / len(s)
        if "r" in s and "g" in s:
            c = c[0] + parts, c[1] + parts, c[2]
        elif "r" in s and "b" in s:
            c = c[0] + parts, c[1], c[2] + parts
        elif "g" in s and "b" in s:
            c = c[0], c[1] + parts, c[2] + parts
        elif "r" in s:
            c = c[0] + parts, c[1], c[2]
        elif "g" in s:
            c = c[0], c[1] + parts, c[2]
        else:  # "b" in s:
            c = c[0], c[1], c[2] + parts
        return c

    def brightness(self, factor):
        """
        Adjust the brightness by the given factor.

        Brightness is determined by percieved luminance.
        """

        channels = ["r", "g", "b"]
        total_lumes = clamp(self.get_luminance() + (255.0 * factor) - 255.0, 0.0, 255.0)

        if total_lumes == 255.0:
            # white
            self.r, self.g, self.b = 0xFF, 0xFF, 0xFF
        elif total_lumes == 0.0:
            # black
            self.r, self.g, self.b = 0x00, 0x00, 0x00
        else:
            # Adjust Brightness
            pts = (total_lumes - 0.299 * self.r - 0.587 * self.g - 0.114 * self.b)
            slots = set(channels)
            components = [float(self.r) + pts, float(self.g) + pts, float(self.b) + pts]
            count = 0
            for c in channels:
                overage, components[count] = self._get_overage(components[count])
                if overage:
                    slots.remove(c)
                    components = list(self._distribute_overage(components, overage, slots))
                count += 1

            self.r = clamp(round_int(components[0]), 0, 255)
            self.g = clamp(round_int(components[1]), 0, 255)
            self.b = clamp(round_int(components[2]), 0, 255)

    def __repr__(self):
        """Representation."""

        return 'RGBA(r={}, g={}, b={}, a={})'.format(*self.get_rgba())

    __str__ = __repr__
