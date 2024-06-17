import os
import xml.etree.ElementTree as ET
from typing import List

from bs4 import BeautifulSoup


def getData_html(dir_path) -> List[str]:  # 整体结构封装
    class Tree:  # 树的逻辑结构
        def __init__(self, information: str) -> None:
            self.information: str = information
            self.sons: List[Tree] = []
            self.content: str = ""
            self.fa: str = ""

        def append(self, tree: 'Tree'):
            self.sons.append(tree)

    def extract_text_from_html(html_file):  # 根据html文件路径返回对应内容的字符串
        try:
            with open(html_file, 'r', encoding='utf-8') as file:
                html_content = file.read()
        except:
            with open(html_file, 'r', encoding='gbk') as file:
                html_content = file.read()
        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        text = ""
        for string in soup.stripped_strings:
            text += string + "\n"
        return text

    def buildtree(xmlnode, treenode, dir_name):  # 根据xml文件给出的结构建树
        for node in xmlnode.findall('node'):
            # path =dir_path+"\\" + dir_name + "\documents\\" + node.get('url')  #html文件的路径
            # print(dir_path," ",dir_name," ",node.get("url"))
            new_node = node.get("url").replace("\\", "/")
            path = os.path.join(dir_path, dir_name, "documents", new_node)
            # print(1,path)
            txt = extract_text_from_html(path)
            newnode = Tree(txt.splitlines()[0])
            txt = "".join(txt.split("\n")[2:])
            idx = txt.find("子主题：")
            if idx != -1:
                newnode.content = txt[:idx]
            else:
                newnode.content = txt
            treenode.append(newnode)
            newnode.fa = treenode.fa + '\n' + treenode.content
            buildtree(node, newnode, dir_name)

    def get_list(treeNode, node_list) -> List[str,]:  # 整合生成数据
        node_list.append(
            "前提信息：\n" + treeNode.fa.lstrip().rstrip("\n") + "\n 本节信息：\n" + treeNode.content.lstrip().rstrip(
                "\n"))
        for son in treeNode.sons:
            node_list = get_list(son, node_list)
        return node_list

    def getData(dir_path, dir_name) -> List[str]:  # 生成对应文件夹名字的List[str]
        path = os.path.join(dir_path, dir_name, "nodetree.xml")
        # print(2,path)
        xmltree = ET.parse(path)
        xmlroot = xmltree.getroot()
        noderoot = Tree(dir_name + "的根节点")
        buildtree(xmlroot, noderoot, dir_name)
        return get_list(noderoot, [])

    menu = ["director", "emsplus", "rcp", "umac"]
    ret = []
    for dir_name in menu:
        ret = ret + getData(dir_path, dir_name)
    return ret


def getData_html2(dir_path) -> List[str]:  # 整体结构封装
    class Tree:  # 树的逻辑结构
        def __init__(self, information: str) -> None:
            self.information: str = information
            self.sons: List[Tree] = []
            self.content: str = ""
            self.fa: str = ""

        def append(self, tree: 'Tree'):
            self.sons.append(tree)

    def extract_text_from_html(html_file):  # 根据html文件路径返回对应内容的字符串
        try:
            with open(html_file, 'r', encoding='utf-8') as file:
                html_content = file.read()
        except:
            with open(html_file, 'r', encoding='gbk') as file:
                html_content = file.read()
        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        text = ""
        for string in soup.stripped_strings:
            text += string + "\n"
        return text

    def buildtree(xmlnode, treenode, dir_name):  # 根据xml文件给出的结构建树
        for node in xmlnode.findall('node'):
            path = os.path.join(dir_path, dir_name, "documents", node.get('url').replace("\\", "/"))  # html文件的路径
            txt = extract_text_from_html(path)
            newnode = Tree(txt.splitlines()[0])
            txt = "".join(txt.split("\n")[2:])
            idx = txt.find("子主题：")
            if idx != -1:
                newnode.content = txt[:idx]
            else:
                newnode.content = txt
            treenode.append(newnode)
            newnode.fa = treenode.fa + '\n' + treenode.content
            buildtree(node, newnode, dir_name)

    def get_list(treeNode, node_list) -> List[str]:  # 整合生成数据
        # node_list.append( "前提信息：\n" + treeNode.fa.lstrip().rstrip("\n") + "\n 本节信息：\n" + treeNode.content.lstrip().rstrip("\n"))
        node_list.append(treeNode.content.lstrip().rstrip("\n"))
        for son in treeNode.sons:
            node_list = get_list(son, node_list)
        return node_list

    def getData(dir_name) -> List[str]:  # 生成对应文件夹名字的List[str]
        xmltree = ET.parse(os.path.join(dir_path, dir_name, "nodetree.xml"))
        xmlroot = xmltree.getroot()
        noderoot = Tree(dir_name + "的根节点")
        noderoot.content = dir_name + "的根节点"
        buildtree(xmlroot, noderoot, dir_name)
        return get_list(noderoot, [])

    menu = ["director", "emsplus", "rcp", "umac"]
    ret = []
    for dir_name in menu:
        ret = ret + getData(dir_name)
    return ret


# def getData_html(dir_path) -> List[str]:
#     """
#     从目录dir_path开始进行数据的解析，dir_path的结构为
#     -dir_path
#       | 
#       |-director
#       | ├── doctype.xml
#       | ├── documents
#       | │   ├── License申请操作指南
#       | │   ├── TCF部署TECS Director
#       | │   ├── log.html 缩略语
#       | │   ├── nodes 顶层目录
#       | ...
#       | ├── index
#       | ├── nodetree.xml 文档标题及所在路径
#       | └── package.xml
#       | ...
#       |-emsplus
#       | ...
#      最后返回的是List[str],一个包含若干个字符串的列表
#     @Param dir_path 数据的顶层目录，其子目录分别是director，emsplus，rcp，umac
#     @Return List[str] 每个str中应包含一个文件的所有内容，可以带上父节点的相应内容作为补充信息
#     """
#     pass


def getData_txt(dir_path) -> List[str]:
    """
    从目录dir_path开始进行数据的解析，dir_path的结构为
    -dir_path
      | 
      |-director
      | ├── log.txt 一些缩略语
      | ├── nodes 一些顶层的父节点
      | |—— ...  其他为一些底层的节点
      | ...
      |-emsplus
      | ...
    最后返回的是List[str],一个包含若干个字符串的列表
    @Param dir_path 数据的顶层目录，其子目录分别是director，emsplus，rcp，umac
    @Return List[str] 每个str中应包含一个文件的所有内容，可以带上父节点的相应内容作为补充信息
    """
    txt_strings = []
    # 递归遍历目录
    for root, _, files in os.walk(dir_path):
        for file_name in files:
            if file_name.endswith(".txt"):
                file_path = os.path.join(root, file_name)
                with open(file_path, 'r', encoding='utf-8') as file:
                    txt_content = file.read()
                    # print(txt_content)
                    txt_strings.append(txt_content)

    return txt_strings


# 根据log.html生成字典
def get_abbreviation_dict(dir_path):
    abbreviation_dict = {}

    def extract_text_from_html(html_file):  # 根据html文件路径返回对应内容的字符串
        try:
            with open(html_file, 'r', encoding='utf-8') as file:
                html_content = file.read()
        except:
            with open(html_file, 'r', encoding='gbk') as file:
                html_content = file.read()
        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        soup = soup.find_all("aside")
        for itm in soup:
            s = itm.find(class_="title termabbr")  # 缩写
            l = itm.find_all(class_="abstract title termfull")  # 全称
            abbreviation_dict[s.text] = []
            for ll in l:
                abbreviation_dict[s.text].append(ll.text)

    menu = ["director", "emsplus", "rcp", "umac"]
    for dir_name in menu:
        extract_text_from_html(os.path.join(dir_path, dir_name, "documents", "log.html"))
    abbreviation_dict = sorted(abbreviation_dict.items())
    return abbreviation_dict


def transforme(question: str) -> str:
    def dfs(lst, idx, rec, ans):  # dfs搜索所有合理的情况
        if idx == len(question):
            i = 0
            str = ""
            while i < len(question):
                if lst[i] == -1:
                    str = str + question[i]
                    i += 1
                else:
                    str += dict[rec[i]][1][lst[i]] + "(" + dict[rec[i]][0] + ")"
                    i += len(dict[rec[i]][0])
            if ans == "":
                ans = str
            else:
                ans = ans + "<!>" + str
            return ans
        if len(lst) <= idx:
            lst.append(-1)
        if rec[idx] == -1:
            ans = dfs(lst, idx + 1, rec, ans)
        else:
            i = 0
            while i < len(dict[rec[idx]][1]):
                lst[idx] = i
                ans = dfs(lst, idx + 1, rec, ans)
                i += 1
        return ans

    def get_rec(question, dict):  # 记录缩略语关键词位置
        i = 0
        rec = [-1] * len(question)
        while i < len(dict):
            j = question.find(dict[i][0])
            if j == -1:
                i += 1
                continue
            while j != -1:
                rec[j] = i
                if j + 1 < len(question):
                    j = question.find(dict[i][0], j + 1)
                else:
                    j = -1
            i += 1
        i = 0
        while i < len(question):
            if rec[i] != -1:
                j = i + len(dict[rec[i]][0])
                i += 1
                while i < len(question) and i < j:
                    rec[i] = -1
                    i += 1
            else:
                i += 1
        return rec

    dict = [('1xCSFB', ['1x Circuit Switched Fallback1x电路交换回落']),
            ('1xRTT', ['1x Radio Transmission Technology1x无线传输技术']),
            ('2G', ['The 2nd Generation Mobile Communications第二代移动通信']),
            ('3G', ['The 3rd Generation Mobile Communications第三代移动通信']),
            ('3GPP', ['3rd Generation Partnership Project第三代合作伙伴计划']),
            ('3GPP2', ['3rd Generation Partnership Project 23G协作组2']),
            ('4A', ['Account, Authorization, Authentication, Audit认证、账号、授权、审计']),
            ('5G-GUTI', ['5G Globally Unique Temporary Identity5G全球唯一临时标识']),
            ('5GC', ['5G Core Network5G核心网']), ('5GS', ['5G System5G系统']), ('5QI', ['5G QoS Indicator5G QoS指示']),
            ('A-SMF', ['Anchor-SMF锚点SMF']), ('AAA', ['Answer-Auth-Answer应答鉴权响应']),
            ('AAR', ['Answer-Auth-Request应答鉴权请求']), ('ACK', ['Acknowledgement应答']),
            ('ACL', ['Access Control List访问控制列表']), ('ACR', ['Accounting Request计费请求']),
            ('AD', ['Active Directory活动目录']), ('ADC', ['Application Detection and Control应用检测控制']),
            ('ADD', ['Automatic Device Detection自动设备检测']),
            ('ADMC', ['Auto Detected Manually Cleared自动产生人工清除']),
            ('AES', ['Advanced Encryption Standard高级加密标准']),
            ('AF', ['Application Function应用功能', 'Assured Forwarding确保转发']),
            ('AI', ['Artificial Intelligence人工智能']), ('AIA', ['Authentication-Information-Answer鉴权信息检索响应']),
            ('AIC', ['Automatic Integration Center自动化集成中心']),
            ('AIR', ['Authentication-Information-Request鉴权信息检索请求']),
            ('AKA', ['Authentication and Key Agreement鉴权和密钥协商']),
            ('AM', ['Access and Mobility Management接入移动管理']),
            ('AMBR', ['Aggregate Maximum Bit Rate聚合最大比特率']), ('AMF', [
            'Access and Mobility Management Function接入和移动管理功能', 'Authentication Management Field鉴权管理域']),
            ('AMQP', ['Advanced Message Queuing Protocol高级消息队列协议']),
            ('AMU', ['Arbitration Management Unit仲裁管理单元']), ('AN', ['Access Network接入网']),
            ('ANDSP', ['Access Network Discovery & Selection Policy接入网发现和选择策略']),
            ('ANM', ['Answer\nMessage应答消息']),
            ('API', ['Application Programming Interface应用编程接口', 'Application Program Interface应用程序接口']),
            ('APN', ['Access Point Name接入点名称', 'Access Point Network接入点网络']), ('APP', ['Application应用']),
            ('APR', ['Automatic Power Reduction自动功率减小']), ('AR', ['Augmented Reality增强现实']),
            ('ARD', ['Access Restriction Data\t接入限制数据']),
            ('ARP', ['Allocation and Retention Priority分配保持优先级', 'Address Resolution Protocol地址解析协议']),
            ('ARPU', ['Average Revenue Per User每用户平均收入']),
            ('AS', ['Access Stratum接入层', 'Application Server应用服务器']),
            ('ASA', ['Abort-Session-Answer中断会话响应']), ('ASN.1', ['Abstract Syntax Notation One抽象语法编码1']),
            ('ASP', ['Application Server Process应用服务器进程']), ('ASR', ['Abort-Session-Request中断会话请求']),
            ('ATCA', ['Advanced Telecommunications Computing Architecture先进的电信计算架构']),
            ('ATCF', ['Access Transfer Control Function接入转换控制功能']),
            ('ATGW', ['Access Transfer Gateway接入转换网关']),
            ('AUSF', ['Authentication Server Function鉴权服务器功能']), ('AUTN', ['Authentication Token鉴权令牌']),
            ('AVP', ['Attribute Value Pair属性值对']), ('AZ', ['Availability Zone可用性区域']),
            ('B/S', ['Browser/Server浏览器和服务器结构']), ('BAR', ['Buffer Action Rule报文缓存规则']),
            ('BBERF', ['Bearer Binding and Event Reporting Function承载绑定和事件上报功能']),
            ('BCM', ['Basic Call Manager基本呼叫管理器']), ('BDR', ['Backup Designate Router备用指定路由器']),
            ('BE', ['Back End后端/后台', 'Best Effort尽力而为']),
            ('BFD', ['Bidirectional Forwarding Detection双向转发检测']), ('BG', ['Border Gateways边界网关']),
            ('BGCF', ['Breakout\nGateway Control Function出口网关控制功能']),
            ('BGP', ['Border Gateway Protocol边界网关协议']), ('BIOS', ['Basic Input/Output System基本输入/输出系统']),
            ('BM-SC', ['Broadcast Multimedia–Service Center广播多媒体业务中心']),
            ('BMC', ['Baseboard Management Controller主板管理控制器']),
            ('BOSS', ['Business and Operation Support System运营和运维支撑系统']),
            ('BS', ['Base Station基站', 'Billing System计费系统']), ('BSC', ['Base Station Controller基站控制器']),
            ('BSF', ['Binding Support Function绑定支持功能']), ('BSID', ['Base station identifier基站识别号']),
            ('BSR', ['Bootstrap Router自举路由器']), ('BSS', ['Business Support System业务支撑系统',
                                                              'Base Station System基站系统',
                                                              'Base Station Subsystem基站子系统']), ('BSSGP', [
            'Base\nStation Subsystem GPRS Protocol基站子系统GPRS协议',
            'Base Station System GPRS ProtocolGPRS基站子系统协议']), ('BTS', ['Base Transceiver Station基站收发信机']),
            ('BVCI', ['BSSGP\nVirtual Connection IdentifierBSSGP虚连接标识符']),
            ('C-SGN', ['CIoT Serving Gateway Node蜂窝物联网服务网关节点']), ('C/S', ['Client/Server客户端/服务器模式']),
            ('CA', ['Carrier Aggregation载波聚合']), ('CAC', ['Connection Admission Control连接允许控制']),
            ('CAG', ['Closed Access Group闭合接入组']),
            ('CAMEL', ['Customized Applications for Mobile Network Enhanced Logic移动网络增强逻辑的客户化应用']),
            ('CAPEX', ['Capital Expenditure资本性支出']), ('CBC', ['Cell broadcast center小区广播短消息中心']),
            ('CC', ['Control Center控制中心', 'Connection Confirmation连接确认']),
            ('CCA', ['Credit Control Answer信用控制应答']),
            ('CCA-I', ['Credit Control Answer-Initial初始信用控制应答']),
            ('CCA-T', ['Credit Control Answer-Terminate终止信用控制应答']),
            ('CCA-U', ['Credit Control Answer-Update更新信用控制应答']),
            ('CCC', ['China Compulsory Certificate中国强制性产品认证制度', 'CDB Control CenterCDB控制中心']),
            ('CCR', ['Credit Control Request信用控制请求']),
            ('CCR-I', ['Credit Control Request-Initial初始信用控制请求']),
            ('CCR-T', ['Credit Control Request-Terminate终止信用控制请求']),
            ('CCR-U', ['Credit Control Request-Update更新信用控制请求']),
            ('CDB', ['Cloud Database云数据库', 'Context Database内容上下文数据库']),
            ('CDMA', ['Code Division Multiple Access码分多址']),
            ('CDN', ['Context Data Node上下文数据节点', 'CDB Data NodeCDB数据节点']),
            ('CDR', ['Charging Data Record计费数据记录', 'Call Detail Record呼叫详细记录，即话单']),
            ('CDU', ['Cloud Database Unit云数据库单元', 'Cooling Distribution Unit冷量分配单元']),
            ('CE', ['CONFORMITE EUROPENDE欧洲合格认证的简称', 'Carrier Ethernet电信级（运营级）以太网']),
            ('CEA', ['Capabilities Exchange Answer能力交换响应']),
            ('CER', ['Capabilities Exchange Request能力交换请求']), ('CG', ['Charging Gateway计费网关']),
            ('CGF', ['Charging\nGateway Function 计费网关功能']), ('CGI', ['Cell Global Identification小区全球识别码']),
            ('CGNAT', ['Carrier Grade Network Address Translation运营商级网络地址转换']),
            ('CGSL', ['Carrier Grade Server Linux电信级服务器Linux']), ('CGW', ['CDB GatewayCDB接入网关']),
            ('CHAP', ['Challenge Handshake Authentication Protocol挑战握手认证协议']),
            ('CHF', ['Charging Function计费功能']), ('CHR', ['Call History Record呼叫历史记录']),
            ('CI', ['Cell Identity小区标识号']), ('CIDR', ['Classless Inter-Domain Routing无类别域间路由']),
            ('CIM', ['Container Infrastructure Manager容器基础设施管理器']),
            ('CIoT', ['Cellular Internet of Things蜂窝物联网']), ('CM', ['Configuration Management配置管理']),
            ('CMCC', ['China Mobile Communications Corporation中国移动通信集团公司']),
            ('CMF', ['Charging Management Function计费管理功能']), ('CMM', ['Chassis Management Module机框管理模块']),
            ('CMP', ['Calling Main Processor主呼叫处理模块', 'Control Maintenance Processor控制维护处理机']),
            ('CMPP', ['China Mobile Peer to Peer中国移动点对点协议']), ('CN', ['Core Network核心网']),
            ('CNF', ['CloudNative Network Function云原生网络功能']),
            ('CNGP', ['China Netcom Short Message Gateway Protocol中国网通短消息网关协议']),
            ('COTS', ['Commercial Off The Shelf商用货架产品']), ('CP',
                                                                 ['Control Plane控制平面', 'Connection Point连接点',
                                                                  'Content Provider内容提供商',
                                                                  'Communication Pattern通信模式']),
            ('CPE', ['Customer Premises Equipment用户驻地设备']), ('CPU', ['Central Processing Unit中央处理器']),
            ('CR', ['Connection Request接续请求']), ('CRC', ['Cyclic Redundancy Check循环冗余校验']),
            ('CREF', ['Connection Refused连接拒绝']), ('CRTP', ['Compressing IP/UDP/RTP Headers头部压缩技术']),
            ('CS', ['Circuit Service电路域业务应用', 'Circuit Switched电路交换']),
            ('CSC', ['Customer Service Center客户服务中心']),
            ('CSCF', ['Call Session Control Function呼叫对话控制功能']),
            ('CSFB', ['Circuit Switched Fallback电路域回落']), ('CSG', ['Closed Subscriber Group闭合用户组']),
            ('CT', ['Communication Technology通信技术']), ('CTS', ['Call Trace System呼叫跟踪系统']),
            ('CU', ['Centralized Unit集中式单元', 'Charging Unit计费单元']),
            ('CUDR', ['Cloud Unified Data Repository云化统一数据仓库']),
            ('CUI', ['Chargeable User Identity用户计费标识']),
            ('CUPS', ['Control and User Plane Separation控制面与用户面分离']),
            ('CaaS', ['Container as a Service容器即服务']), ('DAP', ['Diameter Access PointDiameter 接入节点']),
            ('DAUD', ['Destination State Audit目的地查询']), ('DAVA', ['Destination Available目的地可用']),
            ('DB', ['Database数据库']), ('DC', ['Data Center数据中心']),
            ('DCNR', ['Dual Connectivity with NR 与NR的双重连通性']), ('DCU', ['Data Collection Unit数据采集单元']),
            ('DDB', ['DSC DatabaseDSC数据库模块']), ('DDN', ['Downlink Data Notification下行数据通知']),
            ('DDoS', ['Distributed Denial of Service分布式拒绝服务']), ('DECOR', ['Dedicated Core Network专用核心网']),
            ('DES', ['Data Encryption Standard数据加密标准']),
            ('DHCP', ['Dynamic Host Configuration Protocol动态主机配置协议']), ('DL', ['Down Link下行链路']),
            ('DMCC', ['Distributed Monitoring and Control Center分布式监控中心']),
            ('DMZ', ['Demilitarized Zone隔离区']), ('DN', ['Data Network数据网']),
            ('DNAI', ['DN Access Identifier数据网络接入标识符']), ('DNN', ['Data Network Name数据网名称']),
            ('DNS', ['Domain Name Server域名服务器', 'Domain Name System域名系统']),
            ('DPD', ['Dead Peer Detect对等体死亡检测']), ('DPDK', ['Data Plane Development Kit数据平面开发套件']),
            ('DPI', ['Deep Packet Inspection深度包检测']), ('DPM', ['Data Push Manager数据推送管理器']),
            ('DPR', ['Disconnect Peer Request拆除对等端连接请求']), ('DPU', ['Data Processing Unit数据处理单元']),
            ('DR', ['Designated Router指定路由器']), ('DRA', ['Diameter Routing AgentDiameter路由代理']),
            ('DRS', ['Data Receive Server数据接收服务器']), ('DRST', ['Destination Restricted目的地受限']),
            ('DRX', ['Discontinuous Reception 不连续接收']),
            ('DSA', ['Directory Service Agent目录服务代理', 'Directory System Agent目录系统代理']),
            ('DSCP', ['Differentiated Services Code Point差分服务编码点']), ('DT', ['Direct Tunnel直传隧道']),
            ('DTI', ['Digital Trunk Interface\t数字中继接口板']), ('DU', ['Distributed Unit分布式单元']),
            ('DUNA', ['Destination Unavailable目的地不可及']),
            ('DUPU', ['Destination User Part Unavailable 目的用户部分不可用']),
            ('DVS', ['Distributed Virtual Switch分布式虚拟交换机']),
            ('DWA', ['Device Watchdog Answer设备监控应答消息']), ('DWR', ['Device Watchdog Request设备监控请求消息']),
            ('DeNB', ['Donor eNB施主基站']), ('DoS', ['Denial of Service拒绝服务']),
            ('E-RAB', ['E-UTRAN Radio Access BearerE-UTRAN无线接入承载']),
            ('E-SMLC', ['Evolved Serving Mobile Location Center演进的服务位置中心']),
            ('E-UTRA', ['Evolved Universal Terrestrial Radio Access演进通用陆地无线接入']),
            ('E-UTRAN', ['Evolved Universal Terrestrial Radio Access Network演进的通用陆地无线接入网络']),
            ('E2E', ['End-to-End终端到终端']), ('EBI', ['EPS Bearer IDEPS承载标识']),
            ('EBS', ['Excess Burst Size超额突发数据量']), ('ECC', ['Error Check and Correction错误检查和纠正']),
            ('ECGI', ['E-UTRAN Cell Global IdentifierE-UTRAN小区全球标识']),
            ('ECI', ['E-UTRAN Cell IdentifierE-UTRAN小区标识']), ('ECM', ['EPS Connection ManagementEPS连接管理']),
            ('ECMM', ['ETCA Chassis Management ModuleETCA机框管理模块']),
            ('ECMP', ['Equal-Cost Multi-Path routing等价多路由']),
            ('ECP', ['Enterprise Communications Portal企业通信门户']),
            ('EDGE', ['Enhanced Data rates for GSM EvolutionGSM用的增强型数据速率']),
            ('EDR', ['Event Detail Record事件详细记录']), ('EF', ['Expedited Forwarding 快速转发']),
            ('EGBS', ['ETCA GE Base SwitchETCA 控制面(Base平面)交换板']),
            ('EGFS', ['ETCA GE Fabric SwitchETCA 媒体面(Fabric平面)交换板']),
            ('EIR', ['Equipment Identity Register设备标识寄存器']),
            ('EM', ['Element Management网元管理', 'Engineering Mode工程模式']),
            ('EMB', ['Enterprise Message Bus企业消息总线']), ('EMC', ['Elastic Management Center弹性管理中心']),
            ('EME', ['Electromagnetic Energy电磁能量']), ('EMS', ['Element Management System网元管理系统']),
            ('EN-DC', ['E-UTRA-NR Dual ConnectivityE-UTRA和NR的双连接']), ('EP', ['Elementary Procedure\xa0基本过程']),
            ('EPC', ['Evolved Packet Core演进的分组核心网']),
            ('EPLMN', ['Equivalent Public Land Mobile Network对等公用陆地移动网']),
            ('EPS', ['Evolved Packet System演进的分组系统']), ('ESD', ['Electrostatic Discharge静电放电']),
            ('ESM', ['EPS Session ManagementEPS会话管理']),
            ('ETSI', ['European Telecommunications Standards Institute欧洲电信标准化协会']),
            ('EoR', ['End of Row列末综合布线']), ('FAR', ['Forwarding Action Rule报文转发规则']),
            ('FC', ['Fiber Channel光纤通道']), ('FCAPS', [
            'Fault Configuration Accounting Performance and Security错误、配置、计帐、性能和安全（指网络管理的要素）']),
            ('FCC', ['Federal Communication Commission联邦通信委员会（美国）']),
            ('FDD', ['Frequency Division Duplex频分双工']), ('FE', ['Front End前端/前台']),
            ('FQDN', ['Fully Qualified Domain Name全称域名']), ('FRR', ['Fast Reroute快速重路由']),
            ('FTP', ['File Transfer Protocol文件传输协议']), ('FUP', ['Fair Usage Policy公平使用策略']),
            ('FWU', ['Firewall Service Unit防火墙业务单元']), ('FlexE', ['Flex Ethernet灵活以太网']),
            ('GBR', ['Guaranteed Bit Rate保证比特率']), ('GCID', ['GPRS Charging\nIdentifierGPRS计费标识']),
            ('GDPR', ['General Data Protection Regulation通用数据保护条例']), ('GE', ['Gigabit Ethernet千兆以太网']),
            ('GERAN', ['GSM/EDGE Radio Access NetworkGSM/EDGE无线接入网']),
            ('GFBR', ['Guaranteed Flow Bit Rate保证流比特率']), ('GGSN', ['Gateway GPRS Support NodeGPRS网关支持节点']),
            ('GMLC', ['Gateway for Mobile Location Center移动定位中心网关']),
            ('GMM', ['GPRS Mobile ManagementGPRS 移动性管理']), ('GMSC', [
            'Gateway Mobile-service Switching Center网关移动业务交换中心',
            'Gateway Mobile Switching Center网关移动交换中心']), ('GMT', ['Greenwich Mean Time格林尼治标准时间']),
            ('GPRS', ['General Packet Radio Service通用无线分组数据业务']),
            ('GPSI', ['Generic Public Subscription Identifier一般公共用户标识']), ('GR', ['Graceful Restart优雅重启']),
            ('GRE', ['General Routing Encapsulation通用路由封装']),
            ('GSM', ['Global System for Mobile Communications全球移动通信系统']),
            ('GSO', ['Global Service Orchestrator全局业务编排器']), ('GSU', ['General Service Unit通用业务单元']),
            ('GT', ['Global Title全局名', 'GSM/TD-SCDMAGSM和TD-SCDMA两种无线接入制式']),
            ('GTP', ['GPRS Tunneling ProtocolGPRS隧道协议']), ('GTP-C', ['GTP Control PlaneGTP控制面']),
            ('GTP-U', ['GTP User PlaneGTP用户面']), ('GTSM', ['Generalized TTL Security Mechanism通用TTL安全保护机制']),
            ('GUAMI', ['Globally Unique AMF ID全球唯一AMF标识']), ('GUI', ['Graphical User Interface图形用户界面']),
            ('GUMMEI', ['Globally Unique MME Identifier全球唯一移动性管理实体标识']),
            ('GUTI', ['Globally Unique Temporary Identity全球唯一临时标识']), ('GW', ['GateWay网关']),
            ('GWCN', ['Gateway Core Network网关核心网']), ('HA', ['High Availability高可用性']),
            ('HLCom', ['High Latency Communication高时延通讯']), ('HLD', ['High Level Design高层次设计']),
            ('HLR', ['Home Location Register归属位置寄存器']), ('HNB', ['Home Node B3G家庭基站']),
            ('HO', ['Handover切换']), ('HPLMN', ['Home Public Land Mobile Network归属公众陆地移动网']),
            ('HR', ['Home Routed本地路由']), ('HSS', ['Home Subscriber Server归属用户服务器']),
            ('HTTP', ['Hypertext Transfer Protocol超文本传输协议']),
            ('HTTPS', ['Hypertext Transfer Protocol Secure超文本传输安全协议']), ('HeNB', ['Home eNode BLTE家庭基站']),
            ('I-CSCF', ['Interrogating-Call Session Control Function查询呼叫会话控制功能']),
            ('I-SMF', ['Intermediate-SMF中间SMF']), ('I/O', ['Input/Output输入/输出']),
            ('IAAS', ['Infrastructure as a Service基础设施即服务']), ('IAM', ['Initial Address Message初始地址消息']),
            ('ICID', ['IM CN\nsubsystem charging identifierIM子系统计费标识']),
            ('ICMP', ['Internet Control Message ProtocolInternet控制报文协议']),
            ('ICS', ['IMS Centralized ServiceIMS集中式业务提供']), ('ID', ['Identifier识别']),
            ('IDA', ['Insert-Subscriber-Data- Answer插入用户数据响应']),
            ('IDC', ['Internet Data Center互联网数据中心']),
            ('IDR', ['Insert-Subscriber-Data-Request插入用户数据请求']),
            ('IDS', ['Intrusion Detection System入侵检测系统']),
            ('IE', ['Information Element信息元', 'Internet Explorer因特网浏览器']),
            ('IEEE', ['Institute of Electrical and Electronics Engineers电气与电子工程师学会']),
            ('IETF', ['Internet Engineering Task Force因特网工程任务组']),
            ('IGMP', ['Internet Group Management Protocol因特网组播管理协议']), ('IK', ['Integrity Key鉴权密钥']),
            ('IM', ['Instant Message即时消息']), ('IM-MGW', ['IP Multimedia-Media GatewayIP多媒体媒体网关']),
            ('IMEI', ['International Mobile Equipment Identity国际移动设备标识']), ('IMEISV', [
            'International Mobile Equipment Identity and Software Version number国际移动设备识别码和软件版本号']),
            ('IMPI', ['IP Multimedia Private IdentityIP多媒体私有标识']),
            ('IMPU', ['IP Multimedia Public IdentityIP多媒体公有标识']),
            ('IMS', ['IP Multimedia SubsystemIP多媒体子系统']),
            ('IMSI', ['International Mobile Subscriber Identity国际移动用户标识']), ('INIT', ['Initiation开始']),
            ('IO', ['Input &\nOutput输入输出']), ('IOMMU', ['Input/Output Memory Management UnitI/O内存管理单元']),
            ('IOPS', ['Input/Output Operations Per Second每秒输入/输出操作']),
            ('IOT', ['Interoperability Test互操作测试']), ('IP', ['Internet Protocol因特网协议']),
            ('IP-CAN', ['IP Connectivity Access NetworkIP连通接入网']),
            ('IPDR', ['Internet Protocol Detail Record互联网协议详细记录']),
            ('IPHC', ['Internet Protocol Header CompressionIP头压缩']), ('IPPD', ['IP Path DetectionIP通路检测']),
            ('IPS', ['IP Path Source endIP通路源端']), ('IPSP', ['IP Server ProcessIP服务器进程']),
            ('IPSec', ['IP Security ProtocolIP安全协议']), ('IPU', ['Interface Process Unit接口处理单元']),
            ('IPX', ['Internetwork Packet Exchange protocolInternet网络分组交换协议']),
            ('IPv4', ['Internet Protocol version 4第四版互联网协议']),
            ('IPv6', ['Internet Protocol Version 6IP协议的版本6']), ('ISDN', [
            'Integrated Services Digital Network综合业务数字网',
            'International Subscriber Directory Number国际用户目录号']),
            ('ISIM', ['IMS Subscriber Identity ModuleIMS用户身份模块']),
            ('ISO', ['International Organization for Standardization国际标准化组织']),
            ('ISP', ['Internet Service Provider因特网业务提供者']),
            ('IT', ['Information Technology信息技术', 'Inactivity Test不活动性测试']),
            ('ITU', ['International Telecommunications Union国际电信联盟']), ('ITU-T', [
            'International Telecommunication Union - Telecommunication Standardization Sector国际电信联盟－电信标准部']),
            ('IVR', ['Interactive Voice Response交互式语音应答']), ('IWF', ['Interworking Function网络互通功能']),
            ('IWMSC', ['Interworking Mobile Switching Center网间移动交换中心']),
            ('IWS', ['Interworking Solution互操作解决方案']), ('IaaS', ['Infrastructure as a Service基础设施即服务']),
            ('IoT', ['Internet of Things物联网']), ('JSON', ['Java Script Object NotationJava脚本对象标记']),
            ('KPI', ['Key Performance Index关键性能指标', 'Key Performance Indicator关键性能指标']),
            ('KVM', ['Kernel-based Virtual Machine基于内核的虚拟机']),
            ('L2TP', ['Layer2 Tunneling Protocol第二层隧道协议']),
            ('L3VPN', ['Layer 3 Virtual Private Network三层虚拟专用网']), ('LA', ['Location Area位置区']),
            ('LAC', ['Location Area Code位置区码']), ('LACP', ['Link Aggregation Control Protocol链路聚合控制协议']),
            ('LADN', ['Local Area Data Network局域数据网']),
            ('LAI', ['Location Area Information移动台位置信息', 'Location Area Identity位置区标识']),
            ('LAN', ['Local Area Network局域网']), ('LB', ['Load Balance负载均衡']),
            ('LBO', ['Local Breakout本地路由疏导']), ('LC', ['Load Control负载控制']),
            ('LCI', ['Load Control Information负荷控制信息']), ('LCS', ['LoCation Services定位业务']),
            ('LDAP', ['Lightweight Directory Access Protocol轻量级目录访问协议']), ('LDAPS', ['LDAP over SSL安全LDAP']),
            ('LDB', ['Local Database本地数据库']), ('LDN', ['Local Data Network本地数据网络']),
            ('LDP', ['Label Distribution Protocol标记分发协议']), ('LGW', ['Local Gateway本地接入网关']),
            ('LIB', ['Label Information Base标签信息库']), ('LIPA', ['Local IP Access本地IP接入']),
            ('LLC', ['Logical Link Control逻辑链路控制']), ('LLD', ['Low Level Design详细设计']),
            ('LMF', ['Local Management Function本地管理功能', 'Location Management Function定位管理功能']),
            ('LNS', ['L2TP Network ServerL2TP网络服务器']), ('LPP', ['LTE Positioning ProtocolLTE定位协议']),
            ('LPWAN', ['Low-Power Wide-Area Network低功耗广域网']),
            ('LRDIMM', ['Load Reduced Dual Inline Memory Module低负载双列直插内存模块']),
            ('LSA', ['Link State Advertisement链路状态广播']),
            ('LSP', ['Link State Protocol Data Unit链路状态协议数据单元', 'Label Switched Path标签交换路径']),
            ('LSU', ['Log Store Unit日志存储单元']),
            ('LTE', ['Long Term Evolution长期演进', 'Long Time Evolution更长期发展']),
            ('LTM', ['Logical Topology Management逻辑拓扑管理', 'Link Trace Message链路跟踪消息']),
            ('LUDT', ['Long Unit Data长单元数据']), ('LUDTS', ['Long Unit Data Service长单元数据业务']),
            ('M-CDR', ['Mobility Management - Call Detail Record移动性管理-呼叫详细记录']),
            ('M2M', ['Machine to Machine机器对机器']),
            ('M3UA', ['MTP3-User Adaptation layer protocolMTP第三层的用户适配层协议']),
            ('MAA', ['Multimedia-Authorization-Answer多媒体鉴权响应']), ('MAC', ['Media Access Control媒介接入控制']),
            ('MAN', ['Manager Node管理节点']), ('MANO', ['Management and Orchestration管理和编排']),
            ('MAP', ['Mobile Application Part移动应用部分']),
            ('MAR', ['Multimedia-Authorization-Request多媒体鉴权请求']),
            ('MBMS', ['Multimedia Broadcast/Multicast Service多媒体广播/组播业务']),
            ('MBMSGW', ['Multimedia Broadcast Multicast Service Gateway多媒体广播多播业务网关']),
            ('MBR', ['Maximum Bit Rate最大比特率']), ('MCC', ['Mobile Country Code移动国家码']),
            ('MCE', ['Multi-cell/Multicast Coordination Entity多小区/多播协调实体标识']),
            ('MCPTT', ['Mission Critical Push To Talk关键任务一键通']),
            ('MD5', ['Message Digest 5 Algorithm信息-摘要算法5']), ('MDS', ['Message Dispatch Service消息分发服务']),
            ('MDT', ['Minimization of Drive Tests最小化路测']), ('ME', ['Mobile Equipment移动设备']),
            ('MEC', ['Mobile Edge Computing移动边缘计算']), ('MEID', ['Mobile Equipment Identifier移动设备标识']),
            ('MEP', ['MEC Platform多接入边缘计算平台']), ('MFBR', ['Maximum Flow Bit Rate最大流比特率']),
            ('MGCF', ['Media Gateway Control Function媒体网关控制功能']), ('MGW', ['Media GateWay媒体网关']),
            ('MIB', ['Management Information Base管理信息库']),
            ('MICO', ['Mobile Initiated Connection Only仅限移动发起连接']), ('MM', ['Mobility Management移动性管理']),
            ('MME', ['Mobility Management Entity移动管理实体']), ('MMEC', ['MME CodeMME编码']),
            ('MML', ['Man Machine Language人机语言']), ('MMTel', ['Multimedia Telephony多媒体电话']),
            ('MNC', ['Mobile Network Code移动网络号']),
            ('MO', ['Mobile Originated移动台发起', 'Managed Object管理对象']),
            ('MO-LR', ['Mobile Originating Location Request移动台发起位置请求/移动发起定位请求']),
            ('MOC', ['Managed Object Class管理对象类']), ('MOCN', ['Multi-Operator Core Network多运营商核心网']),
            ('MP', ['Main Processor主处理器']),
            ('MPDCCH', ['MTC Physical Downlink Control Channel机器类型通信物理下行控制信道']),
            ('MPLS', ['Multiprotocol Label Switching多协议标记交换']),
            ('MPS', ['Mobile Positioning System移动定位系统', 'Multimedia Priority Service多媒体优先业务']),
            ('MPU', ['Main Processing Unit主处理单元', 'Management Process Unit主控卡功能子单元']),
            ('MR-DC', ['Multi-RAT Dual Connectivity多RAT双连接']),
            ('MRFC', ['Multimedia Resource Function Controller多媒体资源功能控制器']),
            ('MRFP', ['Multimedia Resource Function Processor多媒体资源功能处理器']), ('MS', ['Mobile Station移动台']),
            ('MSA', ['Micro Service Architecture微服务架构']), ('MSC', ['Mobile Switching Center移动交换中心']),
            ('MSCS', ['Mobile Switching Center Server移动交换中心服务器']),
            ('MSDP', ['Multicast Source Discovery Protocol组播源发现协议']),
            ('MSISDN', ['Mobile Station International Subscriber Directory Number移动台国际用户目录号']),
            ('MT', ['Mobile Terminated移动台终止', 'Mobile Terminal移动终端']),
            ('MTBF', ['Mean Time Between Failures平均故障间隔时间']),
            ('MTC', ['Machine Type Communication机器类型通信']),
            ('MTP3', ['Message Transfer Part layer 3消息传递部分第三层']),
            ('MTTR', ['Mean Time To Recovery平均恢复时间']),
            ('MTU', ['Maximum Transfer Unit最大传输单元', 'Maximum Transmission Unit最大传输单元']),
            ('MU', ['Merging Unit合并单元']), ('MeNB', ['Macro eNodeB与HeNB（LTE家庭基站）相对应']),
            ('NACC', ['Network Assisted Cell Change网络辅助小区式切换']),
            ('NAI', ['Network Access Identifier网络接入标识']), ('NAS', ['Non-Access Stratum非接入层',
                                                                         'Network Access Service网络接入服务',
                                                                         'Network Attached Storage网络附加存储']),
            ('NAT', ['Network Address Translation网络地址转换']),
            ('NB-IoT', ['Narrow Band Internet of Things窄带物联网']),
            ('NCC', ['Next Hop Chaining Counter下一跳链接计数器']),
            ('NCMM', ['New Chassis Management Module新型机框管理模块']),
            ('NDF', ['Native Direct Function本地直连接口']), ('NE', ['Network Element网络单元（网元）']),
            ('NE-DC', ['NR-E-UTRA Dual ConnectivityNR和E-UTRA的双连接']),
            ('NEF', ['Network Exposure Function网络开放功能']), ('NF', ['Network Function网络功能']),
            ('NFS', ['Network Function Service网络功能服务', 'Network File System网络文件系统']),
            ('NFV', ['Network Functions Virtualization网络功能虚拟化']),
            ('NFVI', ['Network Functions Virtualization Infrastructure网络功能虚拟化基础设施']),
            ('NFVO', ['Network Functions Virtualization Orchestrator网络功能虚拟化编排器']),
            ('NG-RAN', ['Next Generation Radio Access Network下一代无线接入网']),
            ('NGEN-DC', ['NG-RAN E-UTRA-NR Dual ConnectivityNG-RAN E-UTRA和NR的双连接']),
            ('NI', ['Network Identifier网络标识']), ('NIF', ['Node Interworking Function节点互通功能']),
            ('NITZ', ['Network Identity and Time Zone网络标志和时区']), ('NM', ['Network Management网络管理']),
            ('NMS', ['Network Management System网络管理系统']),
            ('NNSF', ['NAS Node Selection Function非接入层节点选择功能']), ('NOR', ['Notify-Request通知请求']),
            ('NPDCCH', ['Narrowband Physical Downlink Control Channel窄带物理下行控制信道']),
            ('NR', ['New Radio新无线']), ('NRF', ['NF Repository Function网络功能仓储']),
            ('NRI', ['Network Resource Identifier网络资源标识']), ('NS', ['Network Service网络服务']),
            ('NSA', ['Non-Standalone5G非独立组网']),
            ('NSAPI', ['Network-layer\nService Access Point Identifier网络层业务接入点标识']),
            ('NSE', ['Network Service Entity网络服务实体']),
            ('NSEI', ['Network\nService Entity Identifier网络业务实体标识']),
            ('NSI', ['Network Slice Instance网络切片实例']),
            ('NSMF', ['Network Slice Management Function网络切片管理功能']),
            ('NSSAI', ['Network Slice Selection Assistance Information网络切片选择辅助信息']),
            ('NSSF', ['Network Slice Selection Function网络切片选择功能']),
            ('NSSI', ['Network Slice Subnet Instance网络子切片实例']),
            ('NSSMF', ['Network Slice Subnet Management Function网络子切片管理功能']),
            ('NSST', ['Network Slice Subnet Template网络子切片模板']),
            ('NSVC', ['Network Service Virtual Connection网络服务虚连接']),
            ('NTP', ['Network Time Protocol网络时间协议']),
            ('NUMA', ['Non-Uniform Memory Access Architecture非统一内存访问架构']),
            ('NWDAF', ['Network Data Analytics Function网络数据分析功能']), ('OA', ['Office Automation办公自动化']),
            ('OAM', ['Operation, Administration and Maintenance操作管理维护']), ('OC', ['Overload Control过负荷控制']),
            ('OCI', ['Overload Control Information过载控制信息']), ('OCS', ['Online Charging System在线计费系统']),
            ('ODB', ['Operator Determined Barring运营商闭锁']),
            ('OFDMA', ['Orthogonal Frequency Division Multiple Access正交频分多址接入']),
            ('OID', ['Object Identifier对象标识符']), ('OLAP', ['On-Line Analytical Processing联机分析处理']),
            ('OLR', ['Organic Loading Rate有机负荷率']), ('OMC', ['Operation & Maintenance Center操作维护中心']),
            ('OMM', ['Operation and Maintenance Management操作维护管理', 'Operation & Maintenance Module操作维护模块']),
            ('OMMP', ['Operation and Maintenance Management Platform操作维护管理平台']), ('OMP', [
            'Operation & maintenance Main Processor操作维护主处理板',
            'Operation & Maintenance Processor操作维护处理器']),
            ('OMS', ['Operation and Maintenance Subsystem操作维护子系统']),
            ('OMU', ['Operation & Management Unit操作管理单元']), ('OPEX', ['Operating Expenditure运营性支出']),
            ('OS', ['Operating System操作系统']), ('OSD', ['Open Script Designer脚本设计器']),
            ('OSE', ['Open Script Execution Engine脚本执行引擎']), ('OSP', ['OpenStack PlatformOpenStack平台']),
            ('OSPF', ['Open Shortest Path First开放最短路径优先']), ('OSS', ['Operation Support System运营支撑系统']),
            ('OTA', ['Over The Air空中传输']), ('OTDR', ['Optical Time Domain Reflectometer光时域反射仪']),
            ('OTT', ['Over The Top通过互联网向用户提供各种应用服务']), ('OVS', ['Open VSwitch虚拟交换机']),
            ('P-CSCF', ['Proxy-Call Session Control Function代理呼叫会话控制功能']),
            ('P-GW', ['Packet Data Network Gateway分组数据网网关']),
            ('P-TMSI', ['Packet Temporary Packet Temporary Mobile Subscriber Identity分组临时移动用户标识']),
            ('P2P', ['Point to Point点对点']), ('PANI', ['P-Access-Network-Info接入网信息（SIP私有扩展之一）']),
            ('PAP', ['Password Authentication Protocol密码认证协议']), ('PC', ['Personal Computer个人电脑']),
            ('PCC', ['Policy and Charging Control计费和策略控制']), ('PCCPI', ['PCC Private IdentityPCC私有标识']),
            ('PCEF', ['Policy and Charging Enforcement Function计费和策略控制实施功能']),
            ('PCF', ['Policy Control Function策略控制功能']),
            ('PCIe', ['Peripheral Component Interconnect Express快速外设组件互连']),
            ('PCO', ['Protocol Configuration Option协议配置选项']),
            ('PCRF', ['Policy and Charging Rules Function策略和计费规则功能']),
            ('PDB', ['Process Data Block进程数据区', 'Packet Delay Budget数据包时延预算']),
            ('PDCP', ['Packet Data Convergence Protocol分组数据收敛协议']), ('PDN', ['Packet Data Network分组数据网']),
            ('PDP', ['Packet Data Protocol分组数据协议']), ('PDR', ['Packet Detection Rule报文检测规则']),
            ('PDS', ['Primary Directory Server主用目录服务器']),
            ('PDU', ['Packet Data Unit分组数据单元', 'Protocol Data Unit协议数据单元']),
            ('PE', ['Provider Edge运营商网络边缘']), ('PEI', ['Permanent Equipment Identifier永久设备标识']),
            ('PF', ['Packet Filter包过滤']), ('PFCP', ['Packet Forwarding Control Protocol报文转发控制协议']),
            ('PFI', [' Payload FCS Indicator净负荷FCS标识']), ('PFU', ['Packet Forwarding Unit网络处理单元']),
            ('PGW', ['Provision Gateway受理网关', 'PDN Gateway分组数据网网关']),
            ('PGW-C', ['PDN Gateway Control plane functionPGW控制面网关']),
            ('PGW-U', ['PDN Gateway User plane functionPGW用户面网关']), ('PHB', ['Per Hop Behavior逐跳行为']),
            ('PI', ['Performance Index性能指标']), ('PL', ['Priority Level优先等级']),
            ('PLMN', ['Public Land Mobile Network公共陆地移动网']), ('PM', ['Performance Management性能管理']),
            ('PNA', ['Push-Notification-Answer推送通知响应']), ('PNF', ['Physical Network Function物理网络功能']),
            ('PNI-NPN', ['Public Network Integrated NPN公共网络集成的NPN网络，即非独立专网']),
            ('PNR', ['Push-Notification-Request推送通知请求']), ('POD', ['Point of Deployment部署单元']),
            ('PP', ['Peripheral Processor外围处理器']), ('PPD', ['Parallel Presence Detect并行存在检测']),
            ('PPE', ['Personal Protective Equipment个人防护用品']), ('PPI', ['Paging Policy Indication寻呼策略指示']),
            ('PPM', ['Product and Package Management产品与套餐管理']), ('PPS', ['Packets Per Second数据包每秒']),
            ('PRA', ['Presence Reporting Area出现上报区域']), ('PRB', ['Physical Resource Block物理资源块']),
            ('PRN', ['PGW Restart NotificationPGW重启通知']),
            ('PS', ['Packet Switched分组交换', 'Packet Switched domain分组交换域']),
            ('PSA', ['PDU Session AnchorPDU会话锚点']), ('PSI', ['PCF Session IdentityPCF会话标识']),
            ('PSM', ['Power Saving Mode节电模式']), ('PTW', ['Paging Time Window寻呼时间窗']),
            ('PUDR', ['Policy UDR统一的策略数据存储库']), ('PUI', ['Public User Identity公开用户标识']),
            ('PUR', ['Purge-UE-RequestPurge UE请求']), ('PVI', ['Private User Identity私有用户标识']),
            ('PVID', ['Port VLAN ID端口虚拟局域网标识']),
            ('PWS', ['Power System电源系统', 'Public Warning System公共预警系统']),
            ('PaaS', ['Platform as a Service平台即服务']), ('QCI', ['QoS Class IdentifierQoS类别标识']),
            ('QER', ['QoS Enforcement RuleQoS执行规则']), ('QFI', ['QoS Flow IdentityQoS流标识']),
            ('QPS', ['Queries-per-second每秒查询率']), ('QoS', ['Quality of Service服务质量']),
            ('RA', ['Router Advertisement路由器通告报文', 'Routing Area路由区']),
            ('RAA', ['Re-Auth-Answer重新鉴权响应']), ('RAB', ['Radio Access Bearer无线接入承载']),
            ('RAC', ['Routing Area Code路由区域码']),
            ('RADIUS', ['Remote Authentication Dial In User Service远端鉴权拨号用户服务']),
            ('RAI', ['Routing Area Identity路由区标识']),
            ('RAID', ['Redundant Array of Independent Disks独立冗余磁盘阵列']),
            ('RAN', ['Radio Access Network无线接入网']),
            ('RANAP', ['Radio Access Network Application Protocol无线接入网应用协议']),
            ('RAR', ['Re-Auth-Request重新鉴权请求']), ('RAS', ['Real-time Analysis System实时分析系统']),
            ('RAT', ['Radio Access Technology无线接入技术']), ('RAU', ['Routing Area Update路由区更新']),
            ('RB', ['Radio Bearer无线承载']), ('RCA', ['Root Cause Analysis根本原因分析']),
            ('RCM', ['Real-time CHR Manager实时CHR管理器']), ('RCP', ['Resource Control Platform资源控制平台']),
            ('RD', ['Route Distinguisher路由标识符']),
            ('RDIMM', ['Registered Dual Inline Memory Module带寄存器的双列直插内存模块']),
            ('REST', ['Representational State Transfer表述性状态转移']), ('RF', ['Radio Frequency射频']),
            ('RFC', ['Remote Feature Control远端特征控制', 'Request For Comments请求注解']),
            ('RFSP', ['RAT/Frequency Selection Priority无线/频率选择优先级']), ('RG', ['Rating Group费率组']),
            ('RGW', ['Replication Gateway局间复制模块']), ('RIM', ['RAN Information Management无线接入网络信息管理']),
            ('RIP', ['Routing Information Protocol路由信息协议']),
            ('RLC', ['Radio Link Control无线链路控制', 'Release Complete释放完成消息']),
            ('RN', ['Radio Network无线网络']), ('RNC', ['Radio Network Controller无线网络控制器']),
            ('RNL', ['Radio Network Layer无线网络层']),
            ('RNTI', ['Radio Network Temporary Identifier无线网络临时标识']),
            ('ROHC', ['Robust Header Compression健壮性头压缩']),
            ('ROSng', ['Realtime OS Next Generation下一代实时操作系统']), ('RP', ['Rendezvous Point汇聚点']),
            ('RQA', ['Reflective QoS Attribute反射QoS属性']), ('RRC', ['Radio Resource Control无线资源控制']),
            ('RRM', ['Radio Resource Management无线资源管理']), ('RS', ['Router Solicitation路由器请求报文']),
            ('RSC', ['Reset Confirmation复位/复原确认']), ('RSR', ['Reset Request复原请求/复位请求']),
            ('RTCP', ['Real-time Transport Control Protocol实时传输控制协议']),
            ('RTP', ['Real-time Transport Protocol实时传输协议']), ('RTT', ['Round Trip Time往返时间']),
            ('S-CDR', ['Serving GPRS Support Node -Call Detail Record服务GPRS支持节点-呼叫详细记录']),
            ('S-CSCF', ['Serving-Call Session Control Function服务呼叫会话控制功能']),
            ('S-GW', ['Serving Gateway服务网关']),
            ('S-NSSAI', ['Single Network Slice Selection Assistance Information单个网络切片选择辅助信息']),
            ('S1AP', ['S1 Application ProtocolS1应用协议']), ('SA', ['Standalone5G独立组网']),
            ('SAC', ['Service Area Code业务区码']), ('SACK', ['Selective Acknowledgement选择性确认']),
            ('SAE', ['System Architecture Evolution系统架构演进']), ('SAI', ['Service Area Identity业务区域标识']),
            ('SAR', ['Server-Assignment-Request服务器指派请求']),
            ('SAS', ['Serial Attached SCSI串行小型计算机系统接口']), ('SATA', ['Serial ATA串行ATA']),
            ('SBA', ['Service Based Architecture基于服务的架构']), ('SBC', ['Session Border Controller会话边界控制器']),
            ('SBI', ['Service Based Interface基于服务的接口']), ('SC', ['Service Component服务组件']),
            ('SCC', ['Service Centralization and Continuity业务集中和连续']),
            ('SCCP', ['Signaling Connection Control Part信号连接控制部分']),
            ('SCCU', ['Service Component Control Unit服务组件控制单元']),
            ('SCEF', ['Service Capability Exposure Function服务能力开放功能（平台）']),
            ('SCG', ['Secondary Cell Group辅助小区组']), ('SCON', ['SS7 Network Congestion七号信令网拥塞']),
            ('SCP', ['Service Control Point业务控制点']),
            ('SCR', ['Service Component Repository服务组件仓库', 'Sustainable Cell Rate可维持信元速率']),
            ('SCTP', ['Stream Control Transmission Protocol流控制传输协议']),
            ('SD', ['Slice Differentiator切片差异区分器']), ('SDH', ['Synchronous Digital Hierarchy同步数字体系']),
            ('SDK', ['Software Development Kit软件开发工具']), ('SDN', ['Software Defined Network软件定义网络']),
            ('SDP', ['Session Description Protocol会话描述协议']),
            ('SDS', ['Secondary Directory Server备用目录服务器']),
            ('SEPP', ['Security Edge Protection Proxy安全边缘保护代理']),
            ('SFTP', ['Secure File Transfer Protocol安全文件传输协议']),
            ('SGIP', ['Short Message Gateway Interface Protocol中国联合通信公司短消息网关系统接口协议']),
            ('SGP', ['Signaling Gateway Process 信令网关处理']),
            ('SGSN', ['Serving GPRS Support Node服务GPRS支持节点']), ('SGW', ['Serving Gateway服务网关']),
            ('SGW-C', ['Serving Gateway Control plane functionSGW控制面网关']),
            ('SGW-U', ['Serving Gateway User plane functionSGW用户面网关']),
            ('SHA', ['Secure Hash Algorithm安全哈希算法']), ('SI3', ['System Information 3系统信息3']),
            ('SID', ['Service Identifier业务标识']), ('SIG', ['Signal信令']),
            ('SIGTRAN', ['Signalling Transport信令传输']), ('SIM', ['Subscriber Identity Module用户识别卡']),
            ('SIP', ['Simple Internet Protocol简单IP协议']),
            ('SIPI', ['Signaling IP bearer Interface信令IP承载接入板']),
            ('SIPTO', ['Selected IP Traffic Offload选定的IP流量分流 ']),
            ('SLA', ['Service Level Agreement服务等级协议']),
            ('SLR', ['Spending Limit Request消费限额请求', 'Subscriber Location Report发送者定位报告']),
            ('SM', ['Session Management会话管理']), ('SMC', ['Short Message Center短消息中心']),
            ('SMF', ['Session Management Function会话管理功能', 'Service Management Function业务管理功能']),
            ('SMGP', ['Short Message Gateway Protocol中国电信短消息网关协议']),
            ('SMLC', ['Serving Mobile Location Center服务移动定位中心']),
            ('SMP', ['Signal Main Processor信令主处理模块']),
            ('SMPP', ['Short Message Peer to Peer Protocol短消息点对点协议']),
            ('SMS', ['Short Message Service短消息业务']), ('SMSC', ['Short Message Service Center短消息中心']),
            ('SMSF', ['Short Message Service Function短消息服务功能']),
            ('SMTP', ['Simple Mail Transfer Protocol简单邮件传输协议']), ('SN', ['Serial Number序列号']), ('SNA', [
            'Subscription-Notification-Answer订阅通知响应', 'Systems Network Architecture系统网络体系结构',
            'Shared Network Area共享网络区域']),
            ('SNDCP', ['Sub Network\nDependent Convergence Protocol子网相关的收敛协议']),
            ('SNMP', ['Simple Network Management Protocol简单网络管理协议']),
            ('SNR', ['Subscription-Notification-Request订阅通知请求']),
            ('SOA', ['Service Oriented Architecture面向服务的架构']),
            ('SOAP', ['Simple Object Access Protocol简单对象访问协议']), ('SON', ['Self-Organizing Network自组织网络']),
            ('SP', ['Service Provider服务提供商']), ('SPR', ['Subscription Profile Repository用户签约数据库']),
            ('SQL', ['Structured Query Language结构化查询语言']),
            ('SR-IOV', ['Single-Root I/O Virtualization单根I/O虚拟化']),
            ('SRES', ['Signed Response (authentication)随机数（鉴权）']),
            ('SRI', ['Send Routing Information发送路由信息']),
            ('SRNC', ['Serving Radio Network Controller服务无线网络控制器']),
            ('SRNS', ['Serving RNS服务无线网络子系统']),
            ('SRVCC', ['Single Radio Voice Call Continuity单射频语音呼叫连续性']),
            ('SSA', ['Subsystem Allowed子系统允许']), ('SSC', ['Session and Service Continuity会话与业务连续性']),
            ('SSD', ['Solid State Drive固态硬盘']),
            ('SSDS', ['Secondary Synchronization Directory Server数据同步的备用目录服务器']),
            ('SSH', ['Secure Shell安全外壳']), ('SSL', ['Secure Sockets Layer安全套接字层']),
            ('SSM', ['Synchronization Status Message同步状态消息']), ('SSN', ['Sub-System Number子系统号']),
            ('SSP', ['Subsystem Prohibited子系统禁止']), ('SSS', ['Supplementary Service Server（IMS）补充业务服务器']),
            ('SST', ['Subsystem Status Test子系统状态测试', 'Slice/Service Type切片/服务类型']),
            ('STA', ['Session-Termination-Answer会话终止响应']), ('STP', ['Signaling Transfer Point信令转接点']),
            ('STR', ['Session-Termination-Request会话终止请求']),
            ('SUCI', ['Subscription Concealed Identifier签约的隐藏标识符']),
            ('SUDS', ['Secondary Unsynchronization Directory Server数据未同步的备用目录服务器']),
            ('SUPI', ['Subscriber Permanent Identifier用户永久标识']), ('SaaS', ['Software as a Service软件即服务']),
            ('SeGW', ['Security Gateway安全网关']), ('T-ADS', ['Terminating Access Domain Selection终结接入域选择']),
            ('TA', ['Tracking Area跟踪区域']), ('TAC', ['Tracking Area Code跟踪区域码']),
            ('TACACS', ['Terminal Access Controller Access Control System终端访问控制器访问控制系统']),
            ('TAI', ['Tracking Area Identity跟踪区标识']), ('TAU', ['Tracking Area Update跟踪区域更新']),
            ('TCE', ['Trace Collection Entity跟踪采集实体']), ('TCM', ['Trusted Cryptography Module可信密码模块']),
            ('TCO', ['Total Cost of Ownership总体拥有成本']), ('TCP', ['Transmission Control Protocol传输控制协议']),
            ('TD-SCDMA', ['Time Division-Synchronization Code Division\nMultiple Access时分同步码分多址接入']),
            ('TDD', ['Time Division Duplex时分双工']), ('TDF', ['Traffic Detection Function流量检测功能']),
            ('TE', ['Terminal Equipment终端设备']), ('TEC', ['Thermoelectric Cooler热电制冷器']),
            ('TECS', ['Tulip Elastic Cloud System郁金香弹性云系统']),
            ('TEID', ['Tunnel Endpoint Identifier隧道端点标识']),
            ('TELNET', ['Telecommunication Network Protocol远程登录协议']),
            ('TFT', ['Traffic Flow Template话务流量模型']), ('THP', ['Traffic Handling Priority 业务处理优先级']),
            ('TI', ['Transparent Interface透明接口']), ('TIN', ['Terminating Intelligent Network终呼智能网']),
            ('TIPC', ['Transparent Interprocess Communication透明的进程间通信']),
            ('TLS', ['Transport Layer Security传输层安全']), ('TLV', ['Tag, Length, Value标记、长度、取值']),
            ('TMSI', ['Temporary Mobile Subscriber Identity临时移动用户识别码']),
            ('TMSP', ['Telecom Microservices Platform电信级微服务平台']), ('TOS', ['Type of Service服务类型']),
            ('TOSCA', ['Topology and Orchestration Specification for Cloud\nApplications云应用的拓扑和编排规范']),
            ('TPM', ['Trusted Platform Module可信平台模块']), ('TPS', ['Transactions Per Second每秒处理事务数']),
            ('TSA', ['TDF Session Answer业务探测会话应答']), ('TSN', ['Transmission Sequence Number传输顺序号']),
            ('TSR', ['TDF Session Request业务探测会话请求']),
            ('TWAMP', ['Two-Way Active Measurement Protocol双向主动测量协议']), ('ToR', ['Top of Rack机架顶部交换机']),
            ('UAA', ['User-Authorization- Answer用户授权响应']), ('UAR', ['User-Authorization-Request用户授权请求']),
            ('UBAS', ['User Behavior Analysis System用户行为分析系统']), ('UDA', ['User-Data-Answer用户数据响应']),
            ('UDB', ['User Database用户数据库']), ('UDM', ['Unified Data Management统一数据管理']),
            ('UDP', ['User Datagram Protocol用户数据报协议']),
            ('UDR', ['Unified Data Repository统一数据存储', 'User Data Request用户数据（读取）请求']),
            ('UDSF', ['Unstructured Data Storage Function非结构化数据存储功能']), ('UDT', ['Unit Data单元数据']),
            ('UDTS', ['Unit Data Service单元数据业务']), ('UE', ['User Equipment用户设备']),
            ('UL', ['Underwriters Laboratories美国保险商实验所安全标准']),
            ('ULA', ['Update-Location-Answer位置更新响应']), ('ULCL', ['Uplink Classifier上行分类器']),
            ('ULI', ['User Location Information用户位置信息']), ('ULP', ['Upper-Layer Protocol上层协议']),
            ('ULR', ['Update-Location-Request位置更新请求']), ('UME', ['Unified Management Expert统一管理专家']),
            ('UMM', ['Unified Maintenance Module集中维护模块']), ('UMMP', ['Unified Master Main Processor统一主控板']),
            ('UMTS', ['Universal Mobile Telecommunication System通用移动通讯系统']),
            ('UOMP', ['Universal Operation & maintenance Main Processor通用操作维护主处理模块']),
            ('UP', ['User Plane用户面']), ('UPF', ['User Plane Function用户平面功能']),
            ('UPSC', ['UE Policy Section CodeUE策略分片码']), ('UPU', ['User Part Unavailable用户部分不可用']),
            ('URI', ['Uniform Resource Identifier统一资源标识符']), ('URL', ['Uniform Resource Locator统一资源定位符']),
            ('URLLC', ['Ultra Reliable Low Latency Communication超高可靠超低时延通信']),
            ('URN', ['Uniform Resource Name统一资源名']), ('URR', ['Usage Reporting Rule用量上报规则']),
            ('URSP', ['UE Route Selection PolicyUE路由选择策略']), ('USB', ['Universal Serial Bus通用串行总线']),
            ('USIM', ['User Service Identity Module通用用户身份识别模块']),
            ('USM', ['UDS System MaintenanceUDS系统维护工具']),
            ('USPP', ['Universal Subscriber Profile Platform通用用户数据平台']),
            ('USUP', ['Universal Service User plane Processor通用业务用户面处理模块']), ('UTRAN', [
            'UMTS Terrestrial Radio Access NetworkUMTS陆地无线接入网',
            'Universal Terrestrial Radio Access Network通用地面无线接入网络']),
            ('UUID', ['Universal Unique Identifier全局唯一标识符']), ('VAS', ['Value-Added Service增值服务']),
            ('VDC', ['Virtual Data Center虚拟数据中心']),
            ('VIM', ['Virtualized Infrastructure Manager虚拟化基础设施管理系统']),
            ('VIP', ['Very Important Person贵宾']), ('VJHC', ['Van Jacobson’s Header Compression范•雅各布森头压缩']),
            ('VL', ['Virtual Link虚拟链路']), ('VLAN', ['Virtual Local Area Network虚拟局域网']),
            ('VLR', ['Visitor Location Register拜访位置寄存器']), ('VM', ['Virtual Machine虚拟机']),
            ('VNC', ['Virtual Network Computing虚拟网络计算']), ('VNF', ['Virtualized Network Function虚拟化网络功能']),
            ('VNFC', ['Virtualized Network Function Component虚拟网络功能组件']),
            ('VNFD', ['Virtualized Network Function Descriptor虚拟化网络功能描述符']),
            ('VNFM', ['Virtualized Network Function Manager虚拟化网络功能管理器']),
            ('VNFO', ['Virtualized Network Function Orchestration虚拟化网络功能编排器']),
            ('VPC', ['Virtual Private Cloud虚拟私有云']),
            ('VPLMN', ['Visited Public Land Mobile Network拜访公众陆地移动网']),
            ('VPN', ['Virtual Private Network虚拟专用网']), ('VR', ['Virtual Reality虚拟现实']),
            ('VRF', ['Virtual Route Forwarding虚拟路由转发']),
            ('VRRP', ['Virtual Router Redundancy Protocol虚拟路由器冗余协议']),
            ('VRU', ['Virtual Running Unit虚拟运行单元']),
            ('VXLAN', ['Virtual Extensible Local Area Network虚拟可扩展局域网']),
            ('VoIP', ['Voice over Internet Protocol在IP协议上传送语音']), ('VoLTE', ['Voice over LTELTE语音']),
            ('VoNR', ['Voice over New Radio新空口承载语音']), ('VoWiFi', ['Voice over WiFi基于WiFi的语音业务']),
            ('WAF', ['Web Application FirewallWeb应用防火墙']), ('WB', ['Wideband\xa0宽频带/宽带']),
            ('WCDMA', ['Wideband Code Division Multiple Access宽带码分多址']), ('WEB', ['Web环球网']),
            ('WLAN', ['Wireless Local Area Network无线局域网']), ('WUS', ['Wake Up Signal唤醒信号']),
            ('WiFi', ['Wireless Fidelity无线保真']), ('XDR', ['x(Application) Data Record应用数据记录']),
            ('XRES', ['Expected User Response预期的用户响应']), ('XUDT', ['Enhanced Unit Data增强的单位数据']),
            ('XUDTS', ['Enhanced Unit Data Service加强单元数据服务']), ('ZDB', ['ZIP Database压缩数据库']),
            ('ZENIC', ['ZTE Elastic Network Intelligent Controller中兴通讯弹性网络智能控制器']),
            ('ZTE', ['Zhongxing Telecommunications Equipment中兴通讯']),
            ('e1xCSFB', ['Evolved 1x Circuit Switched Fallback演进的1x电路交换回落']),
            ('eAN', ['eHRPD Access Network演进的高速分组数据接入网']),
            ('eDECOR', ['Enhancements of Dedicated Core Network增强专用核心网']),
            ('eDRX', ['extended Idle Mode DRX演进的DRX']),
            ('eHRPD', ['evolved High Rate Packet Data演进的高速分组数据']),
            ('eMBB', ['Enhanced Mobile Broadband增强移动宽带']),
            ('eMBMS', ['Evolved Multimedia Broadcast Multicast Service演进的多媒体广播多播业务']),
            ('eMLPP', ['enhanced Multi-Level Precedence and Pre-emption\t增强型多级优先和占先业务']),
            ('eMSC', ['Enhanced Mobile Switching Center增强移动交换中心']),
            ('eMTC', ['Enhanced Machine Type Communication增强机器类通信']),
            ('eNB', ['E-UTRAN NodeBE-UTRAN基站', 'Evolved Node B演进型基站']), ('eNodeB', ['Evolved NodeB演进的NodeB']),
            ('eSRVCC', ['enhanced SRVCC增强SRVCC']), ('iFC', ['initial Filter Criteria初始过滤规则']),
            ('iSAC', ['Integrated Server Administrator Controller服务器管理控制器']),
            ('iTop', ['Intelligent Traffic Operation Platform智能流量经营平台']),
            ('mMTC', ['Massive Machine Type Communication海量机器类通信']), ('rSRVCC', ['reverse SRVCC反向SRVCC']),
            ('uMAC', ['unified Mobile Access Controller统一的移动性接入控制器']),
            ('vFW', ['virtual Firewall虚拟防火墙']), ('vGSU', ['Virtualized General Service Unit虚拟化通用业务子单元']),
            ('xGW', ['Extendable Gateway综合接入网关'])]
    rec = get_rec(question, dict)
    return dfs([], 0, rec, "")

# import os
# import pprint
# import sys
# from typing import List
# import xml.etree.ElementTree as ET
# from bs4 import BeautifulSoup
# import markdown
# def prt(treeNode,num,data):#这个是输出看看的函数
#     data.append(f"前提信息：\n{treeNode.fa}+\n 本节信息：\n+{treeNode.content}")
#     # treelist[treeNode.information]="前提信息：\n"+treeNode.fa+"\n 本节信息：\n"+treeNode.content
#     for son in treeNode.sons:
#         prt(son,num+1,data)

# def buildtree(xmlnode,treenode,dir_documents):
#     for node in xmlnode.findall('node'):
#         # path = "C:\\Users\chy\Desktop\\"+cate+"\documents\\"+node.get('url')
#         path = os.path.join(dir_documents,"documents",node.get("url"))
#         txt=extract_text_from_html(path)
#         newnode=Tree(txt.splitlines()[0])
#         idx = txt.find("子主题：")
#         if idx != -1:
#              newnode.content=txt[:idx]
#         else:
#             newnode.content = txt
#         treenode.append(newnode)
#         newnode.fa=treenode.fa+'\n'+treenode.content
#         buildtree(node, newnode)

# def extract_text_from_html(html_file):
#     try:
#         with open(html_file, 'r', encoding='utf-8') as file:
#             html_content = file.read()
#     except:
#         with open(html_file, 'r', encoding='gbk') as file:
#             html_content = file.read()
#     # 使用 BeautifulSoup 解析 HTML
#     soup = BeautifulSoup(html_content, 'html.parser')
#     text = ""
#     for string in soup.stripped_strings:
#         text += string + "\n"
#     return text

# class Tree:
#     def __init__(self, information: str) -> None:
#         self.information: str = information
#         self.sons: List[Tree] = []
#         self.content: str=""
#         self.fa: str = ""
#     def append(self,tree:'Tree'):
#         self.sons.append(tree)
# def parse_html_to_list_str(total_dir:str) -> list[str]:
#     # 设置你想要列出子文件夹的目录路径
#     directory_path = total_dir
#     # 使用os.listdir()获取目录下的所有文件和文件夹
#     entries = os.listdir(directory_path)
#     # 使用os.path.isdir()检查每个条目是否是文件夹
#     sonsDir = [entry for entry in entries if os.path.isdir(os.path.join(directory_path, entry))]
#     data = []
#     for dir_name in sonsDir:
#         nodetree = ET.parse(os.path.join(total_dir,dir_name,"nodetree.xml"))
#         root = nodetree.getroot()
#         noderoot=Tree(dir_name)
#         buildtree(root,noderoot,os.path.join(total_dir,dir_name))
#         prt(noderoot,0,data)
#     return data


# # demo中的读取方法
# def read_txt_files(dir_path):
#     txt_strings = []
#     # 递归遍历目录
#     for root, _, files in os.walk(dir_path):
#         for file_name in files:
#             if file_name.endswith(".txt"):
#                 file_path = os.path.join(root, file_name)
#                 with open(file_path, 'r', encoding='utf-8') as file:
#                     txt_content = file.read()
#                     # print(txt_content)
#                     txt_strings.append(txt_content)


# if __name__ == "__main__":
#     # cate="umac" #目前正在处理哪个文件夹就写啥
#     # nodetree = ET.parse(f"../data/{cate}")
#     # root = nodetree.getroot()
#     # noderoot=Tree(cate)
#     # buildtree(root,noderoot)
#     # treelist={}
#     # prt(noderoot,0)
#     # with open("C:\\Users\chy\Desktop\\"+cate+".txt", 'w', encoding='utf-8') as file:
#     #     file.write(str(treelist))
#     data = parse_html_to_list_str("../sourceData/data")
