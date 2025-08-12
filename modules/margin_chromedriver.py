import sys
import bs4
import traceback
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
 
 
# ドライバーのフルパス
CHROMEDRIVER = "chromedriver.exeのパス"
# 改ページ（最大）
PAGE_MAX = 2
# 遷移間隔（秒）
INTERVAL_TIME = 3
# 開始年・月・日
SY = 2020
SM = 1
SD = 1
# 終了年・月・日
EY = 2020
EM = 12
ED = 31
 
 
# ドライバー準備
def get_driver():
    # ヘッドレスモードでブラウザを起動
    options = Options()
    options.add_argument('--headless')
 
    # ブラウザーを起動
    driver = webdriver.Chrome(CHROMEDRIVER, options=options)
 
    return driver
 
 
# 対象ページのソース取得
def get_source_from_page(driver, page):
    try:
        # ターゲット
        driver.get(page)
        driver.implicitly_wait(10)  # 見つからないときは、10秒まで待つ
        page_source = driver.page_source
 
        return page_source
 
    except Exception as e:
 
        print("Exception\n" + traceback.format_exc())
 
        return None
 
 
# ソースからスクレイピングする
def get_data_from_source(src):
    # スクレイピングする
    soup = bs4.BeautifulSoup(src, features='lxml')
    # print(soup)
    try:
        info = []
        table = soup.find("table", class_="boardFin")
 
        if table:
            elems = table.find_all("tr")
 
            for elem in elems:
                td_tags = elem.find_all("td")
 
                if len(td_tags) > 0:
                    row_info = []
                    tmp_counter = 0
                    for td_tag in td_tags:
                        tmp_text = td_tag.text
 
                        if tmp_counter == 0:
                            # 年月日
                            tmp_text = tmp_text
                        else:
                            tmp_text = extract_num(tmp_text)
 
                        row_info.append(tmp_text)
                        tmp_counter = tmp_counter + 1
 
                    info.append(row_info)
 
        return info
 
    except Exception as e:
 
        print("Exception\n" + traceback.format_exc())
 
        return None
 
 
# 次のページへ遷移
def next_btn_click(driver):
    try:
        # 次へボタン
        elem_btn = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.LINK_TEXT, '次へ'))
        )
 
        # クリック処理
        actions = ActionChains(driver)
        actions.move_to_element(elem_btn)
        actions.click(elem_btn)
        actions.perform()
 
        # 間隔を設ける(秒単位）
        time.sleep(INTERVAL_TIME)
 
        return True
 
    except Exception as e:
 
        print("Exception\n" + traceback.format_exc())
 
        return False
 
 
# 数値だけ抽出
def extract_num(val):
    num = None
    if val:
        match = re.findall("\d+\.\d+", val)
        if len(match) > 0:
            num = match[0]
        else:
            num = re.sub("\\D", "", val)
 
    if not num:
        num = 0
 
    return num
 
 
if __name__ == "__main__":
 
    # 引数
    args = sys.argv
    # 銘柄コード
    code = "1301"
    if len(args) == 2:
        # 引数があれば、それを使う
        code = args[1]
 
    # 対象ページURL
    page = "https://info.finance.yahoo.co.jp/history/margin/?code=" + code
    page = page + "&amp;sy=" + str(SY) + "&amp;sm=" + str(SM) + "&amp;sd=" + str(SD)
    page = page + "&amp;ey=" + str(EY) + "&amp;em=" + str(EM) + "&amp;ed=" + str(ED)
 
 
    # ブラウザのdriver取得
    driver = get_driver()
 
    # ページのソース取得
    source = get_source_from_page(driver, page)
    result_flg = True
 
    # ページカウンター制御
    page_counter = 0
 
    while result_flg:
        page_counter = page_counter + 1
 
        # ソースからデータ抽出
        data = get_data_from_source(source)
 
        # データ保存
        print(data)
 
        # 改ページ処理を抜ける
        if page_counter == PAGE_MAX:
            break
 
        # 改ページ処理
        result_flg = next_btn_click(driver)
        source = driver.page_source
 
    # 閉じる
    driver.quit()