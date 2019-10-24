# 在 python3.6 体验新的 f-string

`f-string` 是 python3.6 新增的功能. 这里简要摘录一下 f-string 语法避免遗忘.

# 语法

f-string 的标准语法非常简单, 理解为待格式化字符串的 `{}` 将会被当作 python 代码求值即可.

```py
name = 'mohanson'
pi = 3.14

# 语法: 执行 python 代码
print(f'name: {name}')             # name: mohanson
print(f'name: {str.upper(name)}')  # name: MOHANSON
print(f'2 * pi = {2 * pi}')        # 2 * pi = 6.28
# 语法: 对齐
print(f'pi: {pi:0<10}')            # pi: 3.14000000
print(f'pi: {pi:0>10}')            # pi: 0000003.14
print(f'pi: {pi:0^10}')            # pi: 0003.14000
# 语法: 固定浮点数位数
print(f'pi: {pi:.1f}')             # pi: 3.1
# 语法: !r, !s, !a 替代 repr(), str(), ascii()
print(f'name: {name!r}')           # name: 'mohanson'
```

# 参考

- [1] Eric V.Smith: PEP 498 -- Literal String Interpolation [https://www.python.org/dev/peps/pep-0498/](https://www.python.org/dev/peps/pep-0498/)
