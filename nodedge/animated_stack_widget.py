from PySide6.QtCore import (
    QAbstractAnimation,
    QEasingCurve,
    QParallelAnimationGroup,
    QPoint,
    QPropertyAnimation,
    Qt,
    QTimeLine,
    Slot,
)
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QStackedWidget, QWidget


class AnimatedStackWidget(QStackedWidget):
    def __init__(self, parent=None):
        super(AnimatedStackWidget, self).__init__(parent)

        self.fadeTransition = False
        self.slideTransition = False
        self.transitionDirection = Qt.Vertical
        self.transitionTime = 500
        self.fadeTime = 500
        self.transitionEasingCurve = QEasingCurve.OutBack
        self.fadeEasingCurve = QEasingCurve.Linear
        self.currentWidget = 0
        self.nextWidget = 0
        self._currentWidgetPosition = QPoint(0, 0)
        self.widgetActive = False

    def setTransitionDirection(self, direction):
        self.transitionDirection = direction

    def setTransitionSpeed(self, speed):
        self.transitionTime = speed

    def setFadeSpeed(self, speed):
        self.fadeTime = speed

    def setTransitionEasingCurve(self, easingCurve: QEasingCurve):
        self.transitionEasingCurve = easingCurve

    def setFadeCurve(self, easingCurve):
        self.fadeEasingCurve = easingCurve

    def setFadeTransition(self, fadeState):
        if isinstance(fadeState, bool):
            self.fadeTransition = fadeState
        else:
            raise TypeError("setFadeTransition() only accepts boolean inputs.")

    def setSlideTransition(self, slideState):
        if isinstance(slideState, bool):
            self.slideTransition = slideState
        else:
            raise TypeError("setSlideTransition() only accepts boolean inputs.")

    @Slot()
    def slideToPreviousWidget(self):
        currentWidgetIndex = self.currentIndex()
        if currentWidgetIndex > 0:
            self.slideToWidgetIndex(currentWidgetIndex - 1)

    @Slot()
    def slideToNextWidget(self):
        currentWidgetIndex = self.currentIndex()
        if currentWidgetIndex < (self.count() - 1):
            self.slideToWidgetIndex(currentWidgetIndex + 1)

    def slideToWidgetIndex(self, index):
        if index > (self.count() - 1):
            index = index % self.count()
        elif index < 0:
            index = (index + self.count()) % self.count()
        if self.slideTransition:
            self.slideToWidget(self.widget(index))
        else:
            self.setCurrentIndex(index)

    def slideToWidget(self, newWidget):
        if self.widgetActive:
            return

        self.widgetActive = True

        _currentWidgetIndex = self.currentIndex()
        _nextWidgetIndex = self.indexOf(newWidget)

        if _currentWidgetIndex == _nextWidgetIndex:
            self.widgetActive = False
            return

        offsetX, offsetY = self.frameRect().width(), self.frameRect().height()
        self.widget(_nextWidgetIndex).setGeometry(self.frameRect())

        if not self.transitionDirection == Qt.Horizontal:
            if _currentWidgetIndex < _nextWidgetIndex:
                offsetX, offsetY = 0, -offsetY
            else:
                offsetX = 0
        else:
            if _currentWidgetIndex < _nextWidgetIndex:
                offsetX, offsetY = -offsetX, 0
            else:
                offsetY = 0

        nextWidgetPosition = self.widget(_nextWidgetIndex).pos()
        currentWidgetPosition = self.widget(_currentWidgetIndex).pos()
        self._currentWidgetPosition = currentWidgetPosition

        # Animate transition
        offset = QPoint(offsetX, offsetY)
        self.widget(_nextWidgetIndex).move(nextWidgetPosition - offset)
        self.widget(_nextWidgetIndex).show()
        self.widget(_nextWidgetIndex).raise_()

        anim_group = QParallelAnimationGroup(self, finished=self.animationDoneSlot)

        for index, start, end in zip(
            (_currentWidgetIndex, _nextWidgetIndex),
            (currentWidgetPosition, nextWidgetPosition - offset),
            (currentWidgetPosition + offset, nextWidgetPosition),
        ):
            animation = QPropertyAnimation(
                self.widget(index),
                b"pos",
                duration=self.transitionTime,
                easingCurve=self.transitionEasingCurve,
                startValue=start,
                endValue=end,
            )
            anim_group.addAnimation(animation)

        self.nextWidget = _nextWidgetIndex
        self.currentWidget = _currentWidgetIndex

        self.widgetActive = True
        anim_group.start(QAbstractAnimation.DeleteWhenStopped)

        if self.fadeTransition:
            FadeWidgetTransition(
                self, self.widget(_currentWidgetIndex), self.widget(_nextWidgetIndex)
            )

    @Slot()
    def animationDoneSlot(self):
        self.setCurrentIndex(self.nextWidget)
        self.widget(self.currentWidget).hide()
        self.widget(self.currentWidget).move(self._currentWidgetPosition)
        self.widgetActive = False

    @Slot()
    def setCurrentWidget(self, widget):
        currentIndex = self.currentIndex()
        nextIndex = self.indexOf(widget)
        if self.currentIndex() == self.indexOf(widget):
            return
        if self.slideTransition:
            self.slideToWidgetIndex(nextIndex)

        if self.fadeTransition:
            self.fader_widget = FadeWidgetTransition(
                self,
                self.widget(self.currentIndex()),
                self.widget(self.indexOf(widget)),
            )
            if not self.slideTransition:
                self.setCurrentIndex(nextIndex)

        if not self.slideTransition and not self.fadeTransition:
            self.setCurrentIndex(nextIndex)


class FadeWidgetTransition(QWidget):
    def __init__(self, animationSettings, oldWidget, newWidget):
        QWidget.__init__(self, newWidget)

        self.oldPixmap = QPixmap(newWidget.size())
        oldWidget.render(self.oldPixmap)
        self.pixmapOpacity = 1.0

        self.timeline = QTimeLine()
        self.timeline.valueChanged.connect(self.animate)
        self.timeline.finished.connect(self.close)
        self.timeline.setDuration(animationSettings.fadeTime)
        self.timeline.setEasingCurve(animationSettings.fadeEasingCurve)
        self.timeline.start()

        self.resize(newWidget.size())
        self.show()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setOpacity(self.pixmapOpacity)
        painter.drawPixmap(0, 0, self.oldPixmap)
        painter.end()

    def animate(self, value):
        self.pixmapOpacity = 1.0 - value
        self.repaint()
