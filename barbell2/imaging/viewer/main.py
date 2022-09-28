"""
https://stackoverflow.com/questions/30488155/opengl-fastest-way-to-draw-2d-image
"""
import sys, pygame
pygame.init()

size = width, height = 320, 240
speed = [2, 2]
black = 0, 0, 0

screen = pygame.display.set_mode(size)

ball = pygame.image.load("intro_ball.gif")
ballrect = ball.get_rect()

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    ballrect = ballrect.move(speed)
    if ballrect.left < 0 or ballrect.right > width:
        speed[0] = -speed[0]
    if ballrect.top < 0 or ballrect.bottom > height:
        speed[1] = -speed[1]

    screen.fill(black)
    screen.blit(ball, ballrect)
    pygame.display.flip()

# import sys
#
# from PySide6.QtCore import Qt
# from PySide6.QtWidgets import QApplication, QLabel
#
#
# def main():
#     app = QApplication(sys.argv)
#     label = QLabel('Hello, world')
#     label.setAlignment(Qt.AlignCenter)
#     label.show()
#     sys.exit(app.exec())
#
#
# if __name__ == '__main__':
#     main()
# import numpy as np
# from OpenGL import GL
# from PySide6.QtOpenGLWidgets import QOpenGLWidget
# from PySide6.QtWidgets import QApplication
# from PySide6.QtCore import Qt
#
#
# class OpenGLWidget(QOpenGLWidget):
#
#     def initializeGL(self):
#         vertices = np.array([0.0, 1.0, -1.0, -1.0, 1.0, -1.0], dtype=np.float32)
#
#         bufferId = GL.glGenBuffers(1)
#         GL.glBindBuffer(GL.GL_ARRAY_BUFFER, bufferId)
#         GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL.GL_STATIC_DRAW)
#
#         GL.glEnableVertexAttribArray(0)
#         GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, GL.GL_FALSE, 0, None)
#
#     def paintGL(self):
#         GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)
#
#
# QApplication.setAttribute(Qt.AA_UseDesktopOpenGL)
# app = QApplication([])
# widget = OpenGLWidget()
# widget.show()
# app.exec()
