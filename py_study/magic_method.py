class Cat(object):
# __init__ 类创建自动执行
    def __init__(self, name, age):
        self.name = name
        self.age = age
        print("哈吉米被创建")
# __del__ 类销毁自动执行
    def __del__(self):
        print("哈吉米被销毁")
# __str__ 当类对象转换为字符串时,自动被调用,应返回什么结果
    def __str__(self) -> str:
        return f"我叫{self.name}, 今年{self.age}岁"
# __lt__ 当类对象使用<和它人比较时,自动被调用,other为被比较对象
    def __lt__(self, other):
        return self.age < other.name
# le <=, gl >, ge >=, eq ==, ne !=

