import requests
from bs4 import BeautifulSoup
import os
import re

'''
url 및 헤더 정보
검색 필터링을 수월하게 해주신 흐냐냥님께 감사드립니다!! ㅜㅠ
'''
url = 'http://gall.dcinside.com/board/lists/?id=seungyeon&page='
search_para = '&s_type=search_name&s_keyword=%ED%9D%90%EB%83%90%EB%83%A5'
header = {'User-Agent': ''}

def get_post_info(page_num):
	post_info = list() # 글 정보를 ({},{}) 형태로 반환
	cnt = 0

	req = requests.get(url + str(page_num) + search_para, headers = header)
	html = req.text
	soup = BeautifulSoup(html, "html.parser")
	posts_title = soup.find_all(attrs={"class": "t_subject"})
	posts_author = soup.find_all(attrs={"class": "t_writer user_layer"})
	posts_date = soup.find_all(attrs={"class": "t_date"})

	for t in posts_title:
		post_info.append({'post_title': re.sub('\[.*?]', '', t.text).replace('\n', '')})

	for z in zip(posts_author, posts_date, posts_title):
		post_info[cnt]['author'], post_info[cnt]['date'], post_info[cnt]['link'] = z[0].text, z[1].text, z[2].a['href']
		cnt += 1


	return [i for i in post_info if i['author'] != '운영자']

def get_image_info(post_info):
	image_info = list() # get_post_info를 통해 받아온 글 링크 내 이미지 정보 추출 

	req = requests.get("http://gall.dcinside.com" + post_info['link'], headers=header)
	html = req.text
	soup = BeautifulSoup(html, "html.parser")
	images = soup.select('div.re_gall_box_3 > div > ul > li > a')

	for l in images:
		image_info.append({
			'img_link': l['href'],
			'img_name': l.text
			})
	return image_info

def download_image(date, image_info):
	url = image_info['img_link'].replace('download.php?', 'viewimage.php?') # 다운로드 링크를 보기 링크로 바꾼 후 파일에 쓴다
	req = requests.get(url, headers=header)
	d_name = date.replace('.', '_')
	'''
	날짜별로 이미지를 categorize한다.
	해당하는 날짜 디렉토리가 없을 경우 디렉토리 생성 후 파일 씀
	'''
	if os.path.exists(d_name):
		f = open(d_name + "/" + image_info['img_name'], 'wb')
		f.write(req.content)
		f.close()
	else:
		try:
			os.makedirs(d_name)
		except OSError:
			print("Error occured while creating directory '%s'" %d_name)
		f = open(d_name + "/" + image_info['img_name'], 'wb')
		f.write(req.content)
		f.close()
	return




i = 1

while(i <= 380):
	for post_info in get_post_info(i):
		for image_info in get_image_info(post_info):
			download_image(post_info['date'], image_info)
	i += 1