# Sign-WenShuShu
**自动签到文叔叔**
本程序使用selenium编写



# 使用教程

### 1.获取Push Plus Token
**首先打开[Push Plus](http://www.pushplus.plus/)点击登录，并使用微信扫描二维码**
**之后点击**一对一推送**获取自己的Token**

### 2.fork本项目
**在本页面点击**[**Fork按钮**](https://github.com/jiongjiongJOJO/Sign-WenShuShu/fork "Fork按钮")**，将本项目复制到自己仓库里。**

### 3.部署
**在fork后的github仓库的 `Settings` -->`Secrets and variables` -->`Actions` 中选择`New repository secret`添加"Secrets"，name(不用在意大小写)和value分别为：**

| key          | value                                                                          | 必填 |
|--------------|--------------------------------------------------------------------------------|----|
| USER         | 你的账号                                                                           | ✔️ |
| PASSWORD     | 你的密码                                                                           | ✔️ |
| PUSH_MESSAGE | 第一步获取到的Token                                                                   | ❌️ |
| SHOW_USER    | 0或1或2，表示是否显示账号，0: 完全不显示（默认），1：显示部分（例如：131\*\*\*\*1234，或aa\*\*\*\*\*\*@github.com），2：完全显示 | ❌️ |

### 4.运行脚本
**添加完上面的"Secrets"后，进入"Actions" -->"run main"，点击右边的"Run workflow"即可第一次启动**
首次fork可能要去actions(正上方的actions不是Settings里面的actions)里面同意使用actions条款，如果"Actions"里面没有"run main"，点一下右上角的"star"，"run main"就会出现在"Actions"里面
后面脚本就会每天自动执行一遍了，成功失败都会微信推送的。
