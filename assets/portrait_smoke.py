"""Three-second ManimGX portrait smoke scene; copy into work/ before rendering."""
import manimgx as m

m.config.pixel_width, m.config.pixel_height = 1080, 1920
m.config.frame_rate = 30
m.config.background_color = m.BLACK


class MathvidSmoke(m.Scene):
    def construct(self) -> None:
        title = m.Text("Mathvid", font_size=48).move_to([0, 4.8, 0])
        equation = m.MathTex(r"x^2 + 2x + 1 = (x+1)^2", font_size=40)
        if equation.width > 6.4:
            equation.scale(6.4 / equation.width)
        box = m.Rectangle(width=6.8, height=1.4, color=m.YELLOW)
        self.play(m.Write(title), m.Write(equation), run_time=1)
        self.play(m.Create(box), run_time=0.5)
        self.wait(1.5)
