from modules.aiztradingview import GetIndustryProfit, GetSectorProfit

industryList = [
    "Advertising/Marketing Services",
    "Aerospace & Defense",
    "Agricultural Commodities/Milling",
    "Air Freight/Couriers",
    "Airlines",
    "Alternative Power Generation",
    "Aluminum",
    "Apparel/Footwear",
    "Apparel/Footwear Retail",
    "Auto Parts: OEM",
    "Automotive Aftermarket",
    "Beverages: Alcoholic",
    "Beverages: Non-Alcoholic",
    "Biotechnology",
    "Broadcasting",
    "Building Products",
    "Cable/Satellite TV",
    "Casinos/Gaming",
    "Catalog/Specialty Distribution",
    "Chemicals: Agricultural",
    "Chemicals: Major Diversified",
    "Chemicals: Specialty",
    "Coal",
    "Commercial Printing/Forms",
    "Computer Communications",
    "Computer Peripherals",
    "Computer Processing Hardware",
    "Construction Materials",
    "Consumer Sundries",
    "Containers/Packaging",
    "Contract Drilling",
    "Data Processing Services",
    "Department Stores",
    "Discount Stores",
    "Drugstore Chains",
    "Electric Utilities",
    "Electrical Products",
    "Electronic Components",
    "Electronic Equipment/Instruments",
    "Electronic Production Equipment",
    "Electronics Distributors",
    "Electronics/Appliance Stores",
    "Electronics/Appliances",
    "Engineering & Construction",
    "Environmental Services",
    "Finance/Rental/Leasing",
    "Financial Conglomerates",
    "Financial Publishing/Services",
    "Food Distributors",
    "Food Retail",
    "Food: Major Diversified",
    "Food: Meat/Fish/Dairy",
    "Food: Specialty/Candy",
    "Forest Products",
    "Gas Distributors",
    "Home Furnishings",
    "Home Improvement Chains",
    "Homebuilding",
    "Hospital/Nursing Management",
    "Hotels/Resorts/Cruise lines",
    "Household/Personal Care",
    "Industrial Conglomerates",
    "Industrial Machinery",
    "Industrial Specialties",
    "Information Technology Services",
    "Insurance Brokers/Services",
    "Integrated Oil",
    "Internet Retail",
    "Internet Software/Services",
    "Investment Banks/Brokers",
    "Investment Managers",
    "Investment Trusts/Mutual Funds",
    "Life/Health Insurance",
    "Major Banks",
    "Major Telecommunications",
    "Managed Health Care",
    "Marine Shipping",
    "Media Conglomerates",
    "Medical Distributors",
    "Medical Specialties",
    "Medical/Nursing Services",
    "Metal Fabrication",
    "Miscellaneous",
    "Miscellaneous Commercial Services",
    "Miscellaneous Manufacturing",
    "Motor Vehicles",
    "Movies/Entertainment",
    "Multi-Line Insurance",
    "Office Equipment/Supplies",
    "Oil & Gas Pipelines",
    "Oil & Gas Production",
    "Oil Refining/Marketing",
    "Oilfield Services/Equipment",
    "Other Consumer Services",
    "Other Consumer Specialties",
    "Other Metals/Minerals", 
    "Other Transportation",
    "Packaged Software",
    "Personnel Services",
    "Pharmaceuticals: Generic",
    "Pharmaceuticals: Major",
    "Pharmaceuticals: Other",
    "Precious Metals",
    "Property/Casualty Insurance",
    "Publishing: Books/Magazines",
    "Publishing: Newspapers",
    "Pulp & Paper",
    "Railroads",
    "Real Estate Development",
    "Real Estate Investment Trusts",
    "Recreational Products",
    "Regional Banks",
    "Restaurants",
    "Savings Banks",
    "Semiconductors",
    "Services to the Health Industry",
    "Specialty Insurance",
    "Specialty Stores",
    "Specialty Telecommunications",
    "Steel",
    "Telecommunications Equipment",
    "Textiles",
    "Tobacco",
    "Tools & Hardware",
    "Trucking",
    "Trucks/Construction/Farm Machinery",
    "Water Utilities",
    "Wholesale Distributors",
    "Wireless Telecommunications"
]

resDict = {}
for industry in industryList:
    portfolio = GetIndustryProfit(industry)
    vol = 1/len(portfolio)
    total = 0
    for k, v in portfolio.items():
        performance = 1 + v/100
        total += vol * performance
    if total > 1:
        resDict[industry] = total
resDict = dict(sorted(resDict.items(), key=lambda item: item[1], reverse=True))
print(resDict)

resList = []
for k, v in resDict.items():
    resList.append(k)
print(resList)


def GetIndustry():
    global industryList
    loser = ['Airlines', 'Aluminum', 'Automotive Aftermarket', 'Consumer Sundries', 'Electronics/Appliance Stores', 'Electronics/Appliances', 'Financial Publishing/Services', 'Home Furnishings', 'Home Improvement Chains', 'Hospital/Nursing Management', 'Internet Retail', 'Major Telecommunications', 'Media Conglomerates', 'Other Consumer Specialties',
    'Pharmaceuticals: Generic', 'Publishing: Newspapers', 'Services to the Health Industry']

    for industry in industryList:
        data = GetIndustryProfit(industry)
        profit = False
        for k, v in data.items():
            if v > 0:
                profit = True
                break
        if not profit:
            loser.append(industry)
    print(loser)

sectorList = [
    "Commercial Services",
    "Communications",
    "Consumer Durables",
    "Consumer Non-Durables",
    "Consumer Services",
    "Distribution Services",
    "Electronic Technology",
    "Energy Minerals",
    "Finance",
    "Health Services",
    "Health Technology",
    "Industrial Services",
    "Miscellaneous",
    "Non-Energy Minerals", 
    "Process Industries",
    "Producer Manufacturing",
    "Retail Trade",
    "Technology Services",
    "Transportation",
    "Utilities"
]

def GetSector():
    global sectorList
    loser = []

    for sector in sectorList:
        data = GetSectorProfit(sector)
        profit = False
        for k, v in data.items():
            if v > 0:
                profit = True
                break
        if not profit:
            loser.append(sector)
    print(loser)