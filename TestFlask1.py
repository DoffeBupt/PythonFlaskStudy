from flask import Flask
import JWXT

app = Flask(__name__)

# @ 装饰器下边那个称为wiew function
# @ 将响应结果输出到浏览器
@app.route('/<ID>/<Passwd>')
def hello(ID,Passwd):
    return (JWXT.main(ID,Passwd))

# return的东西可以写h1啥的


app.run(host='0.0.0.0', port=5000)
# debug = True 的话，那边刷新就可以看到最新的结果
# 称为调试模式