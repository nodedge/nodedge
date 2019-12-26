from nodedge.graphics_node import GraphicsNode


class GraphicsBlock(GraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width = 160
        self.height = 80
        self.edge_size = 5.
        self._padding = 8.
