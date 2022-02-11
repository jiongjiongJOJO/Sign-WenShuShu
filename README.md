# Sign-WenShuShu
**自动签到文叔叔
本程序使用selenium编写



# 使用教程

### 1.获取Push Plus Token
**首先打开[Push Plus](http://pushplus.hxtrip.com/)点击登录，并使用微信扫描二维码**
**之后点击**一对一推送**获取自己的Token**

### 2.fork本项目
**在本页面点击右上角的Fork按钮**![](http://ww1.sinaimg.cn/large/005W9YjGly1gnaeodm3sgj303a017a9t.jpg "Fork按钮")**，将本项目复制到自己仓库里。**

### 3.部署
**在fork后的github仓库的 “Settings” -->“Secrets” 中添加"Secrets"，name(不用在意大小写)和value分别为：**
```
PUSH_TOKEN
key
```
**这里的key就是自己再第一步获取到的Token**

### 4.运行脚本
**添加完上面的"Secrets"后，进入"Actions" -->"run main"，点击右边的"Run workflow"即可第一次启动**
首次fork可能要去actions(正上方的actions不是Settings里面的actions)里面同意使用actions条款，如果"Actions"里面没有"run main"，点一下右上角的"star"，"run main"就会出现在"Actions"里面
后面脚本就会每天自动执行一遍了，成功失败都会微信推送的。
