import requests
import json

def request_weather(location):
    # api地址
    url = 'http://t.weather.sojson.com/api/weather/city/'

    # # 输入城市中文
    # city = input("请输入你要查询的城市：")
    city = location

    # 读取json文件
    f = open('city.json', 'rb')

    # 使用json模块的load方法加载json数据，返回一个字典
    cities = json.load(f)

    # 通过城市的中文获取城市代码
    city = cities.get(city)

    # 网络请求，传入请求api+城市代码
    response = requests.get(url + city)

    # 将数据以json形式返回，这个d就是返回的json数据
    d = response.json()

    # # 当返回状态码为200，输出天气状况
    # if d['status'] == 200 :
    #     print("城市：", d["cityInfo"]["parent"], d["cityInfo"]["city"])
    #     print("时间：", d["time"], d["data"]["forecast"][0]["week"])
    #     print("温度：", d["data"]["forecast"][0]["high"], d["data"]["forecast"][0]["low"])
    #     print("天气：", d["data"]["forecast"][0]["type"])
    return d
