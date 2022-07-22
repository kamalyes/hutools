from hutools import captcha

captcha.CaptchaPainter(text="5266", im_x=300).normal.show()

# 字母数字混合型
x, y = captcha.Captcha().letter_digit()
print(x, y)
# 数字型
x, y = captcha.Captcha().digit()
print(x, y)
# 字母型
x, y = captcha.Captcha().letter()
print(x, y)
# 增强
x, y = captcha.Captcha(enhance=True).letter_digit()
print(x, y)
# 边缘凸显
x, y = captcha.Captcha(edge=True).letter_digit()
print(x, y)
# 浮雕效果
x, y = captcha.Captcha(emboss=True).letter_digit()
print(x, y)
# 轮廓
x, y = captcha.Captcha(contour=True).letter_digit()
print(x, y)
# gif动态图
x, y = captcha.Captcha(gif=True).letter_digit()
print(x, y)
