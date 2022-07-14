from bs4 import BeautifulSoup
import re
import urllib.request,urllib.error
import xlwt
import sqlite3

def main():
    baseurl ="https://movie.douban.com/top250?start="
    #1.爬取网页
    datalist = getData(baseurl)
    # savepath =".\\豆瓣电影Top250.xls"
    dbpath = "movie.db"
    #3.保存数据
    # saveData(datalist,savepath)
    saveData2DB(datalist,dbpath)
    # askURL(baseurl)
#影片的详情链接
findLink = re.compile(r'<a href="(.*?)">') #创建正则表达式对象
#影片图片的链接
findImg = re.compile(r'<img alt=".*" class="" src="(.*?)".*/>',re.S)
#影片的片名
findTitle = re.compile(r'<span class="title">(.*)</span>')
#影片的评分
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
#影片的评价人数
findJudge = re.compile(r'<span>(\d*)人评价</span>')
#影片的概况
findInq = re.compile(r'<span class="inq">(.*)</span>')
#影片的相关内容
findBd = re.compile(r'<p class="">(.*?)</p>',re.S)

#1.爬取网页
def getData(baseurl):
    datalist = []
    for i in range(0,10): #调用获取页面信息的函数10次
        url = baseurl + str(i*25)
        html = askURL(url)  #保存获取到的网页源码
    #2.逐一解析数据
        soup = BeautifulSoup(html,"html.parser")
        for item in soup.find_all('div',class_="item"): #查找符合要求的字符串，形成列表
            data = []   #保存一部电影的所有信息
            item = str(item)
            #影片的详情链接
            link = re.findall(findLink,item)[0] #re库通过正则表达式来查找指定的字符串
            data.append(link)

            img = re.findall(findImg,item)[0]
            data.append(img)

            title = re.findall(findTitle,item)
            if len(title) == 2:
                ctitle = title[0]
                data.append(ctitle)
                otitle = title[1].replace("/","")
                data.append(otitle)
            else:
                data.append(title[0])
                data.append(" ")        #留空

            rating = re.findall(findRating,item)[0]
            data.append(rating)

            judge = re.findall(findJudge,item)[0]
            data.append(judge)

            inq = re.findall(findInq,item)
            if len(inq) != 0:
                inq = inq[0].replace("。"," ")
                data.append(inq)
            else:
                data.append(" ")

            bd = re.findall(findBd,item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)?'," ",bd)
            bd = re.sub("/"," ",bd)

            data.append(bd.strip())
            datalist.append(data)

    return datalist

#得到指定一个URL的网页内容
def askURL(url):
    head = {    #模拟浏览器的头部信息
        "User-Agent":"Mozilla/5.0(WindowsNT10.0Win64;x64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/101.0.4951.54Safari/537.36Edg/101.0.1210.39"}
    #用户代理，表示告诉豆瓣服务器，我们是什么类型的机器
    request = urllib.request.Request(url,headers=head)
    html = ""
    try:
        response =urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e,"code.html"):
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)
    return html

#3.保存数据
def saveData(datalist,savepath):
    print("saving....")
    book = xlwt.Workbook(encoding="utf-8",style_compression=0)
    sheet = book.add_sheet("豆瓣电影top250",cell_overwrite_ok=True)
    col = ("电影详情链接","图片链接","影片中文名","影片外文名","影片评分","影片评价人数","影片概况","影片相关内容")
    for i in range(0,8):
        sheet.write(0,i,col[i])
    for i in range(0,250):
        print("第%d条"%(i+1))
        data = datalist[i]
        for j in range(0,8):
            sheet.write(i+1,j,data[j])
    book.save(savepath)

def saveData2DB(datalist,dbpath):
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    for data in datalist:
        for index in range(len(data)):
            if index ==4 or index == 5:
                continue
            else:
                data[index]='"'+data[index]+'"'
        sql = '''
            insert into movie250(
             info_link,pic_link,cname,ename,score,rated,introduction,info)
            values(%s)''' % ",".join(data)
        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close()

def init_db(dbpath):
    sql = '''
        create table movie250
        (id integer primary key autoincrement,
        info_link text,
        pic_link text,
        cname varchar,
        ename varchar,
        score numeric,
        rated numeric,
        introduction text,
        info text);
    '''        #创建数据表
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()