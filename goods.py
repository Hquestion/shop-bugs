import re
import requests
from bs4 import BeautifulSoup
import json
import xlwt
import MySQLdb

headers = {
        "Cookie": "NotwxOpenId_55936259=600a8063-27c5-4637-b5cc-6ea54aa645f3; NotwxWeimobOpenId=f155a619-e1e6-4937-b577-17593642d079; express.vshop.session=s%3AmIbn2wwvbhqPxb5GeNPhedUrZoAR7oUF.6OgnTQgJWtks7jc8KWXSzkpY4hZpc92shQZxuqG1mzI; rprm_gdtvid=; x_aid=55936259; __DAYU_PP=uun3uY22jF2Mu3E7UreAffffffffec53cf9e8028"
    }


def get_goods_detail(id):
    response = requests.get('https://55936259.m.weimob.com/vshop/Goods/GoodsDetail1/' + id)
    soup = BeautifulSoup(response.text, "html.parser")

    list = soup.select('#goods_det img')
    detail_img_list = []
    for img in list:
        try:
            src = img["src"]
            detail_img_list.append('<p><img src="' + src + '"/></p>')
        except:
            pass
    headerImg = soup.select('header .swiper-slide img')[0:1]
    header_img_srcs = []
    for img in headerImg:
        try:
            header_img_srcs.append(img["src"])
        except:
            pass
    name = soup.select('#label_title')[0].get_text().strip()

    price_res = requests.post('''https://55936259.m.weimob.com/vshop/55936259/Ajax/Goods/GoodsDetailAjax/GetGoodsDetailAjaxInfo?Id=1601811&IsSpec=false&ismemprice=false&limitSum=0&Buyed=0&PtId=&PtGoodsSetId=&ShopId=0&_=1528877124431''',
                              data={"GoodsId": id})

    price = price_res.json()["Data"]["SKU"]["lstProductJson"][0]["price"]
    return {
        "name": name,
        "price": price,
        "detail": "".join(detail_img_list),
        "poster": ";".join(header_img_srcs)
    }


def get_classify_data(classification):
    params = {
        "ClassifyId": classification["id"],
        "PageIndex": 0,
        "PageSize": 9999,
        "Search": "",
        "Sort": 10
    }
    goods = requests.post('http://55936259.m.weimob.com/vshop/55936259/api3/v/MGetGoodsByPage', data=params,
                          headers=headers)
    goods_item_list = goods.json()["data"]["GoodsPageList"]
    res_list = []
    for item in goods_item_list:
        result = get_goods_detail(str(item["Id"]))
        res_list.append(result)
    return {
        "classification": classification["title"],
        "list": res_list
    }


cate_list = ('生鲜', '滋补', '油米', '零食')
to_bug_cate = []

classifiction_res = requests.post('http://55936259.m.weimob.com/vshop/55936259/api3/v/GetMClassifyByAid', data={"ClassifyId":"368336"}, headers=headers)

classify_list = classifiction_res.json()['data']["Data"][1]['twoLevel']
for index, item in enumerate(classify_list):
    for cate in cate_list:
        if(item["title"].find(cate) >= 0):
            to_bug_cate.append(item)

book = xlwt.Workbook(encoding='utf-8',style_compression=0)
g_index = 0

db = MySQLdb.connect(host="127.0.0.1",port=3306,db="eight_plates",user="root", passwd="123456")
c = db.cursor()
c.execute('''
select count(*) from  shop_goods;
''')
print(c.fetchall())

for item in to_bug_cate:
    goods_list = get_classify_data(item)
    sheet = book.add_sheet(goods_list["classification"], cell_overwrite_ok=True)
    sheet.write(0,0, '名称')
    sheet.write(0, 1, '价格')
    sheet.write(0, 2, '详情')
    sheet.write(0, 3, '海报')
    for index, goods in enumerate(goods_list["list"]):
        sheet.write(index+1, 0, goods["name"])
        sheet.write(index + 1, 1, goods["price"])
        sheet.write(index + 1, 2, goods["detail"])
        sheet.write(index + 1, 3, goods["poster"])
        g_index += 1

book.save('D:/hxl/python/bugs/data.xls')
