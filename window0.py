from ezgraphics import GraphicsWindow

# Create the window and access the canvas
win = GraphicsWindow()
canvas = win.canvas()

# Draw on the canvas
canvas.drawRect(5, 10, 20, 30)

# Wait for the user to close the window
win.wait()
