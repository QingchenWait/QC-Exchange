# QC-Exchange | 青尘汇率

### 介绍

**轻量级汇率查询 & 展示小工具：常驻桌面，实时查阅。**

<img src="https://github.com/QingchenWait/QC-Exchange/blob/main/images/Guide_1_intro.png?raw=true" alt="1_intro.png" style="zoom: 40%;" />

- 使用中国银行官方数据，每 30 分钟自动刷新汇率牌价，支持自动/手动刷新；
- 支持简洁模式、窗口置顶，占用空间小，可长期放置在桌面，随时随地查询汇率；
- 展示当日汇率变动曲线，方便掌握实时变化。

（注：代码出于个人自用需求编写，因此仅展示澳大利亚元汇率。可以通过修改源代码，方便地进行币种切换；未来也会添加切换功能。）

### 1 软件架构
- 软件基于 ```bocfx``` 核心框架，使用 ```Python 3.12``` 开发。界面基于 ```PyQt 5```，项目 **完全开源** 。
- 目前尚无编译好的版本。用户可参考下面的教程进行部署，并使用 PyInstaller 等工具，自行编译为可执行 APP 。

### 2 使用教程
#### 2.1 部署方式
1. 在 PyCharm IDE 中创建项目：
   - 将代码库下载到本地，使用 PyCharm 新建项目，【路径】选择到 QC-Exchange 文件夹的前一级目录，【名称】填写 ```QC-Exchange``` ，如下图所示。
   - 初学者建议使用 PyCharm 的默认选项 （即自带的 Project venv 虚拟环境）进行部署。
2. 进入 PyCharm 后，点击左下侧的 “终端” 按钮，进入 venv 虚拟环境，开始安装运行环境：
   ```
   pip3 install bocfx
   pip3 install PyQt5
   ```
3. 运行 ```AUD2CNY_V107_main.py``` 文件，即可使用软件。

     <img src="https://github.com/QingchenWait/QC-Exchange/blob/main/images/Guide_2_pycharm.png?raw=true" alt="2_pycharm.png" style="zoom: 40%;" />

#### 2.2 文件树
- **/images** ：存放图片资源。
- **AUD2CNY_V107_main.py**：软件主程序。
- **AUD2CNY_MainWindow_V107.py**：PyQt GUI 控件定义及绘制源码，使用 PyUIC 生成。
- **AUD2CNY_MainWindow_V107.ui**：Qt 窗口样式文件，可使用 Qt Designer 打开及编辑。

### 3 开发说明
- 使用终端，额外安装 ```PyQt5-tools``` 包：
  ```
  pip install PyQt5-tools
  ```
- GUI 编辑工具：**PyQt5**

  - 安装 Qt Designer，随后在 对应的 PyCharm 工程中配置 External Tools：Qt Designer 、 PyUIC 与 PyRcc。

  - 可参照下列教程进行配置：

    [PyCharm 安装 PyQt5 及其工具（Qt Designer、PyUIC、PyRcc）详细教程](https://blog.csdn.net/qq_32892383/article/details/108867482)

  - 若不需要使用 Qt Designer 进行可视化开发，或不打算对界面 GUI 进行修改，可以不安装 pyqt5-tools 包，在配置 External Tools 的过程中也不需要配置 Qt Designer 与 PyUIC 项。
    
- 注意事项：
    1. 若希望修改外汇币种、查询时间段、其他形式的牌价等，可以参考 ```bocfx``` 的官方文档 （ https://github.com/bobleer/bocfx/tree/master ），对本仓库的代码进行修改。
    3. 本工具使用 PyQt 的 QThread 方式实现多线程，在二次开发时请注意各异步线程间的对应关系。
  
### 4 关于作者

软件作者：**青尘工作室**

官方网站：https://qingchen1995.gitee.io

本程序 GitHub 仓库地址：https://github.com/QingchenWait/QC-Exchange
  
