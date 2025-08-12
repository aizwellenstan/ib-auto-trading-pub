rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.aiztradingview import GetClose, GetAttr, GetGainable
import yfinance as yf
from modules.csvDump import DumpCsv, DumpDict, LoadDict
closeDict = GetClose()
perfDict = GetAttr("Perf.All")
industryDict = GetAttr("number_of_employees")

lengthPath = f"{rootPath}/backtest/data/length.csv"
lengthDict = LoadDict(lengthPath,'Length')

def GetLen(symbol, currency = 'USD'):
    try:
        if "." in symbol:
            symbol = symbol.replace(".","-")
        if currency != 'JPY':
            stockInfo = yf.Ticker(symbol)
        else:
            stockInfo = yf.Ticker(symbol+'.T')
        hist = stockInfo.history(period="max")
        print(symbol, len(hist))
        return len(hist)
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return 0

industryAll = {}
industryGain = {}
for symbol, close in closeDict.items():
    if symbol not in perfDict: continue
    if symbol not in industryDict: continue
    if symbol not in lengthDict: continue
    industry = industryDict[symbol]
    length = lengthDict[symbol]
    if length < 1: continue
    lengthDict[symbol] = length
    perf = perfDict[symbol]
    # perf = perfDict[symbol]/length
    if symbol == "TSLA":
        print("TSLA",perf)
    if industry not in industryAll:
        industryAll[industry] = []
    
    v = industryAll[industry]
    v.append(perf)
    industryAll[industry] = v

    if industry not in industryGain:
        industryGain[industry] = []
    
    v = industryGain[industry]
    v.append(perf/length)
    industryGain[industry] = v

industryAvg = {}
for k, v in industryAll.items():
    avg = sum(v) / len(v)
    if avg <= 0: continue
    industryAvg[k] = avg

industryAvgGain = {}
for k, v in industryGain.items():
    avg = sum(v) / len(v)
    if avg <= 0: continue
    industryAvgGain[k] = avg

industryAvg = dict(sorted(industryAvg.items(), key=lambda item: item[1], reverse=True))
print(industryAvg)
industryAvgGain = dict(sorted(industryAvgGain.items(), key=lambda item: item[1], reverse=True))
print(industryAvgGain)

industyrList = []
for k, v in industryAvgGain.items():
    if k not in industryAvg: continue
    industyrList.append(k)
# print(industyrList)
print(industyrList[0],industyrList[1],industyrList[2],industyrList[3],industyrList[4],
industyrList[5],industyrList[6],
industyrList[-1])
industyrList.sort()
print(industyrList[0],industyrList[-1])

gainable = GetGainable()
print(len(gainable))
print(gainable)
# {'Home Improvement Chains': 176981.27205014, 'Managed Health Care': 43579.686683854445, 'Oil & Gas Production': 22074.998012408447, 'Department Stores': 16983.038876961997, 'Airlines': 16350.524682068637, 'Food: Meat/Fish/Dairy': 14384.171447892502, 'Electronics/Appliance Stores': 12677.7856143125, 'Beverages: Non-Alcoholic': 8655.534069946874, 'Industrial Specialties': 8635.006001497224, 'Personnel Services': 7517.542147875862, 'Multi-Line Insurance': 7472.728987935969, 'Railroads': 6719.82819058, 'Tobacco': 6613.769626942857, 'Industrial Machinery': 6401.213065165, 'Steel': 5989.394171422224, 'Drugstore Chains': 5908.6616159000005, 'Specialty Stores': 5728.976683248498, 'Cable/Satellite TV': 5685.654002887273, 'Property/Casualty Insurance': 5528.447265889636, 'Oil Refining/Marketing': 5487.642969126363, 'Beverages: Alcoholic': 5070.415369610769, 'Food: Specialty/Candy': 4852.973726603953, 'Air Freight/Couriers': 4680.035420411051, 'Financial Publishing/Services':
# 4639.367299266666, 'Homebuilding':
# 4609.776471026001, 'Semiconductors': 4528.280965382761, 'Services to the Health Industry': 4493.438936988571, 'Wholesale Distributors': 4399.307424544728, 'Restaurants': 4285.227010446667, 'Insurance Brokers/Services': 4163.366286297894, 'Building Products': 4094.7086628352195, 'Household/Personal Care': 4029.801906712726, 'Aerospace & Defense': 3860.230274636866, 'Telecommunications Equipment': 3761.5361175228827, 'Discount Stores': 3559.2425355875,
# 'Trucking': 3549.909364793182, 'Apparel/Footwear Retail': 3423.099842204063, 'Engineering & Construction': 3366.393924153914, 'Medical Specialties': 3260.3274462766894, 'Information Technology Services': 3122.0809382099997, 'Automotive Aftermarket': 3042.6952679975, 'Other Transportation': 2802.584335558571, 'Apparel/Footwear': 2786.278578521579, 'Electronic Components': 2773.948027618, 'Trucks/Construction/Farm Machinery': 2740.2232525424333, 'Construction Materials': 2656.1997377061543, 'Electronic Equipment/Instruments': 2539.8782398948, 'Agricultural Commodities/Milling': 2426.6022320275606, 'Other Consumer Specialties': 2393.0469803974997, 'Metal Fabrication': 2373.9528873635, 'Home Furnishings': 2301.3218561504546, 'Packaged Software': 2261.385654539274, 'Recreational Products': 2258.9377687369238, 'Computer Processing Hardware': 2093.7240955449997, 'Office Equipment/Supplies': 2089.0395621, 'Containers/Packaging': 2009.9725610150003, 'Data Processing Services': 1734.0932046816665, 'Internet Retail': 1713.0573140196163, 'Forest
# Products': 1679.34391212, 'Chemicals: Specialty': 1677.8239251059322,
# 'Other Consumer Services': 1615.8159464952548, 'Water Utilities': 1521.4753199178574, 'Auto Parts: OEM':
# 1484.357790947805, 'Chemicals: Agricultural': 1433.4241194943477, 'Tools & Hardware': 1379.3170018816666, 'Investment Banks/Brokers': 1375.330809630494, 'Electronic Production Equipment': 1370.0371477750002, 'Medical Distributors': 1347.3089391042856, 'Food Retail': 1308.6053843575, 'Casinos/Gaming': 1190.1304281474997, 'Food: Major Diversified': 1177.1955300599998, 'Investment Managers': 1164.0553551908154, 'Hospital/Nursing Management': 1099.4799286929413, 'Movies/Entertainment': 1090.601075574706, 'Contract Drilling': 1045.3076539712497, 'Electrical Products': 881.9705766173137, 'Regional Banks': 879.3511015400987, 'Miscellaneous Manufacturing': 848.323653681875, 'Electronics Distributors': 791.8116169840001, 'Motor Vehicles': 790.2708539587502, 'Life/Health Insurance': 743.8271290174999, 'Gas Distributors': 656.98233481375,
# 'Wireless Telecommunications': 648.1621105784616, 'Integrated Oil': 622.6498791732691, 'Finance/Rental/Leasing': 598.5980554288487, 'Computer Peripherals': 597.2458794061904,
# 'Hotels/Resorts/Cruise lines': 591.6860804068182, 'Publishing: Newspapers': 586.3166398385714, 'Internet
# Software/Services': 507.43450777551715, 'Major Banks': 488.6409920183224, 'Specialty Insurance': 487.5169742071428, 'Coal': 483.93590170428575, 'Advertising/Marketing Services': 476.29508608666663, 'Biotechnology': 472.5801110599717, 'Miscellaneous Commercial Services': 463.24948508027796, 'Pharmaceuticals: Other': 456.8562322531034, 'Consumer Sundries': 445.72753811666666, 'Pharmaceuticals: Generic': 445.4537495166667, 'Environmental Services': 427.42414624249994, 'Industrial Conglomerates': 381.26222285166665, 'Real Estate Development': 335.9241725678571, 'Textiles': 325.63964133999997, 'Pharmaceuticals: Major': 295.06382824346247, 'Chemicals: Major Diversified': 290.9925318593333, 'Oilfield Services/Equipment': 287.1272382184376, 'Savings Banks': 286.0331221057377, 'Marine Shipping': 279.15753586756756, 'Computer Communications': 273.22282087062496, 'Medical/Nursing Services': 249.99864315296892, 'Precious Metals': 241.83745785214285, 'Broadcasting': 234.09968746423075, 'Electric Utilities': 230.05444791459448, 'Publishing: Books/Magazines': 222.45412176142858, 'Major Telecommunications': 187.11052311040004, 'Oil & Gas Pipelines': 178.55357621815787, 'Other Metals/Minerals': 173.88342531851058, 'Aluminum': 163.92353846999998, 'Pulp & Paper': 157.65121615666666, 'Investment Trusts/Mutual Funds': 151.84723146487744, 'Food Distributors': 138.1486828155556, 'Real Estate Investment Trusts': 106.88921717055696, 'Electronics/Appliances': 92.39827916947368, 'Specialty Telecommunications': 80.48579182692308, 'Commercial
# Printing/Forms': 65.74337884333335, 'Alternative Power Generation': 25.09698436692308, 'Financial Conglomerates': 16.814883192053852, 'Miscellaneous': 2.9482565849999993}

# {'Energy Minerals': 8958.13016032492, 'Retail Trade': 8698.228317564275, 'Consumer Non-Durables': 4865.044319977079, 'Health Services': 4725.38479034206, 'Transportation': 3942.445852824269, 'Electronic Technology': 3234.5967022309255, 'Producer Manufacturing': 3189.9504164652626, 'Distribution Services': 3068.0191796886375, 'Process Industries': 2338.9747401651325, 'Technology Services': 2020.8373723043176, 'Consumer Durables': 2005.73241824509, 'Consumer Services': 1908.461459083596, 'Non-Energy Minerals': 1382.3872822813694, 'Industrial Services': 1290.1357461759874, 'Commercial Services': 1267.8498299711794, 'Health Technology': 1048.8936889225663, 'Finance': 679.8521223151956, 'Utilities': 388.46009277574075, 'Communications': 352.7545819773438, 'Miscellaneous': 151.60057385878213}

# {'Oil & Gas Production': 18.325763181745426, 'Home Improvement Chains': 16.948352593649783, 'Managed Health Care': 4.514243733118532, 'Industrial Specialties': 2.2153088307799913, 'Department Stores': 1.5947569719673953, 'Airlines': 1.5061559048240332, 'Automotive Aftermarket': 1.4749710385270307, 'Electronics/Appliance Stores': 1.3101903467466423, 'Food: Meat/Fish/Dairy': 1.2807646220221018, 'Services to the Health
# Industry': 1.2013813120836143, 'Multi-Line Insurance': 0.9291332456264534, 'Beverages: Non-Alcoholic': 0.8452207569678525, 'Personnel Services': 0.7061564666118614, 'Railroads': 0.6608102987258725, 'Property/Casualty Insurance': 0.6533744652836658, 'Industrial Machinery': 0.6380954333842718, 'Steel': 0.593754802133156, 'Discount Stores': 0.5760513801769955, 'Cable/Satellite TV': 0.5489114628247027, 'Specialty Stores': 0.5346005530402007, 'Oil Refining/Marketing': 0.5317738614866451, 'Wholesale Distributors': 0.5058004962101545, 'Homebuilding': 0.5018173142480331, 'Drugstore Chains': 0.5004181299301158, 'Semiconductors': 0.49380861393601955, 'Air Freight/Couriers': 0.49105767504567044, 'Food: Specialty/Candy': 0.4817394447025135, 'Chemicals: Agricultural': 0.4807549997009997, 'Beverages: Alcoholic': 0.4549008216235154, 'Trucking': 0.4540822459250791, 'Financial Publishing/Services': 0.4383867187464095, 'Aerospace & Defense': 0.40873193181780787, 'Building Products':
# 0.386453653211316, 'Insurance Brokers/Services': 0.38208043029960387,
# 'Apparel/Footwear Retail': 0.3766977675115617, 'Engineering & Construction': 0.3684608360277796, 'Telecommunications Equipment': 0.36581495983386425, 'Restaurants': 0.35677886990778584, 'Tobacco': 0.3443102418079912, 'Household/Personal Care': 0.33926326612151775, 'Medical Specialties': 0.3310865142467504, 'Information Technology Services': 0.31564126911515794, 'Electronic Components': 0.3113331070414482, 'Construction Materials': 0.25621857597172343, 'Apparel/Footwear': 0.25151270238726264, 'Trucks/Construction/Farm Machinery': 0.23894638034517196, 'Forest Products': 0.23853931506842344, 'Electronic Equipment/Instruments': 0.23712369242816275, 'Agricultural Commodities/Milling': 0.20910571324692498, 'Metal Fabrication': 0.1937127105848626, 'Office Equipment/Supplies': 0.19156194195573623, 'Internet Retail': 0.19025685756323044, 'Other Transportation': 0.18896307005640423, 'Coal': 0.18872951032769145, 'Containers/Packaging': 0.1885736913312023, 'Home Furnishings': 0.18408746691949568, 'Packaged Software': 0.1777347476540283, 'Other Consumer Specialties': 0.17181507933970316, 'Recreational Products': 0.157414823863643, 'Chemicals: Specialty': 0.15666122868767343, 'Medical
# Distributors': 0.15563602337008348, 'Auto Parts: OEM': 0.15255989466382802, 'Electronic Production Equipment': 0.1502858958375555, 'Casinos/Gaming': 0.14155696491022954, 'Water Utilities': 0.1413232947850113, 'Hospital/Nursing Management': 0.13940482416790226, 'Contract Drilling': 0.13850799905719355, 'Medical/Nursing Services': 0.13760194297282477, 'Other Consumer Services': 0.13490276670138068, 'Investment Managers': 0.13208309180889918, 'Data Processing Services': 0.13183332639777584, 'Computer Processing Hardware':
# 0.12293958711459507, 'Regional Banks': 0.12153678430193039, 'Food Retail': 0.10634263922610247, 'Motor Vehicles': 0.10625714518101485, 'Miscellaneous Manufacturing': 0.09981755274783392, 'Wireless Telecommunications': 0.09739668471910869, 'Precious Metals': 0.08614443852955747, 'Hotels/Resorts/Cruise lines': 0.08474158471002236, 'Computer Peripherals': 0.0808921533578952, 'Marine Shipping': 0.08046338729117382, 'Food: Major Diversified': 0.07979288854798844, 'Gas Distributors': 0.07878310020899984, 'Integrated Oil': 0.07795983476333859, 'Major Banks': 0.07781233015884295, 'Life/Health Insurance': 0.07764487093285186, 'Electronics Distributors': 0.07575454235438608, 'Finance/Rental/Leasing':
# 0.0742594542789435, 'Pulp & Paper': 0.06743317809910615, 'Electrical Products': 0.06305644713435071, 'Specialty Insurance': 0.049969313065935175, 'Pharmaceuticals: Other': 0.04882681373058586, 'Environmental Services': 0.048093598969602136, 'Consumer Sundries': 0.04664193202950473, 'Investment Banks/Brokers': 0.04461118163335261, 'Savings Banks': 0.04383536637006914, 'Investment Trusts/Mutual Funds': 0.0423241231011186, 'Oilfield Services/Equipment':
# 0.03594420006170549, 'Movies/Entertainment': 0.034362353928659585, 'Textiles': 0.03384275104164629, 'Publishing: Newspapers': 0.03327427635803639, 'Internet Software/Services': 0.03022721702347543, 'Oil & Gas Pipelines': 0.02347434515395783, 'Electric Utilities': 0.022842120052087297, 'Publishing: Books/Magazines': 0.02002866902508054, 'Tools & Hardware': 0.01975024507665984, 'Major Telecommunications': 0.017169505883930403, 'Biotechnology': 0.01373726137967134, 'Other Metals/Minerals': 0.013667740191037848, 'Broadcasting': 0.010874136903531447, 'Real Estate Development': 0.010161120583081567, 'Computer Communications': 0.009177944573698197, 'Food Distributors': 0.007962295244921218, 'Pharmaceuticals: Major': 0.007866005063080902, 'Aluminum': 0.006970188797859461, 'Miscellaneous': 0.0020091447499463524}