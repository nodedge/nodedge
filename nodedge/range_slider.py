from PySide6 import QtCore, QtGui, QtWidgets


class RangeSlider(QtWidgets.QSlider):
    sliderMoved = QtCore.Signal(int, int)
    """ A slider for ranges.

        This class provides a dual-slider for ranges, where there is a defined
        maximum and minimum, as is a normal slider, but instead of having a
        single slider value, there are 2 slider values.

        This class emits the same signals as the QSlider base class, with the 
        exception of valueChanged
    """

    def __init__(self, *args):
        super(RangeSlider, self).__init__(*args)

        self._low = self.minimum()
        self._high = self.maximum()

        self.pressed_control = QtWidgets.QStyle.SC_None
        self.tick_interval = 0
        self.tick_position = QtWidgets.QSlider.NoTicks
        self.hover_control = QtWidgets.QStyle.SC_None
        self.click_offset = 0

        # 0 for the low, 1 for the high, -1 for both
        self.active_slider = 0

    def low(self):
        return self._low

    def setLow(self, low: int):
        self._low = low
        self.update()

    def high(self):
        return self._high

    def setHigh(self, high):
        self._high = high
        self.update()

    def setRange(self, low, high):
        self.setLow(low)
        self.setHigh(high)

    def paintEvent(self, event):

        painter = QtGui.QPainter(self)
        style = QtWidgets.QApplication.style()

        opt = QtWidgets.QStyleOptionSlider()
        self.initStyleOption(opt)
        opt.siderValue = 0
        opt.sliderPosition = 0
        opt.subControls = QtWidgets.QStyle.SC_SliderGroove
        if self.tickPosition() != QtWidgets.QSlider.NoTicks:  # self.NoTicks:
            opt.subControls |= QtWidgets.QStyle.SC_SliderTickmarks
        style.drawComplexControl(QtWidgets.QStyle.CC_Slider, opt, painter, self)
        groove = style.subControlRect(
            QtWidgets.QStyle.CC_Slider, opt, QtWidgets.QStyle.SC_SliderGroove, self
        )

        # opt = QtWidgets.QStyleOptionSlider()
        self.initStyleOption(opt)
        opt.subControls = QtWidgets.QStyle.SC_SliderGroove
        # if self.tickPosition() != self.NoTicks:
        #    opt.subControls |= QtWidgets.QStyle.SC_SliderTickmarks
        opt.siderValue = 0
        opt.sliderPosition = self._low
        low_rect = style.subControlRect(
            QtWidgets.QStyle.CC_Slider, opt, QtWidgets.QStyle.SC_SliderHandle, self
        )
        opt.sliderPosition = self._high
        high_rect = style.subControlRect(
            QtWidgets.QStyle.CC_Slider, opt, QtWidgets.QStyle.SC_SliderHandle, self
        )

        low_pos = self.__pick(low_rect.center())
        high_pos = self.__pick(high_rect.center())

        min_pos = min(low_pos, high_pos)
        max_pos = max(low_pos, high_pos)

        c = QtCore.QRect(low_rect.center(), high_rect.center()).center()
        if opt.orientation == QtCore.Qt.Horizontal:
            span_rect = QtCore.QRect(
                QtCore.QPoint(min_pos, c.y() - 2), QtCore.QPoint(max_pos, c.y() + 1)
            )
        else:
            span_rect = QtCore.QRect(
                QtCore.QPoint(c.x() - 2, min_pos), QtCore.QPoint(c.x() + 1, max_pos)
            )

        # self.initStyleOption(opt)
        if opt.orientation == QtCore.Qt.Horizontal:
            groove.adjust(0, 0, -1, 0)
        else:
            groove.adjust(0, 0, 0, -1)

        if True:  # self.isEnabled():
            highlight = self.palette().color(QtGui.QPalette.Highlight)
            painter.setBrush(QtGui.QBrush(highlight))
            painter.setPen(QtGui.QPen(highlight, 0))
            # painter.setPen(QtGui.QPen(self.palette().color(QtGui.QPalette.Dark), 0))
            """
            if opt.orientation == QtCore.Qt.Horizontal:
                self.setupPainter(painter, opt.orientation, groove.center().x(), groove.top(), groove.center().x(), groove.bottom())
            else:
                self.setupPainter(painter, opt.orientation, groove.left(), groove.center().y(), groove.right(), groove.center().y())
            """
            # spanRect =
            painter.drawRect(span_rect.intersected(groove))
            # painter.drawRect(groove)

        for i, value in enumerate([self._low, self._high]):
            opt = QtWidgets.QStyleOptionSlider()
            self.initStyleOption(opt)

            # Only draw the groove for the first slider so it doesn't get drawn
            # on top of the existing ones every time
            if i == 0:
                opt.subControls = (
                    QtWidgets.QStyle.SC_SliderHandle
                )  # | QtWidgets.QStyle.SC_SliderGroove
            else:
                opt.subControls = QtWidgets.QStyle.SC_SliderHandle

            if self.tickPosition() != QtWidgets.QSlider.NoTicks:  # self.NoTicks:
                opt.subControls |= QtWidgets.QStyle.SC_SliderTickmarks

            if self.pressed_control:
                opt.activeSubControls = self.pressed_control
            else:
                opt.activeSubControls = self.hover_control

            opt.sliderPosition = value
            opt.sliderValue = value
            style.drawComplexControl(QtWidgets.QStyle.CC_Slider, opt, painter, self)

    def mousePressEvent(self, event):
        event.accept()

        style = QtWidgets.QApplication.style()
        button = event.button()

        # In a normal slider control, when the user clicks on a point in the
        # slider's total range, but not on the slider part of the control the
        # control would jump the slider value to where the user clicked.
        # For this control, clicks which are not direct hits will slide both
        # slider parts

        if button:
            opt = QtWidgets.QStyleOptionSlider()
            self.initStyleOption(opt)

            self.active_slider = -1

            for i, value in enumerate([self._low, self._high]):
                opt.sliderPosition = value
                # hit = style.hitTestComplexControl(style.CC_Slider, opt, event.pos(), self)
                hit = style.hitTestComplexControl(
                    style.ComplexControl.CC_Slider,
                    opt,
                    event.position().toPoint(),
                    self,
                )
                # if hit == style.SC_SliderHandle:
                if hit == style.SubControl.SC_SliderHandle:
                    self.active_slider = i
                    self.pressed_control = hit

                    # self.triggerAction(self.SliderMove)
                    self.triggerAction(self.SliderAction.SliderMove)
                    # self.setRepeatAction(self.SliderNoAction)
                    self.setRepeatAction(self.SliderAction.SliderNoAction)
                    self.setSliderDown(True)
                    break

            if self.active_slider < 0:
                self.pressed_control = QtWidgets.QStyle.SC_SliderHandle
                # self.click_offset = self.__pixelPosToRangeValue(self.__pick(event.pos()))
                self.click_offset = self.__pixelPosToRangeValue(
                    self.__pick(event.position().toPoint())
                )
                # self.triggerAction(self.SliderMove)
                self.triggerAction(self.SliderAction.SliderMove)
                # self.setRepeatAction(self.SliderNoAction)
                self.setRepeatAction(self.SliderAction.SliderNoAction)
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        if self.pressed_control != QtWidgets.QStyle.SC_SliderHandle:
            event.ignore()
            return

        event.accept()
        # new_pos = self.__pixelPosToRangeValue(self.__pick(event.pos()))
        new_pos = self.__pixelPosToRangeValue(self.__pick(event.position().toPoint()))
        opt = QtWidgets.QStyleOptionSlider()
        self.initStyleOption(opt)

        if self.active_slider < 0:
            offset = new_pos - self.click_offset
            self._high += offset
            self._low += offset
            if self._low < self.minimum():
                diff = self.minimum() - self._low
                self._low += diff
                self._high += diff
            if self._high > self.maximum():
                diff = self.maximum() - self._high
                self._low += diff
                self._high += diff
        elif self.active_slider == 0:
            if new_pos >= self._high:
                new_pos = self._high - 1
            self._low = new_pos
        else:
            if new_pos <= self._low:
                new_pos = self._low + 1
            self._high = new_pos

        self.click_offset = new_pos

        self.update()

        # self.emit(QtCore.SIGNAL('sliderMoved(int)'), new_pos)
        self.sliderMoved.emit(self._low, self._high)

    def __pick(self, pt):
        if self.orientation() == QtCore.Qt.Horizontal:
            return pt.x()
        else:
            return pt.y()

    def __pixelPosToRangeValue(self, pos):
        opt = QtWidgets.QStyleOptionSlider()
        self.initStyleOption(opt)
        style = QtWidgets.QApplication.style()

        # gr = style.subControlRect(style.CC_Slider, opt, style.SC_SliderGroove, self)
        gr = style.subControlRect(
            style.ComplexControl.CC_Slider, opt, style.SubControl.SC_SliderGroove, self
        )
        # sr = style.subControlRect(style.CC_Slider, opt, style.SC_SliderHandle, self)
        sr = style.subControlRect(
            style.ComplexControl.CC_Slider, opt, style.SubControl.SC_SliderHandle, self
        )

        if self.orientation() == QtCore.Qt.Horizontal:
            slider_length = sr.width()
            slider_min = gr.x()
            slider_max = gr.right() - slider_length + 1
        else:
            slider_length = sr.height()
            slider_min = gr.y()
            slider_max = gr.bottom() - slider_length + 1

        return style.sliderValueFromPosition(
            self.minimum(),
            self.maximum(),
            pos - slider_min,
            slider_max - slider_min,
            opt.upsideDown,
        )


if __name__ == "__main__":
    import sys

    def echo(low_value, high_value):
        print(low_value, high_value)

    app = QtWidgets.QApplication(sys.argv)
    slider = RangeSlider(QtCore.Qt.Horizontal)
    slider.setMinimumHeight(30)
    slider.setMinimum(0)
    slider.setMaximum(255)
    slider.setLow(15)
    slider.setHigh(35)
    slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
    slider.sliderMoved.connect(echo)
    # QtCore.QObject.connect(slider, QtCore.SIGNAL('sliderMoved(int)'), echo)
    slider.show()
    slider.raise_()
    app.exec()
