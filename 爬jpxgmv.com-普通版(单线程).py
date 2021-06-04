import requests
import parsel
import os
import time

#图片地址
# https://www.jpxgmn.cc/YouMi/  + upload。。。。

'''
need-
1:相册自建立
2：input相册网址智能下载
3：所有站都可：如优美etc
'''

#请求相册的第一页
def getFirstHtml(url, headers):
    response = requests.get(url, headers)
    response.encoding = response.apparent_encoding
    response = response.text
    return response


#获取相册总页数
def totalPageNum(response):
    html_data = parsel.Selector(response)   #return a selector object
    total_page_num_list = html_data.xpath('//article[@class="article-content"]/div[1]/ul/a/text()').extract()
    total_page_num = total_page_num_list[-2]   #获取倒数第二个值作为总页数，因为这个列表的倒数第一个是“下一页”
    return total_page_num

def getImg(total_page_num, url, img_source, headers):
    file_name = url.split('/')[-2] + "-" + url.split('/')[-1].split('.')[0]
    if not os.path.exists("jpxgmv.com\\" + file_name):
        os.mkdir("jpxgmv.com\\" + file_name)

    for num in range(int(total_page_num)):
        if num == 0:
            #根据图片地址规则发现，为1时是第二页，为0时，就是第一页，所以保持原地址
            next_img_page_url = url
        else:
            next_img_page_url = base_url + '/{}/'.format(img_source) + url.split("/")[-1].split(".")[0] + '_{}'.format(num) + '.html'

        response_1 = requests.get(next_img_page_url).text
        requests.packages.urllib3.disable_warnings()
        html_data_1 = parsel.Selector(response_1)
        img_url_list = html_data_1.xpath('//article[@class="article-content"]/p/img/@src').extract()
        #print(img_url_list)

        for img_url in img_url_list:
            new_img_url = base_url + img_url
            #verify = False 是为了关闭SSL认证（关于网址重定向的，as requests是基于http的，访问https会重定向）
            img_data = requests.get(new_img_url, headers=headers, verify=False).content
            #这是去除警告
            requests.packages.urllib3.disable_warnings()

            img_name = str(num + 1) + "-" + str(img_url_list.index(img_url) + 1) + '.jpg'

            with open('jpxgmv.com\\' + file_name +'\\'+ img_name, "wb") as f:
                print('正在保存图片：'+ img_name)
                f.write(img_data)




if __name__ == "__main__":
    url = input("请输入jpxgmv.com的目标相册网址: ")

    start_t = time.time()

    img_source = url.split('/')[-2]
    base_url = "https://www.jpxgmn.cc"
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 Edg/90.0.818.66'}

    response = getFirstHtml(url,headers)
    total_page_num = totalPageNum(response)
    getImg(total_page_num, url, img_source,headers)
    print("==============================DONE!!!!!!!")

    end_t = time.time()
    cost = end_t - start_t
    print("爬取用时：{} seconds".format(cost))

