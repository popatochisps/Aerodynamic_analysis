from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.core.text import LabelBase, DEFAULT_FONT
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import random
import pandas as pd
import glob
import datetime
from kivy.uix.popup import Popup


#表示するウィンドウのサイズと位置の指定
Window.size = (1200, 900)
Window.top = 100
Window.left = 100

#表示するグラフのメモリの向きを内向きに設定
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'

#フォントの指定（kivyのデフォルトフォントには日本語がないのでデフォルトフォントを変更する）
LabelBase.register(DEFAULT_FONT, "03SmartFontUI.ttf")

#揚力・抗力のグラフ
class GraphForce(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #空のグラフの生成
        self.fig, self.ax = plt.subplots()
        #初期設定
        self.lift = [0]
        self.drag = [0]
        self.AoA = [0]
        #揚力・抗力のグラフの生成
        self.line_lift = self.ax.plot(self.AoA, self.lift, marker="o")[0]
        self.line_drag = self.ax.plot(self.AoA, self.drag, marker="o")[0]
        self.ax.set_xlabel("AoA [deg]")
        self.ax.set_ylabel("Force [N]")
        self.ax.set_title("Lift and Drag", size=14)
        #凡例の設定
        self.ax.legend(['Lift', 'Drag'], loc='lower right')
        #ウィンドウへの表示
        self.add_widget(FigureCanvasKivyAgg(self.fig))
           
    def update(self):
        #データの更新
        self.line_lift.set_data(self.AoA, self.lift)
        self.line_drag.set_data(self.AoA, self.drag)
        #軸の再設定
        self.ax.relim()
        self.ax.autoscale_view()
        #グラフの更新・再描画
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

#揚力係数・抗力係数のグラフ
class GraphCoefficient(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #空のグラフの生成
        self.fig, self.ax = plt.subplots()
        #初期設定
        self.lift_coefficient = [0]
        self.drag_coefficient = [0]
        self.AoA = [0]
        #揚力係数・抗力係数のグラフの生成
        self.line_lift = self.ax.plot(self.AoA, self.lift_coefficient, marker="o")[0]
        self.line_drag = self.ax.plot(self.AoA, self.drag_coefficient, marker="o")[0]
        self.ax.set_xlabel("AoA [deg]")
        self.ax.set_ylabel("coefficient")
        self.ax.set_title("Lift and Drag coefficient", size=14)
        #凡例の設定
        self.ax.legend(['Lift Coefficient', 'Drag Coefficient'], loc='lower right')
        #ウィンドウへの表示
        self.add_widget(FigureCanvasKivyAgg(self.fig))

    def update(self):
        #データの更新
        self.line_lift.set_data(self.AoA, self.lift_coefficient)
        self.line_drag.set_data(self.AoA, self.drag_coefficient)
        #軸の再設定
        self.ax.relim()
        self.ax.autoscale_view()
        #グラフの更新・再描画
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

#揚抗比のグラフ
class GraphRatio(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #空のグラフの生成
        self.fig, self.ax = plt.subplots()
        #初期設定
        self.lift_to_drag = [0]
        self.AoA = [0]
        #揚力係数・抗力係数のグラフの生成
        self.line = self.ax.plot(self.AoA, self.lift_to_drag, marker="o")[0]
        self.ax.set_xlabel("AoA [deg]")
        self.ax.set_ylabel("ratio")
        self.ax.set_title("Lift-to-Drag ratio", size=14)
        #凡例の設定
        self.ax.legend(['Lift-to-Drag Ratio'], loc='lower right')
        #ウィンドウへの表示
        self.add_widget(FigureCanvasKivyAgg(self.fig))

    def update(self):
        #データの更新
        self.line.set_data(self.AoA, self.lift_to_drag)
        #軸の再設定
        self.ax.relim()
        self.ax.autoscale_view()
        #グラフの更新・再描画
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

#フォルダ選択用のポップアップ
class Load_Folder(Popup):
    def __init__(self, main, **kwargs):
        super().__init__(**kwargs)
        self.title='フォルダの選択'
        self.size_hint=(0.8, 0.8)
        self.auto_dismiss=False
        self.main = main

    #ポップアップの終了
    def close_reference(self):
        self.dismiss()

class Graphing_USLG25(BoxLayout):
    #Fx,Fyの計算
    def culc_Force(self, filepath):
        datas = []
        #これで読み込むファイルは名前順のためファイルの順番に注意
        files = sorted(glob.glob(filepath))
        for file in files:
            #csvの読み込み
            df = pd.read_csv(file, header=None, usecols=[0,1]).T.values.tolist()
            datas.append(df)
        #無風状態の計算
        offset_x = (sum(datas[0][0])/len(datas[0][0]) + sum(datas[len(datas)-1][0])/len(datas[len(datas)-1][0]))/2
        offset_y = (sum(datas[0][1])/len(datas[0][1]) + sum(datas[len(datas)-1][1])/len(datas[len(datas)-1][1]))/2
        Fx = []
        Fy = []
        for data in datas: 
            #最初と最後はoffsetなので飛ばしている
            if not (data == datas[0] or data == datas[len(datas)-1]):
                Fx.append(sum(data[0])/len(data[0])-offset_x)
                Fy.append(sum(data[1])/len(data[1])-offset_y)
        return Fx, Fy

    #グラフに出力するものの計算
    def culc_lift_drag(self):
        self.culc_reynolds()
        #本試験のファイル読み込み
        Force = self.culc_Force(self.ids.Force_folder_path.text + '/*.csv')
        #治具のみのファイル読み込み
        nowing = self.culc_Force(self.ids.nowing_folder_path.text + '/*.csv')
        #迎角の設定
        self.AoA_length = int((float(self.ids.AoA_end.text) - float(self.ids.AoA_start.text)) / float(self.ids.AoA_step.text)) + 1
        self.ids.graphforce.AoA = self.ids.graphcoefficient.AoA = self.ids.graphratio.AoA = [ float(self.ids.AoA_start.text) + float(self.ids.AoA_step.text) * i for i in range(self.AoA_length) ]

        #試験結果から治具のみの送風時の力を引く
        for i in range(len(Force[0])):
            Force[0][i] -= nowing[0][0]
            Force[1][i] -= nowing[1][0]

        #計算式はFx*sin(-α) + Fy*cos(α)
        self.ids.graphforce.lift = [ Force[0][i]*np.sin(np.radians(-1*self.ids.graphforce.AoA[i])) + Force[1][i]*np.cos(np.radians(self.ids.graphforce.AoA[i])) for i in range(len(self.ids.graphforce.AoA))]
        #計算式はFx*cos(-α) + Fy*sin(α)
        self.ids.graphforce.drag = [ Force[0][i]*np.cos(np.radians(-1*self.ids.graphforce.AoA[i])) + Force[1][i]*np.sin(np.radians(self.ids.graphforce.AoA[i])) for i in range(len(self.ids.graphforce.AoA))]

        #計算式はFL / (1/2 * ρ * U^2 * S)
        self.ids.graphcoefficient.lift_coefficient = [ self.ids.graphforce.lift[i] / (0.5 * self.density * (self.velocity**2) * (float(self.ids.wing_area.text) * 10 ** (-6))) for i in range(len(self.ids.graphcoefficient.AoA))]
        #計算式はFD / (1/2 * ρ * U^2 * S)
        self.ids.graphcoefficient.drag_coefficient = [ self.ids.graphforce.drag[i] / (0.5 * self.density * (self.velocity**2) * (float(self.ids.wing_area.text) * 10 ** (-6))) for i in range(len(self.ids.graphcoefficient.AoA))]

        self.ids.graphratio.lift_to_drag = [self.ids.graphforce.lift[i]/self.ids.graphforce.drag[i] for i in range(len(self.ids.graphratio.AoA))]
        #それぞれのグラフ更新
        self.ids.graphforce.update()
        self.ids.graphcoefficient.update()
        self.ids.graphratio.update()
        
    #レイノルズ数の計算
    def culc_reynolds(self):
        self.velocity = float(self.ids.velocity.text)
        self.pressure = float(self.ids.pressure.text) * 100
        self.temperature = float(self.ids.temperature.text) + 273
        self.length = float(self.ids.length.text) * (10 ** (-3))
        self.density = (self.pressure * 28.8)/(8.31432 * (10 ** 3) * self.temperature)
        self.viscosity = ((1.485 * (10 ** (-6))) * (self.temperature ** 1.5))/(self.temperature + 100)
        self.reynolds = (self.density * self.velocity * self.length) / self.viscosity
        self.ids.reynolds.text = str(self.reynolds)
        print(self.density)
    '''参考文献:U.S. Standard Atmosphere, 1976'''

    #フォルダ選択ポップアップの生成
    def reference(self, state):
        self.popup = Load_Folder(self)
        self.state = state
        self.popup.open()
    #選択したフォルダの読み込み
    def load(self):
        if self.state == 'nowing':
            self.ids.nowing_folder_path.text = self.popup.ids.file_chooser.path
        elif self.state == 'Force':
            self.ids.Force_folder_path.text = self.popup.ids.file_chooser.path

class Graphing_USLG25App( App ):
    def build( self ):
        return Graphing_USLG25()

if __name__ == "__main__":
    Graphing_USLG25App().run()
