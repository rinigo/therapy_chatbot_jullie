import datetime
import sys, traceback
from pytz import timezone
#エラーを吐くためのdef
def error_msg(*, text=""):
    now = datetime.datetime.now(timezone('Asia/Tokyo')).strftime("%Y-%m-%d %H:%M:%S")
    # エラーの情報をsysモジュールから取得
    info = sys.exc_info()
    # tbinfoにエラー詰まっているprintすりゃわかる。
    tbinfo = traceback.format_tb(info[2])
    error = now+"(Asia/Tokyo)"+"\n"+text+"\n"+str(info[0])+"\n"+str(info[1])+"\n\n"
    for tbi in tbinfo:
        error += str(tbi)
    #returnのリストにslackに送る用のerrorとエクセルにテスト結果載せる用で分けて返している。テスト用の場合slack送らなずにprintでもする
    return [error,[str(info[0])+str(info[1]),str(tbinfo[0])]]