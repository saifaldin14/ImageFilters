import wx
import cv2
import numpy as np
from wx_gui import BaseLayout
from tools import apply_hue_filter
from tools import apply_rgb_filters
from tools import load_img_resized
from tools import spline_to_lookup_table
from tools import cartoonize
from tools import pencil_sketch_on_canvas

INCREASE_LOOKUP_TABLE = spline_to_lookup_table([0, 64, 128, 192, 256],
                                               [0, 70, 140, 210, 256])
DECREASE_LOOKUP_TABLE = spline_to_lookup_table([0, 64, 128, 192, 256],
                                               [0, 30, 80, 120, 192])

class FilterLayout(BaseLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        color_canvas = load_img_resized('pencilsketch_bg.jpg',
                                        (self.imgWidth, self.imgHeight))
        self.canvas = cv2.cvtColor(color_canvas, cv2.COLOR_RGB2GRAY)

    def augment_layout(self):
        """ Add a row of radio buttons below the camera feed. """

        # create a horizontal layout with all filter modes as radio buttons
        pnl = wx.Panel(self, -1)
        self.mode_warm = wx.RadioButton(pnl, -1, 'Warming Filter', (10, 10),
                                        style=wx.RB_GROUP)
        self.mode_cool = wx.RadioButton(pnl, -1, 'Cooling Filter', (10, 10))
        self.mode_sketch = wx.RadioButton(pnl, -1, 'Pencil Sketch', (10, 10))
        self.mode_cartoon = wx.RadioButton(pnl, -1, 'Cartoon', (10, 10))
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.mode_warm, 1)
        hbox.Add(self.mode_cool, 1)
        hbox.Add(self.mode_sketch, 1)
        hbox.Add(self.mode_cartoon, 1)
        pnl.SetSizer(hbox)

        # add panel with radio buttons to existing panels in a vertical
        # arrangement
        self.panels_vertical.Add(pnl, flag=wx.EXPAND | wx.BOTTOM | wx.TOP,
                                 border=1)

    @staticmethod
    def _render_warm(rgb_image: np.ndarray) -> np.ndarray:
        interim_img = apply_rgb_filters(rgb_image,
                                        red_filter=INCREASE_LOOKUP_TABLE,
                                        blue_filter=DECREASE_LOOKUP_TABLE)
        return apply_hue_filter(interim_img, INCREASE_LOOKUP_TABLE)

    @staticmethod
    def _render_cool(rgb_image: np.ndarray) -> np.ndarray:
        interim_img = apply_rgb_filters(rgb_image,
                                        red_filter=DECREASE_LOOKUP_TABLE,
                                        blue_filter=INCREASE_LOOKUP_TABLE)
        return apply_hue_filter(interim_img, DECREASE_LOOKUP_TABLE)

    def process_frame(self, frame_rgb: np.ndarray) -> np.ndarray:
        """Process the frame of the camera (or other capture device)
        Choose a filter effect based on the which of the radio buttons
        was clicked.
        :param frame_rgb: Image to process in rgb format, of shape (H, W, 3)
        :return: Processed image in rgb format, of shape (H, W, 3)
        """
        if self.mode_warm.GetValue():
            return self._render_warm(frame_rgb)
        elif self.mode_cool.GetValue():
            return self._render_cool(frame_rgb)
        elif self.mode_sketch.GetValue():
            return pencil_sketch_on_canvas(frame_rgb, canvas=self.canvas)
        elif self.mode_cartoon.GetValue():
            return cartoonize(frame_rgb)
        else:
            raise NotImplementedError()


def main():
    # open webcam
    capture = cv2.VideoCapture(0)
    # opening the channel ourselves, if it failed to open.
    if not(capture.isOpened()):
        capture.open()

    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # start graphical user interface
    app = wx.App()
    layout = FilterLayout(capture, title='Fun with Filters')
    layout.Center()
    layout.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()