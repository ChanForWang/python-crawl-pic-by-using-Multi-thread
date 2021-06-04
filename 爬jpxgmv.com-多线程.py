import requests
import parsel
import threading
import os
import time

#图片地址
# https://www.jpxgmn.cc/YouMi/  + upload。。。。

'''
need:
1:相册自建立
2：input相册网址智能下载
3：所有站都可：如优美etc
'''


# 设置最大线程锁 =>  等同于10个线程一起做，然后只有这10个线程的锁release了，
# 才会给下面另外10个线程获得锁。  如：下载30个任务，有10个线程， 前10个获得锁，只有等这10个下完了，第11到20才能获得锁，
# 其实就是规定只有10个线程在跑，其他的没有获得锁的线程，就被阻塞了

#然而如果不加这把锁，便代表有几个图片，就有几个线程在跑。

#if value=1, 其实就是单线程在跑，就和普通版一模一样。需要完全等待下载完成，锁释放，才轮到下一个。而value=10，有10把锁，这10个线程可以同时下载，不用非等下载完成。但第11个就要等待其中的某个线程完成下载，把锁释放，才能获取，从而工作
thread_lock = threading.BoundedSemaphore(value=81)


#请求相册的第一页
def getHtml(url, headers):
    response = requests.get(url, headers)
    response.encoding = response.apparent_encoding
    response = response.text
    return response



def getPagesDataList(url,headers,base_url,img_source):
    response = getHtml(url,headers)
    html_data = parsel.Selector(response)   #return a selector object
    total_page_num_list = html_data.xpath('//article[@class="article-content"]/div[1]/ul/a/text()').extract()
    total_page_num = total_page_num_list[-2]   #获取倒数第二个值作为总页数，因为这个列表的倒数第一个是“下一页”
    print("-----共有{}页".format(total_page_num))

    pages_data = []
    for num in range(int(total_page_num)):
        if num == 0:
            #根据图片地址规则发现，为1时是第二页，为0时，就是第一页，所以保持原地址
            next_img_page_url = url
        else:
            next_img_page_url = base_url + '/{}/'.format(img_source) + url.split("/")[-1].split(".")[0] + '_{}'.format(num) + '.html'
        print(next_img_page_url)

        res = getHtml(next_img_page_url,headers)
        requests.packages.urllib3.disable_warnings()
        pages_data.append(res)

    return pages_data


#获取所有页面的img_urls, 放入一个list
def getImgUrlsList(pages_data):
    img_urls = []
    for page in pages_data:
        html_data = parsel.Selector(page)
        img_url_list = html_data.xpath('//article[@class="article-content"]/p/img/@src').extract()
        img_urls.extend(img_url_list)
    print("------------------{} pics in total".format(len(img_urls)))
    return img_urls


def downloadImg(img_url,headers,num,base_url,file_name):
    if not os.path.exists("jpxgmv.com/" + file_name):
        os.mkdir("jpxgmv.com/" + file_name)

    path = "jpxgmv.com/" + file_name + "/" + str(num)+ ".jpg"
    new_img_url = base_url + img_url
    # verify = False 是为了关闭SSL认证（关于网址重定向的，as requests是基于http的，访问https会重定向）
    img_data = requests.get(new_img_url, headers=headers, verify=False).content
    # 这是去除警告
    requests.packages.urllib3.disable_warnings()

    with open(path,"wb") as f:
        f.write(img_data)
    # 下载完了，解锁
    thread_lock.release()


def main():
    url = input("请输入jpxgmv.comの相册-网址：")
    start_t = time.time()

    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37","referer":url}
    img_source = url.split('/')[-2]
    base_url = "https://www.jpxgmn.cc"
    file_name = url.split('/')[-2] + "-" + url.split('/')[-1].split('.')[0]

    pages_data = getPagesDataList(url,headers,base_url,img_source)
    img_urls = getImgUrlsList(pages_data)

    num = 0
    for img_url in img_urls:
        num += 1
        print('Downloading No.{} Pic'.format(num))

        #上锁
        thread_lock.acquire()
        t = threading.Thread(target=downloadImg, args=(img_url,headers,num,base_url,file_name))
        t.start()

    print("-------------------------------------DONE!!")
    end_t = time.time()
    cost = end_t - start_t
    print("爬取用时：{} seconds".format(cost))




main()

