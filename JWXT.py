import urllib.request
from PIL import Image
import pytesseract
from http import cookiejar
import re
import getpass


def MakeHeader():
    cookie = cookiejar.CookieJar()
    handler = urllib.request.HTTPCookieProcessor(cookie)
    opener = urllib.request.build_opener(handler)
    opener.open('http://jwxt.bupt.edu.cn/validateCodeAction.do?random=')
    CookieVal = ''
    for item in cookie:
        CookieVal += str(item.name)
        CookieVal += '='
        CookieVal += str(item.value)
    header = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        'Host': 'jwxt.bupt.edu.cn',
        'Origin': 'http://jwxt.bupt.edu.cn',
        'Referer': 'http://jwxt.bupt.edu.cn/logout.do',
        'Cookie': ''
    }
    header['Cookie'] = CookieVal
    return header

def GetValNum(header):
    req = urllib.request.Request('http://jwxt.bupt.edu.cn/validateCodeAction.do?random=', headers=header)
    response = urllib.request.urlopen(req)
    Val_img = response.read()
    with open('Valimag.jpg', 'wb') as f:
        f.write(Val_img)
    ValNum = pytesseract.image_to_string(Image.open('Valimag.jpg'))
    return ValNum

def Login(ValNum,header):
    global StudentId
    global PassWord
    if len(StudentId)+len(PassWord) == 0:
        StudentId = input('请输入您的学号：')
        PassWord = getpass.getpass('请输入您的教务系统密码：')
    data = {
        'type': 'sso',
        'zjh': '',
        'mm': '',
        'v_yzm': '',
    }
    data['v_yzm'] = ValNum
    data['zjh'] = StudentId
    data['mm'] = PassWord
    url = 'http://jwxt.bupt.edu.cn/jwLoginAction.do'
    postData = urllib.parse.urlencode(data).encode('utf-8')
    req = urllib.request.Request(url, postData, headers=header)
    response = urllib.request.urlopen(req)
    return postData

def GetHtml(postData, header):
    url = 'http://jwxt.bupt.edu.cn/gradeLnAllAction.do?type=ln&oper=qbinfo&lnxndm=2016-2017%E5%AD%A6%E5%B9%B4%E7%AC%AC%E4%BA%8C%E5%AD%A6%E6%9C%9F(%E6%98%A5)(%E4%B8%89%E5%AD%A6%E6%9C%9F)#2016-2017%E5%AD%A6%E5%B9%B4%E7%AC%AC%E4%BA%8C%E5%AD%A6%E6%9C%9F(%E6%98%A5)(%E4%B8%89%E5%AD%A6%E6%9C%9F)'
    req = urllib.request.Request(url, postData, headers=header)
    response = urllib.request.urlopen(req)
    html = response.read().decode('gbk')
    html = html.replace('\r\n', '').replace('\t', '').replace(' ', '')
    return html

def GetScore(html):
    Pattern = re.compile('<tdalign="center">.{1,4}</td><tdalign="center">.修</td><tdalign="center"><palign="center">.*?&nbsp')
    Data = Pattern.findall(html)
    QuanHe = 0.0
    FenHe = 0.0
    for each in Data:
        Quan = each.split("</td>", 1)[0].split(">", 1)[1]
        Fen = each.split(">", 6)[6].split("&", 1)[0]
        QuanHe += float(Quan)
        try:
            FenHe += float(Fen) * float(Quan)
        except:
            QuanHe -= float(Quan)
            continue
        print("学分%s,分数%s" % (Quan, Fen))
    return FenHe, QuanHe

def HandleScore(FenHe, QuanHe):
    # print('本程序会计算必修课与专业选修课的加权成绩，如果有其他特例请进行分数修正')
    # FenHe_Sub = input('请输入分数修正量(不参与计算的课程分数×学分和)(不输入默认为0): ')
    # FenHe_Sub = float(FenHe_Sub if FenHe_Sub else 0)
    # QuanHe_Sub = input('请输入学分修正量(不参与计算的课程学分和)(不输入默认为0): ')
    # QuanHe_Sub = float(QuanHe_Sub if QuanHe_Sub else 0)
    FenHe_Sub = QuanHe_Sub = 0 # Modified
    AverageScore = (FenHe-FenHe_Sub)/(QuanHe-QuanHe_Sub)
    #print('您的均分是%s' % AverageScore)
    return AverageScore



def main(id,passwd):
    Fenhe = 0.0
    tryNum = 10
    global StudentId
    global PassWord
    StudentId = id
    PassWord = passwd
    while (not(Fenhe)):
        if (tryNum):
            header = MakeHeader()
            ValNum = GetValNum(header)
            postData = Login(ValNum, header)
            html = GetHtml(postData, header)
            Fenhe, Quanhe = GetScore(html)
            tryNum -= 1
        else:
            print('请检查密码是否有误')
            StudentId = ''
            PassWord = ''
            tryNum = 10
        AverageScore = HandleScore(Fenhe, Quanhe)
    Answer = '您的均分是%s' % AverageScore
    return (Answer)

if __name__ == '__main__':
    StudentId = ''
    PassWord = ''
    main()
