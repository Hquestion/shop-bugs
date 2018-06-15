import xlrd
import requests

data = xlrd.open_workbook('data.xls')

order = 0
cate_id_map = {
    "农产": '1',
    "特色": '2',
    "生鲜": '3',
    "酒茶": "4"
}

for index, item in enumerate(data.sheet_names()):
    sheet = data.sheet_by_index(index)
    rows_count = sheet.nrows
    for j in range(1, rows_count):
        order += 1
        goods_meta = sheet.row_values(j)
        name = goods_meta[0]
        price = goods_meta[1]
        category_id = cate_id_map[goods_meta[2]]
        tag_name = [goods_meta[3]]
        spec = [price]
        location = goods_meta[4]
        content = goods_meta[5]
        poster = goods_meta[6]
        content = content.replace("src=\">", "src=\"")

        postData = {
            "poster": poster,
            "name": name,
            "category_id": category_id,
            "origin": location,
            "price": price,
            "tag_name": tag_name,
            "content": content
        }

        result = requests.post("http://admin.bagepanzi.com/platform/addFromImport", data=postData)
        print(result.text)





