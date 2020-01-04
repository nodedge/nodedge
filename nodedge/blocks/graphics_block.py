from nodedge.graphics_node import GraphicsNode


class GraphicsBlock(GraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width = 160
        self.height = 80
        self.edgeRoundness = 10.
        self.edgePadding = 0.
        self.titleHorizontalPadding = 8.
        self.titleVerticalPadding = 10.
