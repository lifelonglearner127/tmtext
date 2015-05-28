# -*- coding: utf-8 -*-
#
# See http://bugzilla.contentanalyticsinc.com/show_bug.cgi?id=285
#

# list of departments and their categories
DEPARTMENTS_CATEGORIES = [
    u'Books', 
    u'Home & Kitchen', 
    u'Electronics', 
    u'Sports & Outdoors', 
    u'Cell Phones & Accessories', 
    u'Collectibles & Fine Art', 
    u'Industrial & Scientific', 
    u'Automotive', 
    u'Clothing & Accessories', 
    u'Tools & Home Improvement', 
    u'Jewelry', 
    u'Office Products', 
    u'CDs & Vinyl', 
    u'Health & Personal Care', 
    u'Kindle Store', 
    u'Toys & Games', 
    u'Patio, Lawn & Garden', 
    u'Arts, Crafts & Sewing', 
    u'Beauty', 
    u'Movies & TV', 
    u'Grocery & Gourmet Food', 
    u'Pet Supplies', 
    u'Shoes', 
    u'Baby', 
    u'Musical Instruments', 
    u'Watches', 
    u'Appliances', 
    u'Software', 
    u'Video Games', 
    u'Apps & Games', 
    u'Kindle Accessories', 
    u'Gift Cards', 
    u'Toutes nos boutiques', 
    u'Animalerie', 
    u'Applis & Jeux', 
    u'Auto et Moto', 
    u'Bagages', 
    u'Beauté et Parfum', 
    u'Bijoux', 
    u'Boutique chèques-cadeaux', 
    u'Boutique Kindle', 
    u'Bricolage', 
    u'Bébés & Puériculture', 
    u'Chaussures et Sacs', 
    u'Cuisine & Maison', 
    u'DVD & Blu-ray', 
    u'Fournitures de bureau', 
    u'Gros électroménager', 
    u'High-tech', 
    u'Informatique', 
    u'Instruments de musique & Sono', 
    u'Jardin', 
    u'Jeux et Jouets', 
    u'Jeux vidéo', 
    u'Livres anglais et étrangers', 
    u'Livres en français', 
    u'Logiciels', 
    u'Luminaires et Eclairage', 
    u'Montres', 
    u'Musique : CD & Vinyles', 
    u'Musique classique', 
    u'Santé et Soins du corps', 
    u'Sports et Loisirs', 
    u'Téléchargement de musique', 
    u'Vêtements et accessoires', 
    u'Amazon Cloud Drive', 
    u'Liseuses Kindle & ebooks', 
    u'Tablettes Fire', 
    u'App-Shop pour Android', 
    u'Jeux et Logiciels Digitaux', 
    u'Livres', 
    u'Musique, DVD et Blu-ray', 
    u'Jeux vidéo et Consoles', 
    u'High-Tech et Informatique', 
    u'Jouets, Enfants et Bébés', 
    u'Maison, Bricolage, Animalerie', 
    u'Beauté, Santé, Alimentation', 
    u'Vêtements et Chaussures', 
    u'Montres et Bijoux', 
    u'全部分类', 
    u'Kindle商店', 
    u'应用程序和游戏', 
    u'图书', 
    u'音乐', 
    u'游戏/娱乐', 
    u'音像', 
    u'软件', 
    u'教育音像', 
    u'手机/通讯', 
    u'摄影/摄像', 
    u'电子', 
    u'数码影音', 
    u'电脑/IT', 
    u'办公用品', 
    u'小家电', 
    u'大家电 u', 
    u'电视/音响 u', 
    u'家用', 
    u'家居', 
    u'厨具', 
    u'家居装修', 
    u'宠物用品', 
    u'食品', 
    u'酒', 
    u'美容化妆', 
    u'个护健康', 
    u'母婴用品', 
    u'玩具', 
    u'运动户外休闲', 
    u'服饰箱包', 
    u'鞋靴', 
    u'钟表', 
    u'珠宝首饰', 
    u'汽车用品', 
    u'乐器', 
    u'礼品卡', 
    u'电子书阅读器', 
    u'Kindle', 
    u'Kindle Paperwhite', 
    u'Kindle Voyage', 
    u'Kindle配件', 
    u'Kindle电子书', 
    u'排行榜', 
    u'今日特价书', 
    u'进口原版', 
    u'小说', 
    u'经济管理', 
    u'杂志', 
    u'文学', 
    u'免费书', 
    u'少儿', 
    u'社科人文', 
    u'免费阅读软件', 
    u'安卓版', 
    u'iPhone版', 
    u'iPad版', 
    u'PC版', 
    u'Mac版', 
    u'使用攻略', 
    u'管理内容和设备', 
    u'管理我的内容', 
    u'管理我的设备', 
    u'付款方式设置', 
    u'Kindle帮助', 
    u'常见问题', 
    u'帮助视频', 
    u'Fire平板电脑', 
    u'Fire HD 7', 
    u'Fire HDX', 
    u'Fire HDX 8.9', 
    u'Fire配件', 
    u'亚马逊应用商店', 
    u'游戏', 
    u'热销推荐', 
    u'全球精选', 
    u'Fire应用程序', 
    u'管理我的内容和设备', 
    u'中文图书', 
    u'教材教辅', 
    u'社科', 
    u'经管', 
    u'进口图书', 
    u'Children\'s Books', 
    u'Literature & Fiction', 
    u'进口港台图书', 
    u'人文社科', 
    u'考试', 
    u'外语学习', 
    u'教材', 
    u'教辅', 
    u'词典与工具书', 
    u'0-2岁', 
    u'3-6岁', 
    u'7-10岁', 
    u'11-14岁', 
    u'儿童绘本', 
    u'家庭教育', 
    u'文学艺术', 
    u'青春与动漫', 
    u'传记', 
    u'艺术', 
    u'历史', 
    u'国学古籍', 
    u'哲学与宗教', 
    u'法律', 
    u'心理学', 
    u'经济与金融', 
    u'管理', 
    u'投资理财', 
    u'励志与成功', 
    u'心灵读物', 
    u'人际交往', 
    u'职场', 
    u'成功学', 
    u'科技', 
    u'计算机与网络', 
    u'医学', 
    u'建筑', 
    u'科学与自然', 
    u'生活', 
    u'孕产育儿', 
    u'烹饪与美食', 
    u'健康与养生', 
    u'旅游与地图', 
    u'影视', 
    u'电影', 
    u'高清蓝光', 
    u'纪录片', 
    u'卡通动画', 
    u'儿童影视', 
    u'更多影视', 
    u'流行', 
    u'进口CD', 
    u'古典', 
    u'儿童音乐', 
    u'影音', 
    u'更多音乐', 
    u'电钢琴', 
    u'吉他', 
    u'口琴', 
    u'MIDI录音', 
    u'民族乐器', 
    u'乐器配件', 
    u'经管培训', 
    u'英语学习', 
    u'儿童歌谣', 
    u'更多音像', 
    u'角色扮演', 
    u'桌游', 
    u'游戏设备', 
    u'Xbox ONE', 
    u'操作系统', 
    u'学习软件', 
    u'杀毒软件', 
    u'更多软件', 
    u'手机通讯', 
    u'Apple iPhone', 
    u'三星', 
    u'诺基亚', 
    u'华为', 
    u'小米', 
    u'联想', 
    u'索尼', 
    u'中兴', 
    u'HTC', 
    u'魅族', 
    u'酷派', 
    u'所有手机', 
    u'智能生活馆', 
    u'智能家居', 
    u'智能健康', 
    u'智能配饰', 
    u'视听娱乐', 
    u'中控', 
    u'监控', 
    u'手机配件', 
    u'移动电源', 
    u'蓝牙/耳机', 
    u'存储卡', 
    u'保护壳', 
    u'手机音箱', 
    u'蓝牙配件', 
    u'摄影摄像', 
    u'便携相机', 
    u'单反相机', 
    u'单电/微单', 
    u'镜头', 
    u'数码摄像机', 
    u'拍立得', 
    u'运动相机及配件', 
    u'监控安防', 
    u'望远镜', 
    u'相机配件', 
    u'摄影器材箱包', 
    u'三脚架/云台', 
    u'滤镜', 
    u'自拍杆', 
    u'闪光灯', 
    u'电池', 
    u'BOSE', 
    u'Apple iPod', 
    u'MP3/MP4', 
    u'耳机/耳麦', 
    u'音箱', 
    u'高清播放器', 
    u'录音笔', 
    u'数码相框', 
    u'录音机', 
    u'智能数码', 
    u'可穿戴设备', 
    u'智能手表', 
    u'娱乐影像', 
    u'创意数码', 
    u'锅具/壶具', 
    u'刀剪具', 
    u'餐具', 
    u'厨用小工具', 
    u'厨房收纳', 
    u'保鲜盒', 
    u'水具', 
    u'保温杯', 
    u'茶具', 
    u'咖啡用品', 
    u'烘培用具', 
    u'烧烤用具', 
    u'酒具', 
    u'家纺', 
    u'床单件套', 
    u'被子', 
    u'被套被罩', 
    u'枕头', 
    u'枕套枕巾', 
    u'床褥', 
    u'抱枕靠垫', 
    u'毛巾浴巾', 
    u'毯子', 
    u'电热毯', 
    u'蚊帐', 
    u'凉席', 
    u'窗帘', 
    u'地毯', 
    u'家具', 
    u'置物架', 
    u'收纳柜', 
    u'鞋柜', 
    u'电脑桌', 
    u'电脑椅', 
    u'书柜书架', 
    u'衣柜', 
    u'床垫', 
    u'沙发', 
    u'电视柜', 
    u'餐桌', 
    u'椅凳', 
    u'床', 
    u'户外家具', 
    u'儿童家具', 
    u'生活日用', 
    u'收纳用品', 
    u'清洁用品', 
    u'浴室用品', 
    u'缝纫', 
    u'洗晒熨', 
    u'雨伞', 
    u'暖宝', 
    u'家居装饰', 
    u'布艺装饰', 
    u'装饰画', 
    u'照片墙/相框相册', 
    u'摆件', 
    u'花瓶/花艺', 
    u'净水', 
    u'工具', 
    u'灯具', 
    u'厨卫', 
    u'开关插座', 
    u'劳保安防', 
    u'口罩', 
    u'滤水壶', 
    u'五金', 
    u'花洒', 
    u'龙头', 
    u'水槽', 
    u'洁身器', 
    u'墙纸/涂料', 
    u'宠物商店', 
    u'狗用品', 
    u'猫用品', 
    u'小宠用品', 
    u'水族用品', 
    u'电脑整机', 
    u'笔记本', 
    u'超极本', 
    u'游戏本', 
    u'台式机', 
    u'平板电脑', 
    u'电脑品牌', 
    u'Apple', 
    u'华硕', 
    u'戴尔', 
    u'宏碁', 
    u'电脑外设', 
    u'鼠标键盘', 
    u'平板保护套', 
    u'电脑包', 
    u'摄像头', 
    u'插座', 
    u'耳机耳麦', 
    u'线缆', 
    u'UPS电源', 
    u'清洁维修', 
    u'存储产品', 
    u'固态硬盘', 
    u'移动硬盘', 
    u'U盘', 
    u'内置硬盘', 
    u'网络存储', 
    u'DIY电脑组件', 
    u'组装电脑', 
    u'CPU', 
    u'主板', 
    u'显卡', 
    u'显示器', 
    u'内存', 
    u'机箱', 
    u'电源', 
    u'网络用品', 
    u'路由器', 
    u'网卡', 
    u'4G/3G上网', 
    u'网络配件', 
    u'交换机', 
    u'监控器', 
    u'办公设备及耗材', 
    u'打印机', 
    u'多功能一体机', 
    u'投影机', 
    u'办公耗材', 
    u'电话机', 
    u'扫描仪', 
    u'传真机', 
    u'碎纸机', 
    u'验钞机', 
    u'数位板', 
    u'设备配件', 
    u'办公及学生用品', 
    u'笔类', 
    u'桌上用品', 
    u'文档管理', 
    u'文件装订', 
    u'教具文具', 
    u'电子辞典', 
    u'早教机', 
    u'点读机', 
    u'办公家具', 
    u'财务用品', 
    u'计算器', 
    u'电视/音响', 
    u'平板电视', 
    u'迷你音响', 
    u'影音播放器', 
    u'家庭影院', 
    u'功放', 
    u'洗衣机', 
    u'烘干机', 
    u'热水器', 
    u'烟灶套餐', 
    u'油烟机', 
    u'燃气灶', 
    u'冰箱', 
    u'冰柜', 
    u'酒柜', 
    u'空调', 
    u'消毒柜', 
    u'洗碗机', 
    u'厨房电器', 
    u'电饭煲', 
    u'电压力锅', 
    u'微波炉/光波炉', 
    u'豆浆机', 
    u'电磁炉', 
    u'搅拌/榨汁机', 
    u'面包机', 
    u'电水壶/瓶', 
    u'电烤箱', 
    u'酸奶机', 
    u'蒸/煮锅', 
    u'电饼铛/三明治机', 
    u'咖啡机', 
    u'冰激凌机', 
    u'豆芽机', 
    u'烧烤炉', 
    u'居家电器', 
    u'空气净化器', 
    u'吸尘器', 
    u'取暖器', 
    u'加湿器', 
    u'电风扇', 
    u'电熨斗', 
    u'挂烫机', 
    u'饮水机', 
    u'除湿机', 
    u'个护电器', 
    u'电动剃须刀', 
    u'电吹风', 
    u'电动牙刷', 
    u'电动理发器', 
    u'电动剃毛器/脱毛器', 
    u'耳鼻毛修剪器', 
    u'电子秤', 
    u'电动美容器', 
    u'美发器', 
    u'按摩器', 
    u'足浴盆', 
    u'高端化妆品店', 
    u'奢品护肤', 
    u'香水', 
    u'美发', 
    u'身体沐浴', 
    u'男士护理', 
    u'彩妆及工具', 
    u'面部护肤', 
    u'洁面', 
    u'化妆水', 
    u'精华', 
    u'面霜乳液', 
    u'面膜', 
    u'眼霜', 
    u'防晒', 
    u'套装', 
    u'时尚彩妆', 
    u'面部', 
    u'眼部', 
    u'唇部', 
    u'美甲', 
    u'化妆工具', 
    u'礼盒套装', 
    u'美发护发', 
    u'洗发水', 
    u'护发', 
    u'洗护套装', 
    u'染烫用品', 
    u'头发造型', 
    u'美发工具', 
    u'身体护理 u', 
    u'沐浴', 
    u'身体乳', 
    u'脱毛', 
    u'止汗香体', 
    u'手足护理', 
    u'精油香薰', 
    u'面部护理', 
    u'洗发护发', 
    u'剃须护理', 
    u'身体护理', 
    u'男士香水', 
    u'香水精油', 
    u'女士香水', 
    u'香膏', 
    u'眼睛护理', 
    u'隐形眼镜', 
    u'彩色隐形眼镜', 
    u'护理液', 
    u'太阳镜', 
    u'老花镜', 
    u'眼镜架', 
    u'日用清洁', 
    u'纸品', 
    u'牙刷/牙膏', 
    u'衣物清洁', 
    u'卫生巾', 
    u'家居清洁', 
    u'驱蚊杀虫', 
    u'保健用品', 
    u'按摩椅', 
    u'按摩器械 u', 
    u'保健护具', 
    u'进口食品', 
    u'牛奶', 
    u'咖啡', 
    u'糕点饼干', 
    u'零食', 
    u'意大利面', 
    u'方便食品', 
    u'橄榄油', 
    u'酒水', 
    u'白酒', 
    u'葡萄酒', 
    u'洋酒', 
    u'啤酒', 
    u'日韩酒', 
    u'海外酒庄直采', 
    u'牛奶饮料', 
    u'果蔬饮料', 
    u'饮用水', 
    u'即饮咖啡', 
    u'冲调', 
    u'茶', 
    u'麦片', 
    u'奶粉', 
    u'奶茶', 
    u'蜂蜜', 
    u'柚子茶', 
    u'芝麻糊', 
    u'休闲零食', 
    u'巧克力', 
    u'糖果', 
    u'红枣', 
    u'干果', 
    u'牛肉干', 
    u'蜜饯', 
    u'粮油', 
    u'食用油', 
    u'调味品', 
    u'杂粮', 
    u'干货', 
    u'保健食品', 
    u'维生素', 
    u'蛋白粉', 
    u'胶原蛋白', 
    u'美容养颜', 
    u'减肥瘦身', 
    u'增强免疫', 
    u'婴幼', 
    u'益智拼插', 
    u'动漫', 
    u'遥控', 
    u'模型', 
    u'拼图', 
    u'运动户外', 
    u'毛绒', 
    u'0-12个月', 
    u'1-3岁', 
    u'4-6岁', 
    u'7-12岁', 
    u'12岁以上', 
    u'婴儿尿裤', 
    u'NB/S', 
    u'M', 
    u'L', 
    u'XL', 
    u'XXL', 
    u'成长裤', 
    u'布尿裤', 
    u'1段', 
    u'2段', 
    u'3段', 
    u'4段', 
    u'孕产奶粉', 
    u'特殊配方奶粉', 
    u'营养辅食', 
    u'米粉汤粥', 
    u'饮品', 
    u'DHA', 
    u'钙铁锌', 
    u'清火开胃', 
    u'鱼油', 
    u'肉松', 
    u'喂养洗护', 
    u'奶瓶', 
    u'奶嘴', 
    u'洗浴', 
    u'护肤', 
    u'清洁', 
    u'吸奶器', 
    u'防溢乳垫', 
    u'童车', 
    u'汽车安全座椅', 
    u'婴儿推车', 
    u'自行车', 
    u'伞车', 
    u'寝具家具', 
    u'餐椅', 
    u'睡袋', 
    u'抱被', 
    u'枕头枕套', 
    u'隔尿垫', 
    u'摇椅', 
    u'婴幼服装', 
    u'内衣服饰', 
    u'帽子/围巾/手套', 
    u'服饰礼盒', 
    u'背包箱子', 
    u'妈妈用品', 
    u'孕妇装', 
    u'产后塑身', 
    u'内衣', 
    u'背带', 
    u'妈咪包', 
    u'孕妈洗护', 
    u'户外服装', 
    u'冲锋衣', 
    u'抓绒衣', 
    u'皮肤风衣', 
    u'冲锋裤', 
    u'长裤', 
    u'帽子', 
    u'户外装备', 
    u'钓鱼', 
    u'帐篷', 
    u'吊床/桌椅', 
    u'烧烤', 
    u'水壶', 
    u'背包', 
    u'户外鞋', 
    u'徒步鞋', 
    u'登山鞋', 
    u'越野跑鞋', 
    u'溯溪鞋', 
    u'户外凉鞋', 
    u'营地鞋', 
    u'折叠车', 
    u'山地车', 
    u'通勤车', 
    u'附配件', 
    u'骑行服', 
    u'头盔', 
    u'健身训练', 
    u'跑步机', 
    u'健身车', 
    u'腰腹训练器', 
    u'椭圆训练机', 
    u'哑铃', 
    u'瑜伽', 
    u'运动服装', 
    u'帽衫/卫衣', 
    u'风衣/夹克', 
    u'毛衣/针织衫', 
    u'T恤', 
    u'短裤', 
    u'运动鞋', 
    u'跑步鞋', 
    u'篮球鞋', 
    u'休闲运动鞋', 
    u'足球鞋', 
    u'羽毛球鞋', 
    u'体育用品', 
    u'足球', 
    u'游泳', 
    u'羽毛球', 
    u'篮球', 
    u'乒乓球', 
    u'网球', 
    u'高尔夫', 
    u'服装服饰', 
    u'女装', 
    u'男装', 
    u'童装', 
    u'潮服', 
    u'连衣裙', 
    u'女士呢大衣', 
    u'羽绒服', 
    u'夹克', 
    u'外套', 
    u'休闲裤', 
    u'衬衫', 
    u'牛仔裤', 
    u'围巾', 
    u'手套', 
    u'女鞋', 
    u'男鞋', 
    u'进口鞋', 
    u'童鞋', 
    u'专业运动鞋', 
    u'板鞋', 
    u'帆布鞋', 
    u'专业户外鞋', 
    u'高跟鞋', 
    u'单鞋', 
    u'平底鞋', 
    u'商务休闲鞋', 
    u'正装鞋', 
    u'凉鞋', 
    u'人字拖', 
    u'居家鞋', 
    u'皮具箱包', 
    u'女包', 
    u'男包', 
    u'拉杆箱', 
    u'双肩背包', 
    u'单肩/斜挎包', 
    u'钱包', 
    u'运动/户外包', 
    u'商务公文包', 
    u'皮带/皮具礼盒', 
    u'旅行箱包', 
    u'男表', 
    u'女表', 
    u'机械表', 
    u'情侣表', 
    u'儿童表', 
    u'石英表', 
    u'钟', 
    u'卡西欧', 
    u'天梭', 
    u'浪琴', 
    u'欧米茄', 
    u'斯沃琪', 
    u'精工', 
    u'汉米尔顿', 
    u'美度', 
    u'天王', 
    u'海鸥', 
    u'罗西尼', 
    u'依波', 
    u'颂拓', 
    u'郎坤', 
    u'飞亚达', 
    u'ZStyle亚马逊尚品馆', 
    u'黄金首饰', 
    u'银饰饰品', 
    u'铂金饰品', 
    u'钻石', 
    u'手链/手镯', 
    u'项链/吊坠', 
    u'耳饰', 
    u'男士饰品', 
    u'头饰', 
    u'流行饰品', 
    u'天然水晶', 
    u'天然玉石', 
    u'珍珠饰品', 
    u'戒指', 
    u'胸针', 
    u'碧玺', 
    u'原木', 
    u'进口首饰', 
    u'施华洛世奇', 
    u'车载电器', 
    u'GPS导航仪', 
    u'行车记录仪', 
    u'汽车影音', 
    u'车载充电器', 
    u'胎压检测', 
    u'车载空气净化器', 
    u'汽车装饰', 
    u'坐垫', 
    u'座套', 
    u'脚垫', 
    u'汽车香水', 
    u'挂件摆饰', 
    u'后备箱垫', 
    u'车载收纳用品', 
    u'防爆膜', 
    u'美容养护', 
    u'汽车油品', 
    u'洗车工具', 
    u'车蜡', 
    u'洗车液', 
    u'皮革养护', 
    u'轮胎养护', 
    u'汽车配件', 
    u'轮胎轮毂', 
    u'雨刷器', 
    u'车灯', 
    u'滤清器', 
    u'迎宾脚踏板', 
    u'防撞装饰条', 
    u'车顶架', 
    u'车衣/车罩', 
    u'挡泥板', 
    u'车牌框架', 
    u'后视镜', 
    u'自驾装备', 
    u'摩托车头盔', 
    u'骑行护具', 
    u'护目镜', 
    u'儿童安全座椅', 
    u'维修工具', 
    u'安全应急设备', 
    u'体感车',
]


def amazon_parse_department(cats):
    DEP_CAT_LOW = [x.lower() for x in DEPARTMENTS_CATEGORIES]
    for r in cats:
        cat = r.get('category')
        rank = r.get('rank')
        print('+'*50)
        print cat
        print('+'*50)
        # first, try to match the full category
        if cat in DEPARTMENTS_CATEGORIES or cat.lower() in DEP_CAT_LOW:
            return {cat: rank}
        cats = [_c.strip() for _c in cat.split('>')]
        if cats:
            if cats[0] in DEPARTMENTS_CATEGORIES \
                or cats[0].lower() in DEP_CAT_LOW:
                return {cats[0]: rank}
            if len(cats) > 1:
                if cats[1] in DEPARTMENTS_CATEGORIES \
                    or cats[1].lower() in DEP_CAT_LOW:
                    return {cats[1]: rank}
