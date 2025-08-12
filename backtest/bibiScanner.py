rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.csvDump import load_csv_to_dict
from modules.aiztradingview import GetCloseJP
from modules.loadPickle import LoadPickle
from modules.movingAverage import SmaArr

from modules.csvDump import load_csv_to_dict
from modules.data import GetDataLts
from modules.csvDump import LoadCsv
# from modules.aiztradingview import GetAttr, GetAttrJP
import numpy as np
from modules.rsi import GetRsi
from concurrent.futures import ThreadPoolExecutor, as_completed

# floatDictJP = GetAttrJP("float_shares_outstanding")
# totalShareDictJP = GetAttrJP("total_shares_outstanding_fundamental")

def GetZandakaHiritsu(symbol, zandakaDict, floatDictJP, totalShareDictJP):
    zandaka = zandakaDict[symbol]
    return zandaka[0][7] / zandaka[0][1]
    urizan_kashitsukezan = zandaka[0][7] - zandaka[0][1]

    floatShares = 0
    if symbol in floatDictJP:
        floatShares = floatDictJP[symbol]
    elif symbol in totalShareDictJP:
        floatShares = totalShareDictJP[symbol]
    zandakaHiritsuTofloatShares = urizan_kashitsukezan/floatShares
    return zandakaHiritsuTofloatShares


def GetBias(npArr, period):
    closeArr = npArr[:,3]
    sma25 = SmaArr(closeArr, period)
    bias25 = (closeArr-sma25)/closeArr
    return bias25

similarCompanyDict = load_csv_to_dict(f"{rootPath}/data/SimilarCompanyJP.csv")

rironkabukaPath = f"{rootPath}/backtest/pickle/pro/compressed/rironkabuka.p"
shisannkachiPath = f"{rootPath}/backtest/pickle/pro/compressed/shisannkachi.p"
ryuudoumeyasuPath = f"{rootPath}/backtest/pickle/pro/compressed/ryuudoumeyasu.p"
# financialScorePath = f"{rootPath}/backtest/pickle/pro/compressed/financialScore.p"
financialDetailPath = f"{rootPath}/backtest/pickle/pro/compressed/financialDetail.p"
shuuekiPath = f"{rootPath}/backtest/pickle/pro/compressed/shuueki.p"
shijouPath = f"{rootPath}/backtest/pickle/pro/compressed/shijou.p"
shijousizePath = f"{rootPath}/backtest/pickle/pro/compressed/shijousize.p"
gyoushuPath = f"{rootPath}/backtest/pickle/pro/compressed/gyoushu.p"
gennhairiskPath = f"{rootPath}/backtest/pickle/pro/compressed/gennhairisk.p"
gerakuriskPath = f"{rootPath}/backtest/pickle/pro/compressed/gerakurisk.p"
zandakaPath = f"{rootPath}/backtest/pickle/pro/compressed/zandaka.p"
kaitennritsuPath = f"{rootPath}/backtest/pickle/pro/compressed/dekidakakaitennritsu.p"
haitoukakutsukePath = f"{rootPath}/backtest/pickle/pro/compressed/haitoukakutsuke.p"
haitourimawarirankPath = f"{rootPath}/backtest/pickle/pro/compressed/haitourimawarirank.p"
haitourimawariPath = f"{rootPath}/backtest/pickle/pro/compressed/haitourimawari.p"
kiboriskPath = f"{rootPath}/backtest/pickle/pro/compressed/kiborisk.p"
fusairiskPath = f"{rootPath}/backtest/pickle/pro/compressed/fusairisk.p"
inventoryPath = f"{rootPath}/backtest/pickle/pro/compressed/inventoryJP.p"
netIncomePath = f"{rootPath}/backtest/pickle/pro/compressed/netIncomeJP.p"
operatingPath = f"{rootPath}/backtest/pickle/pro/compressed/operatingJP.p"
investementPath = f"{rootPath}/backtest/pickle/pro/compressed/investementJP.p"
freeCashFlowPath = f"{rootPath}/backtest/pickle/pro/compressed/freeCashFlowJP.p"
treasurySharesPath = f"{rootPath}/backtest/pickle/pro/compressed/treasurySharesJP.p"
ordinarySharesPath = f"{rootPath}/backtest/pickle/pro/compressed/ordinarySharesJP.p"
totalSharesPath = f"{rootPath}/backtest/pickle/pro/compressed/totalSharesJP.p"
interestExpensePath = f"{rootPath}/backtest/pickle/pro/compressed/interestExpenseJP.p"
operatingIncomePath = f"{rootPath}/backtest/pickle/pro/compressed/operatingIncomeJP.p"
# shuuekiriskPath = f"{rootPath}/backtest/pickle/pro/compressed/shuuekirisk.p"
# haitouseikouriskPath = f"{rootPath}/backtest/pickle/pro/compressed/haitouseikourisk.p"
# shisannriskPath = f"{rootPath}/backtest/pickle/pro/compressed/shisannrisk.p"
dataPathUS = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeUS.p"
dataPathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeJP.p"
ignorePathJP = f"{rootPath}/data/IgnoreJPLts.csv"

rironkabukaDict, financialScoreDict, financialDetailDict = {}, {}, {}
rironkabukaDict = LoadPickle(rironkabukaPath)
shisannkachiDict = LoadPickle(shisannkachiPath)
ryuudoumeyasuDict = LoadPickle(ryuudoumeyasuPath)
# financialScoreDict = LoadPickle(financialScorePath)
financialDetailDict = LoadPickle(financialDetailPath)
shuuekiDict = LoadPickle(shuuekiPath)
shijouDict = LoadPickle(shijouPath)
shijousizeDict = LoadPickle(shijousizePath)
gyoushuDict = LoadPickle(gyoushuPath)
gennhairiskDict = LoadPickle(gennhairiskPath)
gerakuriskDict = LoadPickle(gerakuriskPath)
zandakaDict = LoadPickle(zandakaPath)
kaitennritsuDict = LoadPickle(kaitennritsuPath)
haitoukakutsukeDict = LoadPickle(haitoukakutsukePath)
haitourimawarirankDict = LoadPickle(haitourimawarirankPath)
kiboriskDict = LoadPickle(kiboriskPath)
haitourimawariDict = LoadPickle(haitourimawariPath)
fusairiskDict = LoadPickle(fusairiskPath)
inventoryDict = LoadPickle(inventoryPath)
netIncomeDict = LoadPickle(netIncomePath)
operatingDict = LoadPickle(operatingPath)
investementDict = LoadPickle(investementPath)
treasurySharesDict = LoadPickle(treasurySharesPath)
ordinarySharesDict = LoadPickle(ordinarySharesPath)
totalSharesDict = LoadPickle(totalSharesPath)
interestExpenseDict = LoadPickle(interestExpensePath)
operatingIncomeDict = LoadPickle(operatingIncomePath)
# freeCashFlowDict = LoadPickle(freeCashFlowPath)
# shuuekiriskDict = LoadPickle(shuuekiriskPath)
# haitouseikouriskDict = LoadPickle(haitouseikouriskPath)
# shisannriskDict = LoadPickle(shisannriskPath)
dataDictUS = LoadPickle(dataPathUS)
dataDictJP = LoadPickle(dataPathJP)
ignoreListJP = LoadCsv(ignorePathJP)

financialScoreDict = dict(sorted(financialScoreDict.items(), key=lambda item: item[1], reverse=True))
# zandakaHiritsu = GetZandakaHiritsu("7721",zandakaDict,floatDictJP,totalShareDictJP)
# print(zandakaHiritsu)
# print(gyoushuDict["2788"])
# dataDict = dataDictUS
# dataDict.update(dataDictJP)
# print(freeCashFlowDict["9827"])
# totalShares = totalSharesDict[symbol]
# treasuryShares = treasurySharesDict[symbol]
# print((treasuryShares[0]/totalShares[0])/(treasuryShares[1]/totalShares[1]))
# print(zandakaDict[symbol][0][7]/zandakaDict[symbol][0][1])
# urizan = zandakaDict[symbol][0][3]
# print(urizan)
# urizan1 = zandakaDict[symbol][0][3]
# if urizan1 < 1: urizan1 = 1
# urizan2 = zandakaDict[symbol][1][3]
# if urizan2 < 1: urizan2 = 1
# print(zandakaDict[symbol][0][1]/urizan1)
# print(zandakaDict[symbol][1][1]/urizan2)
# symbol = "9827"
# zandaka = zandakaDict[symbol]
# print(ordinarySharesDict[symbol][0])
# print((zandaka[0][1]-zandaka[0][3])/ordinarySharesDict[symbol][0])
# print(zandaka[0][1]/ordinarySharesDict[symbol][0])
# print(zandaka[1][1]/ordinarySharesDict[symbol][0])
# sys.exit()

# @njit
def split_list_average_high_low(lst):
    # Calculate the average of all values in the list
    average = np.mean(lst)
    
    # Filter high values and calculate the average
    high_values = lst[lst > average]
    average_high = np.mean(high_values)
    
    # Filter low values and calculate the average
    low_values = lst[lst < average]
    average_low = np.mean(low_values)
    
    return np.array([average_high, average_low])

# @njit
def round_down_to_multiple_of_10(number):
    return (number // 10) * 10

# @njit
def round_up_to_multiple_of_100(number):
    remainder = number % 100
    if remainder == 0:
        return number
    else:
        return number + (100 - remainder)

def Backtest(dataDict, length, similarCompanyDict, 
    financialDetailDict, shuuekiDict, shisannkachiDict, 
    ryuudoumeyasuDict, shijouDict, gyoushuDict, 
    shijousizeDict, gennhairiskDict, gerakuriskDict, 
    kaitennritsuDict, haitoukakutsukeDict, 
    haitourimawarirankDict, haitourimawariDict, 
    kiboriskDict, fusairiskDict,
    inventoryDict, netIncomeDict,
    operatingDict, investementDict,
    treasurySharesDict, totalSharesDict,
    interestExpenseDict, operatingIncomeDict):
    balance = 1
    attrDict = {2: [-0.12853470437017994, 0.10566356720202874], 3: [-0.1677577741407529,
0.21712158808932994], 4: [-0.18214716525934863, 0.3202119606358819], 5: [-0.18328996819890142, 0.39698814482537653], 6: [-0.18568340139322603, 0.46295088079038116], 7: [-0.18279495833046358, 0.5218150087260035], 8: [-0.17643486182812027, 0.5719972958762112],
9: [-0.17469162518935294, 0.6138186304750154], 10: [-0.18246274055852987,
0.6448692152917505], 11: [-0.18952401651814824, 0.6704980842911877], 12: [-0.2109244675485898, 0.6951239267779038], 13: [-0.22575544624033728, 0.7180095983834303], 14: [-0.23164097914777879, 0.7572931137130384], 15: [-0.23657818880614945, 0.8039358600583092], 16: [-0.24340912261124284, 0.8484580961368687], 17: [-0.24566088117489987, 0.8905494505494507], 18: [-0.24779961046325294, 0.9287347883784624], 19: [-0.2477229472539423, 0.9648745129029621], 20: [-0.2563988000255314, 0.9998946037099495], 21: [-0.2562473399404146, 1.0326208936951642], 22: [-0.2506286182094615, 1.0624490501716854],
23: [-0.24007373794668177, 1.0883077732851638], 24: [-0.22587075696328704, 1.1131760283984131], 25: [-0.2120530318525818, 1.13523732361083], 26: [-0.20734558797079025, 1.1563442458149396], 27: [-0.2009463281768341, 1.17529296875], 28: [-0.19534773320674104, 1.194275802254987], 29: [-0.18801724565141972, 1.212561066323556], 30: [-0.17985193787196982, 1.2323529411764707], 31: [-0.17191981592964978, 1.2506313131313131], 32: [-0.16353093578434397, 1.2675330495182613], 33: [-0.154549576783555, 1.2853519224803374], 34: [-0.14604510565154258, 1.301969599657461], 35: [-0.13707835750338182, 1.317294439889042], 36: [-0.12891113892365463, 1.3324341858162323], 37: [-0.12715287517531557, 1.3467426546779424], 38: [-0.12574375247917496, 1.360847357736887], 39: [-0.1253483379778397, 1.3745768422403697], 40: [-0.12477885315849724, 1.3877685846415202], 41:
[-0.12311174406184827, 1.3998982015609096], 42: [-0.12203124417434093, 1.4113464447806354], 43: [-0.1267603667983307, 1.4219689211451978], 44: [-0.14113227797155886, 1.431806597247506], 45: [-0.15739012933530663, 1.4412820036310094], 46: [-0.16860241233245962, 1.450999663034932], 47: [-0.17410417748577914, 1.4603426395939085], 48:
[-0.17755952801526179, 1.4690287077448558], 49: [-0.1849857676875064, 1.4779462715207077], 50: [-0.1874776626161544, 1.4865027780689801], 51: [-0.18771140520836754, 1.4947795823665895], 52: [-0.1870547658189085, 1.501457725947522], 53: [-0.1864133187035786, 1.5108606096921577], 54: [-0.18606458029026943, 1.520323203502601], 55: [-0.18601812578194135, 1.5293561638855562], 56: [-0.18469451059656988, 1.5377946550118222], 57: [-0.1822860692347889, 1.5461104768182299], 58: [-0.17966016019908232, 1.5541914222057187], 59: [-0.17725704427832084, 1.56181279390396], 60: [-0.17312318854306774, 1.5694844104404349], 61: [-0.16853248395709403, 1.5760020474929337], 62: [-0.16426566364958636, 1.5809246969780069], 63: [-0.1619353246112071, 1.5864083341446793], 64: [-0.16143614865777553, 1.5911069386361696], 65: [-0.1614873790883863, 1.595677291046268], 66: [-0.16284543631767062, 1.600124571784491], 67: [-0.1638791683820502, 1.6044270086450607], 68: [-0.16442868001013425, 1.6081683393468968], 69: [-0.1640924872817498, 1.6123587098576375], 70: [-0.16414995240127372, 1.6157724233681579], 71: [-0.16217224515616255, 1.6190985351439098], 72: [-0.1597892254758066, 1.6227431105479888], 73:
[-0.15741835172419258, 1.626845433943658], 74: [-0.15461440618080746, 1.629026671285071], 75: [-0.15174858333268554, 1.6310802566140994], 76: [-0.14922460716853242, 1.6341891114338163], 77: [-0.1514794095841478, 1.639177399252181], 78: [-0.1533559051981677, 1.6454501581854257], 79: [-0.15487290214937682, 1.6509129492904195], 80: [-0.1570807153214113, 1.6567723191627142], 81: [-0.15871553805107352, 1.6624428353658536], 82: [-0.16080370555833756, 1.6683415792768148], 83: [-0.16314134188455845, 1.6737148580741548],
84: [-0.16563895385923882, 1.67893608975167], 85: [-0.168212832176203, 1.6840541844868615], 86: [-0.1709071611781008, 1.6895153647743284], 87: [-0.17385875246834703, 1.6956205809833282], 88: [-0.17700557700557698, 1.7009365446516669], 89: [-0.17961945031712478, 1.706348506822862], 90: [-0.18238644256146688, 1.7113383238999453], 91: [-0.18505230870351103, 1.7169201236733826], 92: [-0.18762151652624762, 1.7224240911997257], 93: [-0.18986094091320793, 1.7276626658732064], 94: [-0.19167959607647203, 1.732537208251308], 95: [-0.19345207186623736, 1.7370350969093769], 96: [-0.1951181990667145, 1.7415774304484264], 97: [-0.19719058466211084, 1.7459588085665054], 98: [-0.19941041271110224, 1.7504677666269772], 99: [-0.2013568521031208, 1.755041431399868], 100: [-0.2032163742690058, 1.7597390792143286], 101: [-0.20472440944881892, 1.7643792145973822], 102: [-0.20627290466898296, 1.7689237328144896], 103: [-0.20784138482525044, 1.7730600604435363], 104: [-0.20961256885211615, 1.7772070309751324], 105: [-0.2117768595041322, 1.7815200547264376], 106: [-0.21408489025938696, 1.7858033240997229], 107: [-0.21633667801469272, 1.7898660254208176], 108: [-0.2184131902179927, 1.793712680971726], 109: [-0.22073066748289208, 1.7976504484031974], 110: [-0.22290874524714832, 1.8015274347686032], 111: [-0.22495302357362487, 1.8053637193071255], 112: [-0.22665653110350945, 1.8087704690535664], 113: [-0.22837095662705956, 1.8118115295845574], 114: [-0.2300797224172828, 1.8152452594453194], 115: [-0.23178280321137468, 1.8181360299103078], 116: [-0.23337173346268114, 1.821235852805086], 117: [-0.23483530329393412, 1.8244150986603567], 118: [-0.23638954305277946, 1.8275653046920877], 119: [-0.23755314771636263, 1.8306694245957127], 120: [-0.23869390605901863, 1.833869532479978], 121: [-0.23994390871720003, 1.8364980727416484], 122: [-0.24095285208721792, 1.839610664409649], 123: [-0.2422284185538264, 1.8420562340935938], 124: [-0.24314032926419535, 1.8444664736425345], 125: [-0.244426781027025, 1.84675672269664], 126: [-0.24582662176014053, 1.8490821233011385], 127: [-0.24693999673599654, 1.8515770602957098], 128: [-0.2477624815786636, 1.8541043614164763], 129: [-0.2485436893203884, 1.8577974956948131], 130: [-0.24936431699392564, 1.8610614952794078], 131: [-0.2500393914459287, 1.8642004470767175], 132: [-0.2505859680191676, 1.8670360110803321], 133: [-0.2509429737689672, 1.8696223186214034], 134: [-0.2514222260186214, 1.8721745908028058], 135: [-0.25184306414710617, 1.8747580170019358], 136: [-0.2523829536858031, 1.877308001070377], 137: [-0.25292665843978257, 1.8798092368365664], 138: [-0.25363457435371567,
1.8827068414128685], 139: [-0.2543065262328969, 1.8856158201362108], 140:
[-0.25517376024990235, 1.8885046972860127], 141: [-0.2562907284340925, 1.8914988814317675], 142: [-0.25743619266935325, 1.8944569771189173], 143: [-0.2588559745138129, 1.8973796328923342], 144: [-0.26018099547511314, 1.9002982666567596], 145: [-0.2617130934400448, 1.903213042101931], 146: [-0.2630360285264425, 1.9056973841538878],
147: [-0.26425750757645333, 1.9083037045532742], 148: [-0.26551425839644266, 1.9110453454683038], 149: [-0.26666164960866945, 1.9133499234894975], 150: [-0.26797600214906125, 1.9156422864167182], 151: [-0.26952778270903605, 1.9174621599743407], 152: [-0.2709243993311233, 1.9197922677437969], 153: [-0.2722869485534756, 1.9217279726261762], 154: [-0.27418169239417134, 1.9235679304462665], 155: [-0.27594925859261166, 1.9253136795619679], 156:
[-0.2780026608543041, 1.927270659553112], 157: [-0.2802708499810742, 1.929550941336703], 158: [-0.28264582147369594, 1.9321642688783045], 159: [-0.28532941127957, 1.934535215103442], 160: [-0.28799858470666684, 1.936766654736455], 161: [-0.2903091004677622, 1.9388040749184725], 162: [-0.29295409954219664, 1.9409316609741396], 163:
[-0.29520270806336446, 1.9429661593503047], 164: [-0.29686639569948864, 1.944908938634718], 165: [-0.2988577443374527, 1.9472884052377413], 166: [-0.2999754974659221, 1.9496291718170577], 167: [-0.3010674243587774, 1.9521380659586363], 168: [-0.30206321780668766, 1.9546760589489294], 169: [-0.30300049188391537, 1.9569974273147253], 170: [-0.30395041632755276, 1.959485123443765], 171: [-0.3047397607738791, 1.9618802459162297], 172: [-0.30587814239346406, 1.9639821272885791], 173: [-0.3068213843722047, 1.965928649840305], 174: [-0.30751536542323377, 1.966175545773066], 175: [-0.30838399342526673, 1.9664196604446116], 176: [-0.30937323749295, 1.9667401037595054], 177: [-0.31030743565300284, 1.9670569943151448], 178: [-0.31064948600123166, 1.967605039801782], 179: [-0.31123061354169124, 1.9681471609901031], 180: [-0.31168360366260095, 1.9684512428298282], 181: [-0.31237075074935516, 1.9687520259319289], 182: [-0.3129617657923901, 1.9691771988651021], 183: [-0.31291478173008475, 1.9699026261434047], 184: [-0.3126171000319883, 1.9703425158666688], 185: [-0.3122363828601962, 1.970802919708029], 186:
[-0.3119449755082186, 1.971508676214291], 187: [-0.31174941191036276, 1.9720702912328605], 188: [-0.3114941370157578, 1.9726261405774763], 189: [-0.3112029957871743, 1.9731763125823865], 190: [-0.3109452460434527, 1.9734633703787703], 191: [-0.3107432544280748, 1.9741379310344827], 192: [-0.310475102686318, 1.9772633324137547], 193: [-0.3101718258132214, 1.9927699122700764], 194: [-0.3099689998368413, 2.008276492126398], 195: [-0.3096859403925475, 2.02378307198272], 196: [-0.30950226244343887, 2.039289651839041], 197: [-0.3092536993351919, 2.054796231695363], 198: [-0.30908120798207234, 2.0703028115516844], 199: [-0.30897641474370546, 2.0858093914080063], 200: [-0.30904788065756666, 2.101315971264328], 201: [-0.3091331448332405, 2.1168225511206495], 202: [-0.3093836583198285, 2.132329130976972]}
    smaDict = {}
    for i in range(203, length):
        topPefToAvg = 1
        topSymbol = ""
        topSimilarCompanyMin = 1
        for symbol, npArr in dataDict.items():
            if npArr[i-1][4] >= npArr[i-2][4]: continue
            if npArr[i-1][3] < 327: continue
            if npArr[i-1][3] / npArr[i-1][0] < 0.8540462428: continue
            if npArr[i-1][3] / npArr[i-2][3] < 0.7722095672: continue
            # if npArr[i-1][4] < 15700: continue
            # if npArr[i-1][3] * npArr[i-1][4] < 23204600: continue
            # if npArr[i-1][3] / npArr[i-1][0] > 1.22734375: continue
            closeArr = npArr[:,3]
            if symbol not in smaDict:
                smaDict[symbol] = {}
                for period in attrDict.keys():
                    smaDict[symbol][period] = SmaArr(closeArr, period)
            
            for period in attrDict.keys():
                sma = smaDict[symbol][period][i-1]
                bias = (npArr[i-1][3]-sma)/sma
                attrLimit = attrDict[period]
                if bias < attrLimit[0]: continue
                if bias > attrLimit[1]: continue
                
                    
            # if symbol not in ryuudoumeyasuDict: continue
            # if ryuudoumeyasuDict[symbol][0] <= 100: continue

            
            # if (
            #     npArr[i-1][4] <= npArr[i-2][4] and
            #     npArr[i-2][4] <= npArr[i-3][4] and
            #     npArr[i-3][4] <= npArr[i-4][4] and
            #     npArr[i-1][3] <= npArr[i-1][0] and
            #     npArr[i-2][3] <= npArr[i-2][0] and
            #     npArr[i-3][3] / npArr[i-4][0] > 1.1
            # ): continue
            
            # if (
            #     npArr[i-3][3] / npArr[i-3][0] > 1.21 and
            #     npArr[i-3][4] / npArr[i-4][4] > 7 and
            #     # npArr[i-1][3] < npArr[i-2][2] and
            #     # npArr[i-1][3] < npArr[i-3][3] and
            #     # npArr[i-1][1] < npArr[i-2][1] and
            #     # npArr[i-1][3] / npArr[i-1][0] < 0.91 and
            #     # abs(npArr[i-3][3] - npArr[i-3][0]) / 
            #     # abs(npArr[i-4][3] - npArr[i-4][0]) > 20 and
            #     npArr[i-3][0] < npArr[i-4][2]
            # ): continue
            
            
            # similarPerfomanceList = np.empty(0)
            # similarCompanyList = similarCompanyDict[symbol]
            # similarPerfomanceList = np.array([dataDict[t][i][0] / dataDict[t][i-1][3] for t in similarCompanyList if t in dataDict])
            # if len(similarPerfomanceList) < 1: continue
            # similarCompanyMin = np.min(similarPerfomanceList)
            # if npArr[i-1][3] * similarCompanyMin - npArr[i][0] < 16: continue
            performance = npArr[i-1][3] / npArr[i-1][0]
            # pefToAvg = performance/similarCompanyMin
            if performance > topPefToAvg:
                topPefToAvg = performance
                topSymbol = symbol
            #     topSimilarCompanyMin = similarCompanyMin
        if topSymbol == "": continue
        npArr = dataDict[topSymbol]
        op = npArr[i][0]
        tp = npArr[i][3]
        # shisannkachiTp = shisannkachiDict[topSymbol] * 7.7
        # target = npArr[i-1][3] * topSimilarCompanyMin * 0.99
        # if npArr[i][1] > npArr[i-1][3] * target:
        #     tp = target
        gain = tp / op
        balance *= gain
        print(topSymbol, balance)

def GetSimilarCompanyDict(industryDict, dataDict):
    grouped_dict = {}
    for key, value in industryDict.items():
        if key not in dataDict: continue
        if value not in grouped_dict:
            grouped_dict[value] = [key]
        else:
            grouped_dict[value].append(key)
    new_dict = {}
    for industry, symbols in grouped_dict.items():
        for symbol in symbols:
            filtered_symbols = [s for s in symbols if s != symbol and len(symbols) >= 2]
            if len(filtered_symbols) >= 3:
                new_dict.setdefault(symbol, []).extend(filtered_symbols)
    return new_dict

# @njit
def BacktestWR(npArr):
    win = 0
    loss = 0
    winList = np.empty(0)
    lossList = np.empty(0)
    for i in range(1, len(npArr)):
        if npArr[i-1][4] >= npArr[i-2][4]: continue
        if npArr[i][3] > npArr[i][0]:
            win += 1
            winList = np.append(winList, npArr[i][3]-npArr[i][0])
        else:
            loss += 1
            lossList = np.append(lossList, npArr[i][0]-npArr[i][3])
    wr = win / (win+loss)
    if wr * np.mean(winList) <= (1-wr) * np.mean(lossList):
        wr = 0
    return wr

def HandleBacktestWR(dataDict, symbol):
    npArr = dataDict[symbol]
    wr = BacktestWR(npArr)
    return [symbol, wr]

group = ""
# group = "US"
if group == "US":
    length = len(dataDictUS["AAPL"])
    dataDict = dataDictUS
else:
    length = len(dataDictJP["9101"])
    dataDict = dataDictJP

# import itertools
# count = 3945
# industryDict = dict(itertools.islice(industryDict.items(), count))

# similarCompanyDict = GetSimilarCompanyDict(industryDict, dataDict)

cleanDataDict = {}
ignoreList = [
    "Electronic Production Equipment", 
    "Telecommunications Equipment", 
    "Environmental Services",
    "Computer Peripherals",
    "Biotechnology",
    "Commercial Printing/Forms",
    "Trucks/Construction/Farm Machinery",
    "Auto Parts: OEM",
    "Tools & Hardware",
    "Recreational Products",
    "Metal Fabrication",
    "Forest Products",
    "Industrial Specialties",
    "Other Consumer Specialties",
    "Movies/Entertainment",
    "Medical Specialties",
    "Office Equipment/Supplies",
    "Electronics/Appliances",
    "Pulp & Paper",
    "Electrical Products",
    "Alternative Power Generation"
]

closeDictJP = GetCloseJP()

def get_unique_values(dictionary):
    unique_values = []
    
    for value in dictionary.values():
        if value not in unique_values:
            unique_values.append(value)
    
    return unique_values

# gyoushuList = get_unique_values(gyoushuDict)
# print(gyoushuList)
gyoushuList = ['情報通信', '電機', '保険', '精密', '輸送用機器', '卸売業', '機械', 
'不動産', 'その他製造', '銀行', '小売業', '医薬品', 'サービス', 
'化学', '鉱業', '建設', '陸運', '食品', '鉄鋼', 'ゴム', 'その他金融', '海運', '電力・ガス', 
'証券', '石油', '空運', '非鉄金属', '窯業', '繊維', '金属製品', '紙・パルプ', '倉庫・運輸', 
'水産・農林']

bibi = [
"7686",
"4485",
"5258",
"8031",
"8058",
"6526",
"7203",
"3561",
"3099",
"3399",
"4911",
"6080",
"7014",
"3697",
"8002",
"6857",
"8766",
"6027",
"7373",
"8001",
"4005",
"4063",
"4185",
"4186",
"8316",
"8424",
"4046",
"6723",
"9432",
"8411",
"8306",
"6890",
"5533",
"3498",
"5401",
"5406",
"9107",
"8750",
"8411",
"4487",
"3083",
"6104",
"7388",
"2222",
"3498",
"5137",
"4413",
"4176",
"4570",
"2884",
"7373",
"7369",
"2651",
"6146",
"9158",
"6305",
"3758",
"4617",
"9552",
"3496",
"4739",
"8136",
"6418",
"6457",
"8002",
"7011",
"5344",
"5122",
"3186",
"4886",
"7687",
"4933",
"7267",
"7246",
"5310",
"5202",
"2340",
"4691",
"7048",
"9346",
"7214",
"3452",
"7532",
"7611",
"6857",
"8306",
"7130",
"7011",
"3097"
]

bibiGyoushu = [
    "サービス",
    "不動産",
    "保険",
    "化学",
    "医薬品",
    "卸売業",
    "小売業",
    "情報通信",
    "機械",
    "窯業",
    "輸送用機器",
    "銀行",
    "電機",
    "食品"
]
bibiGyoushu = ['その他金融', 'ゴム', 'サービス', '不動産', 
    '保険', '化学', '医薬品', '卸売業', '小売業', 
    '情報通信', '機械', '海運', '窯業', '輸送用機器', 
    '鉄鋼', '銀行', '電機', '食品']
shijousizeIgnoreList = ['地方株', 'ＰＲＭ小型']
bibiTotalShares = []
for symbol in dataDict.keys():
    if symbol not in gyoushuDict: continue
    gyoushu = gyoushuDict[symbol]
    if symbol not in shijousizeDict: continue
    shijouSize = shijousizeDict[symbol]
    if shijouSize in shijousizeIgnoreList: continue
    if symbol not in ryuudoumeyasuDict: continue
    if symbol not in totalSharesDict: continue
    totalShares = totalSharesDict[symbol]
    if totalShares[0] > 16314987460: continue


    npArr = dataDict[symbol]
    if len(npArr) < length: continue
    cleanDataDict[symbol] = npArr


bibiTotalShares.sort()
print(bibiTotalShares)
# sys.exit()
Backtest(
    cleanDataDict, length, similarCompanyDict, 
    financialDetailDict, shuuekiDict, shisannkachiDict, 
    ryuudoumeyasuDict, shijouDict, gyoushuDict, 
    shijousizeDict, gennhairiskDict, gerakuriskDict, 
    kaitennritsuDict, haitoukakutsukeDict, 
    haitourimawarirankDict, haitourimawariDict, 
    kiboriskDict, fusairiskDict,
    inventoryDict, netIncomeDict,
    operatingDict, investementDict,
    treasurySharesDict, totalSharesDict,
    interestExpenseDict, operatingIncomeDict)
